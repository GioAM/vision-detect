from django.urls import path
from . import views


urlpatterns = [
    path('dispositivo/add', views.adicionar_dispositivo, name='adicionar_dispositivo'),
    path('dispositivo/select/<int:dispositivo_id>', views.select_dispositivo, name='select_dispositivo'),
    path('dispositivo/delete/<int:dispositivo_id>', views.deletar_dispositivo, name='deletar_dispositivo'),
]
