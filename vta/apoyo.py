import datetime
from datetime import date
from com.models import CotizacionMsr, ProformaMsr, OrdenCompraMsr, EntradaMercaderiaMsr
from .models import Cliente, Forma_pago, Cooperativa, ExoRubroCliente, Membresia, TempCombo, InstanciaFactMsr, Facturamsr, Facturadet
from inv.models import TempCatalogo,ExoRubro, N4Item, N4ItemXPrecio, N4ItemCombo, Estado, Bodega, ExoTipo, TempCatalogoMsr, ExistenciaBodega, Kardex,N4ItemVencimiento
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from usuarios.models import LoggedInUser

def calcular_descuento(cli, fp, art):#Cliente, FormaPago, Articulo
    Client = get_object_or_404(Cliente,identificacion = cli)
    formPago = get_object_or_404(Forma_pago,pk = fp)
    item = get_object_or_404(N4Item,pk = art)
    descontar = 0
    #Tarjeta,efectivo,fenibillete
    if formPago.condicion.pk ==  1:
        nota_Cliente = float(Client.descuento/100)
        extra = float(0.15)
        porcentaje_descuento = float((1-extra)*nota_Cliente+extra)
        descontar = (item.preciomax-item.preciomin)*porcentaje_descuento
    #Credito
    if formPago.condicion.pk == 2:
        nota_Cliente = float(Client.descuento/100)
        extra = float(0.15)
        porcentaje_descuento = float((1-extra)*nota_Cliente)
        descontar = (item.preciomax-item.preciomin)*porcentaje_descuento
    #devolver lo descontado
    return descontar

def impuesto(temppk, xtra=0):
    tempo = TempCatalogo.objects.get(pk=temppk)
    descuento = calcular_descuento(tempo.maestro.cedula, tempo.maestro.tipopago, tempo.articulo.pk )
    xdescuento = (tempo.articulo.preciomax - descuento)*xtra/100
    iva = tempo.cantidad * (tempo.articulo.preciomax - descuento - xdescuento)* 0.15
    subtotal=0
    aux= False
    if tempo.articulo.producto.naturaleza != 'C': #Si no es un combo 
        if tempo.articulo.producto.exorubro.pk != 1 and tempo.articulo.exotipo.pk=='X': #Checar si el articulo es exonerable   
            exorubro=ExoRubroCliente.objects.filter(cliente=tempo.maestro.cedula, rubro=tempo.articulo.producto.exorubro.pk)
            cantidad = exorubro.filter(rubro__unidades=True).aggregate(u=Sum('unidades'))
            costo = exorubro.filter(rubro__costo=True).aggregate(cost=Sum('costo'))
            precio = exorubro.filter(rubro__precio=True).aggregate(p=Sum('precio'))   
            if cantidad['u']:
                if cantidad['u'] >= tempo.cantidad:
                    aux=True
            if precio['p']:
                if precio['p'] >= (tempo.cantidad * tempo.articulo.precio):
                    aux=True
            if aux:
                iva = 0                  
    else: # SI el item es Combo
        tcombo = TempCombo.objects.filter(cata=temppk)
        if tcombo:
            for i in tcombo:
                price = N4ItemCombo.objects.filter(combo=tempo.articulo.pk).get(item=i.item.pk)
                if i.item.n3.exo_rubro.pk != 1 and i.item.ExoTipo=='X': #Cheacr si el articulo es exonerable                                
                    cantidad = ExoRubroCliente.objects.filter(cliente=tempo.maestro.cedula, rubro=i.item.n3.exo_rubro.pk, rubro__unidades=True).aggregate(u=Sum('unidades'))
                    costo = ExoRubroCliente.objects.filter(cliente=tempo.maestro.cedula, rubro=i.item.n3.exo_rubro.pk, rubro__costo=True).aggregate(cost=Sum('costo'))
                    precio = ExoRubroCliente.objects.filter(cliente=tempo.maestro.cedula, rubro=i.item.n3.exo_rubro.pk, rubro__precio=True).aggregate(p=Sum('precio'))   
                    if cantidad['u']:
                        if cantidad['u'] >= (tempo.cantidad * price.cantidad):
                            aux=True
                    if precio['p']:
                        if precio['p'] >= (tempo.cantidad * price.precio):
                            aux=True
                    if aux:
                        iva = 0
                    else:
                        iva = tempo.cantidad * price.precio * 0.15 
                else:
                    iva = tempo.cantidad * price.precio * 0.15
    # print(tempo.articulo.exotipo.id_exo)
    if tempo.articulo.exotipo.id_exo == 'E':
        iva = 0.0
    subtotal = tempo.cantidad * tempo.articulo.preciomax
    return {'st':subtotal, 'iva':iva}

