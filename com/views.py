import csv, io, datetime
from . import forms, models
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Sum, ExpressionWrapper, F, FloatField
from django.forms import ModelForm, Form, modelformset_factory, inlineformset_factory
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from inv.models import Sucursal, N4Item, Estado, ExoTipo, Bodega, ExistenciaBodega, N2Familia, MarcaItem, MarcaVehiculo, ExoRubro, Kardex,N4ItemVencimiento
from vta.models import ExoRubroCliente, Cliente
from vta.apoyo import reino, prikey
from vta.forms import FormCatalogo
from usuarios.models import LoggedInUser
from django.db import transaction

class Echo:
    def write(self, value):
        return value

@login_required
def index(request):
    reino(request)
    return render(request,'com/index.html',{'suc':LoggedInUser.objects.get(user=request.user)})

# ---------------------------------------------------------------------
#          VENTANA PROVEEDORES
# ---------------------------------------------------------------------
@login_required
def Proveedor_list(request):
    reino(request)
    return render(request,'com/comProveedor/Proveedor_List.html',{
        'proveedor':models.Proveedor.objects.all(),
        'suc':LoggedInUser.objects.get(user=request.user)})

class ProveedorNuevo(BSModalCreateView):
    template_name = 'com/comProveedor/modal_create.html'
    form_class = forms.ProveedorForm
    success_message = 'Se ha agregado un nuevo registro'
    success_url = reverse_lazy(Proveedor_list)

class ProveedorEditar(BSModalUpdateView):
    model = models.Proveedor
    template_name = 'com/comProveedor/modal_update.html'
    form_class = forms.ProveedorForm
    success_message = 'Registros actualizados satisfactoriamente'
    success_url = reverse_lazy(Proveedor_list)

@login_required
def ProveedorContacto(request,cod):
    reino(request)
    msr = models.Proveedor.objects.get(abreviatura=cod)
    det = inlineformset_factory(models.Proveedor,models.ProveedorContacto, fields=('nombre','telefonos','cargo',), extra=1)
    if request.method == 'POST':
        formset = det(request.POST, instance=msr)
        if formset.is_valid():
            formset.save()
            return redirect('com_proveedorContact', cod=msr.abreviatura)
    formset = det(instance=msr)
    return render(request,'com/comProveedor/Proveedor_Contacto.html',{'formset':formset,'Proveedor':msr,
        'suc':LoggedInUser.objects.get(user=request.user)})

@login_required
def ProveedorDireccion(request,cod):
    reino(request)
    msr = models.Proveedor.objects.get(abreviatura=cod)
    det = inlineformset_factory(models.Proveedor,models.ProveedorDireccion,fields =('nombre','direccion','telefono'),extra=1)
    if request.method == 'POST':
        formset = det(request.POST,instance= msr)
        if formset.is_valid():
            formset.save()
            return redirect('com_proveedorAddress',cod=msr.abreviatura)
    formset = det(instance = msr)
    return render(request,'com/comProveedor/Proveedor_Direccion.html',{'formset':formset, 'Proveedor':msr,
        'suc':LoggedInUser.objects.get(user=request.user)})

# ---------------------------------------------------------------------
#          VENTANA COTIZACION
# ---------------------------------------------------------------------

@login_required
def Cotizacion_list(request):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    return render(request,'com/comCotizacion/Cotizacion_List.html',{
        'cotizacion':models.CotizacionMsr.objects.filter(referencia__contains=suc.sucursal.pk).order_by('-fecha'),
        'suc':suc})

class CotizacionNuevo(BSModalCreateView):
    template_name = 'com/comCotizacion/modal_create.html'
    form_class = forms.CotizacionMsrForm
    success_message = 'Registros actualizados satisfactoriamente'
    success_url = reverse_lazy(Cotizacion_list)
    def form_valid(self, form):
        suc = LoggedInUser.objects.get(user=self.request.user)
        form.instance.referencia = prikey(suc, '-CO-')
        return super(CotizacionNuevo, self).form_valid(form)

class CotizacionEditar(BSModalUpdateView):
    model = models.CotizacionMsr
    template_name = 'com/comCotizacion/modal_update.html'
    form_class = forms.CotizacionMsrForm
    def get_success_url(self):
        llave = self.kwargs['pk']
        return reverse_lazy(CotizacionDetalle, kwargs={'cod':llave}) 

