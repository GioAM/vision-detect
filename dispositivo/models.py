from django.db import models


class Dispositivo(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50)
    ip = models.CharField(max_length=50)
    selecionado = models.BooleanField(default=False)

    def __str__(self):
        return self.nome