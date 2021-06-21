from django.db import models
#from inventario.models import Sucursal
from inv.models import Sucursal
from vta.models import Cliente, Cooperativa, Vendedores

class Monedas(models.Model):
    id_moneda = models.CharField(max_length=3, primary_key=True)
    descripcion = models.CharField(max_length=7,unique=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.descripcion

class Producto_tipos(models.Model):
    descripcion = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.descripcion

class Producto(models.Model):
    id_producto = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=50, unique=True)
    tipo_producto = models.ForeignKey(Producto_tipos, on_delete=models.CASCADE)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.descripcion

class Estado_prestamos(models.Model):
    descripcion = models.CharField(max_length=40, unique=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.descripcion

class Tipos_garantias(models.Model):
    descripcion = models.CharField(max_length=50, unique=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.descripcion

class Fondos(models.Model):
    descripcion = models.CharField(max_length=20, unique=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.descripcion

class Formas_recuperacion(models.Model):
    descripcion = models.CharField(max_length=30, unique=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.descripcion

class Frecuencias_pago(models.Model):
    descripcion = models.CharField(max_length=30, unique=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.descripcion

class Prestamos(models.Model):
    referencia = models.CharField(max_length=15, primary_key=True)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    consecutivo = models.BigIntegerField(unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    #cooperativa = models.ForeignKey(Cooperativa, on_delete=models.CASCADE)
    fondo = models.ForeignKey(Fondos, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_otorgado = models.DateField(auto_now_add=True)
    fecha_vence = models.DateField(auto_now=False)
    frecuencia_pago = models.ForeignKey(Frecuencias_pago, on_delete=models.CASCADE)
    principal = models.FloatField(default=0)
    moneda = models.ForeignKey(Monedas, on_delete= models.CASCADE)
    tipo_cambio = models.FloatField(default=0)
    principal_ofi = models.FloatField(default=0)
    numcuotas = models.IntegerField(default=0)
    cuota = models.FloatField(default=0)
    intcorriente = models.FloatField(default=3)
    intmoratorio = models.FloatField(default=1)
    gracia = models.IntegerField(default=0)
    notas = models.CharField(max_length=255, blank=True, null=True)
    estado_prestamo = models.ForeignKey(Estado_prestamos, on_delete=models.CASCADE)
    tipo_garantia = models.ForeignKey(Tipos_garantias, on_delete=models.CASCADE)
    formas_recuperacion = models.ForeignKey(Formas_recuperacion, on_delete=models.CASCADE)

    def __str__(self):
        return self.referencia

class EstadoCuenta(models.Model):
    fecha = models.DateField(auto_now_add=True)
    cliente=models.ForeignKey(Cliente, on_delete=models.CASCADE)
    referencia = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=100)
    debe = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    haber= models.DecimalField(max_digits=19, decimal_places=2, default=0)
    saldo= models.DecimalField(max_digits=19, decimal_places=2, default=0)

class Roc(models.Model):
    numero = models.CharField(max_length=10, primary_key=True)
    tipo = models.CharField(max_length=2, default='RC')
    fecha = models.DateField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    concepto = models.TextField(default='Abono', null=True, blank=True)
    vendedor = models.ForeignKey(Vendedores, on_delete=models.CASCADE)





