from django.urls import path
from . import views

urlpatterns = [
    path('teste', views.index, name='index'),
]