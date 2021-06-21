from django.contrib.auth.models import User
from django.db.models import Sum, F, FloatField, ExpressionWrapper, Q
from django.http import JsonResponse
from . import models as tabla
from inv.models import TempCatalogo, N4Item, ExistenciaBodega, N4ItemXPrecio, Sucursal, TempCatalogoMsr, ModeloVehiculo, ExoTipo, Bodega, N4ItemCombo, ExoRubro
from com.models import TempRem, CotizacionMsr, ProformaMsr, OrdenCompraMsr, OrdenCompraDet
from usuarios.models import LoggedInUser
from .apoyo import impuesto, calcular_descuento

def obtener_items(request):
    x = request.GET.get('item')
    if x:
        consulta = N4Item.objects.filter(
                Q(item__n3__familia__descripcion__icontains=x)
                 | Q(item__marca__marca__icontains=x) | Q(item__n3__descripcion__icontains=x) | Q(item__descripcion__icontains=x))
    return JsonResponse(consulta)

def obtener_proveedor(request):
    ref = request.GET.get('ref')
    if ref[3:5] == 'CO':
        consulta = CotizacionMsr.objects.get(pk=ref)
    else:
        consulta = ProformaMsr.objects.get(pk=ref)
    prov = {}
    prov['proveedor'] = consulta.proveedor.pk
    return JsonResponse(prov)

# --------------- COMPRAS --------------------
def guardarrem(request, oc):
    mercaderia = list(request.GET.get('item').split(','))
    regalia = ''
    for i in range(0, len(mercaderia), 2):
        try:
            ocdet = OrdenCompraDet.objects.filter(referencia=oc).get(item=mercaderia[i])
        except OrdenCompraDet.DoesNotExist:
            try:
                tempo= TempRem.objects.filter(orden=oc).get(item=mercaderia[i])
            except TempRem.DoesNotExist:
                TempRem.objects.create(item=N4Item.objects.get(pk=mercaderia[i]), 
                    unidades=float(mercaderia[i+1]), costo=0, impuesto=0, editable=False, 
                    orden=OrdenCompraMsr.objects.get(pk=oc))
    tempo = TempRem.objects.all()
    if tempo:
        regalia += '<tr><td colspan="7">Regalias</td></tr>'
        for i in tempo:
            regalia += (
                            '<tr>'+
                                '<td>'+ str(i.item.pk) + '</td>'+
                                '<td>'+str(i.unidades) +'</td>'+
                                '<td>0.0</td>'+
                                '<td>0.0</td>'+
                                '<td>0.0</td>'+
                                '<td>Gravado</td>'+
                            
                                '<td>'+
                                '<input id="r'+ str(i.pk) + '" type="date" class="form-control form-control-sm det fecha" step="any" value="'+ str(i.fecha_venc)+'" onchange="actualizavenc(this.id,this.value)" >'+
                                '</td>'+

                                '<td>'+
                                    '<a href="/compras/rem/quitar/'+ str(i.pk) +'/" class="delete" title="Eliminar" data-placement="auto">'+
                                    '<i class="fa fa-trash" aria-hidden="true"></i></a>'+
                                '</td>'+
                            '</tr>' 
                        ) 
    respuesta = {}
    respuesta['regalia'] = regalia
    return JsonResponse(respuesta)

def actualizarrem(request):
    mercaderia = request.GET.get('item')
    tempo = TempRem.objects.get(pk=mercaderia)
    tempo.save()
    respuesta={}
    respuesta['ok']='ok'
    return JsonResponse(respuesta)

def cantidadrem(request):
    mercaderia = request.GET.get('item')
    cant = request.GET.get('cant') 
    cost = request.GET.get('costo') 
    tempo = TempRem.objects.get(pk=mercaderia)
    tempo.unidades = cant
    tempo.costo = cost
    tempo.save()
    respuesta={}
    respuesta['ok']='ok'
    return JsonResponse(respuesta)