@transaction.atomic
@login_required
def CotizacionDetalle(request,cod):
    reino(request)
    msr = models.CotizacionMsr.objects.get(referencia=cod)
    if msr.finalizado:
        raise PermissionDenied()
    else:
        det = inlineformset_factory(models.CotizacionMsr, models.CotizacionDet, form=forms.CotizacionDetForm,extra=1)
        if request.method == 'POST':
            formset = det(request.POST,instance=msr)
            if formset.is_valid():
                if 'submit_aplicar' in request.POST:
                    for form in formset:
                        if form.cleaned_data != {}:
                            if form.cleaned_data['DELETE']:
                                if form.cleaned_data['id'] != None:
                                    linea = models.CotizacionDet.objects.get(id = form.cleaned_data['id'].id)
                                    linea.delete()
                            else:
                                if form.is_valid():
                                    decimales = form.cleaned_data['unidades']
                                    item = form.cleaned_data['item']
                                    if item.producto.entero == 'S':
                                        print(decimales)
                                        if float(decimales)-float(int(decimales)) > float(0):
                                            messages.warning(request,'No se puede efectuar operacion, el item : "%s" pertenece a un producto cuyos movimientos son enteros, no decimales'%(
                                                form.cleaned_data['item']
                                                )
                                            )
                                            return redirect('com_cotizacionDetail',cod=msr.referencia)
                                    form.save()
                    return redirect('com_cotizacionDetail',cod=msr.referencia)
                else:
                    if 'document' in request.FILES:
                        archivo1 = request.FILES['document']
                        if not archivo1.name.endswith('.csv'):
                            messages.warning(request,'No es un archivo delimitado por comas (CSV)')
                        else:
                            data_set = archivo1.read().decode('UTF-8')
                            io_string = io.StringIO(data_set)
                            next(io_string)
                            e = []
                            for i in csv.reader(io_string, delimiter=',', quotechar="|"):
                                try:
                                    it = N4Item.objects.get(pk=i[0])
                                    try:
                                        if float(i[1]) > 0:
                                            decimales = float(i[1])
                                            if it.producto.entero == 'S':
                                                if float(decimales)-float(int(decimales)) > float(0):
                                                    messages.warning(request,'No se puede cargar del excel, el item : "%s" pertenece a un producto cuyos movimientos son enteros, no decimales'%(
                                                        it
                                                        )
                                                    )
                                                else:
                                                    models.ProforDet.objects.update_or_create(unidades = i[1],
                                                        item = it, referencia=models.ProformaMsr.objects.get(pk=msr.referencia),
                                                        costo = float(i[2]), impuesto=float(i[3]))
                                            else:
                                                models.CotizacionDet.objects.update_or_create(unidades = i[1],
                                                    item = it, referencia=models.CotizacionMsr.objects.get(pk=msr.referencia))
                                    except:
                                        e.append(i[0])      
                                except N4Item.DoesNotExist:
                                    e.append(i[0])
                            if len(e) > 0:
                                messages.warning(request,'{} items no fueron ingresado porque no cumplen los criterios'.format(len(e)))
                    else:
                        messages.warning(request,'No se ha seleccionado ningun archivo')
        formset = det(instance=msr)
        return render(request,'com/comCotizacion/Cotizacion_Det.html',{'formset':formset,'Cotizacion':msr,
            'suc':LoggedInUser.objects.get(user=request.user) })

