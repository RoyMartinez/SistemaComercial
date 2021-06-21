from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

class N1Rubro(models.Model):
    id_n1 = models.CharField(max_length=3,primary_key = True)
    descripcion = models.CharField(max_length=100)
    codigo_sac = models.CharField(max_length=20)
    def __str__(self):
        return self.descripcion

class N2Familia(models.Model):
    id_n2  = models.CharField(max_length=7,primary_key=True)
    descripcion = models.CharField(max_length=100)
    codigo = models.CharField(max_length=3)
    rubro = models.ForeignKey(N1Rubro,on_delete = models.CASCADE,)
    def __str__(self):
        return self.descripcion

class ExoTipo(models.Model):
    id_exo = models.CharField(max_length=1, primary_key=True)
    nombre = models.CharField(max_length=15)
    def __str__(self):
        return self.nombre

class ExoRubro(models.Model):
    nombre = models.CharField(max_length=50,unique=True)
    unidades = models.BooleanField(default= False)
    costo = models.BooleanField(default= False)
    precio = models.BooleanField(default= False)
    def __str__(self):
        return self.nombre

class Um(models.Model):
    id_um = models.CharField(max_length=3, primary_key=True)
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre

class MarcaVehiculo(models.Model):
    siglas = models.CharField(max_length=2,primary_key=True)
    marca = models.CharField(max_length=45,unique = True)
    def __str__(self):
        return self.marca

class TipoVehiculo(models.Model):
    descripcion = models.CharField(max_length=30,unique = True)
    def __str__(self):
        return self.descripcion

class ModeloVehiculo(models.Model):
    id_modelo = models.CharField(max_length=14, primary_key=True)
    marca = models.ForeignKey(MarcaVehiculo,null=False, blank=False, on_delete=models.CASCADE)
    modelo = models.CharField(max_length=45)
    tipo = models.ForeignKey(TipoVehiculo, null=False, blank=False, on_delete=models.CASCADE)
    cilindraje = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.5)],default = 0.5)
    combustible = models.CharField(max_length=1,choices=[('G','Gasolina'),('D','Diesel')],default='G')
    anyo = models.CharField(max_length=10)
    def __str__(self):
        return self.modelo + ' ' + self.anyo

class N3Producto(models.Model):
    id_n3 = models.CharField(max_length = 251,primary_key= True)
    descripcion = models.CharField(max_length = 100,null = False)
    familia = models.ForeignKey(N2Familia,null= False,blank = False, on_delete = models.CASCADE)
    medida = models.ForeignKey(Um,null = False,blank =False,on_delete = models.CASCADE,default='UNI')
    # codfabrica = models.CharField(max_length = 20)
    sac  = models.CharField(max_length= 20)
    minimo = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    maximo = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    descontinuado = models.CharField(max_length=1,choices=[('S','Producto Descontinuado'),('N','Producto Activo')],default='N')
    costo = models.CharField(max_length=1,choices = [('S','Puede ser sin costo'),('N','Debe tener costo')],default = 'N')
    entero = models.CharField(max_length=1,choices=[('S','Se vende por toda la medida'),('N','Se vende por partes de la medida')],default='S')
    naturaleza = models.CharField(max_length=1,choices=[('C','Combo'),('D','Descuento'),('E','Elemento'),('P','Procesado'),('S','Servicio'),('U','Unico')],default='U')
    exorubro = models.ForeignKey(ExoRubro, on_delete = models.CASCADE,default='1')
    aplicacion = models.ManyToManyField(ModeloVehiculo,default = 'NE.NEE000')
    def __str__(self):
        return self.descripcion

class CodigoFabrica(models.Model):
    producto = models.ForeignKey(N3Producto,null = False,blank= False,on_delete = models.CASCADE)
    codfabrica = models.CharField(max_length = 255)
    class Meta:
        unique_together= (('producto','codfabrica'),)

class N3ProductoImagen(models.Model):
    producto = models.ForeignKey(N3Producto,null=True,blank=True,on_delete= models.CASCADE)
    ruta = models.ImageField(upload_to='inv/Producto/',blank = False, null = False)
    nota = models.CharField(max_length= 255)

class MarcaItem(models.Model):
    siglas = models.CharField(max_length=3,primary_key= True)
    marca = models.CharField(max_length=45)
    def __str__(self):
        return self.marca

