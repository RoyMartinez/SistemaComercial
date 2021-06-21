from django.db import models
from inv.models import N4Item, Bodega, ExoTipo, Estado
from vta.models import Condicion, Cliente

class Proveedor(models.Model):
    abreviatura = models.CharField(max_length=4,primary_key=True)
    nombre = models.CharField(max_length=100)
    ruc = models.CharField(max_length=20, unique=True)
    web = models.CharField(max_length=45, null=True, blank=True, default='No posee')
    comentario = models.CharField(max_length=255, null=True, blank=True, default='.')

    def __str__(self):
        return self.nombre

class ProveedorContacto(models.Model):
    proveedor = models.ForeignKey(Proveedor,null = False,blank= False, on_delete= models.CASCADE)
    nombre = models.CharField(max_length=100)
    telefonos = models.CharField(max_length=255, default='505')
    cargo = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class ProveedorDireccion(models.Model):
    proveedor = models.ForeignKey(Proveedor,null = False,blank= False, on_delete= models.CASCADE)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=255, default='505')

    def __str__(self):
        return self.direccion

# ************  COTIZACION ***********************

class CotizacionMsr(models.Model):
    referencia = models.CharField(max_length=20, primary_key=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    notas = models.CharField(max_length=255, null=True, blank=True, default='.')
    finalizado = models.BooleanField(default=False)

    def __str__(self):
        return self.referencia

class CotizacionDet(models.Model):
    referencia = models.ForeignKey(CotizacionMsr, null=False, blank=False, on_delete=models.CASCADE)
    item = models.ForeignKey(N4Item, null=False, blank=False, on_delete=models.CASCADE)
    unidades = models.FloatField()

    class Meta:
        unique_together =(('referencia','item'),)

# ************  PROFORMA ***********************

class ProformaMsr(models.Model):
    referencia = models.CharField(max_length=20, primary_key=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    notas = models.CharField(max_length=255, default=".")
    cotizacion = models.ForeignKey(CotizacionMsr, null=True, blank=True, on_delete=models.CASCADE)
    finalizado = models.BooleanField(default=False)
    importado = models.BooleanField(default=False)

    def __str__(self):
        return self.referencia + ' | ' + self.proveedor.nombre

class ProforDet(models.Model):
    referencia = models.ForeignKey(ProformaMsr, null=False, blank=False, on_delete=models.CASCADE)
    item = models.ForeignKey(N4Item, null=False, blank=False, on_delete=models.CASCADE)
    unidades = models.FloatField()
    costo = models.FloatField()
    impuesto = models.FloatField()

    class Meta:
        unique_together =(('referencia','item'),)

# ************  ORDEN DE COMPRA ***********************

class OrdenCompraMsr(models.Model):
    referencia = models.CharField(max_length=20, primary_key=True)
    proveedor = models.ForeignKey(Proveedor, null=False, blank=False, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    proforma = models.ForeignKey(ProformaMsr, null=True, blank=True, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    vencimiento = models.DateField(null=True)
    condicion = models.ForeignKey(Condicion, on_delete=models.CASCADE, default=1)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    importado = models.BooleanField(default=False)
    recibido = models.BooleanField(default=False)
    tipo = models.CharField(max_length=1, choices=(('L', 'Local'),('I','Internacional')), default='L')
    moneda = models.CharField(max_length=1, choices=(('C','Cordobas'),('D','Dolares')), default='C')

    def __str__(self):
        return self.referencia + ' | ' + self.proveedor.nombre

class OrdenCompraDet(models.Model):
    referencia = models.ForeignKey(OrdenCompraMsr, null=False, blank=False, on_delete=models.CASCADE)
    item = models.ForeignKey(N4Item, null=False, blank=False, on_delete=models.CASCADE)
    unidades = models.FloatField()
    despachado = models.FloatField(default=0)
    costo = models.FloatField()
    impuesto = models.FloatField(default=0)
    fecha_venc = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        unique_together =(('referencia','item'),)

# ************  ENTRADA DE MERCADERIA ***********************

class EntradaMercaderiaMsr(models.Model):
    referencia = models.CharField(max_length=20,primary_key=True)
    proveedor = models.ForeignKey(Proveedor, null=False, blank=False, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    condicion = models.ForeignKey(Condicion, on_delete=models.CASCADE, default=1)
    fecha = models.DateTimeField(auto_now_add=True)
    facturas = models.CharField(max_length=255)
    ordenes_compra = models.ForeignKey(OrdenCompraMsr, on_delete=models.CASCADE, null=True, blank=True)
    fecha_vencimiento = models.DateTimeField()
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, default=4)
    poliza = models.CharField(max_length=50, default='0')
    costo_compra = models.FloatField(default=0)
    costo_iva = models.FloatField(default=0)

    def __str__(self):
        return self.referencia + ' | ' + self.proveedor.nombre

class EntradaMercaderiaDet(models.Model):
    referencia = models.ForeignKey(EntradaMercaderiaMsr,null=False,blank=False,on_delete=models.CASCADE)
    bodega = models.ForeignKey(Bodega,null= False, blank = False,on_delete=models.CASCADE)
    item = models.ForeignKey(N4Item,null= False,blank = False,on_delete=models.CASCADE)
    unidades = models.FloatField()
    costo = models.FloatField()
    impuesto = models.FloatField()
    tipo_exo = models.ForeignKey(ExoTipo, on_delete=models.CASCADE)
    fecha_venc = models.CharField(max_length=10, default='2020-04-16')
    devuelto = models.IntegerField(default=0)
    class Meta:
        unique_together =(('referencia','item','bodega'),)

class TempRem(models.Model):
    #bodega = models.ForeignKey(Bodega, null=True, blank=True, on_delete=models.CASCADE)
    item = models.ForeignKey(N4Item, on_delete=models.CASCADE)
    unidades = models.FloatField(default=0)
    costo = models.FloatField(default=0)
    impuesto = models.FloatField(default=0.15)
    tipo_exo = models.ForeignKey(ExoTipo, on_delete=models.CASCADE, default='G')
    editable = models.BooleanField(default=True) 
    orden = models.ForeignKey(OrdenCompraMsr, on_delete=models.CASCADE, null=True, blank=True)
    fecha_venc = models.CharField(max_length=10, null=True, blank=True)