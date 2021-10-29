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

    data = {
        'objeto': objeto_to_show,
        'imagens': imagens
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

        return redirect('/objeto/' + str(objeto_id))
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
    except Exception as e:
        print(e)

    return redirect('/objeto/' + str(objeto_id))


def delete_image(request, image_id):
    imagem = Imagem.objects.filter(id=image_id)[0]
    id = imagem.objeto.id
    if 'default.png' not in imagem.image.name:
        os.remove(imagem.image.name)
    Imagem.objects.filter(id=image_id).delete()
    return redirect('/objeto/' + str(id))