class N4Item(models.Model):
    id_n4 = models.CharField(max_length=255,primary_key=True)
    descripcion = models.CharField(max_length=100,blank=True,null = True)
    producto = models.ForeignKey(N3Producto,on_delete= models.CASCADE)
    marca = models.ForeignKey(MarcaItem,on_delete= models.CASCADE)
    preciomax = models.FloatField(default= 1.0,validators=[MinValueValidator(0.0)])
    preciomin  = models.FloatField(default = 1.0,validators=[MinValueValidator(0.0)])
    codanterior = models.CharField(max_length=9)
    codbarra = models.CharField(max_length = 20,unique=True)
    sac = models.CharField(max_length=20)
    exotipo = models.ForeignKey(ExoTipo,null= False,blank = False,on_delete=models.CASCADE,default='G')
    cantidad_impuesto = models.PositiveIntegerField(default=15)
    minimo = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    maximo = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    descontinuado = models.CharField(max_length=1,choices=[('S','Item Descontinuado'),('N','Item Activo')],default='N')
    def __str__(self):
        return  self.producto.familia.descripcion +' '+self.producto.descripcion+' '+ self.marca.marca +' '+self.descripcion

class Sucursal(models.Model):
    siglas = models.CharField(max_length=2,primary_key=True)
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=255)
    telefonos = models.CharField(max_length=255)
    encabezado = models.CharField(max_length=255)
    pie_pagina = models.CharField(max_length=255)
    usuarios = models.ManyToManyField(User)
    serie = models.CharField(max_length=1,default='A', unique=True)
    existencia = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    saldo = models.FloatField(null=True,blank=True,validators=[MinValueValidator(0.0)],default=0)
    def __str__(self):
        return self.nombre

class TempCatalogoMsr(models.Model):
    borrador = models.IntegerField(default=1)
    cedula = models.CharField(max_length=15, default='0')
    nombre = models.CharField(max_length=100, default='PARTICULAR / INDIVIDUAL')
    cooperativa = models.IntegerField(default=1)
    membresia = models.IntegerField(default=1)
    tipopago = models.IntegerField(default=2)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)

class N4ItemCombo(models.Model):
    combo = models.ForeignKey(N4Item,null=False,blank=False,on_delete=models.CASCADE,related_name='Combo')
    item = models.ForeignKey(N4Item,null=False,blank=False,on_delete=models.CASCADE,related_name='Product')
    opcion = models.PositiveIntegerField()
    cantidad = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    precio = models.FloatField()
    def __str__(self):
        return '{}'.format(self.combo)

class N4ItemReceta(models.Model):
    receta = models.ForeignKey(N4Item,null=False,blank=False,on_delete=models.CASCADE,related_name='Receta')
    item = models.ForeignKey(N4Item,null=False,blank=False,on_delete=models.CASCADE,related_name='Ingrediente')
    cantidad = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    costo = models.FloatField(null=True,blank=True,validators=[MinValueValidator(0.0)])
    def __str__(self):
        return '{}'.format(self.receta)
    class Meta:
        unique_together= (('receta','item'),)

class N4ItemImagen(models.Model):
    item = models.ForeignKey(N4Item,null = False, blank = False,on_delete=models.CASCADE)
    ruta = models.ImageField(upload_to='inv/Item/',blank = False, null = False)
    nota = models.CharField(max_length = 255)
    
class Precio(models.Model):
    id_precio = models.CharField(max_length =1,primary_key=True)
    descripcion  = models.CharField(max_length=100)
    def __str__(self):
        return self.descripcion

class N4ItemXPrecio(models.Model):
    item = models.ForeignKey(N4Item, null=False, blank=False, on_delete=models.CASCADE)
    precio = models.ForeignKey(Precio, null=False, blank=False, on_delete=models.CASCADE)
    valor = models.FloatField()
    def __str__(self):
        return '{} -- {}'.format(self.precio,self.valor)
    class Meta:
        unique_together= (('item','precio'),)

class Bodega(models.Model):
    id_bodega = models.CharField(max_length=4,primary_key=True,default = 'DUTR')
    sucursal = models.ForeignKey(Sucursal,null = True, blank= True, on_delete = models.CASCADE, default = 'DU')
    siglas = models.CharField(max_length=2)
    nombre = models.CharField(max_length=50,unique = True)
    tipo = models.CharField(max_length=1,choices=[('F','Facturable'),('N','No facturable'),('T','Transito')],default='F')
    existencia = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    saldo = models.FloatField(null=True,blank=True,validators=[MinValueValidator(0.0)],default=0)
    def __str__(self):
        return self.nombre
    class Meta:
        unique_together= (('sucursal','siglas'),)
    

