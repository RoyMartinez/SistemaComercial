from django.db import models
from inv.models import Sucursal, Estado

class TipoCambio(models.Model):
    fecha = models.DateField(auto_now_add=False)
    oficial = models.FloatField()
    compra = models.FloatField()
    venta = models.FloatField()

class Cajas(models.Model):
    codigo = models.CharField(max_length=4, primary_key=True)
    no_caja = models.IntegerField(unique=True)
    monto_max = models.FloatField(default=10000)   
    suc = models.ForeignKey(Sucursal, on_delete=models.CASCADE)

    def __str__(self):
        return self.codigo

class Naturaleza(models.Model):
    codigo = models.CharField(max_length=1, primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class TipoMovimiento(models.Model):
    codigo = models.CharField(max_length=2, primary_key=True)
    naturaleza = models.ForeignKey(Naturaleza, on_delete=models.CASCADE)
    movimiento = models.CharField(max_length=50)

    def __str__(self):
        return self.movimiento

class Registros(models.Model):
    caja = models.ForeignKey(Cajas, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.ForeignKey(TipoMovimiento, on_delete=models.CASCADE)
    referencia = models.CharField(max_length=50)
    total = models.FloatField(default=0)
    real = models.FloatField(default=0)
    nio_in = models.FloatField(default=0)
    usd_in = models.FloatField(default=0)
    tarjeta = models.FloatField(default=0)
    fenibillete = models.FloatField(default=0)
    nio_out = models.FloatField(default=0)
    usd_out = models.FloatField(default=0)
    voucher = models.CharField(max_length=20, null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, default=3)