from django.shortcuts import render, redirect
from dispositivo.models import Dispositivo
from objeto.models import Objeto


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
        new_objeto = Objeto.objects.create(nome=nome, pasta=pasta)
        new_objeto.save()

        return redirect('/')

    return render(request, 'objeto/novo_objeto.html')
