from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('objeto/', include('objeto.urls')),
    path('imagem/', include('imagem.urls')),
    path('admin/', admin.site.urls),
]
