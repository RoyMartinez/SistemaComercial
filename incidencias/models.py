from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class catInforme(models.Model):
    descripcion = models.CharField(max_length=200)
    def __str__(self):
        return self.descripcion

class catSeccion(models.Model):
    informe = models.ForeignKey(catInforme,null = False, blank= False, on_delete = models.CASCADE)
    descripcion = models.CharField(max_length = 200)
    def __str__(self):
        return self.descripcion

class catArea(models.Model):
    seccion = models.ForeignKey(catSeccion,null = False, blank = False, on_delete = models.CASCADE)
    descripcion = models.CharField(max_length = 200)
    def __str__(self):
        return self.descripcion

class catEnunciado(models.Model):
    descripcion  = models.CharField(max_length = 200)
    def __str__(self):
        return self.descripcion

class catResultado(models.Model):
    descripcion = models.CharField(max_length= 200)
    def __str__(self):
        return self.descripcion

class catPregunta(models.Model):
    area = models.ForeignKey(catArea,null = False, blank = False, on_delete = models.CASCADE)
    enunciado = models.ForeignKey(catEnunciado,null = False, blank = False, on_delete = models.CASCADE)
    def __str__(self):
        return self.seccion +' '+ self.enuncionado

class catRespuesta(models.Model):
    enunciado = models.ForeignKey(catEnunciado, null = False, blank = False, on_delete = models.CASCADE)
    resultado = models.ForeignKey(catResultado, null = False, blank = False, on_delete = models.CASCADE)

class supervisor(models.Model):
    codigoempleado = models.CharField(max_length=4,primary_key = True)
    nombre  = models.CharField(max_length=75)
    def __str__(self):
        return self.nombre

class documentoMsr(models.Model):
    referencia = models.CharField(max_length=15,primary_key=True,default='ES-31129999-001')
    informe = models.ForeignKey(catInforme,null = False, blank = False , on_delete = models.CASCADE)
    fecha = models.DateField(auto_now_add = True)
    turno = models.CharField(max_length=1,choices=[('D','Diurno'),('N','Nocturno')],default='D')
    supervisor = models.ForeignKey(supervisor,null = False, blank = False, on_delete = models.CASCADE)
    corte = models.CharField(max_length= 20)
    def __str__(self):
        return self.referencia

class documentoDet(models.Model):
    maestro = models.ForeignKey(documentoMsr,null = False, blank = False, on_delete = models.CASCADE)
    pregunta = models.ForeignKey(catPregunta, null = False, blank = False, on_delete = models.CASCADE)
    respuesta = models.ForeignKey(catRespuesta, null = False, blank = False, on_delete = models.CASCADE)
    hora = models.TextField(null = True)
    nota = models.TextField(null = True)




