import json
import re
import shutil
from time import gmtime, strftime
import os
import cv2
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from dispositivo.models import Dispositivo
from imagem.models import Imagem
from objeto.models import Objeto
from scripts.script import prepare_data
from visiondetect import settings
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import warnings
import time
from object_detection.utils import label_map_util
import tensorflow as tf
from object_detection.utils import visualization_utils as viz_utils
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

path_to_labels = 'C:/projetos/vision-detect/TensorFlow/workspace/training_demo/annotations/label_map.pbtxt'
path_to_saved_model = "C:/projetos/vision-detect/TensorFlow/workspace/training_demo/exported-models/my_model/" \
                      "saved_model"

print('Loading model...', end='')
start_time = time.time()
detect_fn = tf.saved_model.load(path_to_saved_model)
end_time = time.time()
elapsed_time = end_time - start_time
print('Done! Took {} seconds'.format(elapsed_time))
category_index = label_map_util.create_category_index_from_labelmap(path_to_labels)
print(category_index)
warnings.filterwarnings('ignore')


def index(request):
    all_dispositivos = Dispositivo.objects.filter().order_by("nome")
    all_objetos = Objeto.objects.filter().order_by("nome")

    data = {
        'dispositivos': all_dispositivos,
        'objetos': all_objetos
    }
    return render(request, 'index.html', data)