class TempCatalogo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    articulo = models.ForeignKey(N4Item, on_delete=models.CASCADE)
    cantidad = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    maestro = models.ForeignKey(TempCatalogoMsr, on_delete=models.CASCADE, default=1)
    bodega = models.ForeignKey(Bodega,null = True, blank= True,on_delete=models.CASCADE)

class ExistenciaBodega(models.Model):
    bodega = models.ForeignKey(Bodega,null = False, blank= False, on_delete = models.CASCADE)
    item = models.ForeignKey(N4Item,null = False, blank= False, on_delete = models.CASCADE)
    cantidad = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    def __str__(self):
        return self.bodega +' '+ self.item

class Estado(models.Model):
    estado_desc = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.estado_desc

class CentroCosto(models.Model):
    nombre = models.CharField(max_length=45)
    cuenta_contab = models.CharField(max_length=15)
    def __str__(self):
        return self.nombre

class AjusteTipo(models.Model):
    tipo_mov = models.CharField(max_length = 2)
    descripcion = models.CharField(max_length=20)
    def __str__(self):
        return self.descripcion

class DevolucionCondicion(models.Model):
    descripcion = models.CharField(max_length=45)
    valor = models.FloatField()
    def __str__(self):
        return self.descripcion
    class Meta:
        unique_together= (('descripcion'),)


class DevolucionMsr(models.Model):
    referencia = models.CharField(max_length=20,primary_key=True,default='DE-DU-31129999-00001')
    fecha = models.DateTimeField(auto_now_add = True)
    nota = models.CharField(max_length=255)
    notacredito = models.CharField(max_length=255)
    rem = models.CharField(max_length= 20,default = 'REM-001',null= True, blank = True)
    factura = models.CharField(max_length=20,default= 'SF-001',null = True,blank = True)
    sucursal = models.ForeignKey(Sucursal,null = False, blank= False, on_delete = models.CASCADE,default='DU')
    estado = models.ForeignKey(Estado, null = False, blank= False, on_delete = models.CASCADE,default = 4)
    costo_total = models.FloatField(null=True,blank=True)
    precio_total = models.FloatField(null=True,blank=True)
    impuesto_total = models.FloatField(null=True,blank=True)
    penalizacion_total = models.FloatField(null=True,blank=True)
    monto_total = models.FloatField(null=True,blank=True)

class DevolucionDet(models.Model):
    referencia = models.ForeignKey(DevolucionMsr,null = False, blank= False, on_delete = models.CASCADE)
    bodega = models.ForeignKey(Bodega,null = False, blank= False, on_delete = models.CASCADE)
    item = models.ForeignKey(N4Item,null = False, blank= False, on_delete = models.CASCADE)
    fecha_venc = models.CharField(null=True,blank=True,max_length=10)
    estado = models.ForeignKey(DevolucionCondicion,null = False, blank= False, on_delete = models.CASCADE,default=1)
    cantidad = models.FloatField()
    costo = models.FloatField(default=1)
    precio = models.FloatField(default=1)
    impuesto = models.FloatField(default=1)
    penalizacion = models.FloatField(default=1)
    monto = models.FloatField(default=1)
    def monto_penaliza(self):
        return self.penalizacion
    def costo_total(self):
        return (self.costo)
    class Meta:
        unique_together= (('referencia','bodega','item','estado'),)


class DevolucionDettemp(models.Model):
    referencia = models.ForeignKey(DevolucionMsr,null = False, blank= False, on_delete = models.CASCADE)
    bodega = models.ForeignKey(Bodega,null = False, blank= False, on_delete = models.CASCADE)
    item = models.ForeignKey(N4Item,null = False, blank= False, on_delete = models.CASCADE)
    fecha_venc = models.CharField(null=True,blank=True,max_length=10)
    estado = models.ForeignKey(DevolucionCondicion,null = False, blank= False, on_delete = models.CASCADE,default=1)
    cantidad = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    costo = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    precio = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    impuesto = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    penalizacion = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    monto = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    def monto_penaliza(self):
        return self.precio-(self.precio * self.penalizacion)
    def monto_penaliza(self):
        return self.costo-(self.costo * self.penalizacion)
    class Meta:
        unique_together= (('referencia','bodega','item','estado'),)

