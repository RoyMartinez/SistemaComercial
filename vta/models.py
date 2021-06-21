from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from inv import models as inventario
from caja.models import Cajas
from datetime import date, datetime

class Uniones(models.Model):# debe incluir Particular
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']

class Cooperativa(models.Model):# debe incluir Particular
    nombre = models.CharField(max_length=255,unique=True)
    union = models.ForeignKey(Uniones, on_delete=models.PROTECT)
    segmento = models.CharField(max_length=1, choices=(('0','Particular'),('1','Cooperativa'),('2','Empleados')), default='1')

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']

class Membresia(models.Model):# debe incluir PArticular
    descripcion = models.CharField(max_length=30, unique=True)
    prioridad = models.IntegerField(default=0)
    descuento = models.DecimalField(max_digits=6, decimal_places=4, default=0)

    def __str__(self):
        return self.descripcion

class Cliente(models.Model):
    civil = [('C','Casado / Casada'),('U','Unión'),('S','Soltero / Soltera'),('V','Viudo / Viuda'),]
    identificacion = models.CharField(max_length=15, primary_key=True)
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    correo = models.CharField(max_length=100, null=True, blank=True)
    membresia = models.ForeignKey(Membresia, on_delete=models.CASCADE, default=1)
    estado_civil = models.CharField(max_length=1, choices=civil, default='S')
    dependientes = models.IntegerField(default=0)
    limite_credito = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    saldo = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    cooperativa = models.ManyToManyField(Cooperativa, default=1)
    tipo = models.CharField(max_length=1, default='N') #N=Normal, C=Cooperativa
    magnetico = models.CharField(max_length=255, unique=True)
    descuento = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    def __str__(self):
        return (self.nombres + ' ' + self.apellidos).title()

class ClienteTelefono(models.Model):
    telefonos = [('C','Claro'),('M','Movistar'),('O','Cootel')]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15)  #Aqui debe ser UNIQUE, pero hay conflictos de constraint con la tabla temporal
    operador = models.CharField(max_length=1, choices=telefonos, default='C')
    valido = models.BooleanField(default=True)
    predeterminado = models.BooleanField(default=False)

    def __str__(self):
        return self.telefono

class ClienteDireccion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=255)
    valido = models.BooleanField(default=True)
    predeterminado = models.BooleanField(default=False)

    def __str__(self):
        return self.direccion

class ClienteDocumento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=100)
    nota = models.CharField(max_length=100, null=True, blank=True)
    rutaimagen = models.CharField(max_length=500)

    def __str__(self):
        return self.descripcion

class ClienteVehiculoColor(models.Model):
    codigo = models.CharField(max_length=7, primary_key=True)
    descripcion = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.descripcion

class ClienteVehiculo(models.Model):
    chasis = models.CharField(max_length=20, primary_key=True)
    placa = models.CharField(max_length=10, null=True, blank=True)
    motor = models.CharField(max_length=50)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    color = models.ForeignKey(ClienteVehiculoColor, on_delete=models.CASCADE)
    circulacion = models.CharField(max_length=9, null=True, blank=True)
    observaciones = models.CharField(max_length=100, null=True, blank=True)
    modelo = models.ForeignKey(inventario.ModeloVehiculo, on_delete=models.CASCADE)

    def __str__(self):
        return self.chasis

class Condicion(models.Model):
    nombre = models.CharField(max_length=45, choices=[('Contado','Contado'),('Credito','Credito')], unique=True)

    def __str__(self):
        return self.nombre

class Vendedores(models.Model):
    identificacion = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    genero = models.CharField(max_length=1, choices=[('M','Masculino'),('F','Femenino')])
    codigo_empleado = models.CharField(max_length=5, unique=True)
    activo = models.BooleanField(default=True)   
    cajero = models.ForeignKey(Cajas, on_delete=models.CASCADE, default='ES01')