def prikey(sucursal, documento):
    suc = sucursal.sucursal.pk
    hoy=datetime.datetime.today()
    tomorrow=hoy + datetime.timedelta(days=1)
    if documento == '-CO-':
        x = CotizacionMsr.objects.all()
    elif documento == '-PF-':
        x = ProformaMsr.objects.all()
    elif documento=='-OC-':
        x = OrdenCompraMsr.objects.all()
    else:
        x = EntradaMercaderiaMsr.objects.all()
    contador = (x.filter(referencia__contains=suc, fecha__range=(hoy.date(),tomorrow.date())).count()) + 1
    contador ='{:0>2}'.format(contador)
    return suc + documento + hoy.strftime("%Y%m%d") + '-' + contador

def grabarFactura(request, valor):
    instancia = InstanciaFactMsr.objects.get(pk=valor)
    fact = Facturamsr.objects.filter(sucursal=instancia.sucursal.pk).count()
    f = Facturamsr.objects.create(
        referencia          = instancia.sucursal.pk + '-SV-00' + str(fact+1),
        serie               = instancia.sucursal.serie + '000000' + str(fact+1),
        formapago           = instancia.formapago,
        sucursal            = instancia.sucursal,
        fechavencimiento    = datetime.date.today() + datetime.timedelta(days=30),
        cliente             = instancia.cliente,
        membresia           = instancia.membresia,
        cooperativa         = instancia.cooperativa, 
        vendedor            = instancia.vendedor,
        estado              = Estado.objects.get(pk=3),
        preciofinaltotal    = instancia.preciofinaltotal,
        descuentotal        = instancia.descuentotal,
        extradescuento      = instancia.extradescuento,
        impuestototal       = instancia.impuestototal,
        impreso             = 0,
        nombre              = instancia.nombre,
        cct                 = instancia.cct,
        monto_cct           = instancia.monto_cct)
    tempo = TempCatalogo.objects.filter(usuario=request.user, sucursal=instancia.sucursal.pk, maestro=instancia.borrador)
    for i in tempo:
        if i.articulo.producto.naturaleza != 'C': # No es un combo
            exoneracion = impuesto(i.pk, xtra=f.extradescuento)
            desc = float(calcular_descuento(f.cliente.identificacion, f.formapago.pk, i.articulo.pk))
            xdesc = (i.articulo.preciomax - desc)*f.extradescuento/100 
            iva = 1 if exoneracion['iva'] == 0 else 1.15
            Facturadet.objects.create(
                referencia          = Facturamsr.objects.get(pk=f.pk),
                bodega              = Bodega.objects.get(pk=i.bodega.pk),
                item                = N4Item.objects.get(pk=i.articulo.id_n4),
                unidades            = i.cantidad,
                preciofinal         = i.cantidad * (i.articulo.preciomax - desc - xdesc) * iva,
                descuento           = i.cantidad * (desc + xdesc),
                impuesto            = exoneracion['iva'],
                costo               = 0,
                tipoexo             = ExoTipo.objects.get(pk='G'),
                comercializacion    = 1)

            #restamos su existencia
            exItem = ExistenciaBodega.objects.get(item = N4Item.objects.get(pk=i.articulo.id_n4), bodega = Bodega.objects.get(pk=i.bodega.pk) )
            exItem.cantidad -= i.cantidad
            exItem.save()

            #restamos su vencimiento
            cantidad = i.cantidad
            while cantidad > 0:
                vencimiento = N4ItemVencimiento.objects.filter(item =N4Item.objects.get(pk=i.articulo.id_n4)).exclude(cantidad = 0).order_by('fecha_venc').first()
                if vencimiento:
                    if cantidad > vencimiento.cantidad:
                        cantidad -= vencimiento.cantidad
                        vencimiento.cantidad = 0
                        vencimiento.fecha_cero = date.today().strftime('%Y-%m-%d')
                        vencimiento.save()
                    else:
                        vencimiento.cantidad -= cantidad
                        cantidad = 0
                        vencimiento.save()
                else:
                    cantidad = 0
                    
            #ingresamos su registro en el kardex
            inKardex = Kardex.objects.create(
                sucursal = instancia.sucursal,
                bodega = i.bodega,
                item = N4Item.objects.get(pk=i.articulo.id_n4),
                referencia = f.pk,
                salida = i.cantidad,
                haber = 0,
                existencia = exItem.cantidad,
                tipotransaccion = 'SS'
            )
            if iva == 1: #Si hay exoneracion
                coop = Cooperativa.objects.get(pk=i.maestro.cooperativa)
                cant=cost=prec=0
                if i.articulo.producto.exorubro.unidades:
                    cant = i.cantidad
                if i.articulo.producto.exorubro.costo:
                    cost = 0,
                if i.articulo.producto.exorubro.precio:
                    prec = i.cantidad * i.articulo.preciomax
                ExoRubroCliente.objects.create(
                    referencia = f.pk, cooperativa = coop, costo = cost * -1, precio = prec * -1,
                    unidades = cant * -1, cliente = Cliente.objects.get(pk=f.cliente.pk),
                    rubro = ExoRubro.objects.get(pk=i.articulo.producto.exorubro.pk)
                                )
        else: #Si el item es un combo
            Facturadet.objects.create(
                referencia          = Facturamsr.objects.get(pk=f.pk),
                bodega              = Bodega.objects.get(pk=i.bodega.pk),
                item                = N4Item.objects.get(pk=i.articulo.id_n4),
                unidades            = i.cantidad,
                preciofinal=0, descuento=0, impuesto=0, costo=0,
                tipoexo             = ExoTipo.objects.get(pk='G'),
                comercializacion    = 1)
            itemcombo = TempCombo.objects.filter(cata=i.pk)
            for j in itemcombo:
                Facturadet.objects.create(
                    referencia          = Facturamsr.objects.get(pk=f.pk),
                    bodega              = Bodega.objects.get(pk=i.bodega.pk),
                    item                = N4Item.objects.get(pk=j.item.id_n4),
                    unidades            = i.cantidad,
                    preciofinal         = i.cantidad * float(j.item.precio) * iva,
                    descuento           = 0,
                    impuesto            = i.cantidad * float(j.item.precio) *0.15,
                    costo               = 0,
                    tipoexo             = ExoTipo.objects.get(pk='G'),
                    comercializacion    = 1)
            itemcombo.delete() 
    maestro = TempCatalogoMsr.objects.get(pk=instancia.borrador.pk)
    maestro.cedula = '0'
    maestro.nombre = 'PARTICULAR / INDIVIDUAL'
    maestro.membresia = 1
    maestro.cooperativa =1
    maestro.tipopago =2
    maestro.save()
    tempo.delete()
    instancia.delete()
    #voucher.auto_facturar(f.pk)
    return f   

