from django.db import models


class Objeto(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50)
    pasta = models.CharField(max_length=50)

    def __str__(self):
        return self.nome
