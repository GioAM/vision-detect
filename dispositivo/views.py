from django.shortcuts import render, redirect
from dispositivo.models import Dispositivo


def select_dispositivo(request, dispositivo_id):
    Dispositivo.objects.filter().update(selecionado=False)
    dispositivo_to_update = Dispositivo.objects.get(id=dispositivo_id)
    dispositivo_to_update.selecionado = True
    dispositivo_to_update.save()

    return redirect('/')


def adicionar_dispositivo(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        ip = request.POST['ip']
        new_dispositivo = Dispositivo.objects.create(nome=nome, ip=ip, selecionado=False)
        new_dispositivo.save()

        return redirect('/')

    return render(request, 'dispositivo/novo_dispositivo.html')


def deletar_dispositivo(request, dispositivo_id):
    Dispositivo.objects.filter(id=dispositivo_id).delete()
    return redirect('/')


def camera(request):
    data = {
        "dispositivo": Dispositivo.objects.filter(selecionado=True)[0]
    }
    return render(request, 'dispositivo/camera.html', data)