from django.urls import path
from . import views

urlpatterns = [
    path('camera', views.camera, name='camera'),
    path('rodar_camera', views.rodar_camera, name='rodar_camera')
]
