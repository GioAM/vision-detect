from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('objeto/add', views.adicionar_objeto, name='adicionar_objeto'),
]
