from django.contrib import admin

from dispositivo.models import Dispositivo
from imagem.models import Imagem
from objeto.models import Objeto

admin.site.register(Objeto)
admin.site.register(Dispositivo)
admin.site.register(Imagem)