class TrasladoMsr(models.Model):
    referencia = models.CharField(max_length=20,primary_key=True,default='TR-DU-31129999-01-DU')
    fecha = models.DateTimeField(auto_now_add = True)
    estado = models.ForeignKey(Estado,null = False, blank= False, on_delete = models.CASCADE,default=4)
    nota = models.CharField(max_length=255)
    sucursal = models.ForeignKey(Sucursal,null = False, blank= False, on_delete = models.CASCADE,default='DU')
    sucursalD = models.ForeignKey(Sucursal,null = False, blank = False, on_delete=models.CASCADE,default = 'DU',related_name='Destino')

class TrasladoDet(models.Model):
    referencia = models.ForeignKey(TrasladoMsr,null = False, blank= False, on_delete = models.CASCADE)
    bodegaO = models.ForeignKey(Bodega,null = False, blank= False, on_delete = models.CASCADE,related_name='Origen')
    bodegaD = models.ForeignKey(Bodega,null = True, blank= True, on_delete = models.CASCADE,related_name='Destino')
    item = models.ForeignKey(N4Item,null = False, blank= False, on_delete = models.CASCADE)
    cantidad = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    costo = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    estado = models.ForeignKey(Estado,null=False,blank=False,on_delete=models.CASCADE,default=4)
    recepcionado = models.FloatField(null=True,blank=True,validators=[MinValueValidator(0.0)],default=0)

class TrasladoDettemp(models.Model):
    referencia = models.ForeignKey(TrasladoMsr,null = False, blank= False, on_delete = models.CASCADE)
    bodegaO = models.ForeignKey(Bodega,null = False, blank= False, on_delete = models.CASCADE,related_name='Origentemp')
    bodegaD = models.ForeignKey(Bodega,null = True, blank= True, on_delete = models.CASCADE,related_name='Destinotemp')
    item = models.ForeignKey(N4Item,null = False, blank= False, on_delete = models.CASCADE)
    cantidad = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    costo = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    estado = models.ForeignKey(Estado,null=False,blank=False,on_delete=models.CASCADE,default=4)

class AjusteMsr(models.Model):
    referencia = models.CharField(max_length=20,primary_key=True,default='AJ-DU-31129999-01-DU')
    fecha = models.DateTimeField(auto_now_add = True)
    nota = models.CharField(max_length=255) 
    sucursal = models.ForeignKey(Sucursal,null = False, blank= False, on_delete = models.CASCADE,default='DU')
    estado = models.ForeignKey(Estado,null = False, blank= False, on_delete = models.CASCADE,default=4)
    centro_costo = models.ForeignKey(CentroCosto,null = False, blank= False, on_delete = models.CASCADE,default=1)
    ajuste = models.ForeignKey(AjusteTipo,null = False, blank= False, on_delete = models.CASCADE,default=1)
    costo_total = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
   
class AjusteDet(models.Model):
    referencia = models.ForeignKey(AjusteMsr,null = False, blank= False, on_delete = models.CASCADE)
    bodega = models.ForeignKey(Bodega,null = False, blank= False, on_delete = models.CASCADE)
    fecha_venc = models.CharField(null=True,blank=True,max_length=10)
    item = models.ForeignKey(N4Item,null = False, blank= False, on_delete = models.CASCADE)
    cantidad = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    costo = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0) 
    def costo_unitario(self):
        return self.costo/self.cantidad
    class Meta:
        unique_together= (('referencia','bodega','item'),)


class AjusteDettemp(models.Model):
    referencia = models.ForeignKey(AjusteMsr,null = False, blank= False, on_delete = models.CASCADE)
    bodega = models.ForeignKey(Bodega,null = False, blank= False, on_delete = models.CASCADE)
    fecha_venc = models.CharField(null=True,blank=True,max_length=10)
    item = models.ForeignKey(N4Item,null = False, blank= False, on_delete = models.CASCADE)
    cantidad = models.FloatField()
    costo = models.FloatField(null=True,blank=True,validators=[MinValueValidator(0.0)])
    class Meta:
        unique_together= (('referencia','bodega','item'),)
    
