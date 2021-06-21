from django.db import models

class Condicion_consumo(models.Model):
    nombre_condicion = models.CharField(max_length=30, unique=True)
    tipo_condicion = models.CharField(max_length=2, primary_key=True)

    def __str__(self):
        return self.nombre_condicion
