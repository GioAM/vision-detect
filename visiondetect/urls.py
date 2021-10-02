from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('objeto.urls')),
    path('', include('imagem.urls')),
    path('admin/', admin.site.urls),
]