def calculo(vendedor):
    subtotal,iva = 0,0
    tempo = TempCatalogo.objects.filter(usuario=vendedor).annotate(factor=ExpressionWrapper(
            F('cantidad')*F('articulo__precio') + F('cantidad')* F('articulo__precio') * 0.15,
            output_field=FloatField()))
    for i in tempo:
        #if i.articulo.especificacion == "G":
        iva += i.cantidad * i.articulo.precio * 0.15
        subtotal += i.cantidad * i.articulo.precio
    resultado = {}
    resultado['subtotal'] = subtotal
    resultado['iva'] = iva
    resultado['tempo'] = tempo
    return resultado 

def reino(request):
    r = LoggedInUser.objects.get(user=request.user)
    if r.sucursal.pk == 'DU':
        raise PermissionDenied()
    else:
        return None

def existencias(arreglo,bodega):
    pass
    #for i in arreglo:
        #cant = ExistenciaBodega.objects.filter(bodega=bodega).get(item=i.)

def combo(item, bodega):
    respuesta={}
    modal,oferta=False,True
    itemcombo = N4ItemCombo.objects.filter(combo=item).order_by('opcion')
    if itemcombo:
        encabezado=menu=''
        contador=0
        for i in itemcombo:
            opciones=itemcombo.filter(opcion=i.opcion).count() #Cuento el numero de opciones
            if opciones > 1:
                if contador != i.opcion: 
                    encabezado='<br><p><strong>Opcion ' + str(i.opcion) + ':</strong></p><hr>'
                    contador=i.opcion
                else:
                    encabezado=''
                menu += encabezado + '<input class="combo" type="radio" checked name="'+ str(i.opcion) +'" value="'+str(i.pk)+'"> '+ str(i.item) + '<br>'
                modal=True
        respuesta['menu']=menu
    return respuesta
        #if not modal:
            #Validar existencias