def exorem(request):
    mercaderia = request.GET.get('item')
    exo = request.GET.get('exo') 
    tempo = TempRem.objects.get(pk=mercaderia)
    tempo.tipo_exo = ExoTipo.objects.get(pk=exo)
    imp = 0 if exo=='E' else 0.15
    tempo.impuesto = imp
    tempo.save()
    respuesta={}
    respuesta['ok']='ok'
    return JsonResponse(respuesta)

#para actualizar las fechas de vencimiento
def fechavencrem(request):
    codigo = request.GET.get('id') 
    fecha = request.GET.get('fecha') 
    print(codigo[:1])
    print(fecha)
    if codigo[:1] == 'o':#viene de la orden de commpra(ordencompradet)
        print('entre')
        item_oc = OrdenCompraDet.objects.get(pk = codigo[1:])
        item_oc.fecha_venc = fecha
        item_oc.save()
    if codigo[:1] == 'r':#viene de la regalia(temprem)
        print(codigo[1:])
        item_regalia = TempRem.objects.get(pk = codigo[1:])
        item_regalia.fecha_venc = fecha
        item_regalia.save()
    respuesta={}
    respuesta['ok']='ok'
    return JsonResponse(respuesta)


def recalculo(request):
    tem_cat = TempCatalogo.objects.filter(usuario=request.user)
    respuesta={}
    if tem_cat:    
        subtotal = TempCatalogo.objects.filter(usuario=request.user).aggregate(
            suma=Sum(F('articulo__precio')*F('cantidad'), output_field=FloatField()))
        subtotal = round(float(subtotal['suma']),2)
        for i in tem_cat:
            x = N4ItemXPrecio.objects.filter(item=i.articulo.pk).get(precio=prec.precio.pk)
            desc += (x.valor * i.cantidad)
        respuesta['descuento'] = desc
        respuesta['subtotal'] = subtotal
        respuesta['iva'] = round((subtotal -desc) * 0.15,2)
        respuesta['total'] = round(subtotal - desc + respuesta['iva'],2)
    else:
        respuesta['descuento'] = 0
        respuesta['subtotal'] = 0
        respuesta['iva'] = 0
        respuesta['total'] = 0
    return JsonResponse(respuesta)

# --------------- FACTURACION --------------------
def obtener_cliente(request, borra):
    ced = request.GET.get('cedula')
    response=exoneracion={}
    memb = coop = ''
    if ced:
        if borra == 989:
            data = tabla.Cliente.objects.get(pk=ced)
            #Calcular el incentivo disponible
            incentivo = tabla.IncentivoMsr.objects.filter(cliente=data.pk).aggregate(suma=Sum('monto'))
            response['incentivo'] = incentivo['suma'] if incentivo['suma'] else '0.00'
        else:
            try:
                data = tabla.Cliente.objects.get(magnetico=ced)
                suc = LoggedInUser.objects.get(user=request.user) 
                iva=subtotal=descuento=0       
                response['nombre'] = (data.nombres).title() + ' ' + (data.apellidos).title()
                cliente = TempCatalogoMsr.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk).get(borrador=borra)
                cliente.cedula = data.pk
                cliente.nombre = data.nombres + ' ' + data.apellidos
                cliente.save()
                response['existe'] = 0
                response['credito'] = str(data.saldo)
                # for i in data.membresia.all():
                memb += '<option value="' + str(data.pk) + '" selected>' + str(data.membresia.descripcion) + '</option>'
                cliente.membresia = int(data.membresia.pk)
                cliente.save()
                for i in data.cooperativa.all():
                    coop += '<option value="' + str(i.pk) + '" selected>' + str(i) + '</option>'
                    cliente.cooperativa = int(i.pk)
                    cliente.save()
                consulta = TempCatalogo.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk, maestro=cliente.pk)
                if consulta: #Si hay elementos facturados
                    for i in consulta:
                        exoneracion= impuesto(i.pk)
                        iva += exoneracion['iva']
                        subtotal += exoneracion['st']
                        descuento += (calcular_descuento(cliente.cedula,cliente.tipopago,i.articulo.pk)*i.cantidad)
                response['cedula'] = data.pk
                response['subtotal'] = round(subtotal,2)
                response['iva']= round((iva),2)
                response['membresia'] = memb
                response['cooperativa'] = coop
                response['descuento'] = round(descuento,2)
                response['total']=round(subtotal-descuento+iva,2)
            except tabla.Cliente.DoesNotExist:
                try:
                    permisos = tabla.PermisosCliente.objects.filter(modelo='Cliente').get(clave=ced)
                    response['existe'] =  1
                except tabla.PermisosCliente.DoesNotExist:
                    response['existe'] = 2
    return JsonResponse(response)

def reset_cliente(request, borra):
    suc = LoggedInUser.objects.get(user=request.user)
    respuesta={}
    subtotal = iva = 0
    cliente = TempCatalogoMsr.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk).get(borrador=borra)
    cliente.cedula ='0'
    cliente.nombre='PARTICULAR / INDIVIDUAL'
    cliente.cooperativa = 1
    cliente.membresia=1
    cliente.tipopago=2
    cliente.save()
    consulta = TempCatalogo.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk, maestro=cliente.pk)
    if consulta:
        for i in consulta:
            subtotal += i.cantidad * i.articulo.precio
            iva += i.cantidad * i.articulo.precio * 0.15
    respuesta['subtotal'] = round(subtotal,2)
    respuesta['iva'] =  round(iva, 2)
    respuesta['total'] = round(subtotal + iva,2)
    return JsonResponse(respuesta)

def temporal_item(request, borra):
    """ Almacena en una tabla temporal los items registrados durante la facturacion """
    suc = LoggedInUser.objects.get(user=request.user)
    cliente = TempCatalogoMsr.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk).get(borrador=borra)
    art = list(request.GET.get('item').split(','))
    respuesta = {}
    modal=False
    for i in art:
        elemento = ExistenciaBodega.objects.get(pk=i)
        consulta = TempCatalogo.objects.filter(articulo=elemento.item.pk, usuario=request.user,
                sucursal=suc.sucursal.pk, maestro=cliente.pk, bodega=elemento.bodega.pk)
        if elemento.item.producto.naturaleza != 'C':
            if not consulta:
                TempCatalogo.objects.create(usuario=request.user, articulo=N4Item.objects.get(pk=elemento.item.pk),  
                    cantidad=1, sucursal=Sucursal.objects.get(pk=suc.sucursal.pk), maestro=cliente,
                    bodega=Bodega.objects.get(pk=elemento.bodega.pk))
        else: #Entonces si es un combo
            itemcombo = N4ItemCombo.objects.filter(combo=elemento.item.pk).order_by('opcion')
            if itemcombo:
                titulo=x=''
                contador=0
                for j in itemcombo:
                    opciones=itemcombo.filter(opcion=j.opcion).count()
                    if opciones > 1:
                        if contador != j.opcion:
                            titulo = '<br><p><strong>Opcion ' + str(j.opcion) + ':</strong></p><hr>'
                            contador = j.opcion
                        else:
                            titulo = ''
                        x += titulo + '<input class="combo" type="radio" checked name="'+ str(j.opcion) +'" value="'+str(j.pk)+'"> '+ str(j.item) + '<br>'
                        modal=True   #else modal=False
                respuesta['opciones']=x
                if not modal:
                    existe=True
                    if not consulta:
                        #Validar existencias
                        for l in itemcombo:
                            existencia = ExistenciaBodega.objects.filter(bodega=elemento.bodega.pk).get(item=l.item.pk)
                            if l.cantidad > existencia.cantidad:
                                respuesta['excedente'] = True
                                existe=False
                                break
                        if existe:
                            respuesta['excedente'] = False
                            tmpcmb = TempCatalogo.objects.create(usuario=request.user, articulo=N4Item.objects.get(pk=elemento.item.pk),  
                                cantidad=1, sucursal=Sucursal.objects.get(pk=suc.sucursal.pk), maestro=cliente,
                                bodega=Bodega.objects.get(pk=elemento.bodega.pk))
                            for k in itemcombo:
                                tabla.TempCombo.objects.create(cata=TempCatalogo.objects.get(pk=tmpcmb.pk), item=N4Item.objects.get(pk=k.item.pk))
    respuesta['modal']=modal
    return JsonResponse(respuesta)

def descuento(request, borra):
    suc = LoggedInUser.objects.get(user=request.user)
    cliente = TempCatalogoMsr.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk).get(borrador=borra)
    tem_cat = TempCatalogo.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk, maestro=cliente.pk)
    respuesta ={}
    subtotal=desc=iva=0
    if tem_cat: #Si existen items
        para = list(request.GET.get('parametros').split(','))
        cat = tabla.Membresia.objects.get(pk=para[0])
        pago = tabla.Forma_pago.objects.get(pk=para[1])
        prec = tabla.Precio_formula.objects.filter(categoria=cat.pk).get(tipopago=pago)
        #ya conozco el precio ahora quiero buscar el valor del descuento en la tabla item por precio
        #calculo subtotal
        subtotal = TempCatalogo.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk, maestro=cliente.pk).aggregate(
            suma=Sum(F('articulo__precio')*F('cantidad'), output_field=FloatField()))
        subtotal = round(float(subtotal['suma']),2)
        for i in tem_cat:
            x = N4ItemXPrecio.objects.filter(item=i.articulo.pk).get(precio=prec.precio.pk)
            desc += i.cantidad * (i.articulo.precio - x.valor)
            exoneracion = impuesto(i.pk)
            if exoneracion['iva']:
                iva += i.cantidad * (i.articulo.precio - desc) * 0.15
    respuesta['subtotal'] = subtotal
    respuesta['descuento'] = desc
    respuesta['iva'] = round(iva,2)
    respuesta['total'] = round(subtotal - desc + iva,2)
    return JsonResponse(respuesta)

def actualizar_temp(request, borra):
    suc = LoggedInUser.objects.get(user=request.user)
    cabecera = TempCatalogoMsr.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk).get(borrador=borra)
    qty = list(request.GET.get('cantidad').split(',')) #idTempCatalogo, cantidad
    respuesta = {}
    respuesta['excedente'] = False
    actualizar = TempCatalogo.objects.get(pk=qty[0])
    # How many items exist within the branch
    articulos = ExistenciaBodega.objects.filter(bodega=actualizar.bodega.pk).get(item=actualizar.articulo.pk)
    #Compare qty[1] vs articulos.cantidad
    if float(qty[1]) > float(articulos.cantidad):
        actualizar.cantidad = 1
        actualizar.save()
        respuesta['excedente'] = True
    else:
        actualizar.cantidad = float(qty[1])
        actualizar.save()
    temporal = TempCatalogo.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk, maestro=cabecera.pk)
    subtotal = temporal.aggregate(suma=Sum(F('articulo__preciomax')*F('cantidad'), output_field=FloatField()))
    subtotal = round(float(subtotal['suma']),2)
    tabla1 = ''
    iva=descuento=0 
    for i in temporal:
        tabla1 +=  ('<tr>'+
                    '<td>'+ str(i.articulo.pk) + '</td>'+
                    '<td>'+ str(i.bodega.pk) +'</td>'+                   
                    '<td>'+
                    '<input id="' + str(i.pk) + '" class="form-control form-control-sm cant" style="width:4em;" type="number" value="' + str(i.cantidad) + '" min="1" step="1" onkeypress="return event.charCode >= 48 && event.charCode <= 57 || event.charCode == 13;" onchange="multiplicar(this);">'+
                    '</td>'+
                    '<td>' + str(round(i.articulo.preciomax * i.cantidad,2)) + '</td>'+ 
                    '<td>'+'<a href="/ventas/facturar/quitar/' + str(i.pk) +'/" class="delete" title="Eliminar" data-placement="auto">'
                    '<i class="fa fa-trash"></i></a>'+
                    '</td>'
                    '</tr>')
        exoneracion = impuesto(i.pk)
        iva += exoneracion['iva']
        descuento += (calcular_descuento(cabecera.cedula,cabecera.tipopago,i.articulo.pk)*i.cantidad)
    respuesta['tabla'] = tabla1 + '<tr><td colspan="4" style="text-align: center;"><a href="#" onclick="location.reload();"><i class="fas fa-sync-alt"></i> Haga clic aqu&iacute; para refrescar</a></td></tr>'
    respuesta['subtotal'] = subtotal
    respuesta['descuento'] = descuento
    respuesta['iva'] = round(iva,2)
    respuesta['total'] = round(subtotal - descuento + iva,2)
    return JsonResponse(respuesta)

def obtener_marca(request):
    """ Almacena en una tabla temporal los items registrados durante la facturacion """
    vehiculo = request.GET.get('marca')
    modelo = ModeloVehiculo.objects.filter(marca=vehiculo)
    opcion = '<option value="" selected="">---------</option>'
    for i in modelo:
        opcion += f'<option value="{i.pk}">{i.modelo} {i.anyo}</option>'
    respuesta = {}
    respuesta['opcion'] = opcion
    return JsonResponse(respuesta)

def producto_mk(request, borra):
    pdto = request.GET.get('producto')
    suc = LoggedInUser.objects.get(user=request.user)
    cabecera = TempCatalogoMsr.objects.filter(usuario=request.user,sucursal=suc.sucursal.pk).get(borrador=borra)
    tabla1 = x = ''
    subtotal=iva=0
    encontrado=True
    combo=existe=modal=False
    try: #Si el producto ya existe
        barra = N4Item.objects.get(codbarra=pdto)
    except N4Item.DoesNotExist:
        try:
            barra = N4Item.objects.get(pk=pdto)
        except N4Item.DoesNotExist:     
            encontrado=False
    if encontrado:
        if barra.producto.naturaleza != 'C': #Si no es combo
            bod = Bodega.objects.filter(tipo='F', sucursal=suc.sucursal.pk)
            for i in bod:
                existencia = ExistenciaBodega.objects.filter(bodega=i.pk).get(item=barra.pk)
                try:
                    temporal = TempCatalogo.objects.filter(
                        usuario=request.user, sucursal=suc.sucursal.pk, maestro=cabecera.pk, bodega=i.pk).get(
                        articulo=barra.pk)
                    if temporal.cantidad < existencia.cantidad:
                        temporal.cantidad += 1
                        temporal.save()
                        existe=True
                        break
                except TempCatalogo.DoesNotExist: #Si el producto no esta en la tabla temporal
                    if existencia.cantidad >= 1:
                        TempCatalogo.objects.create(usuario=request.user, articulo=N4Item.objects.get(pk=barra.pk), 
                            cantidad=1, sucursal=Sucursal.objects.get(pk=suc.sucursal.pk), maestro=cabecera,
                            bodega=Bodega.objects.get(pk=i.pk))  
                        existe=True
                        break
        else: #Si es combo
            combo=True  
            itemcombo = N4ItemCombo.objects.filter(combo=barra.pk).order_by('opcion')
            if itemcombo: #SI hay elementos en item combo                
                contador = 0
                bod = Bodega.objects.filter(tipo='F', sucursal=suc.sucursal.pk).first()
                for i in itemcombo:
                    opciones = itemcombo.filter(opcion=i.opcion).count()
                    if opciones > 1:
                        if contador != i.opcion:
                            titulo = f'<br><p><strong>Opcion {i.opcion}:</strong></p><hr>'
                            contador = i.opcion
                        else:
                            titulo = ''
                        x += titulo + f'<input class="combo" type="radio" checked name="{i.opcion}" value="{i.pk}">{i.item}<br>' 
                        modal=True  
                if not modal:
                    try:
                        temporal = TempCatalogo.objects.filter(usuario=request.user, 
                        sucursal=suc.sucursal.pk, maestro=cabecera.pk, bodega=bod.pk).get(articulo=barra.pk)
                        temporal.cantidad += 1
                        temporal.save()
                        existe=True
                    except TempCatalogo.DoesNotExist:  
                        tmpcmb = TempCatalogo.objects.create(usuario=request.user, articulo=N4Item.objects.get(pk=barra.pk), 
                        cantidad=1, sucursal=Sucursal.objects.get(pk=suc.sucursal.pk), maestro=cabecera,
                        bodega=Bodega.objects.get(pk=bod.pk))  
                        for i in itemcombo:
                            tabla.TempCombo.objects.create(cata=TempCatalogo.objects.get(pk=tmpcmb.pk), item=N4Item.objects.get(pk=i.item.pk))
    temporal = TempCatalogo.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk, maestro=cabecera.pk)
    if temporal:
        subtotal = TempCatalogo.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk, maestro=cabecera.pk).aggregate(
            suma=Sum(F('articulo__preciomax')*F('cantidad'), output_field=FloatField()))
        subtotal = round(float(subtotal['suma']),2)
        for i in temporal:
            tabla1 += ('<tr><td>'+ str(i.articulo.pk) + '</td>'
                    '<td>'+ str(i.bodega.pk) +'</td>' 
                    '<td>'
                    '<input id="' + str(i.pk) + '" class="form-control form-control-sm cant" style="width:4em;" type="number" value="' + str(i.cantidad) + '" min="1" step="1" onkeypress="return event.charCode >= 48 && event.charCode <= 57 || event.charCode == 13;" onchange="multiplicar(this);"></td>'
                    '<td>' + str(round(i.articulo.preciomax * i.cantidad,2)) + '</td>' 
                    '<td>'
                    '<a href="/ventas/facturar/quitar/' + str(i.pk) +'/" class="delete" title="Eliminar" data-placement="auto">'
                    '<i class="fa fa-trash"></i></a></td>'
                    '</tr>')
            exoneracion = impuesto(i.pk)          
            iva += exoneracion['iva']
    respuesta={}
    respuesta['tabla'] = tabla1 + '<tr><td colspan="5" style="text-align: center;"><a href="#" onclick="location.reload();"><i class="fas fa-sync-alt"></i> Haga clic aqu&iacute; para refrescar</a></td></tr>'
    respuesta['encontrado'] = encontrado
    respuesta['subtotal'] = subtotal
    respuesta['iva'] = iva
    respuesta['existe'] = existe
    respuesta['combo']=combo
    respuesta['opciones']=x
    respuesta['modal']=modal
    return JsonResponse(respuesta)

def exocliente(request):
    """ Al seleccionar una cooperativa devuelve los clientes que pertenecen a ella"""
    coop = request.GET.get('cooperativa')
    c = r = ''
    if int(coop) > 0:
        try:
            cliente = tabla.Cliente.objects.filter(cooperativa=coop).get(tipo='C')
            b = tabla.ExoRubroCliente.objects.filter(cliente=cliente.pk)
            rubro = ExoRubro.objects.filter(nombre__in=[i.rubro for i in b])
            c = r = ''
            for i in rubro:
                r += '<option value="' + str(i.pk) + '">' + str(i.nombre) + '</option>'
            cliente = tabla.Cliente.objects.filter(cooperativa=coop).order_by('nombres')
            for i in cliente:
                c += '<option value="' + str(i.pk) + '">' + str(i.nombres) + str(i.apellidos) +  '</option>'
        except tabla.Cliente.DoesNotExist:
            c = r = '<option value="" selected>------------</option>'
    else:
        c = '<option value="0">Todos</option>'
    respuesta={}
    respuesta['rubro'] = r
    respuesta['cliente'] = c
    return JsonResponse(respuesta)

def armarcombo(request, borra):
    cmb = list(request.GET.get('seleccion').split(','))
    suc = LoggedInUser.objects.get(user=request.user)
    cliente = TempCatalogoMsr.objects.filter(usuario=request.user,sucursal=suc.sucursal.pk).get(borrador=borra)
    bod = Bodega.objects.filter(tipo='F', sucursal=suc.sucursal.pk).first()
    #I want to know which combo it belongs to
    itemcombo = N4ItemCombo.objects.get(pk=cmb[0])
    tmpcmb = TempCatalogo.objects.create(usuario=request.user, articulo=N4Item.objects.get(pk=itemcombo.combo.pk), 
        cantidad=1, sucursal=Sucursal.objects.get(pk=suc.sucursal.pk), maestro=cliente,
        bodega=Bodega.objects.get(pk=bod.pk))  
    todocombo = N4ItemCombo.objects.filter(combo=itemcombo.combo).order_by('opcion')
    for i in todocombo:
        opciones = todocombo.filter(opcion=i.opcion).count()
        if opciones == 1:
            tabla.TempCombo.objects.create(cata=TempCatalogo.objects.get(pk=tmpcmb.pk), 
                item=N4Item.objects.get(pk=i.item.pk))
    for j in cmb:
        articulo = N4ItemCombo.objects.get(pk=cmb[0])
        tabla.TempCombo.objects.create(cata=TempCatalogo.objects.get(pk=tmpcmb.pk), 
        item=N4Item.objects.get(pk=articulo.item.pk))
    temporal = TempCatalogo.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk, maestro=cliente.pk)
    subtotal = TempCatalogo.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk, maestro=cliente.pk).aggregate(
        suma=Sum(F('articulo__precio')*F('cantidad'), output_field=FloatField()))
    subtotal = round(float(subtotal['suma']),2)
    tabla1 = ''
    for i in temporal:
        tabla1 += ('<tr><td>'+ str(i.articulo.pk) + '</td>'
            '<td>'+ str(i.bodega.pk) +'</td>' 
            '<td>'
            '<input id="' + str(i.pk) + '" class="form-control form-control-sm cant" style="width:4em;" type="number" value="' + str(i.cantidad) + '" min="1" step="1" onkeypress="return event.charCode >= 48 && event.charCode <= 57 || event.charCode == 13;" onchange="multiplicar(this);"></td>'
            '<td>' + str(round(i.articulo.precio * i.cantidad,2)) + '</td>' 
            '<td>'
            '<a href="/ventas/facturar/quitar/' + str(i.pk) +'/" class="delete" title="Eliminar" data-placement="auto">'
            '<i class="fa fa-trash"></i></a></td>'
            '</tr>')
    respuesta={}
    respuesta['tabla'] = tabla1 + '<tr><td colspan="5" style="text-align: center;"><a href="#" onclick="location.reload();"><i class="fas fa-sync-alt"></i> Haga clic aqu&iacute; para refrescar</a></td></tr>'
    respuesta['subtotal'] = subtotal
    respuesta['iva'] = subtotal *0.15
    return JsonResponse(respuesta)

def cambiar_coop(request, borra):
    coop = request.GET.get('cooperativa')
    memb = int(request.GET.get('membresia'))
    pago = int(request.GET.get('tipopago'))
    extra = float(request.GET.get('extra'))
    suc = LoggedInUser.objects.get(user=request.user)        
    cliente = TempCatalogoMsr.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk).get(borrador=borra)
    cliente.cooperativa = int(coop)
    cliente.membresia = memb
    cliente.tipopago = pago
    cliente.save()
    consulta = TempCatalogo.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk, maestro=cliente.pk)
    iva =descuento=subtotal=extrad=0
    if consulta:
        for i in consulta:
            exoneracion = impuesto(i.pk, xtra=extra)
            xdescuento = (i.articulo.precio - calcular_descuento(memb,pago,i.articulo.pk))*extra/100
            iva += exoneracion['iva']
            subtotal += exoneracion['st']
            descuento += (calcular_descuento(memb,pago,i.articulo.pk)*i.cantidad)
            extrad += i.cantidad * xdescuento
    respuesta={}
    respuesta['subtotal'] = round(subtotal,2)
    respuesta['iva'] = round(iva,2)
    respuesta['descuento'] = descuento
    respuesta['total'] = round(subtotal - descuento - extrad + iva,2)
    return JsonResponse(respuesta)

def verificar_acceso(request):
    codigo = request.GET.get('codigo')
    respuesta = {}
    cod = tabla.PermisosCliente.objects.get(modelo='Xtradesc')
    if cod.clave == codigo:
        respuesta['acceso'] = True
    else:
        respuesta['acceso'] = False
    return JsonResponse(respuesta)