def adicionar_objeto(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        pasta = request.POST['pasta']
        pasta = re.sub(r"[^a-zA-Z0-9]", "", pasta)
        pasta = "\\{0}\\".format(pasta)
        new_objeto = Objeto.objects.create(nome=nome, pasta=pasta)
        new_objeto.save()
        os.makedirs(settings.MEDIA_ROOT + pasta, exist_ok=True)
        return redirect('/objeto/all')

    return render(request, 'objeto/novo_objeto.html')


def get_all_objetos(request):
    all_objetos = Objeto.objects.filter().order_by("id")

    data = {
        'objetos': all_objetos
    }
    return render(request, 'objeto/objetos.html', data)


def get_objeto(request, objeto_id):
    objeto_to_show = get_object_or_404(Objeto, pk=objeto_id)
    imagens = Imagem.objects.filter(objeto=objeto_id).order_by("id")
    total_imagens =  Imagem.objects.filter(objeto=objeto_id).count()

    data = {
        'objeto': objeto_to_show,
        'imagens': imagens,
        'total_imagens': total_imagens
    }
    return render(request, 'objeto/objeto.html', data)


def delete_objeto(request, objeto_id):
    objeto = Objeto.objects.filter(id=objeto_id)[0]
    try:
        shutil.rmtree(settings.MEDIA_ROOT + objeto.pasta)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    Objeto.objects.filter(id=objeto_id).delete()
    return redirect('/objeto/all')


def update_objeto(request, objeto_id):
    if request.method == 'POST':
        nome = request.POST['nome']
        pasta = request.POST['pasta']

        objeto_to_update = Objeto.objects.get(id=objeto_id)
        objeto_to_update.nome = nome
        objeto_to_update.pasta = pasta

        objeto_to_update.save()

        return redirect('/objeto/' + str(objeto_id))

    data = {
        "objeto": get_object_or_404(Objeto, pk=objeto_id),
    }
    return render(request, 'objeto/alterar_objeto.html', data)


def add_image(request, objeto_id):
    if request.method == 'POST':
        objeto = get_object_or_404(Objeto, pk=objeto_id)
        image = request.FILES['image']
        new_imagem = Imagem.objects.create(image=image, objeto=objeto)
        new_imagem.save()
        update_imagem = Imagem.objects.get(id=new_imagem.id)
        initial_path = update_imagem.image.path
        new_path = settings.MEDIA_ROOT + objeto.pasta + str(update_imagem.id) + ".jpg"
        update_imagem.image.name = new_path
        os.rename(initial_path, new_path)
        update_imagem.save()

        return redirect('/objeto/image/' + str(objeto_id))
    data = {
        'objeto_id': objeto_id,
        "dispositivo": Dispositivo.objects.filter(selecionado=True)[0]
    }
    return render(request, 'objeto/add_image.html', data)


def add_image_camera(request, objeto_id):
    dispositivo = Dispositivo.objects.filter(selecionado=True)[0]
    objeto = get_object_or_404(Objeto, pk=objeto_id)
    new_imagem = Imagem.objects.create(objeto=objeto)
    url = 'http://{0}:8080/?action=stream'.format(dispositivo.ip)
    try:
        cap = cv2.VideoCapture(url)
        ret, frame = cap.read()
        path = settings.MEDIA_ROOT + objeto.pasta + str(new_imagem.id) + ".jpg"
        cv2.imwrite(path, frame)
        cap.release()
        new_imagem.image.name = path
        new_imagem.save()

        print("path: {0}".format(path))
        print("objeto.pasta: {0}".format(objeto.pasta))
        print("settings.MEDIA_ROOT: {0}".format(settings.MEDIA_ROOT))

        os.system('labelImg {0} {1}'.format(path, objeto.nome))
    except Exception as e:
        print(e)

    return redirect('/objeto/image/' + str(objeto_id))


def delete_image(request, image_id):
    imagem = Imagem.objects.filter(id=image_id)[0]
    id = imagem.objeto.id
    if 'default.png' not in imagem.image.name:
        os.remove(imagem.image.name)
    Imagem.objects.filter(id=image_id).delete()
    return redirect('/objeto/' + str(id))


def treinamento(request):
    return render(request, 'funcao/treinamento.html')


def deteccao(request):
    return render(request, 'funcao/deteccao.html')


def about(request):
    return render(request, 'about.html')


def dataset(request):
    all_objetos = Objeto.objects.filter().order_by("id")
    prepare_data(all_objetos)
    return redirect('/treinamento')


def detect_objects(request):

    path_image = 'C:/projetos/vision-detect/visiondetect/static/detection/'
    time_now = strftime("%Y%m%d%H%M%S", gmtime())
    image_origin = path_image + time_now + "_origin.jpg"
    name_image_final = time_now + "_final.jpg"
    image_final = path_image + name_image_final
    min_score = 0.75

    cap = cv2.VideoCapture('http://192.168.1.113:8080/?action=stream')
    ret, frame = cap.read()

    print("found frame")
    cv2.imwrite(image_origin, frame)
    image_path = image_origin
    print('Running inference for {}... '.format(image_path), end='')

    image_np = load_image_into_numpy_array(image_path)
    input_tensor = tf.convert_to_tensor(image_np)
    input_tensor = input_tensor[tf.newaxis, ...]
    detections = detect_fn(input_tensor)
    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
    detections['num_detections'] = num_detections
    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)
    image_np_with_detections = image_np.copy()

    viz_utils.visualize_boxes_and_labels_on_image_array(
        image_np_with_detections,
        detections['detection_boxes'],
        detections['detection_classes'],
        detections['detection_scores'],
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=200,
        min_score_thresh=min_score,
        agnostic_mode=False)
    plt.figure()
    plt.imshow(image_np_with_detections)
    print(detections['detection_classes'].astype(np.int64))
    print(detections['detection_scores'])
    plt.savefig(image_final)

    contagem = return_objets_count(detections['detection_classes'].astype(np.int64), detections['detection_scores'],
                                   min_score)
    data = {'imagem': '/static/detection/' + name_image_final, 'contagem': json.dumps(contagem)}
    return JsonResponse(data)


def load_image_into_numpy_array(path):
    return np.array(Image.open(path))


def return_objets_count(id_objects, scores, min_score):
    contagem = {}
    for i in range(0, len(id_objects)):
        sc_i = scores[i]
        if sc_i > min_score:
            r_objeto = get_object_or_404(Objeto, pk=id_objects[i])
            if r_objeto.nome in contagem:
                contagem[r_objeto.nome] = contagem[r_objeto.nome] + 1
            else:
                contagem[r_objeto.nome] = 1
    print(contagem)
    return contagem