class Forma_pago(models.Model):
    condicion = models.ForeignKey(Condicion, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.nombre

class Facturamsr(models.Model):
    referencia = models.CharField(max_length=20, primary_key=True)
    serie = models.CharField(max_length=20, unique=True)
    formapago = models.ForeignKey(Forma_pago, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(inventario.Sucursal, on_delete=models.CASCADE)
    fechaemision = models.DateTimeField(auto_now_add=True)
    fechavencimiento = models.DateField(auto_now=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    membresia = models.IntegerField(default=1)
    cooperativa = models.IntegerField(default=1)
    vendedor = models.ForeignKey(Vendedores, on_delete=models.CASCADE)
    estado = models.ForeignKey(inventario.Estado, on_delete=models.CASCADE)
    preciofinaltotal = models.DecimalField(max_digits=19, decimal_places=4)
    descuentotal = models.DecimalField(max_digits=19, decimal_places=4)
    extradescuento = models.FloatField(default=0)
    impuestototal = models.DecimalField(max_digits=19, decimal_places=4)
    impreso = models.SmallIntegerField(default=0)
    nombre = models.CharField(max_length=80, null=True, blank=True)
    cct = models.CharField(max_length=20, null=True, blank=True, default='0')
    monto_cct = models.FloatField(default=0)

class InstanciaFactMsr(models.Model):
    formapago = models.ForeignKey(Forma_pago, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(inventario.Sucursal, on_delete=models.CASCADE)
    fechaemision = models.DateTimeField(auto_now_add=True)
    fechavencimiento = models.DateField(auto_now=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    membresia = models.IntegerField(default=1)
    cooperativa = models.IntegerField(default=1)
    vendedor = models.ForeignKey(Vendedores, on_delete=models.CASCADE)
    preciofinaltotal = models.DecimalField(max_digits=19, decimal_places=4)
    descuentotal = models.DecimalField(max_digits=19, decimal_places=4)
    extradescuento = models.FloatField(default=0)
    impuestototal = models.DecimalField(max_digits=19, decimal_places=4)
    nombre = models.CharField(max_length=80, null=True, blank=True)
    cct = models.CharField(max_length=20, null=True, blank=True, default='0')
    monto_cct = models.FloatField(default=0)
    borrador = models.ForeignKey(inventario.TempCatalogoMsr, on_delete=models.CASCADE, default=1)
    origen = models.CharField(max_length=20, default='Fact')

class Proformamsr(models.Model):
    referencia = models.CharField(max_length=20, primary_key=True)
    formapago = models.ForeignKey(Forma_pago, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(inventario.Sucursal, on_delete=models.CASCADE)
    fechaemision = models.DateTimeField(auto_now_add=True)
    fechavencimiento = models.DateField(auto_now=False)
    cliente = models.ForeignKey(Cliente,on_delete=models.CASCADE)
    membresia = models.IntegerField(default=1)
    cooperativa = models.IntegerField(default=1)
    vendedor = models.ForeignKey(Vendedores, on_delete=models.CASCADE)
    estado = models.ForeignKey(inventario.Estado, on_delete=models.CASCADE)
    descuento = models.FloatField()
    extradescuento = models.FloatField(default=0)
    impuesto = models.FloatField()
    costo = models.FloatField()
    nombre = models.CharField(max_length=80, null=True, blank=True)

class Proformadet(models.Model):
    referencia = models.ForeignKey(Proformamsr, on_delete=models.CASCADE)
    item = models.ForeignKey(inventario.N4Item, on_delete=models.CASCADE)
    unidades = models.IntegerField()
    preciobase = models.FloatField()
    descuento = models.FloatField()
    impuesto = models.FloatField()
    bodega = models.ForeignKey(inventario.Bodega, null=True, blank=True, on_delete=models.CASCADE)

class Facturadet(models.Model): # Primero se lee la sucursal, luego por el tipo de pago, memebresia
    referencia = models.ForeignKey(Facturamsr, on_delete=models.CASCADE)
    bodega = models.ForeignKey(inventario.Bodega, on_delete=models.CASCADE)
    item = models.ForeignKey(inventario.N4Item, on_delete=models.CASCADE)
    unidades = models.IntegerField()
    preciofinal = models.DecimalField(max_digits=19, decimal_places=4)
    descuento = models.DecimalField(max_digits=19, decimal_places=4)
    impuesto = models.DecimalField(max_digits=19, decimal_places=4)
    costo = models.DecimalField(max_digits=19, decimal_places=4)
    tipoexo = models.ForeignKey(inventario.ExoTipo, on_delete=models.CASCADE)
    comercializacion = models.SmallIntegerField(default=0)
    devuelto = models.IntegerField(default=0)

class ExoRubroCliente(models.Model):
    fecha = models.DateField(auto_now_add=True)
    referencia = models.CharField(max_length=50, default='nothing')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    cooperativa = models.CharField(max_length=100, default='nothing')
    rubro = models.ForeignKey(inventario.ExoRubro, on_delete=models.CASCADE, default=1)
    costo = models.FloatField(default=0)
    precio = models.FloatField(default=0)
    unidades = models.FloatField(default=0)

class TempCombo(models.Model):
    cata = models.ForeignKey(inventario.TempCatalogo, on_delete=models.CASCADE)
    item = models.ForeignKey(inventario.N4Item, on_delete=models.CASCADE)

class PermisosCliente(models.Model):
    modelo = models.CharField(max_length=30, primary_key=True)
    clave = models.CharField(max_length=255) 

    def __str__(self):
        return self.modelo

class IncentivoMsr(models.Model):
    referencia = models.CharField(max_length=20, primary_key=True)
    fecha = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    estado = models.ForeignKey(inventario.Estado, on_delete=models.CASCADE, default=3)
    centro_costo = models.ForeignKey(inventario.CentroCosto, on_delete=models.CASCADE)
    ajuste = models.CharField(max_length=20, choices=[('Entrada', 'Entrada'),('Salida','Salida')])
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class IncentivoDet(models.Model):
    referencia = models.ForeignKey(IncentivoMsr, on_delete=models.CASCADE)
    item = models.ForeignKey(inventario.N4Item, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    debe = models.DecimalField(max_digits=10, decimal_places=2, default=0)
