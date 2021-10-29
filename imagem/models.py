from django.db import models
from objeto.models import Objeto


class Imagem(models.Model):
    id = models.AutoField(primary_key=True)
    objeto = models.ForeignKey(Objeto, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='', default="default.png")

    def __str__(self):
        return str(self.id)