class Kardex(models.Model):
    fecha = models.DateField(auto_now_add = True)
    sucursal = models.ForeignKey(Sucursal,null = False, blank= False, on_delete = models.CASCADE,default='DU')
    bodega = models.ForeignKey(Bodega,null = False, blank= False, on_delete = models.CASCADE, default='ESTR')
    item = models.ForeignKey(N4Item,null = False, blank= False, on_delete = models.CASCADE)
    referencia = models.CharField(max_length=20,default='referencia de apertura')
    entrada = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    salida = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    debe = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    haber = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    saldo = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    saldosuc = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    saldobod = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    costounitario = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    existencia = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    existenciasuc = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    existenciabod = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    tipotransaccion = models.CharField(max_length=2,choices=[('EE','Entrada'),('SS','Salida'),('EA','Entrada por Ajuste'),('SA','Salida por Ajuste'),('EC','Entrada por Costo'),('SC','Salida por Costo')],default='EE');
    estado = models.ForeignKey(Estado,null = False,blank = False, on_delete = models.CASCADE,default = '5')
    fecha_venc = models.DateField(default = '3030-12-31')
    bodega_fin = models.ForeignKey(Bodega,null = False, blank= False, on_delete = models.CASCADE, default='ESTR',related_name='Destinokardex')
    class Meta:
        unique_together= (('id','sucursal','item','referencia'),)

class item_costo(models.Model):
    item = models.OneToOneField(N4Item,null = False, blank= False, on_delete = models.CASCADE,primary_key=True)
    existencia = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    costo = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    saldo = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    preciomax = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    preciomin = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    
class item_costo_historico(models.Model):
    fecha = models.DateField(auto_now_add = True)
    item = models.ForeignKey(N4Item,null = False, blank= False, on_delete = models.CASCADE)
    existencia = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    costo = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    saldo = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    preciomax = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    preciomin = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    class Meta:
        unique_together= (('item','fecha'),)

class bodega_item_costo(models.Model):
    item = models.ForeignKey(N4Item,null = False, blank= False, on_delete = models.CASCADE)
    bodega = models.ForeignKey(Bodega,null = False, blank= False, on_delete = models.CASCADE, default='ESTR')
    existencia = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    saldo = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    class Meta:
        unique_together= (('bodega','item'),)

class bodega_item_costo_historico(models.Model):
    fecha = models.DateField(auto_now_add = True)
    item = models.ForeignKey(N4Item,null = False, blank= False, on_delete = models.CASCADE)
    bodega = models.ForeignKey(Bodega,null = False, blank= False, on_delete = models.CASCADE, default='ESTR')
    existencia = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    saldo = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    class Meta:
        unique_together= (('bodega','item','fecha'),)

class sucursal_item_costo(models.Model):
    item = models.ForeignKey(N4Item,null = False, blank= False, on_delete = models.CASCADE)
    sucursal = models.ForeignKey(Sucursal,null = False, blank= False, on_delete = models.CASCADE, default='ES')
    existencia = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    saldo = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    class Meta:
        unique_together= (('sucursal','item'),)

class sucursal_item_costo_historico(models.Model):
    fecha = models.DateField(auto_now_add = True)
    item = models.ForeignKey(N4Item,null = False, blank= False, on_delete = models.CASCADE)
    sucursal = models.ForeignKey(Sucursal,null = False, blank= False, on_delete = models.CASCADE, default='ES')
    existencia = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    saldo = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default=0)
    class Meta:
        unique_together= (('sucursal','item','fecha'),)

class N4ItemProduccion(models.Model):
    referencia = models.CharField(max_length=20, primary_key =True)
    item = models.ForeignKey(N4Item,null = False, blank= False, on_delete = models.CASCADE)
    fecha = models.DateTimeField(auto_now_add = True)
    bodegao = models.ForeignKey(Bodega,null = True, blank = True, on_delete=models.CASCADE,related_name='OrigenProduccion')
    bodegad = models.ForeignKey(Bodega,null = True, blank = True, on_delete=models.CASCADE,related_name='DestinoProduccion')
    cantidad = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    nota = models.CharField(max_length=50)
    fecha_venc = models.CharField(max_length=10)

class N4ItemVencimiento(models.Model):
    item = models.ForeignKey(N4Item,null = False, blank= False, on_delete = models.CASCADE)
    referencia = models.CharField(max_length=20)
    fecha_venc = models.DateTimeField()
    cantidad = models.FloatField(null=False,blank=False,validators=[MinValueValidator(0.0)],default = 0)
    fecha_cero = models.CharField(max_length = 10,null= True,blank = True,default='.')
    class Meta:
        unique_together= (('item','fecha_venc','referencia'),)

