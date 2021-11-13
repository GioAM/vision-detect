from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('objeto/add', views.adicionar_objeto, name='adicionar_objeto'),
    path('objeto/all', views.get_all_objetos, name='get_all_objetos'),
    path('objeto/<int:objeto_id>', views.get_objeto, name='get_objeto'),
    path('objeto/delete/<int:objeto_id>', views.delete_objeto, name='delete_objeto'),
    path('objeto/update/<int:objeto_id>', views.update_objeto, name='update_objeto'),
    path('objeto/image/<int:objeto_id>', views.add_image, name='add_image'),
    path('objeto/camera/<int:objeto_id>', views.add_image_camera, name='add_image_camera'),
    path('objeto/del_image/<int:image_id>', views.delete_image, name='deletar_image'),
    path('treinamento', views.treinamento, name='treinamento'),
    path('treinamento/dataset', views.dataset, name='dataset')
]
