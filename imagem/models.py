from django.db import models
from objeto.models import Objeto


class Imagem(models.Model):
    LANGUAGES = (
        ('pt_BR', 'Português'),
        ('en_US', 'Inglês'),
        ('es_AR', 'Espanhol'),
    )
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50)
    image = models.ImageField(upload_to='image/', default="default.png")
    objeto = models.ForeignKey(Objeto, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome
