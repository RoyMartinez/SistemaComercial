import os, io, csv
from datetime import date, timedelta, datetime
from cartera.models import EstadoCuenta
from . import models as tabla, forms as formulario, factura as voucher
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView, BSModalReadView
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, F, FloatField, ExpressionWrapper, Q, ProtectedError, Max, Min
from django.http import HttpResponseRedirect, Http404, HttpResponse, FileResponse, StreamingHttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from inv import models as tablainv
from caja.forms import FormRegistros
from caja import models as tablaCaja
from .apoyo import calcular_descuento, reino, impuesto, grabarFactura
from .decorators import confirm_password
from usuarios.models import LoggedInUser

class Echo:
    def write(self, value):
        return value

@login_required
def vta_principal(request):
    reino(request)
    return render(request, 'vta/principal.html', {'suc':LoggedInUser.objects.get(user=request.user)})

# ---------------------------------------------------------------------
#          VENTANA UNIONES
# ---------------------------------------------------------------------

@login_required
def cat_union(request):
    reino(request)
    if request.method == "POST":
        formu = formulario.Frm_union(request.POST)
        if formu.is_valid():
            formu.save()
            return HttpResponseRedirect(reverse('vta_union'))
    else:
        formu = formulario.Frm_union()
    return render(request, 'vta/union.html', {'formu':formu,
        'uniones':tabla.Uniones.objects.all(),'suc':LoggedInUser.objects.get(user=request.user),})

class Editar_union(BSModalUpdateView):
    model = tabla.Uniones
    template_name = 'vta/union_modal.html'
    form_class = formulario.Form_union
    success_message = 'Registros actualizados'
    success_url = reverse_lazy(cat_union)

class DeleteUnion(BSModalDeleteView):
    model = tabla.Uniones
    template_name = 'vta/item_delete.html'
    success_url = reverse_lazy(cat_union)
    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError:
            messages.warning(request,'Cannot delete. Existen registros asociados a esta union en "Cooperativas".')
            return HttpResponseRedirect(reverse('vta_union'))

# ---------------------------------------------------------------------
#          VENTANA COOPERATIVAS
# ---------------------------------------------------------------------

@login_required
def cat_cooperativa(request):
    reino(request)
    if request.method == "POST":
        form = formulario.Form_cooperativa(request.POST)
        if form.is_valid():
            form.save()
            import random, string
            c = tabla.Cooperativa.objects.all().order_by('-pk').first()
            cliente = tabla.Cliente.objects.create(identificacion='J031000000' + str(random.randrange(1000,9999)), nombres='Cooperativa', 
                apellidos=c.nombre.upper(), tipo='C', magnetico=''.join(random.choice(string.ascii_letters) for i in range(10)) )
            cliente.cooperativa.add(c)
            cliente.membresia = tabla.Membresia.objects.get(pk=1)
            cliente.save()
            return HttpResponseRedirect(reverse('vta_cooperativa'))
    else:
        form = formulario.Form_cooperativa()
    return render(request, 'vta/cooperativa.html', {'coop':tabla.Cooperativa.objects.all(),
    'suc':LoggedInUser.objects.get(user=request.user),'form':form})

class Editar_cooperativa(BSModalUpdateView):
    model = tabla.Cooperativa
    template_name = 'vta/coop_modal.html'
    form_class = formulario.Form_cooperativaUpdate
    success_message = 'Registros actualizados'
    success_url = reverse_lazy(cat_cooperativa)

# ---------------------------------------------------------------------
#          VENTANA MEMBRESIAS
# ---------------------------------------------------------------------

@login_required
def membresia(request):
    reino(request)
    if request.method == "POST":
        form = formulario.Form_membresia(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('vta_membresia'))
    else:
        form = formulario.Form_membresia()
    return render(request, 'vta/membresia.html', {'form':form, 
        'tabla':tabla.Membresia.objects.order_by('prioridad'),
        'suc':LoggedInUser.objects.get(user=request.user),})

class Editar_membresia(BSModalUpdateView):
    model = tabla.Membresia
    template_name = 'vta/membresia_edit.html'
    form_class = formulario.Form_membresiaUpdate
    success_message = 'Registros actualizados'
    success_url = reverse_lazy(membresia)

class DeleteMembresia(BSModalDeleteView):
    model = tabla.Membresia
    template_name = 'vta/item_delete.html'
    success_message = 'Eliminacion exitosa'
    success_url = reverse_lazy(membresia)

# ---------------------------------------------------------------------
#          VENTANA CLIENTES
# ---------------------------------------------------------------------

@login_required
def nuevo_cliente(request, origen):
    reino(request)
    plantilla = ['vta/clientes.html', 'cartera/cliente_new.html']
    if request.method=="POST":
        form = formulario.Form_cliente(request.POST)
        if form.is_valid():
            coop = form.cleaned_data['cooperativa']
            contador = coop.filter(segmento='1').count()
            if contador < 2:
                form.save()
                return HttpResponseRedirect(reverse('vta_cliente_listar', args=[origen]))
            else:
                messages.warning(request,'Conforme a la ley, un cliente no puede pertenecer a muchas cooperativas')
    else:
        form = formulario.Form_cliente()
    return render(request, plantilla[origen] ,{'form':form, 'suc':LoggedInUser.objects.get(user=request.user),})

@login_required
def listar_cliente(request, origen):
    reino(request)
    plantilla = ['vta/cliente_list.html','cartera/clientes.html']
    return render (request, plantilla[origen], {'cliente':tabla.Cliente.objects.all().order_by('nombres')[:500],
        'suc':LoggedInUser.objects.get(user=request.user), })

@login_required
def editar_cliente(request, cedula, origen):
    reino(request)
    if cedula == '0':
        raise PermissionDenied()
    else:
        plantilla = ['vta/clientes_edit.html', 'cartera/cliente_edit.html']
        customer = tabla.Cliente.objects.get(pk=cedula)
        vehiculos = tabla.ClienteVehiculo.objects.filter(cliente=customer)
        telefono = tabla.ClienteTelefono.objects.filter(cliente=customer)
        direccion = tabla.ClienteDireccion.objects.filter(cliente=customer)
        exor = tabla.ExoRubroCliente.objects.filter(cliente=customer)
        if request.method == 'GET':
            form = formulario.Form_cliente(instance=customer)
        else:
            form = formulario.Form_cliente(request.POST, instance=customer)
            if form.is_valid():
                coop = form.cleaned_data['cooperativa']
                contador = coop.filter(segmento='1').count()
                if contador < 2:
                    form.save()
                    return HttpResponseRedirect(reverse('vta_cliente_listar', args=[origen]))
                else:
                    messages.warning(request,'Conforme a la ley, un cliente no puede pertenecer a muchas cooperativas')
        return render(request, plantilla[origen], {'form':form, 'cedula':cedula, 
        'vehiculos':vehiculos,'telefono':telefono, 'direccion':direccion, 'exor':exor,
        'suc':LoggedInUser.objects.get(user=request.user)})

class Nuevo_cliente_vehiculo(BSModalCreateView):
    template_name = 'vta/vehiculo_nuevo.html'
    form_class = formulario.Form_clientevehiculo
    def get_success_url(self):
        cedula = self.kwargs['ced']
        origen = self.kwargs['origen']
        return reverse_lazy(editar_cliente, kwargs={'cedula':cedula, 'origen':origen })   

class DelClienteVehiculo(BSModalDeleteView):
    model = tabla.ClienteVehiculo
    template_name = 'vta/item_delete.html'
    success_message = 'Objeto eliminado'    
    def get_success_url(self):
        cedula = self.kwargs['ced']
        origen = self.kwargs['origen']
        return reverse_lazy(editar_cliente, kwargs={'cedula':cedula, 'origen':origen})

class NuevoClienteDireccion(BSModalCreateView):
    template_name = 'vta/dirnuevo.html'
    form_class = formulario.FormClienteDireccion
    def get_success_url(self):
        cedula = self.kwargs['ced']
        origen = self.kwargs['origen']
        return reverse_lazy(editar_cliente, kwargs={'cedula':cedula, 'origen':origen })

class DelClienteDireccion(BSModalDeleteView):
    model = tabla.ClienteDireccion
    template_name = 'vta/item_delete.html'
    success_message = 'Objeto eliminado'    
    def get_success_url(self):
        cedula = self.kwargs['ced']
        origen = self.kwargs['origen']
        return reverse_lazy(editar_cliente, kwargs={'cedula':cedula, 'origen':origen}) 

class NuevoClienteTelefono(BSModalCreateView):
    template_name = 'vta/telnuevo.html'
    form_class = formulario.FormClienteTelefono
    def get_success_url(self):
        cedula = self.kwargs['ced']
        origen = self.kwargs['origen']
        return reverse_lazy(editar_cliente, kwargs={'cedula':cedula, 'origen':origen }) 

class DelClienteTelefono(BSModalDeleteView):
    model = tabla.ClienteTelefono
    template_name = 'vta/item_delete.html'
    success_message = 'Objeto eliminado'    
    def get_success_url(self):
        cedula = self.kwargs['ced']
        origen = self.kwargs['origen']
        return reverse_lazy(editar_cliente, kwargs={'cedula':cedula, 'origen':origen})

@login_required
def exorubro(request):
    reino(request)
    cooperativa = tabla.Cooperativa.objects.exclude(pk=1)
    rubro = tablainv.ExoRubro.objects.exclude(pk=1)
    cliente = tabla.Cliente.objects.all()
    if request.method=="POST":
        form = formulario.FormFiltrado(request.POST)
        if form.is_valid():
            coop = int(form.cleaned_data['cooperativa'])
            clie = form.cleaned_data['cliente']
            rubro = int(form.cleaned_data['rubro'])
            if coop == 0:
                exo=tabla.ExoRubroCliente.objects.all()
            else:
                c = tabla.Cooperativa.objects.get(pk=coop)
                exo=tabla.ExoRubroCliente.objects.filter(cooperativa=c.nombre)
            if clie != 'todos':
                exo = exo.filter(cliente=clie)
            if rubro > 0:
                exo = exo.filter(rubro=rubro)
    else:
        form = formulario.FormFiltrado()
        exo = tabla.ExoRubroCliente.objects.all()[:100]
    return render(request,'vta/exorubro.html',{'suc':LoggedInUser.objects.get(user=request.user),
    'exorubro':exo,'cooperativa':cooperativa, 'rubro':tablainv.ExoRubro.objects.exclude(pk=1),
    'cliente':cliente, 'cantidad':exo.aggregate(suma=Sum('unidades')),
    'precio': exo.aggregate(suma=Sum('precio')), 'costo':exo.aggregate(suma=Sum('costo')) })

@login_required
def nuevoexoajuste(request):
    reino(request)
    cooperativa = tabla.Cooperativa.objects.exclude(pk=1)
    if request.method=="POST":
        form= formulario.Form_exorubro(request.POST)
        if form.is_valid():
            if form.cleaned_data['origen'] == form.cleaned_data['destino']:
                messages.warning(request,'El cliente de origen y destino no pueden ser iguales') 
            else:
                c,r = form.cleaned_data['origen'], form.cleaned_data['rubro']
                totales = tabla.ExoRubroCliente.objects.filter(cliente=c,rubro=r).aggregate(
                    p=Sum('precio'), cost=Sum('costo'), u=Sum('unidades'))
                if form.cleaned_data['precio'] <= totales['p'] and form.cleaned_data['costo'] <= totales['cost'] and form.cleaned_data['cantidad'] <= totales['u']:
                    coop = tabla.Cooperativa.objects.get(pk=form.cleaned_data['cooperativa'])
                    #Grabar la salida
                    tabla.ExoRubroCliente.objects.create(referencia='Salida Ajuste',
                        cooperativa=coop.nombre, costo=float(form.cleaned_data['costo']) * -1, 
                        precio=float(form.cleaned_data['precio']) * -1, unidades=float(form.cleaned_data['cantidad']) * -1,
                        cliente=tabla.Cliente.objects.get(pk=c), rubro=tablainv.ExoRubro.objects.get(pk=r))
                    #Grabar la entrada
                    tabla.ExoRubroCliente.objects.create(referencia='Entrada Ajuste',
                        cooperativa=coop.nombre, costo=float(form.cleaned_data['costo']), 
                        precio=float(form.cleaned_data['precio']), unidades=float(form.cleaned_data['cantidad']),
                        cliente=tabla.Cliente.objects.get(pk=form.cleaned_data['destino']), rubro=tablainv.ExoRubro.objects.get(pk=r))
                    return HttpResponseRedirect(reverse('vta_exorubro'))
                else:
                    messages.warning(request,'Esta realizando un ajuste que excede los saldos')
    else:
        form=formulario.Form_exorubro()
    return render(request, 'vta/exorubroajuste.html', {'form':form, 'cooperativa':cooperativa, })

# ---------------------------------------------------------------------
#          VENTANA VENDEDORES
# ---------------------------------------------------------------------

@login_required
def vendedor(request):
    reino(request)
    venta = tabla.Vendedores.objects.all().order_by('identificacion__username')
    if request.method == "POST":
        form = formulario.Form_vendedor(request.POST)
        if form.is_valid():
            u = User.objects.get(username=form.cleaned_data['identificacion'])
            u.first_name = form.cleaned_data['nombre']
            u.last_name = form.cleaned_data['apellidos']
            u.save()
            form.save()
            return HttpResponseRedirect(reverse('vta_vendedor'))
        else:
            messages.warning(request,'Se ha producido un error. Revise la pestana "Anadir" para mas informacion')
    else:
        form = formulario.Form_vendedor()
    return render(request, 'vta/vendedores.html',{'formulario':form, 'vendedores':venta, 'suc':LoggedInUser.objects.get(user=request.user)})

@login_required
def vendedor_check(request, vendedor_id):
    """ Habilita o deshabilita a un vendedor de acuerdo a su id asociado """
    reino(request)
    venta = get_object_or_404(tabla.Vendedores, pk=vendedor_id)
    if venta.activo:
        venta.activo = False
        venta.save()
    else:
        venta.activo = True
        venta.save()
    return HttpResponseRedirect(reverse('vta_vendedor'))

# ---------------------------------------------------------------------
#          VENTANA FACTURACION
# ---------------------------------------------------------------------

@login_required
def facturar(request, borra):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    try:
        usuario_vendedor = tabla.Vendedores.objects.get(pk=request.user.id)
        if not usuario_vendedor.activo:
            return render(request, 'vta/error1.html',{'texto':'El vendedor "' + request.user.username + '" esta inactivo'})
        else:
            iva=total=descuento=subtotal=0
            pago=tabla.Forma_pago.objects.all()
            if request.method == 'POST': # si el llamado es POST
                cliente = tablainv.TempCatalogoMsr.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk).get(borrador=borra)
                tempo = tablainv.TempCatalogo.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk, maestro=cliente.pk)
                form = formulario.Form_factura(request.POST)
                if tempo:
                    subtotal = tempo.aggregate(suma=Sum(F('articulo__preciomax')*F('cantidad'), output_field=FloatField()))
                    subtotal = float(subtotal['suma'])
                    iva = subtotal * 0.15
                    total = subtotal + iva
                    if form.is_valid():
                        if 'submit_nuevo' in request.POST:
                            quitar = tablainv.TempCatalogo.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk, maestro=cliente.pk)
                            quitar.delete()
                            cliente.cedula = '0'
                            cliente.nombre = 'PARTICULAR / INDIVIDUAL'
                            cliente.membresia = 1
                            cliente.tipopago = 2
                            cliente.save()
                            return HttpResponseRedirect(reverse('vta_facturar', args=[borra]))
                        elif 'submit_proforma' in request.POST:
                            pro = tabla.Proformamsr.objects.filter(sucursal=suc.sucursal.pk).count()
                            a = tabla.Proformamsr.objects.create(
                                referencia          = suc.sucursal.pk + '-PF-00' + str(pro+1),
                                formapago           = form.cleaned_data['formapago'],
                                sucursal            = tablainv.Sucursal.objects.get(pk=suc.sucursal.pk),
                                fechavencimiento    = date.today() + timedelta(days=3),
                                cliente             = form.cleaned_data['cliente'],
                                # membresia           = form.cleaned_data['membresia'],
                                cooperativa         = form.cleaned_data['cooperativa'],
                                vendedor            = usuario_vendedor,
                                estado              = tablainv.Estado.objects.get(pk=3),
                                descuento           = float(form.cleaned_data['descuentotal']),
                                extradescuento      = float(form.cleaned_data['extradescuento']),
                                impuesto            = float(form.cleaned_data['impuestototal']),
                                costo               = 0,
                                nombre              = form.cleaned_data['nombre']
                            )
                            for i in tempo:
                                exoneracion = impuesto(i.pk, xtra=a.extradescuento)
                                # desc=calcular_descuento(int(form.cleaned_data['membresia']), a.formapago.pk, i.articulo.pk)
                                desc=calcular_descuento(a.membresia, a.formapago.pk, i.articulo.pk)
                                xdesc = (i.articulo.preciomax - desc)*a.extradescuento/100 
                                tabla.Proformadet.objects.create(
                                    referencia  = tabla.Proformamsr.objects.get(pk=a.pk),
                                    item        = tablainv.N4Item.objects.get(pk=i.articulo.id_n4),
                                    unidades    = i.cantidad,
                                    preciobase  = i.articulo.preciomax,    
                                    descuento   = i.cantidad * (desc + xdesc),
                                    impuesto    = exoneracion['iva'],
                                    bodega      = i.bodega
                            )
                            return HttpResponseRedirect(reverse('vta_proforma',args=[a.pk]))
                        else: #Grabar Instancia
                            instancia = tabla.InstanciaFactMsr.objects.create(
                                formapago           = form.cleaned_data['formapago'],
                                sucursal            = tablainv.Sucursal.objects.get(pk=suc.sucursal.pk),
                                fechavencimiento    = date.today() + timedelta(days=30),
                                cliente             = form.cleaned_data['cliente'],
                                # membresia           = form.cleaned_data['membresia'],
                                cooperativa         = form.cleaned_data['cooperativa'],
                                vendedor            = usuario_vendedor,
                                preciofinaltotal    = float(form.cleaned_data['preciofinaltotal']),
                                descuentotal        = float(form.cleaned_data['descuentotal']),
                                extradescuento      = float(form.cleaned_data['extradescuento']),
                                impuestototal       = float(form.cleaned_data['impuestototal']),
                                nombre              = form.cleaned_data['nombre'],
                                cct                 = form.cleaned_data['cct'],
                                monto_cct           = form.cleaned_data['monto_cct'],
                                borrador            = cliente,
                                origen              = 'Fact')
                            if instancia.formapago.pk == 4:##si la factura es de credito
                                #verificar si hay saldo
                                if instancia.cliente.saldo > instancia.preciofinaltotal:
                                    f=grabarFactura(request, instancia.pk)
                                    ecuenta = EstadoCuenta.objects.filter(cliente=f.cliente.pk).aggregate(
                                        sdebe = Sum('debe'), shaber=Sum('haber')
                                    )
                                    debito = float(ecuenta['sdebe']) if ecuenta['sdebe'] else 0
                                    credito = float(ecuenta['shaber']) if ecuenta['shaber'] else 0
                                    limite = float(f.cliente.limite_credito)
                                    saldo = float(limite) + debito - credito - float(f.preciofinaltotal)
                                    EstadoCuenta.objects.create(cliente=f.cliente, referencia='Factura-'+f.pk, 
                                        descripcion='Factura de credito',debe=0,haber=f.preciofinaltotal, saldo=saldo)
                                    customer = tabla.Cliente.objects.get(pk=f.cliente.pk)
                                    customer.saldo= saldo
                                    customer.save()
                                else: # Si el saldo es menor a lo facturado
                                    messages.error(request,f'El total de la factura excede el saldo disponible para credito ')
                                    instancia.delete()
                            elif instancia.formapago.pk == 3:#si la factura es por fenibillete
                                f=grabarFactura(request, instancia.pk)
                                tablaCaja.Registros.objects.create(
                                    caja        = tablaCaja.Cajas.objects.get(pk=f.vendedor.cajero.pk),
                                    tipo        = tablaCaja.TipoMovimiento.objects.get(codigo='EF'),
                                    referencia  = f.referencia,
                                    total       = f.preciofinaltotal,
                                    real        = f.preciofinaltotal,
                                    nio_in      = 0,
                                    usd_in      = 0,
                                    tarjeta     = 0,
                                    fenibillete = f.preciofinaltotal,
                                    nio_out     = 0,
                                    usd_out     = 0,
                                )
                            else:#si la factura es tarjeta o efectivo
                                return HttpResponseRedirect(reverse('vta_facturarcaja', args=[instancia.pk]))#aqui me dirijo a la caja
                            return HttpResponseRedirect(reverse('vta_facturar', args=[borra]))
                    else:
                        print(form.errors)

                else:  #Respuesta de error en caso de que no se hayan ingresado items en el detalle          
                    return HttpResponse('<h1>Debe ingresar al menos un item</h1>')
            else: # Si el llamado es GET
                form = formulario.Form_factura()
                try:
                    cliente = tablainv.TempCatalogoMsr.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk).get(borrador=borra)
                except tablainv.TempCatalogoMsr.DoesNotExist:
                    cliente = tablainv.TempCatalogoMsr.objects.create(borrador=borra, usuario=request.user, sucursal=tablainv.Sucursal.objects.get(pk=suc.sucursal.pk))
                tempo = tablainv.TempCatalogo.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk, maestro=cliente.pk)
                # print(tempo)
                if tempo:
                    #validar existencias en la tabla temporal
                    for i in tempo:
                        # print(i)
                        # print('imprimido')
                        try: #Intento el articulo de la tabla temporal en las existencias 
                            if i.articulo.producto.naturaleza != 'C':
                                art = tablainv.ExistenciaBodega.objects.filter(
                                    cantidad__gt=0, bodega=i.bodega.pk).get(item=i.articulo.pk)
                                if art.cantidad < i.cantidad:
                                    i.cantidad = art.cantidad
                                    i.save()  
                        except tablainv.ExistenciaBodega.DoesNotExist:
                            i.delete()
                            continue #Si no lo encuentra, borra el registro y sigue al siguiente elemento del bucle
                        #validar si esta exonerado
                        exoneracion = impuesto(i.pk)
                        subtotal += exoneracion['st']
                        iva += exoneracion['iva']
                        descuento +=(calcular_descuento(cliente.cedula, cliente.tipopago, i.articulo.pk)*i.cantidad)
                tempo = tempo.annotate(factor=ExpressionWrapper(F('cantidad')*F('articulo__preciomax'), output_field=FloatField()))
                total = subtotal - descuento + iva
            # Para calcular el saldo disponible
            cliente2 = tabla.Cliente.objects.get(pk=cliente.cedula)
            return render(request,'vta/factura2.html',{'form':form, 'tempo':tempo,'subtotal':subtotal,
                                                    'iva':iva,'total':total,'descuento':descuento,
                                                    'suc':suc,'borra':borra, 'cliente':cliente,
                                                    'pago':pago,'cliente2':cliente2,
                                                    'cliente3':tabla.Cliente.objects.exclude(pk='0').order_by('nombres')})#Carga los clientes en el modal seleccionable
    except tabla.Vendedores.DoesNotExist:
        return render(request, 'vta/error1.html',{'texto':'El usuario "' + request.user.username + '" no esta calificado como vendedor'})

@login_required
def caja(request, valor):
    suc = LoggedInUser.objects.get(user=request.user)
    instancia = tabla.InstanciaFactMsr.objects.get(pk=valor)
    destino = instancia.origen #initialize where the instance comes from
    tc = tablaCaja.TipoCambio.objects.all().order_by('-pk').first()
    e=s=dif=0
    if request.method == 'POST':
        form = FormRegistros(request.POST)
        if form.is_valid():
            if 'grabar' in request.POST:
                if abs(
                    float(form.cleaned_data['tarjeta']) + 
                    float(form.cleaned_data['nio_in']) + 
                    float(form.cleaned_data['usd_in']) * tc.compra - 
                    float(instancia.preciofinaltotal) - 
                    float(form.cleaned_data['nio_out']) -
                    float(form.cleaned_data['usd_out']) * tc.compra) <= 1:
                    f=grabarFactura(request, instancia.pk) #Grabamos la factura
                    # Registros en CAJA
                    tablaCaja.Registros.objects.create(
                        caja        = tablaCaja.Cajas.objects.get(pk=f.vendedor.cajero.pk),
                        tipo        = tablaCaja.TipoMovimiento.objects.get(codigo='EF'),
                        referencia  = f.referencia,
                        total       = f.preciofinaltotal,
                        real        = float(form.cleaned_data['nio_in']) - float(form.cleaned_data['nio_out']),
                        nio_in      = float(form.cleaned_data['nio_in']),
                        usd_in      = float(form.cleaned_data['usd_in']),
                        tarjeta     = float(form.cleaned_data['tarjeta']),
                        fenibillete = 0,
                        nio_out     = float(form.cleaned_data['nio_out']),
                        usd_out     = float(form.cleaned_data['usd_out']),
                        voucher     = form.cleaned_data['voucher']
                    )
                    if destino == 'Fact':
                        return HttpResponseRedirect(reverse('vta_facturar',args=[1]))
                    else: 
                        proforma = tabla.Proformamsr.objects.get(pk=destino)    
                        proforma.estado = tablainv.Estado.objects.get(pk=2)    
                        proforma.save() #cambiamos el estado de la proforma a ANULADO
                        return HttpResponseRedirect(reverse('vta_admon_prof'))
                else:
                    messages.error(request,f'Hay una diferencia superior a 1 cordoba, favor corregir')
                    e = float(form.cleaned_data['nio_in'])
                    s = float(form.cleaned_data['nio_out'])
                    dif = float(form.cleaned_data['nio_in']) - float(instancia.preciofinaltotal) - float(form.cleaned_data['nio_out'])
            else:
                if destino == 'Fact':
                    return HttpResponseRedirect(reverse('vta_facturar',args=[1]))
                else:
                    return HttpResponseRedirect(reverse('vta_admon_prof'))
    else:
        form = FormRegistros()
    return render(request, 'vta/caja.html', {'instancia':instancia, 'entrada':e, 'cambio':s, 'dif':dif, 'tc':tc, 'suc':suc, 'monto':instancia.preciofinaltotal})

@login_required
#@confirm_password
def admon_fact(request):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    a = datetime.today()
    if request.method == 'GET':
        form = formulario.Form_admon_fact()
        b = a + timedelta(days=1)
        fact = tabla.Facturamsr.objects.filter(
            sucursal=suc.sucursal.pk).filter(fechaemision__range = (a.date(),b.date())).annotate(
            subtotal=ExpressionWrapper(F('preciofinaltotal') - F('impuestototal'), output_field=FloatField())
        )
    else:
        form = formulario.Form_admon_fact(request.POST)
        if form.is_valid():
            a = form.cleaned_data['fecha']
            b = a + timedelta(days=1)
            fact = tabla.Facturamsr.objects.filter(sucursal=suc.sucursal.pk).filter(fechaemision__range=(a,b)).annotate(
                subtotal = ExpressionWrapper(F('preciofinaltotal') - F('impuestototal'), output_field=FloatField())
            )
    valor=a.strftime("%Y-%m-%d")
    hoy = datetime.today()
    return render(request, 'vta/fact_admon.html', {'form':form, 'factura':fact, 'valor':valor,
    'suc':suc, 'hoy':hoy.strftime("%Y-%m-%d")})

# ---------------------------------------------------------------------
#          VENTANA INCENTIVOS
# ---------------------------------------------------------------------
@login_required
def incentivo(request):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    cliente = tabla.Cliente.objects.all().exclude(pk='0')
    articulos = tablainv.ExistenciaBodega.objects.filter(cantidad__gt=0, bodega__tipo='F', bodega__sucursal=suc.sucursal.pk)
    try:  #Se crea o se busca una instancia en la tabla Temporal Maestro
        cabecera = tablainv.TempCatalogoMsr.objects.filter(usuario=request.user, sucursal=suc.sucursal.pk).get(borrador=989)
    except tablainv.TempCatalogoMsr.DoesNotExist:
        tablainv.TempCatalogoMsr.objects.create(borrador=989, usuario=request.user, sucursal=tablainv.Sucursal.objects.get(pk=suc.sucursal.pk))  
    if request.method == "POST":
        form = formulario.FormIncentivo(request.POST)
        if form.is_valid():
            ajuste = form.cleaned_data['ajuste']
            saldo = tabla.IncentivoMsr.objects.filter(cliente=form.cleaned_data['cliente']).aggregate(suma=Sum('monto'))
            detalle = tablainv.TempCatalogo.objects.filter(maestro__borrador=989)
            if ajuste == 'Entrada':
                saldo = (saldo['suma'] + form.cleaned_data['monto']) if saldo['suma'] else form.cleaned_data['monto']
                contador = str(tabla.IncentivoMsr.objects.filter(referencia__contains='EI').count() + 1)
                referencia = f'EI{contador.zfill(5)}'
                tabla.IncentivoMsr.objects.create(referencia=referencia, cliente=form.cleaned_data['cliente'], centro_costo=tablainv.CentroCosto.objects.get(pk=1), ajuste=ajuste, 
                    monto=form.cleaned_data['monto'], saldo=saldo)
                if detalle: 
                    detalle.delete() 
            else:   
                if detalle:
                    saldo = (saldo['suma'] - form.cleaned_data['monto']) if saldo['suma'] else form.cleaned_data['monto']*-1
                    if saldo >= 0: 
                        contador = str(tabla.IncentivoMsr.objects.filter(referencia__contains='SC').count() + 1)
                        referencia = f'SC{contador.zfill(5)}'
                        incentivo = tabla.IncentivoMsr.objects.create(referencia=referencia, cliente=form.cleaned_data['cliente'], 
                            centro_costo=tablainv.CentroCosto.objects.get(pk=1), ajuste=ajuste, monto=form.cleaned_data['monto']*-1, saldo=saldo)
                        for i in detalle:
                            tabla.IncentivoDet.objects.create(referencia=incentivo, item=i.articulo, cantidad=i.cantidad, debe=i.articulo.preciomax * i.cantidad)
                            #restamos su existencia
                            existencia = tablainv.ExistenciaBodega.objects.filter(item=i.articulo.id_n4).get(bodega=i.bodega.pk)
                            existencia.cantidad -= i.cantidad
                            existencia.save()
                            #restamos su vencimiento
                            cantidad = i.cantidad
                            while cantidad > 0:
                                vencimiento = tablainv.N4ItemVencimiento.objects.filter(item=i.articulo.id_n4).exclude(cantidad=0).order_by('fecha_venc').first()
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
                                    break
                            #ingresamos su registro en el kardex
                            tablainv.Kardex.objects.create(sucursal=suc.sucursal, bodega=i.bodega, item=i.articulo,
                                referencia = incentivo.pk, salida = i.cantidad, haber=0, existencia=existencia.cantidad, tipotransaccion = 'SS'
                            )
                        detalle.delete()
                    else:
                        messages.warning(request,'Cliente excede el limite disponible en su cuenta de incentivo')
                else:
                    messages.warning(request,'No se encontraron items en el detalle')
            return HttpResponseRedirect(reverse('vta_incentivo'))
        #else -> form.invalid
    else:
        form = formulario.FormIncentivo()
    detalle = tablainv.TempCatalogo.objects.filter(maestro__borrador=989).annotate(
        factor=ExpressionWrapper(F('cantidad')*F('articulo__preciomax'), output_field=FloatField()))
    subtotal = detalle.aggregate(suma=Sum('factor'))
    return render(request, 'vta/incentivo.html', {'suc':suc, 'cliente':cliente,'articulos':articulos, 'detalle':detalle, 'subtotal':subtotal,})

@login_required
def incentivo_kardex(request):
    reino(request)
    return render(request, 'vta/incentivo-kardex.html', {})

@login_required
def proforma_admon(request):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    pro = tabla.Proformamsr.objects.filter(
        fechavencimiento__gte=date.today()).filter(
        sucursal=suc.sucursal.pk).exclude(estado=2)
    if request.method == "POST":
        form = formulario.FormAdmonProf(request.POST)
        if form.is_valid():
            x = tabla.Proformamsr.objects.get(pk=form.cleaned_data['referencia'])
            detalle = tabla.Proformadet.objects.filter(referencia = x.pk)
            total=0
            valido=True # Si es verdadero, imprime la factura
            for i in detalle:
                existencia = tablainv.ExistenciaBodega.objects.filter(bodega=i.bodega.pk).get(item=i.item.pk)
                if i.unidades > existencia.cantidad:
                    valido = False
                    break
                total += i.unidades * i.preciobase
            if valido: #Si al menos un item tiene existencias
                try:
                    cliente = tablainv.TempCatalogoMsr.objects.filter(
                        usuario=request.user,sucursal=x.sucursal.pk).get(borrador=1000)
                    cliente.cedula = x.cliente.identificacion
                    cliente.nombre = x.cliente.nombres + ' ' + x.cliente.apellidos
                    cliente.save()
                    z = tablainv.TempCatalogo.objects.filter(maestro=cliente.pk)
                    z.delete()
                except tablainv.TempCatalogoMsr.DoesNotExist:
                    cliente = tablainv.TempCatalogoMsr.objects.create(
                        borrador=1000, cedula=x.cliente.identificacion, 
                        nombre=x.cliente.nombres + ' ' + x.cliente.apellidos,
                        cooperativa=x.cooperativa, membresia=x.membresia,
                        usuario = request.user, sucursal = x.sucursal
                    )
                instancia = tabla.InstanciaFactMsr.objects.create(
                    formapago           = x.formapago,
                    sucursal            = x.sucursal,
                    fechavencimiento    = date.today() + timedelta(days=30),
                    cliente             = x.cliente,
                    membresia           = x.membresia,
                    cooperativa         = x.cooperativa,
                    vendedor            = x.vendedor,
                    preciofinaltotal    = total - x.descuento - ((total-x.descuento)*x.extradescuento/100) + x.impuesto,
                    descuentotal        = x.descuento,
                    extradescuento      = x.extradescuento,
                    impuestototal       = x.impuesto,
                    nombre              = x.nombre,
                    borrador            = cliente,
                    origen              = form.cleaned_data['referencia'])
                print(total - x.descuento - ((total-x.descuento)*x.extradescuento/100) + x.impuesto)    
                for i in detalle:
                    tablainv.TempCatalogo.objects.create( usuario=request.user, articulo=i.item, 
                        cantidad=i.unidades, sucursal=x.sucursal, maestro=cliente, bodega=i.bodega)
                if instancia.formapago.pk == 4:
                    if instancia.cliente.saldo > instancia.preciofinaltotal:
                        f=grabarFactura(request, instancia.pk)
                        ecuenta = tabla.EstadoCuenta.objects.filter(cliente=f.cliente.pk).aggregate(
                            sdebe = Sum('debe'), shaber=Sum('haber')
                        )
                        debito = float(ecuenta['sdebe']) if ecuenta['sdebe'] else 0
                        credito = float(ecuenta['shaber']) if ecuenta['shaber'] else 0
                        limite = float(f.cliente.limite_credito)
                        saldo = float(limite) + debito - credito - float(f.preciofinaltotal)
                        tabla.EstadoCuenta.objects.create(cliente=f.cliente, referencia='Factura-'+f.pk, 
                            descripcion='Factura de credito',debe=0,haber=f.preciofinaltotal, saldo=saldo)
                        customer = tabla.Cliente.objects.get(pk=f.cliente.pk)
                        customer.saldo= saldo
                        customer.save()
                        x.estado = tablainv.Estado.objects.get(pk=2)
                        x.save()
                    else: # Si el saldo es menor a lo facturado
                        messages.error(request,f'El total de la factura excede el saldo disponible para credito ')
                        instancia.delete()
                elif instancia.formapago.pk == 3:
                    f=grabarFactura(request, instancia.pk)
                    tablaCaja.Registros.objects.create(
                        caja        = tablaCaja.Cajas.objects.get(pk=f.vendedor.cajero.pk),
                        tipo        = tablaCaja.TipoMovimiento.objects.get(codigo='EF'),
                        referencia  = f.referencia,
                        total       = f.preciofinaltotal,
                        real        = f.preciofinaltotal,
                        nio_in      = 0,
                        usd_in      = 0,
                        tarjeta     = 0,
                        fenibillete = f.preciofinaltotal,
                        nio_out     = 0,
                        usd_out     = 0,
                    )
                    x.estado = tablainv.Estado.objects.get(pk=2)
                    x.save()
                else:
                    return HttpResponseRedirect(reverse('vta_facturarcaja', args=[instancia.pk]))
                #actualizare el estado de la proforma
                return HttpResponseRedirect(reverse('vta_admon_prof'))
            else:
                messages.error(request,f'La proforma no se puede facturar por falta de existencias')
                return HttpResponseRedirect(reverse('vta_admon_prof'))
    else:
        form = formulario.FormAdmonProf()
    return render(request,'vta/proforma_admon.html', {'pro':pro, 'form':form, 'suc':suc})

