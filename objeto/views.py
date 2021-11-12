import os
import re
import shutil
from aifc import Error

import cv2
from django.shortcuts import render, redirect, get_object_or_404
from dispositivo.models import Dispositivo
from imagem.models import Imagem
from objeto.models import Objeto
from visiondetect import settings
from PIL import Image


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
    all_objetos = Objeto.objects.filter().order_by("id")
    script = 'C:/projetos/vision-detect/TensorFlow/workspace/training_demo/scripts/preprocessing'
    labels = 'C:/projetos/vision-detect/TensorFlow/workspace/training_demo/annotations/label_map.pbtxt'
    annotations = 'C:/projetos/vision-detect/TensorFlow/workspace/training_demo/annotations'
    train = 'C:/projetos/vision-detect/TensorFlow/workspace/training_demo/images/train'
    test = 'C:/projetos/vision-detect/TensorFlow/workspace/training_demo/images/test'

    arquivo = open(labels, 'w')
    arquivo.close()
    try:
        shutil.rmtree(train)
        shutil.rmtree(test)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    for objeto in all_objetos:
        os.system('python {0}/partition_dataset.py -x -i {1}{2} -r 0.1'.format(
            script, settings.MEDIA_ROOT, objeto.pasta))
        arquivo = open(labels, 'a')
        arquivo.write("item{\n")
        arquivo.write("    id: {0}\n".format(str(objeto.id)))
        arquivo.write("    name: '{0}'\n".format(objeto.nome))
        arquivo.write("}\n")
        arquivo.close()

    os.system('python {0}/generate_tfrecord.py -x {1} -l {2} -o {3}/train.record'.format(
        script, train, labels, annotations))
    os.system('python {0}/generate_tfrecord.py -x {1} -l {2} -o {3}/test.record'.format(
        script, test, labels, annotations))

    return redirect('/objeto/1')