@login_required
def cotizacion_csv(request):
    tabla = N4Item.objects.all()
    rows = ([i.id_n4,'0'] for i in tabla)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    x = list(writer.writerow(['ITEM', 'CANTIDAD']))
    y = list(((writer.writerow(row) for row in rows)))
    z = x + y
    response = StreamingHttpResponse(z,content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename = "cot_plantilla.csv"'
    return response

# ---------------------------------------------------------------------
#          VENTANA PROFORMA
# ---------------------------------------------------------------------

@login_required
def Proforma_list(request):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    return render(request,'com/comProforma/Proforma_List.html',{
        'proforma':models.ProformaMsr.objects.filter(referencia__contains=suc.sucursal.pk).order_by('-fecha'),
        'suc':suc})

class ProformaNuevo(BSModalCreateView):
    template_name = 'com/comProforma/modal_create.html'
    form_class = forms.ProformaMsrForm
    success_message = 'Nueva proforma creada'
    success_url = reverse_lazy(Proforma_list)
    def form_valid(self, form):
        suc = LoggedInUser.objects.get(user=self.request.user)
        form.instance.referencia = prikey(suc, '-PF-')
        return super(ProformaNuevo, self).form_valid(form)

class ProformaEditar(BSModalUpdateView):
    model = models.ProformaMsr
    template_name = 'com/comProforma/modal_update.html'
    form_class = forms.ProformaMsrForm
    def get_success_url(self):
        llave = self.kwargs['pk']
        return reverse_lazy(ProformaDetalle, kwargs={'cod':llave})

@transaction.atomic
@login_required
def ProformaDetalle(request,cod):
    reino(request)
    msr = models.ProformaMsr.objects.get(referencia=cod)
    if msr.finalizado:
        raise PermissionDenied()
    else:
        if msr.cotizacion:
            detalle = models.CotizacionDet.objects.filter(referencia = msr.cotizacion.pk)
            if not msr.importado and detalle:
                for i in detalle:
                    models.ProforDet.objects.create(
                        referencia = models.ProformaMsr.objects.get(pk=cod),
                        item = i.item, unidades = i.unidades, costo = 1, impuesto=15
                    )
                msr.importado = True
                msr.save()
        det = inlineformset_factory(models.ProformaMsr,models.ProforDet,form= forms.ProformaDetForm,extra=1)
        if request.method == 'POST':
            formset = det(request.POST,instance=msr)
            if formset.is_valid():
                if 'submit_aplicar' in request.POST:
                    for form in formset:
                        if form.cleaned_data != {}:
                            if form.cleaned_data['DELETE']:
                                if form.cleaned_data['id'] != None:
                                    linea = models.ProforDet.objects.get(id = form.cleaned_data['id'].id)
                                    linea.delete()
                            else:
                                if form.is_valid():
                                    decimales = form.cleaned_data['unidades']
                                    item = form.cleaned_data['item']
                                    if item.producto.entero == 'S':
                                        print(decimales)
                                        if float(decimales)-float(int(decimales)) > float(0):
                                            messages.warning(request,'No se puede efectuar operacion, el item : "%s" pertenece a un producto cuyos movimientos son enteros, no decimales'%(
                                                form.cleaned_data['item']
                                                )
                                            )
                                            return redirect('com_proformaDetail',cod = msr.referencia)
                                    form.save()
                    return redirect('com_proformaDetail',cod = msr.referencia)
                else:
                    if 'document' in request.FILES:
                        archivo1 = request.FILES['document']
                        if not archivo1.name.endswith('.csv'):
                            messages.warning(request,'No es un archivo delimitado por comas (CSV)')
                        else:
                            data_set = archivo1.read().decode('UTF-8')
                            io_string = io.StringIO(data_set)
                            next(io_string)
                            e = []
                            for i in csv.reader(io_string, delimiter=',', quotechar="|"):
                                print('recorriendo')
                                try:
                                    print(i[0])
                                    it = N4Item.objects.get(pk=i[0])
                                    try:
                                        if float(i[1]) > 0:
                                            decimales = float(i[1])
                                            if it.producto.entero == 'S':
                                                if float(decimales)-float(int(decimales)) > float(0):
                                                    messages.warning(request,'No se puede cargar del excel, el item : "%s" pertenece a un producto cuyos movimientos son enteros, no decimales'%(
                                                        it
                                                        )
                                                    )
                                                else:
                                                    models.ProforDet.objects.update_or_create(unidades = i[1],
                                                        item = it, referencia=models.ProformaMsr.objects.get(pk=msr.referencia),
                                                        costo = float(i[2]), impuesto=float(i[3]))
                                            else:
                                                models.ProforDet.objects.update_or_create(unidades = i[1],
                                                    item = it, referencia=models.ProformaMsr.objects.get(pk=msr.referencia),
                                                    costo = float(i[2]), impuesto=float(i[3]))
                                        else:
                                            e.append(i[0])
                                    except:
                                        e.append(i[0])      
                                except N4Item.DoesNotExist:
                                    e.append(i[0])
                            if len(e) > 0:
                                messages.warning(request,'{} items no fueron ingresado porque no cumplen los criterios'.format(len(e)))
                                return redirect('com_proformaDetail',cod = msr.referencia)
                    else:
                        messages.warning(request,'No se ha seleccionado ningun archivo')
        formset = det(instance = msr)
        return render(request,'com/comProforma/Proforma_Det.html',{'formset':formset,'Proforma':msr,
            'suc':LoggedInUser.objects.get(user=request.user)})

@login_required
def proforma_csv(request):
    tabla = N4Item.objects.all()
    rows = ([i.id_n4,'0','0','0'] for i in tabla)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    x = list(writer.writerow(['ITEM', 'CANTIDAD','COSTO','IMPUESTO']))
    y = list(((writer.writerow(row) for row in rows)))
    z = x + y
    response = StreamingHttpResponse(z,content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename = "pro_plantilla.csv"'
    return response

# ---------------------------------------------------------------------
#          VENTANA ORDEN DE COMPRA
# ---------------------------------------------------------------------

@login_required
def OrdenCompra_list(request):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    return render(request,'com/comOrdenCompra/OrdenCompra_List.html',{
        'ordencompra':models.OrdenCompraMsr.objects.filter(referencia__contains=suc.sucursal.pk).order_by('-fecha'),
        'suc':suc })

class OrdenCompraNuevo(BSModalCreateView):
    template_name = 'com/comOrdenCompra/modal_create.html'
    form_class = forms.OrdenCompraMsrForm
    success_message = 'Nuevo registro insertado'
    success_url = reverse_lazy(OrdenCompra_list)
    def get_context_data(self, **kwargs):
        hoy = datetime.date.today()
        vence = hoy + datetime.timedelta(days=30)
        context = super(OrdenCompraNuevo, self).get_context_data(**kwargs)
        context['vencimiento'] = vence.strftime("%Y-%m-%d")
        return context
    def form_valid(self, form):
        suc = LoggedInUser.objects.get(user=self.request.user)
        form.instance.referencia = prikey(suc, '-OC-')
        form.instance.estado = Estado.objects.get(pk=4)
        return super(OrdenCompraNuevo, self).form_valid(form)

class OrdenCompraEditar(BSModalUpdateView):
    model = models.OrdenCompraMsr
    template_name = 'com/comOrdenCompra/modal_update.html'
    form_class = forms.OrdenCompraMsrForm
    def get_context_data(self, **kwargs):
        oc = self.kwargs['pk']
        vence = models.OrdenCompraMsr.objects.get(pk=oc)
        context = super(OrdenCompraEditar, self).get_context_data(**kwargs)
        context['vencimiento'] = vence.vencimiento.strftime("%Y-%m-%d")
        return context
    def get_success_url(self):
        llave = self.kwargs['pk']
        return reverse_lazy(OrdenCompraDetalle, kwargs={'cod':llave})

@transaction.atomic
@login_required
def OrdenCompraDetalle(request,cod):
    reino(request)
    msr = models.OrdenCompraMsr.objects.get(referencia=cod)
    if msr.estado.pk == 4:
        if msr.proforma:
            detalle = models.ProforDet.objects.filter(referencia = msr.proforma.pk)
            if not msr.importado and detalle:
                for i in detalle:
                    models.OrdenCompraDet.objects.create(
                        referencia = models.OrdenCompraMsr.objects.get(pk=cod),
                        item = i.item, unidades = i.unidades, costo = i.costo,
                        impuesto= i.impuesto
                    )
                msr.importado = True
                msr.save()
        detform = forms.make_orden_compra_det()
        det = inlineformset_factory(models.OrdenCompraMsr,models.OrdenCompraDet,form = detform,extra=1)
        if request.method == 'POST':
            formset = det(request.POST,instance=msr)
            if formset.is_valid():
                if 'submit_aplicar' in request.POST:
                    for form in formset:
                        if form.cleaned_data != {}:
                            if form.cleaned_data['DELETE']:
                                if form.cleaned_data['id'] != None:
                                    linea = models.OrdenCompraDet.objects.get(id = form.cleaned_data['id'].id)
                                    linea.delete()
                            else:
                                decimales = form.cleaned_data['unidades']
                                item = form.cleaned_data['item']
                                if item.producto.entero == 'S':
                                    if float(decimales)-float(int(decimales))> float(0):
                                            messages.warning(request,'No se puede efectuar operacion, el item : "%s" pertenece a un producto cuyos movimientos son enteros, no decimales'%(
                                                form.cleaned_data['item']
                                                )
                                            )
                                            return redirect('com_ordencompraDetail',cod = msr.referencia)
                                form.save()
                    return redirect('com_ordencompraDetail',cod = msr.referencia)
                else:
                    if 'document' in request.FILES:
                        archivo1 = request.FILES['document']
                        if not archivo1.name.endswith('.csv'):
                            messages.warning(request,'No es un archivo delimitado por comas (CSV)')
                        else:
                            data_set = archivo1.read().decode('UTF-8')
                            io_string = io.StringIO(data_set)
                            next(io_string)
                            e = []
                            for i in csv.reader(io_string, delimiter=',', quotechar="|"):
                                try:
                                    it = N4Item.objects.get(pk=i[0])
                                    try:
                                        if float(i[1]) > 0:
                                            decimales = float(i[1])
                                            if it.producto.entero == 'S':
                                                if float(decimales)-float(int(decimales)) > float(0):
                                                    messages.warning(request,'No se puede cargar del excel, el item : "%s" pertenece a un producto cuyos movimientos son enteros, no decimales'%(
                                                        it
                                                        )
                                                    )
                                                else:
                                                    models.OrdenCompraDet.objects.update_or_create(unidades = float(i[1]),
                                                        item = it, referencia=models.OrdenCompraMsr.objects.get(pk=msr.referencia),
                                                        costo = float(i[2]), impuesto=float(i[3]))
                                        else:
                                            models.OrdenCompraDet.objects.update_or_create(unidades = float(i[1]),
                                                item = it, referencia=models.OrdenCompraMsr.objects.get(pk=msr.referencia),
                                                costo = float(i[2]), impuesto=float(i[3]))
                                    except:
                                        e.append(i[0])      
                                except N4Item.DoesNotExist:
                                    e.append(i[0])
                            if len(e) > 0:
                                messages.warning(request,'{} items no fueron ingresado porque no cumplen los criterios'.format(len(e)))
                    else:
                        messages.warning(request,'No se ha seleccionado ningun archivo')
        formset = det(instance = msr)
        tipo='Internacional' if msr.tipo == 'I' else 'Local'
        moneda='Cordobas' if msr.moneda == 'C' else 'Dolares'
        return render(request,'com/comOrdenCompra/OrdenCompra_Det.html',{'formset':formset,'OrdenCompra':msr,
            'suc':LoggedInUser.objects.get(user=request.user), 'tipo':tipo, 'moneda':moneda })
    else:
        raise PermissionDenied()

@login_required
def ordencompra_csv(request):
    tabla = N4Item.objects.all()
    rows = ([i.id_n4,'0','0','0'] for i in tabla)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    x = list(writer.writerow(['ITEM', 'CANTIDAD','COSTO','IMPUESTO']))
    y = list(((writer.writerow(row) for row in rows)))
    z = x + y
    response = StreamingHttpResponse(z,content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename = "oc_plantilla.csv"'
    return response

# ---------------------------------------------------------------------
#          VENTANA ENTRADA DE MERCADERIA
# ---------------------------------------------------------------------

@login_required
def EntradaMercaderia_list(request):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    oc = models.OrdenCompraMsr.objects.filter(referencia__contains=suc.sucursal.pk, estado=3, recibido=False).order_by('-fecha')
    if request.method=="POST":
        form = forms.EmList(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('com_em', args=[form.cleaned_data['cmboc']]))
    else:
        form = forms.EmList()
    return render(request,'com/comEntradaMercaderia/EntradaMercaderia_List.html',{
        'entradamercaderia':models.EntradaMercaderiaMsr.objects.filter(referencia__contains=suc.sucursal.pk).order_by('-fecha'),
        'suc':suc, 'oc':oc})


@transaction.atomic
@login_required
def nuevarem(request, orden):
    suc = LoggedInUser.objects.get(user=request.user)
    temporal = models.TempRem.objects.all().first()
    if temporal:
        if orden != temporal.orden.pk:
            models.TempRem.objects.all().delete()
    if request.method=='POST':
        form = forms.EntradaMercaderiaMsrForm(request.POST)
        if form.is_valid():
            costoc = float(form.cleaned_data['costo_compra'])
            costoi = float(form.cleaned_data['costo_iva'])
            bod = Bodega.objects.get(pk=form.cleaned_data['bodega'])
            if 'grabar' in request.POST:
                oc=models.OrdenCompraMsr.objects.get(pk=orden)
                c = datetime.datetime.today()
                d = c + datetime.timedelta(days=1)
                x = (models.EntradaMercaderiaMsr.objects.filter(
                    referencia__contains=suc.sucursal.pk).filter(
                    fecha__range = (c.date(),d.date())).count()) + 1
                x = '{:0>5}'.format(x)
                ref = suc.sucursal.pk + '-EM-' + c.strftime("%Y%m%d") + '-' + x
                dias = int(form.cleaned_data['validez'])

                
                with transaction.atomic():
                    try:
                        em = models.EntradaMercaderiaMsr.objects.create(
                            referencia=ref, proveedor=oc.proveedor, cliente=oc.cliente,
                            condicion=form.cleaned_data['condicion'], fecha=datetime.datetime.now(),
                            facturas=form.cleaned_data['facturas'], ordenes_compra=form.cleaned_data['ordenes_compra'],
                            fecha_vencimiento = datetime.datetime.now() + datetime.timedelta(days=dias),
                            estado= Estado.objects.get(pk=5) if costoc==costoi==0 else Estado.objects.get(pk=4), 
                            poliza = form.cleaned_data['poliza'], costo_compra=costoc, costo_iva=costoi)

                        #grabar el detalle de la cotizacion                    
                        ocdet = models.OrdenCompraDet.objects.filter(referencia=oc.pk).order_by('pk')
                        det = list(form.cleaned_data['detalle'].split(','))
                        cont=0
                        # print(list(form.cleaned_data['detalle'].split(',')))
                        for i in ocdet: #Graba desde el detalle de la orden de Compra
                            
                            decimales = float(det[cont])
                            it = i.item
                            
                            if it.producto.entero == 'S':
                                if float(decimales)-float(int(decimales)) > float(0):
                                    messages.warning(request,'No se puede grabar, el item : "%s" pertenece a un producto cuyos movimientos son enteros, no decimales'%(
                                        it
                                        )
                                    )
                                    em.delete()
                                    raise TypeError('el item no puede tener decimales')
                            models.EntradaMercaderiaDet.objects.create(
                                referencia=models.EntradaMercaderiaMsr.objects.get(pk=em.referencia),
                                bodega=bod,
                                item=i.item,
                                unidades=float(det[cont]),  
                                costo=float(det[cont+1]),
                                impuesto=float(det[cont+2]), 
                                tipo_exo=ExoTipo.objects.get(pk=det[cont+3])
                            ) 
                            i.despachado += float(det[cont])
                            i.save() 
                            if em.cliente and i.item.producto.exorubro.pk != 1: #Si el exorubro del item Es any but not exone
                                ExoRubroCliente.objects.create(
                                    referencia=em.pk, 
                                    cooperativa=str(oc.cliente.cooperativa.all().first()),  
                                    costo=float(det[cont+1]),
                                    precio=(float(det[cont]) * i.item.preciomax), 
                                    unidades = float(det[cont]),
                                    cliente=Cliente.objects.get(pk=oc.cliente.pk),
                                    rubro = ExoRubro.objects.get(pk=i.item.producto.exorubro.pk)
                                    )
                            
                            if i.fecha_venc:
                                #creamos o aumentamos la tupla en su registro de vencimiento
                                existevencimiento = N4ItemVencimiento.objects.filter(item = i.item,referencia =em.referencia,fecha_venc = datetime.datetime.strptime(i.fecha_venc,'%Y-%m-%d') ).exists()

                                if existevencimiento:
                                    vencimiento = N4ItemVencimiento.objects.get(item = i.item,referencia =em.referencia,fecha_venc = datetime.datetime.strptime(i.fecha_venc,'%Y-%m-%d'))
                                    vencimiento.cantidad = vencimiento.cantidad + float(det[cont])
                                    vencimiento.fecha_cero ='.'
                                    vencimiento.save()
                                else:
                                    N4ItemVencimiento.objects.create(
                                        referencia = em.referencia,
                                        item = i.item,
                                        fecha_venc = datetime.datetime.strptime(i.fecha_venc,'%Y-%m-%d'),
                                        cantidad = float(det[cont])
                                    )       
                                
                            cont+=5 

                        # grabar el detalle de la tabla temporal
                        tem = models.TempRem.objects.all()
                        if tem:
                            for i in tem: # Graba elementos adicionales (regalias) de la tabla temporal
                                
                                decimales = float(i.unidades)
                                it = i.item
                                
                                if it.producto.entero == 'S':
                                    if float(decimales)-float(int(decimales)) > float(0):
                                        messages.warning(request,'No se puede grabar, el item : "%s" pertenece a un producto cuyos movimientos son enteros, no decimales'%(
                                            it
                                            )
                                        )
                                        em.delete()
                                        raise TypeError('el item no puede tener decimales')
                                
                                models.EntradaMercaderiaDet.objects.create(
                                    referencia = models.EntradaMercaderiaMsr.objects.get(pk=em.referencia),
                                    bodega=bod, 
                                    item=i.item,
                                    unidades=i.unidades,  
                                    costo=0,
                                    impuesto=0,
                                    tipo_exo=ExoTipo.objects.get(pk='G')
                                )
                                
                                if i.fecha_venc:
                                    #creamos o aumentamos la tupla en su registro de vencimiento
                                    existevencimiento = N4ItemVencimiento.objects.filter(item = i.item,referencia =em.referencia,fecha_venc = datetime.datetime.strptime(i.fecha_venc,'%Y-%m-%d') ).exists()

                                    if existevencimiento:
                                        vencimiento = N4ItemVencimiento.objects.get(item = i.item,referencia =em.referencia,fecha_venc = datetime.datetime.strptime(i.fecha_venc,'%Y-%m-%d'))
                                        vencimiento.cantidad = vencimiento.cantidad + i.unidades
                                        vencimiento.fecha_cero ='.'
                                        vencimiento.save()
                                    else:
                                        N4ItemVencimiento.objects.create(
                                            referencia = em.referencia,
                                            item = i.item,
                                            fecha_venc = datetime.datetime.strptime(i.fecha_venc,'%Y-%m-%d'),
                                            cantidad = i.unidades
                                        )

                            tem.delete()

                        cant = models.OrdenCompraDet.objects.filter(referencia=orden).aggregate(Sum('unidades'))
                        desp = models.OrdenCompraDet.objects.filter(referencia=orden).aggregate(Sum('despachado'))
                        if desp['despachado__sum'] >= cant['unidades__sum']:
                            oc.recibido = True
                            oc.save()
                        if em.costo_compra == em.costo_iva == 0: # Actualizar existencia bodega
                            emdet = models.EntradaMercaderiaDet.objects.filter(referencia=em.pk)
                            for i in emdet:
                                #Aumentamos su existencia de bodega
                                exbod = ExistenciaBodega.objects.filter(bodega=bod).get(item=i.item)
                                exbod.cantidad += i.unidades
                                exbod.save()
                                #Creamos el registro en el Kardex
                                Kardex.objects.create(referencia=em.pk, entrada=i.unidades, salida=0, debe=i.costo,bodega = bod,
                                haber=0, saldo=0, costounitario=0, existencia=0, item=i.item, sucursal=Sucursal.objects.get(pk=suc.sucursal.pk))
                        
                        if em.costo_compra > 0 or em.costo_iva >0:
                            em.estado = Estado.objects.get(pk=5)
                        else:
                            em.estado = Estado.objects.get(pk=3)

                        em.save()
                        return HttpResponseRedirect(reverse('com_imprimir', args=[em.pk]))
                    except:
                        print('invoque la excepcion')
                        return redirect('com_em',orden = orden)  

            else:
                return HttpResponse('<h1>Debe ingresar al menos un item</h1>')
        #form invalid
    else:
        form = forms.EntradaMercaderiaMsrForm()
    data = dict()
    data['form'] = form
    data['oc'] = models.OrdenCompraMsr.objects.get(pk=orden)
    data['tipo']='Internacional' if data['oc'].tipo=='I' else 'Local'
    data['moneda']='Cordobas' if data['oc'].moneda=='C' else 'Dolares'
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    data['articulos'] = N4Item.objects.exclude(producto__naturaleza='C').exclude(producto__naturaleza='P').exclude(producto__naturaleza='S')
    data['temporal'] = models.TempRem.objects.all()
    data['exoneracion'] = models.ExoTipo.objects.all()
    data['bodega'] =  Bodega.objects.filter(sucursal=suc.sucursal.pk)
    data['cod'] = orden
    data['detalle'] = models.OrdenCompraDet.objects.filter(referencia=orden).annotate(
        cantidad=ExpressionWrapper(F('unidades')-F('despachado'), output_field=FloatField()),
        costou=ExpressionWrapper(F('costo')/F('unidades'), output_field=FloatField()),
        costot=ExpressionWrapper((F('unidades')-F('despachado')) * (F('costo')/F('unidades')), output_field=FloatField())
    ).order_by('pk')
    data['tempo']=models.TempRem.objects.all()

    return render(request, 'com/comEntradaMercaderia/rem.html', data)

# ---------------------------------------------------------------------
#          DAR POR FINALIZADO COTIZACIONES Y PROFORMAS
# ---------------------------------------------------------------------
@login_required
def finalizar(request,cod):
    suc = LoggedInUser.objects.get(user=request.user)
    origen = cod[3:5]
    if origen == 'CO':
        detalle = models.CotizacionDet.objects.filter(referencia=cod)
        if detalle:
            x = models.CotizacionMsr.objects.get(pk=cod)
            x.finalizado = True
            x.save()
        else:
            messages.warning(request,'La cotizacion {} no puede ser finalizada porque carece de un detalle de items'.format(cod))
        return redirect('com_cotizacion')
    elif origen == 'PF':
        detalle = models.ProforDet.objects.filter(referencia=cod)
        if detalle:
            x = models.ProformaMsr.objects.get(pk=cod)
            x.finalizado = True
            x.save()
        else:
            messages.warning(request,'La proforma {} no puede ser finalizada porque carece de un detalle de items'.format(cod))
        return redirect('com_proforma')
    elif origen == 'OC':
        detalle = models.OrdenCompraDet.objects.filter(referencia=cod)
        if detalle:
            x = models.OrdenCompraMsr.objects.get(pk=cod)
            x.estado = Estado.objects.get(pk=5)
            x.save()
        else:
            messages.warning(request,'La orden No {} no puede ser cerrada porque carece de un detalle de items'.format(cod))
        return redirect('com_ordencompra')
    elif origen=='EM':
        x=models.EntradaMercaderiaMsr.objects.get(pk=cod)
        x.estado = Estado.objects.get(pk=3) 
        x.save()
        det = models.EntradaMercaderiaDet.objects.filter(referencia=x.pk)
        subtotal = det.aggregate(st=Sum('costo'))
        imp = det.aggregate(iva=Sum('impuesto'))
        diferencia = 0
        for i in det:
            proprecio = i.costo/subtotal['st']*x.costo_compra
            proiva = (i.impuesto/imp['iva']*x.costo_iva) if imp['iva'] > 0 else 0
            diferencia += proprecio
            i.costo += proprecio
            i.impuesto += proiva
            i.save()
            bod = i.bodega.pk
        if diferencia < x.costo_compra:
             det = models.EntradaMercaderiaDet.objects.filter(referencia=x.pk).first()
             det.costo += (x.costo_compra - diferencia)
             det.save()
        emdet = models.EntradaMercaderiaDet.objects.filter(referencia=x.pk)
        bod = Bodega.objects.get(pk=bod)
        for i in emdet:
            exbod = ExistenciaBodega.objects.filter(bodega=bod).get(item=i.item)
            exbod.cantidad += i.unidades
            exbod.save()
            Kardex.objects.create(referencia=x.pk, entrada=i.unidades, salida=0, debe=i.costo, haber=0, 
            saldo=0, costounitario=i.costo/i.unidades, existencia=0, item=i.item, sucursal=Sucursal.objects.get(pk=suc.sucursal.pk))
        return redirect('com_emlist')
    else:
        return HttpResponseForbidden()

@login_required
def quitar_items(request, item_id):
    """ Elimina elementos temporales en el detalle de la rem """
    reino(request)
    quitar = models.TempRem.objects.get(pk=item_id)
    x = quitar.orden.pk
    quitar.delete()
    return HttpResponseRedirect(reverse('com_em', args=[x]))

@login_required
def imprimir_em(request,cod):
    """ Imprime la proforma en formato html """
    reino(request)
    origen = cod[3:5]
    if origen=='CO':
        msr = models.CotizacionMsr.objects.get(pk=cod)
        detalle = models.CotizacionDet.objects.filter(referencia=cod)
        plantilla = 'com/comCotizacion/reporte_co.html'
    elif origen=='PF':
        msr = models.ProformaMsr.objects.get(pk=cod)
        detalle = models.ProforDet.objects.filter(referencia=cod)
        plantilla = 'com/comProforma/reporte_pf.html'
    elif origen=='OC':
        msr = models.OrdenCompraMsr.objects.get(pk=cod)
        detalle = models.OrdenCompraDet.objects.filter(referencia=cod)
        plantilla = 'com/comOrdenCompra/reporte_oc.html'
    else:
        msr = models.EntradaMercaderiaMsr.objects.get(pk=cod)
        detalle = models.EntradaMercaderiaDet.objects.filter(referencia=cod)
        plantilla = 'com/emmercaderia.html'
    return render(request, plantilla, {'suc':LoggedInUser.objects.get(user=request.user),
        'maestro':msr,'detalle':detalle,}) 

@login_required
def catalogo(request):
    suc = LoggedInUser.objects.get(user=request.user)
    familia = N2Familia.objects.all().order_by('descripcion')
    marca = MarcaItem.objects.all()
    articulos = None
    if request.method == "POST":
        form = FormCatalogo(request.POST)
        if form.is_valid():
            x = form.cleaned_data['buscar']
            articulos = N4Item.objects.filter(
               Q(producto__familia__descripcion__icontains=x) | Q(producto__descripcion__icontains=x) | Q(marca__marca__icontains=x) | Q(descripcion__icontains=x))
    else:
        form = FormCatalogo()
    return render(request,'com/comEntradaMercaderia/catalogo.html',{'articulos':articulos, 'marcaitem':marca, 
        'vehiculo': MarcaVehiculo.objects.all(), 'familia':familia })