class Detalle_fact(BSModalReadView):
    model = tabla.Facturamsr
    template_name = 'vta/fact_detail.html'
    def get_context_data(self, **kwargs):
        fact = self.kwargs['pk']
        context = super(Detalle_fact, self).get_context_data(**kwargs)
        context['nuevo'] = tabla.Facturadet.objects.filter(referencia=fact)
        return context

class Anular_factura(BSModalUpdateView):
    #pedir permisos
    model = tabla.Facturamsr
    template_name = 'vta/fact_anular.html'
    form_class = formulario.Form_factura_anular
    def get_success_url(self): #Devuelve el inventario de la factura anulada
        factura = self.kwargs['pk']
        detalle = tabla.Facturadet.objects.filter(referencia=factura)
        for i in detalle: # Actualizacion de existencias bodega
            existencia = tablainv.ExistenciaBodega.objects.filter(item=i.item.pk).get(bodega=i.bodega.pk)
            existencia.cantidad += i.unidades
            existencia.save()
        # Actualizamos caja_registros para las facturas en efectivo unicamente
        f = tabla.Facturamsr.objects.get(pk=factura)
        if f.formapago.pk == 4: # Si la factura es de credito tengo que devolver el saldo
            ecuenta=tabla.EstadoCuenta.objects.filter(cliente=f.cliente.pk).aggregate(
                sdebe=Sum('debe'), shaber=Sum('haber')
            )
            debito = float(ecuenta['sdebe']) if ecuenta['sdebe'] else 0
            credito = float(ecuenta['shaber']) if ecuenta['shaber'] else 0
            limite = float(f.cliente.limite_credito)
            saldo = float(limite) + debito - credito + float(f.preciofinaltotal)
            tabla.EstadoCuenta.objects.create(cliente=f.cliente, referencia=f.pk+'-Anulacion', 
                descripcion='Anulacion de factura',debe=f.preciofinaltotal,haber=0, saldo=saldo)
            customer = tabla.Cliente.objects.get(pk=f.cliente.pk)
            customer.saldo= saldo
            customer.save()
        else: # Si es de contado, creo la linea en los registros
            reg = tablaCaja.Registros.objects.get(referencia=factura)
            tablaCaja.Registros.objects.create(caja=tablaCaja.Cajas.objects.get(pk=reg.caja.pk), 
                tipo=tablaCaja.TipoMovimiento.objects.get(pk=reg.tipo.pk), referencia=factura + ' Anulada', 
                total=reg.total * -1, real=reg.real * -1, nio_in=reg.nio_out *-1, usd_in=reg.usd_out *-1, tarjeta=reg.tarjeta * -1,
                fenibillete=reg.fenibillete * -1, nio_out=reg.nio_in *-1, usd_out=reg.usd_in *-1, voucher='', 
                estado=tablainv.Estado.objects.get(pk=2))
        # Actualizamos el kardex rubro
        try:
            exor = tabla.ExoRubroCliente.objects.get(referencia=factura)
            tabla.ExoRubroCliente.objects.create(referencia=factura + ' Anulacion', cooperativa=exor.cooperativa,
                cliente=exor.cliente, rubro=exor.rubro, costo=exor.costo*-1, precio=exor.precio*-1, unidades=exor.unidades*-1 )
        except tabla.ExoRubroCliente.DoesNotExist:
            pass
        return reverse_lazy(admon_fact)

@login_required
def quitar_items(request, item_id):
    """ Elimina elementos temporales en el detalle de factura """
    reino(request)
    quitar = tablainv.TempCatalogo.objects.get(pk=item_id)
    quitar.delete()
    if quitar.maestro.borrador == 989:
        return HttpResponseRedirect(reverse('vta_incentivo'))
    else:
        return HttpResponseRedirect(reverse('vta_facturar', args=[quitar.maestro.borrador]))

@login_required
def proforma(request, no_pro):
    """ Imprime la proforma en formato html """
    reino(request)
    prof = tabla.Proformamsr.objects.get(pk=no_pro)
    prof_det = tabla.Proformadet.objects.filter(referencia=no_pro).annotate(factor=ExpressionWrapper(F('unidades')*F('preciobase'),output_field=FloatField()))
    subtotal = tabla.Proformadet.objects.filter(referencia=no_pro).aggregate(
        st=Sum(F('unidades')*F('preciobase'),output_field=FloatField()),
        desc=Sum('descuento'), iva=Sum('impuesto'))
    cooperativa = tabla.Cooperativa.objects.get(pk=prof.cooperativa)
    membresia = tabla.Membresia.objects.get(pk=prof.membresia)
    return render(request, 'vta/proforma.html', {'proforma':prof,
                                                'total':subtotal['st'] - subtotal['desc'] + subtotal['iva'],
                                                'extra':(subtotal['st'] -  prof.descuento)*prof.extradescuento/100,
                                                'subtotal':subtotal['st'],
                                                'detalle':prof_det,
                                                'suc':LoggedInUser.objects.get(user=request.user),
                                                'cooperativa':cooperativa, 'membresia':membresia,
                                                }) 

@login_required
def facturacion2(request, no_fact):
    """Imprime la factura en formato html"""
    reino(request)
    try:
        fact = tabla.Facturamsr.objects.get(pk=no_fact)
        fact_det = tabla.Facturadet.objects.filter(referencia=no_fact).annotate(
            factor=ExpressionWrapper(F('preciofinal') + F('descuento') -F('impuesto'), output_field=FloatField()))
        subtotal = tabla.Facturadet.objects.filter(referencia=no_fact).aggregate(
            suma=Sum(F('preciofinal') + F('descuento') - F('impuesto'), output_field=FloatField()))
        return render(request, 'vta/facturacion.html', {'factura':fact,
            'detalle':fact_det,
            'subtotal':round(subtotal['suma'],2),
            'suc':LoggedInUser.objects.get(user=request.user),
            })
    except tabla.Facturamsr.DoesNotExist:
        return render(request,'fenimarket/404.html')

@login_required
def color(request):
    reino(request)
    colores = tabla.ClienteVehiculoColor.objects.all()
    if request.method == 'POST':
        form = formulario.Form_colores(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('vta_colores'))
    else:
        form = formulario.Form_colores()
    return render(request, 'vta/vehiculo_color.html', {'form':form, 'colores':colores})

@login_required
def catalogo(request, borra):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    familia = tablainv.N2Familia.objects.all().order_by('descripcion')
    marca = tablainv.MarcaItem.objects.all()
    articulos = None
    if request.method == "POST":
        form = formulario.FormCatalogo(request.POST)
        if form.is_valid():
            x = form.cleaned_data['buscar']
            if x.lower() == 'combo':
                articulos = tablainv.ExistenciaBodega.objects.filter(
                    bodega__tipo='F', bodega__sucursal=suc.sucursal.pk, 
                    item__producto__naturaleza='C')
            else:
                articulos = tablainv.ExistenciaBodega.objects.filter(
                    cantidad__gt=0, bodega__tipo='F', bodega__sucursal=suc.sucursal.pk).filter(
                    Q(item__producto__id_n3__icontains=x)|Q(item__producto__familia__descripcion__icontains=x) | Q(item__marca__marca__icontains=x) | Q(item__producto__descripcion__icontains=x) | Q(item__descripcion__icontains=x))
    else:
        form = formulario.FormCatalogo()
    return render(request,'vta/catalogo.html',{'articulos':articulos, 'marcaitem':marca, 'borra':borra, 
        'vehiculo': tablainv.MarcaVehiculo.objects.all(), 'familia':familia })

def reporteria(request):
    return render(request, 'vta/reportes/rubro.html', {'suc':LoggedInUser.objects.get(user=request.user)})

@login_required
def rpt_formapago(request):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    e = tabla.Facturamsr.objects.filter(sucursal=suc.sucursal.pk).filter(formapago=2).count()
    c = tabla.Facturamsr.objects.filter(sucursal=suc.sucursal.pk).filter(formapago=3).count()
    t = tabla.Facturamsr.objects.filter(sucursal=suc.sucursal.pk).filter(formapago=4).count()
    f = tabla.Facturamsr.objects.filter(sucursal=suc.sucursal.pk).filter(formapago=5).count()
    return render(request, 'vta/reportes/forma_pago.html',{'suc':LoggedInUser.objects.get(user=request.user),
        'e':e, 'c':c, 't':t, 'f':f})

@login_required
def rpt_arqueo(request):
    reino(request)
    arqueo = None
    suc = LoggedInUser.objects.get(user=request.user)
    hoy = datetime.today()
    hoy = hoy.strftime("%Y-%m-%d")
    if request.method == "POST":
        form = formulario.FormArqueo(request.POST)
        if form.is_valid():
            a = form.cleaned_data['fecha']
            v = form.cleaned_data['vendedor']
            b = a + timedelta(days=1)
            arqueo = tabla.Facturamsr.objects.filter(
                fechaemision__range=(a,b)).filter(
                sucursal=suc.sucursal.pk).annotate(
                subtotal = ExpressionWrapper(F('preciofinaltotal') - F('impuestototal') - F('descuentotal'), output_field=FloatField())
            )
            if v != '0':
                arqueo = arqueo.filter(vendedor=int(v)) 
            hoy=a.strftime("%Y-%m-%d")
    return render(request, 'vta/reportes/arqueo.html',{
        'suc':LoggedInUser.objects.get(user=request.user),
        'vendedor':tabla.Vendedores.objects.all(),
        'arqueo':arqueo,
        'hoy':hoy,
        })

@login_required
def rpt_general(request):
    reino(request)
    suc=LoggedInUser.objects.get(user=request.user)
    tabla1=None
    precio=iva=total=v=tipo=0
    a = date.today()
    rango=1
    if request.method=="POST":
        form = formulario.FormGeneral(request.POST)
        if form.is_valid():
            a = form.cleaned_data['fecha']
            rango = int(form.cleaned_data['rango'])
            v = int(form.cleaned_data['vendedor'])
            tipo = int(form.cleaned_data['tipo'])
            if rango == 1:
                b = a + timedelta(days=1)
                tabla1 = tabla.Facturamsr.objects.filter(sucursal=suc.sucursal.pk, fechaemision__range=(a,b))
            else:
                mes = a.strftime('%m')
                tabla1 = tabla.Facturamsr.objects.filter(sucursal=suc.sucursal.pk, fechaemision__month=mes)
            if v != 0:
                tabla1 = tabla1.filter(vendedor=v)
            if tipo==1:
                tabla1 = tabla1.filter(formapago__condicion__pk=1)
            elif tipo==2:
                tabla1 = tabla1.filter(formapago__condicion__pk=2)
            elif tipo==3:
                tabla1 = tabla1.filter(estado=2)
            tabla1 = tabla1.annotate(subtotal = ExpressionWrapper(F('preciofinaltotal') - F('impuestototal'), output_field=FloatField()))
            precio=tabla1.aggregate(suma=Sum(F('preciofinaltotal') - F('impuestototal')))
            iva=tabla1.aggregate(suma=Sum('impuestototal'))
            precio = precio['suma']
            iva = iva['suma']
            if precio and iva:
                total = precio + iva
            lista = a.strftime("%Y%m%d") + ',' + str(rango) +','+ str(v) + ',' + str(tipo)
            if 'submit_imprimir' in request.POST:
                return HttpResponseRedirect(reverse('vta_lprgeneral', kwargs={'tabla1':lista} ))
            elif 'submit_excel' in request.POST:
                return HttpResponseRedirect(reverse('vta_csvgeneral', kwargs={'tabla1':lista} ))
    else:
        form = formulario.FormGeneral()
    return render(request, 'vta/reportes/general.html',{'vendedor':tabla.Vendedores.objects.all(),
    'tabla':tabla1, 'fecha':a.strftime("%Y-%m-%d"),'rango':rango,
    'precio':precio,'iva':iva,'total':total, 'v':v, 'tipo':tipo, })

@login_required
def lpr_general(request,tabla1):
    suc=LoggedInUser.objects.get(user=request.user)
    lista = list(tabla1.split(','))
    a = datetime.strptime(lista[0],'%Y%m%d')
    total = 0
    rango = int(lista[1])
    v = int(lista[2])
    tipo = int(lista[3])
    b = a + timedelta(days=1)
    if rango == 1:
        b = a + timedelta(days=1)
        tabla2 = tabla.Facturamsr.objects.filter(sucursal=suc.sucursal.pk, fechaemision__range=(a,b))
    else:
        mes = a.strftime('%m')
        tabla2 = tabla.Facturamsr.objects.filter(sucursal=suc.sucursal.pk, fechaemision__month=mes)
    if v != 0:
        tabla2 = tabla2.filter(vendedor=v)
    if tipo==1:
        tabla2 = tabla2.filter(formapago__condicion__pk=1)
    elif tipo==2:
        tabla2 = tabla2.filter(formapago__condicion__pk=2)
    elif tipo==3:
        tabla2 = tabla2.filter(estado=2)
    tabla2 = tabla2.annotate(subtotal = ExpressionWrapper(F('preciofinaltotal') - F('impuestototal'), output_field=FloatField()))
    precio=tabla2.aggregate(suma=Sum(F('preciofinaltotal') - F('impuestototal')))
    iva=tabla2.aggregate(suma=Sum('impuestototal'))
    precio = precio['suma']
    iva = iva['suma']
    if precio and iva:
        total = precio + iva
    return render(request, 'vta/reportes/resumeng.html', {'tabla':tabla2,'precio':precio,'iva':iva,'total':total })

@login_required
def reporteg_csv(request, tabla1):
    suc=LoggedInUser.objects.get(user=request.user)
    lista = list(tabla1.split(','))
    a = datetime.strptime(lista[0],'%Y%m%d')
    rango = int(lista[1])
    v = int(lista[2])
    tipo = int(lista[3])
    b = a + timedelta(days=1)
    if rango == 1:
        b = a + timedelta(days=1)
        tabla2 = tabla.Facturamsr.objects.filter(sucursal=suc.sucursal.pk, fechaemision__range=(a,b))
    else:
        mes = a.strftime('%m')
        tabla2 = tabla.Facturamsr.objects.filter(sucursal=suc.sucursal.pk, fechaemision__month=mes)
    if v != 0:
        tabla2 = tabla2.filter(vendedor=v)
    if tipo==1:
        tabla2 = tabla2.filter(formapago__condicion__pk=1)
    elif tipo==2:
        tabla2 = tabla2.filter(formapago__condicion__pk=2)
    elif tipo==3:
        tabla2 = tabla2.filter(estado=2)
    tabla2 = tabla2.annotate(subtotal = ExpressionWrapper(F('preciofinaltotal') - F('impuestototal'), output_field=FloatField()))
    precio=tabla2.aggregate(suma=Sum(F('preciofinaltotal') - F('impuestototal')))
    iva=tabla2.aggregate(suma=Sum('impuestototal'))
    precio = precio['suma']
    iva = iva['suma']
    if precio and iva:
        total = precio + iva
    rows = ([(i.fechaemision).strftime("%Y-%m-%d"), i.serie, i.cliente.pk, i.cliente, i.subtotal, i.impuestototal, i.formapago.condicion, i.vendedor.identificacion.first_name ] for i in tabla2)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    x = list(writer.writerow(['FECHA', 'REFERENCIA', 'COD CLIENTE', 'NOMBRE CLIENTE', 'PRECIO', 'IVA', 'TIPO VENTA', 'VENDEDOR']))
    y = list(((writer.writerow(row) for row in rows)))
    z = x + y
    response = StreamingHttpResponse(z,content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename = "resumengeneral.csv"'
    return response

@login_required
def ventasxitem(request):
    reino(request)
    suc=LoggedInUser.objects.get(user=request.user)
    tabla1=None
    a=date.today()
    rango=1
    if request.method=="POST":
        form = formulario.FormVtaItem(request.POST)
        if form.is_valid():
            a = form.cleaned_data['fecha']
            rango = int(form.cleaned_data['rango'])
            if rango == 1:
                b = a + timedelta(days=1)
                tabla1 = tabla.Facturadet.objects.filter(bodega__sucursal=suc.sucursal.pk, referencia__fechaemision__range=(a,b))
            else:
                mes = a.strftime('%m')
                tabla1 = tabla.Facturadet.objects.filter(bodega__sucursal=suc.sucursal.pk, referencia__fechaemision__month=mes)
            lista = a.strftime("%Y%m%d") + ',' + str(rango)    
            tabla1 = tabla1.values('item__producto__familia__rubro','item__pk','item').annotate(Sum('unidades'),Sum('preciofinal'), Sum('impuesto'))
            if 'submit_imprimir' in request.POST:
                return HttpResponseRedirect(reverse('vta_lprvtaxitem', kwargs={'parametros':lista}))
            elif 'submit_excel' in request.POST:
                return HttpResponseRedirect(reverse('vta_csvixv', kwargs={'parametros':lista }))
    else:
        form = formulario.FormVtaItem()
    return render(request, 'vta/reportes/ventasxitem.html',{'tabla':tabla1, 'fecha':a.strftime("%Y-%m-%d"),
        'rango':rango, 'suc':suc})

@login_required
def lpr_vtaitem(request, parametros):
    suc = LoggedInUser.objects.get(user=request.user)
    lista = list(parametros.split(','))
    a = datetime.strptime(lista[0], '%Y%m%d')
    rango = int(lista[1])
    tabla1=tabla.Facturadet.objects.filter(bodega__sucursal=suc.sucursal.pk)
    if rango==1:
        b = a +timedelta(days=1)
        tabla1 = tabla1.filter(referencia__fechaemision__range=(a,b))
    else:
        mes = a.strftime('%m')
        tabla1 = tabla1.filter(referencia__fechaemision__month=mes)
    tabla1 = tabla1.values('item__producto__familia__rubro','item__pk','item').annotate(Sum('unidades'),Sum('preciofinal'), Sum('impuesto'))
    return render(request, 'vta/reportes/resumenvxi.html', {'tabla':tabla1})

@login_required
def itemxvta_csv(request, parametros):
    suc=LoggedInUser.objects.get(user=request.user)
    lista = list(parametros.split(','))
    a = datetime.strptime(lista[0],'%Y%m%d')
    rango = int(lista[1])
    tabla1=tabla.Facturadet.objects.filter(bodega__sucursal=suc.sucursal.pk)
    if rango==1:
        b = a +timedelta(days=1)
        tabla1 = tabla1.filter(referencia__fechaemision__range=(a,b))
    else:
        mes = a.strftime('%m')
        tabla1 = tabla1.filter(referencia__fechaemision__month=mes)
    tabla1 = tabla1.values('item__producto__familia__rubro','item__pk','item').annotate(Sum('unidades'),Sum('preciofinal'), Sum('impuesto'))
    rows = ([i['item__producto__familia__rubro'], i['item__pk'], i['unidades__sum'], i['preciofinal__sum'], i['impuesto__sum']] for i in tabla1)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    x = list(writer.writerow(['RUBRO', 'CODIGO', 'CANTIDAD', 'PRECIO', 'IVA']))
    y = list(((writer.writerow(row) for row in rows)))
    z = x + y
    response = StreamingHttpResponse(z,content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename = "resumenitemxvta.csv"'
    return response