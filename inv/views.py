from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from datetime import date,datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse,StreamingHttpResponse
from django.template.loader import render_to_string
from django.template import loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy,reverse
from django.core.files.storage import FileSystemStorage
from django.views.generic import ListView,CreateView
from django.views.generic.edit import UpdateView
from django.forms import ModelForm, Form, modelformset_factory, inlineformset_factory
from . import models, forms
from vta.apoyo import reino
from usuarios.models import LoggedInUser
from django.db.models import Q,Sum,Min
from django.db import transaction
from django.contrib import messages 
from django.core.exceptions import PermissionDenied
from . import conecciones

import csv,io
from vta.models import Facturamsr,Facturadet
from com.models import EntradaMercaderiaMsr,EntradaMercaderiaDet

class Echo:
    def write(self, value):
        return value


# ---------------------------------------------------------------------
#          Recalculo
# ---------------------------------------------------------------------

@login_required
def index(request):
    reino(request)
    return render(request,'inv/invShared/Index.html',{'suc':LoggedInUser.objects.get(user=request.user)})

@login_required
def centralizar(request):
    reino(request)
    conecciones.centralizar_datos('MA')
    return redirect('N4Item_Listar')

@login_required
def recalculo(request):
    reino(request)
    conecciones.recalcular()
    return redirect('N4Item_Listar')

# ---------------------------------------------------------------------
#          N1 RUBRO
# ---------------------------------------------------------------------
@login_required
def rubro_listar(request):
    reino(request)
    # conecciones.centralizar_datos('MA')
    return render(request,'inv/invN1Rubro/list.html',{'rubro':models.N1Rubro.objects.all(),
        'suc':LoggedInUser.objects.get(user=request.user)})

class N1RubroCreate(BSModalCreateView):
    template_name = 'inv/invN1Rubro/formulario.html'
    form_class = forms.RubroForm
    success_message = 'Datos registrados'   
    success_url = reverse_lazy(rubro_listar)

class RubroEdit(BSModalUpdateView):
    model = models.N1Rubro
    template_name = 'inv/invN1Rubro/formulario.html'
    form_class = forms.RubroForm
    success_message = 'Registros actualizados'
    success_url = reverse_lazy(rubro_listar)    

def N1Rubro_Eliminar(request,cod):
    reino(request)
    data = dict()
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    data['rubro'] = models.N1Rubro.objects.get(id_n1 = cod)
    if request.method == 'POST':
        rubro = models.N1Rubro.objects.get(id_n1 = cod)
        familia = models.N2Familia.objects.filter(rubro__id_n1 = cod).count()
        # eliminando las filas
        if familia == 0:
            rubro.delete()
        else:
            messages.warning(request,'El rubro tiene familias asociadas a el no se puede eliminar')
        return redirect('N1Rubro_Listar')
        # return render(request,'inv/invN1Rubro/list.html',{'rubro':models.N1Rubro.objects.all(),'suc':LoggedInUser.objects.get(user=request.user)})
    else:
        return render(request,'inv/invN1Rubro/N1Rubro_Eliminar.html',data)

@login_required
def N1Rubro_save_all(request,form,template_name):
    reino(request)
    data = dict()
    suc = LoggedInUser.objects.get(user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            rubro = models.N1Rubro.objects.all()
            data['Pantalla_List']= render_to_string('inv/invN1Rubro/N1Rubro_List_Details.html',{'rubro':rubro,'suc':suc})
        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def N1Rubro_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.N1RubroForm(request.POST)
    else:
        form = forms.N1RubroForm()
    return N1Rubro_save_all(request,form,'inv/invN1Rubro/modal_create.html') 

@login_required
def N1Rubro_Editar(request,cod):
    reino(request)
    n1rubro = get_object_or_404(models.N1Rubro,pk=cod)
    if request.method=='POST':
        form = forms.N1RubroForm(request.POST,instance=n1rubro)
    else:
        form = forms.N1RubroForm(instance=n1rubro)
    return N1Rubro_save_all(request,form,'inv/invN1Rubro/modal_update.html')

def N1Rubro_csv(request):
    tabla =  models.N1Rubro.objects.all().order_by('id_n1')
    rows = ([ i.id_n1 , i.descripcion , i.codigo_sac ] for i in tabla)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    x = list(writer.writerow(['Codigo', 'Descripcion','Codigo Sac']))
    y = list(((writer.writerow(row) for row in rows)))
    z = x + y
    response = StreamingHttpResponse(z,content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename = "N1Rubro.csv"'
    return response

# ---------------------------------------------------------------------
#          N2 FAMILIA
# ---------------------------------------------------------------------
@login_required
def familia_listar(request):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    return render(request,'inv/invN2Familia/familia_list.html',{
        'familia':models.N2Familia.objects.all(),
        'suc':LoggedInUser.objects.get(user=request.user)})

class FamiliaCreate(BSModalCreateView):
    template_name = 'inv/invN2Familia/modal.html'
    form_class = forms.FamiliaForm
    success_message = 'Datos registrados'
    success_url = reverse_lazy(familia_listar)

class FamiliaEdit(BSModalUpdateView):
    model = models.N2Familia
    template_name = 'inv/invN2Familia/modal.html'
    form_class = forms.FamiliaForm
    success_message = 'Registros actualizados'
    success_url = reverse_lazy(familia_listar)

@login_required
def N2Familia_save_all(request,form,template_name):
    reino(request)
    data = dict()
    suc = LoggedInUser.objects.get(user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            # conecciones.insertar_familia('MA',form.cleaned_data['id_n2'])
            data['form_is_valid'] = True
            familia = models.N2Familia.objects.all()
            data['Pantalla_List']= render_to_string('inv/invN2Familia/N2Familia_List_Details.html',{'familia':familia,'suc':suc})
        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def N2Familia_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.N2FamiliaForm(request.POST)
    else:
        form = forms.N2FamiliaForm()
    return N2Familia_save_all(request,form,'inv/invN2Familia/modal_create.html') 

@login_required
def N2Familia_Editar(request,cod):
    reino(request)
    n2familia = get_object_or_404(models.N2Familia,pk=cod)
    if request.method=='POST':
        form = forms.N2FamiliaForm(request.POST,instance=n2familia)
    else:
        form = forms.N2FamiliaForm(instance=n2familia)
    return N2Familia_save_all(request,form,'inv/invN2Familia/modal_update.html')

@login_required
def N2Familia_Eliminar(request,cod):
    reino(request)
    data = dict()
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    data['familia'] = models.N2Familia.objects.get(id_n2 = cod)
    if request.method == 'POST':
        familia = models.N2Familia.objects.get(id_n2 = cod)
        producto = models.N3Producto.objects.filter(familia__id_n2 = cod).count()

        if producto == 0:
            familia.delete()
        else:
            messages.warning(request,'La familia tiene productos asociados no se puede eliminar')
        return redirect('N2Familia_Listar')
        # return render(request,'inv/invN2Familia/familia_list.html',{'familia':models.N2Familia.objects.all(),'suc':LoggedInUser.objects.get(user=request.user)})
    else:
        return render(request,'inv/invN2Familia/N2Familia_Eliminar.html',data)

@login_required
def N2Familia_csv(request):
    tabla =  models.N2Familia.objects.all().order_by('id_n2')
    rows = ([ i.id_n2 , i.descripcion , i.codigo, i.rubro ] for i in tabla)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    x = list(writer.writerow(['Codigo', 'Descripcion','Abreviatura','Rubro']))
    y = list(((writer.writerow(row) for row in rows)))
    z = x + y
    response = StreamingHttpResponse(z,content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename = "N2Familia.csv"'
    return response

# ---------------------------------------------------------------------
#          EXONERACION DE RUBROS
# ---------------------------------------------------------------------
@login_required
def ExoRubro_list(request):
    reino(request)
    return render(request,'inv/invExoRubro/ExoRubro_List.html',{
        'exorubros':models.ExoRubro.objects.all(),
        'suc':LoggedInUser.objects.get(user=request.user)})

@login_required
def ExoRubro_save_all(request,form,template_name):
    reino(request)
    data = dict()
    suc = LoggedInUser.objects.get(user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            exorubros = models.ExoRubro.objects.all()
            data['Pantalla_List']= render_to_string('inv/invExoRubro/ExoRubro_List_Details.html',{'exorubros':exorubros,'suc':suc})
        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def ExoRubro_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.ExoRubroForm(request.POST)
    else:
        form = forms.ExoRubroForm()
    return ExoRubro_save_all(request,form,'inv/invExoRubro/modal_create.html')

@login_required
def ExoRubro_Editar(request,num):
    reino(request)
    exorubro = get_object_or_404(models.ExoRubro,pk=num)
    if request.method=='POST':
        form = forms.ExoRubroForm(request.POST,instance=exorubro)
    else:
        form = forms.ExoRubroForm(instance=exorubro)
    return ExoRubro_save_all(request,form,'inv/invExoRubro/modal_update.html')

# ---------------------------------------------------------------------
#          UNIDAD DE MEDIDA
# ---------------------------------------------------------------------
@login_required
def Um_list(request):
    reino(request)
    return render(request,'inv/invUm/Um_List.html',{'um':models.Um.objects.all(),
        'suc':LoggedInUser.objects.get(user=request.user)})

@login_required
def Um_save_all(request,form,template_name):
    reino(request)
    data = dict()
    suc = LoggedInUser.objects.get(user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            data['Pantalla_List']= render_to_string('inv/invUm/Um_List_Details.html',
            {'um':models.Um.objects.all(),'suc':suc})
        else:
            print(form.errors)
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def Um_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.UmForm(request.POST)
    else:
        form = forms.UmForm()
    return Um_save_all(request,form,'inv/invUm/modal_create.html') 

@login_required
def UMEditar(request,cod):
    reino(request)
    um = get_object_or_404(models.Um,pk=cod)
    if request.method=='POST':
        print('estas haciendo posto')
        form = forms.UmForm(request.POST,instance=um)
    else:
        form = forms.UmForm(instance=um)
    return Um_save_all(request,form,'inv/invUm/modal_update.html')

@login_required
def UM_Eliminar(request,cod):
    reino(request)
    if cod != 'UNI':
        data = dict()
        data['suc'] = LoggedInUser.objects.get(user=request.user)
        data['um'] =  models.Um.objects.get(id_um = cod)
        if request.method == 'POST':
            um = models.Um.objects.filter(id_um = cod)
            producto = models.N3Producto.objects.filter(medida__id_um = cod).count()
            if producto==0:
                um.delete()
            else:
                messages.warning(request,'La unidad de medida tiene productos asociados no se puede eliminar')
            return redirect('Um_Listar')
            # return render(request,'inv/invUm/Um_List.html',{'um':models.Um.objects.all(),'suc':LoggedInUser.objects.get(user=request.user)})
        else:
            return render(request,'inv/invUm/Um_Eliminar.html',data)
    else:
        raise PermissionDenied()
# ---------------------------------------------------------------------
#          N3 PRODUCTO
# ---------------------------------------------------------------------
@login_required
def N3Producto_list(request):
    reino(request)
    data = dict()
    data['n3producto'] = models.N3Producto.objects.all()
    data['suc'] = LoggedInUser.objects.get(user = request.user)
    data['form'] = forms.DescontinuadoForm()
    suc = LoggedInUser.objects.get(user = request.user)
    if request.method == 'POST':
        form = forms.DescontinuadoForm(request.POST)
        if form.is_valid():
            data['form'] = form
            if form.cleaned_data['rubro'] == None:# si el rubro esta vacio Listar todoso los item con el estado indicado
                select = form.cleaned_data['descontinuado']
                if select == 'A':#Activos
                    data['n3producto'] = models.N3Producto.objects.filter(descontinuado = 'N').order_by('familia__rubro').order_by('familia')
                if select == 'D':#Descontinuados
                    data['n3producto'] = models.N3Producto.objects.filter(descontinuado = 'S').order_by('familia__rubro').order_by('familia')
                if select == 'T':#Ambos
                    data['n3producto'] = models.N3Producto.objects.all().order_by('familia__rubro').order_by('familia')
            elif form.cleaned_data['familia'] == None:# si el rubro lleno y familia vacia !--listar todos los item de ese rubro--!
                rubro = form.cleaned_data['rubro']
                select = form.cleaned_data['descontinuado']
                if select == 'A':#Activos
                    data['n3producto'] = models.N3Producto.objects.filter(descontinuado = 'N').filter(familia__rubro = rubro).order_by('familia__rubro').order_by('familia')
                if select == 'D':#Descontinuados
                    data['n3producto'] = models.N3Producto.objects.filter(descontinuado = 'S').filter(familia__rubro = rubro).order_by('familia__rubro').order_by('familia')
                if select == 'T':#Ambos
                    data['n3producto'] = models.N3Producto.objects.all().order_by('familia__rubro').filter(familia__rubro = rubro).order_by('familia')
            else:
                familia = form.cleaned_data['familia']
                select = form.cleaned_data['descontinuado']
                if select == 'A':#Activos
                    data['n3producto'] = models.N3Producto.objects.filter(descontinuado = 'N').filter(familia = familia).order_by('familia__rubro').order_by('familia')
                if select == 'D':#Descontinuados
                    data['n3producto'] = models.N3Producto.objects.filter(descontinuado = 'S').filter(familia = familia).order_by('familia__rubro').order_by('familia')
                if select == 'T':#Ambos
                    data['n3producto'] = models.N3Producto.objects.all().order_by('familia__rubro').filter(familia = familia).order_by('familia')
            
            if form.cleaned_data['tipo'] != 'T':
                data['n3producto'] = data['n3producto'].filter(naturaleza = form.cleaned_data['tipo'])

        else:
            print(form.errors)
    else:
        data['n3producto'] = models.N3Producto.objects.filter(descontinuado = 'N')[:0]

    return render(request,'inv/invN3Producto/N3Producto_List.html',data)

@login_required
def N3Producto_save_all(request,form,template_name):
    reino(request)
    data = dict()
    suc = LoggedInUser.objects.get(user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            if form.cleaned_data['maximo'] >= form.cleaned_data['minimo']:

                form.save()
                data['form_is_valid'] = True
                data['Pantalla_List']= render_to_string('inv/invN3Producto/N3Producto_List_Details.html',
                {'n3producto':models.N3Producto.objects.all(),'suc':suc})
            else:
                messages.warning(request,'la cantidad minima no puede ser mayor que la cantidad maxima del item')
                data['form_is_valid'] = False

        else:
            print(form.errors)
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

    
@login_required
def CodigoProducto(request,cod):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    msr = models.N3Producto.objects.get(id_n3=cod)
    # detform = forms.CodigoFabricaForm()
    det = inlineformset_factory(models.N3Producto,models.CodigoFabrica,form=forms.CodigoFabricaForm,extra=1)
    lineas = models.CodigoFabrica.objects.filter(producto=cod)
    if request.method == 'POST':
        formset = det(request.POST,instance=msr)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data != {}:
                    if form.cleaned_data.get('codfabrica',False):
                        if form.cleaned_data['DELETE']:
                            if form.cleaned_data['id'] != None:
                                linea = models.CodigoFabrica.objects.get(id = form.cleaned_data['id'].id)
                                linea.delete()
                        else:
                            if form.is_valid():
                                form.save()
            return redirect('N3ProductoCodigoFabrica',cod=msr.id_n3)
        else:
            print(formset.errors)
            messages.warning(request,formset.errors)
    formset = det(instance=msr)
    return render(request,'inv/invN3Producto/CodigoFabrica.html',{'formset':formset,'Producto':msr,'suc':suc,'lineas':lineas})

@login_required
def N3Producto_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.N3ProductoForm(request.POST)
    else:
        form = forms.N3ProductoForm()
    return N3Producto_save_all(request,form,'inv/invN3Producto/modal_create.html') 

@login_required
def N3Producto_Editar(request,cod):
    reino(request)
    n3producto = get_object_or_404(models.N3Producto,pk=cod)
    if request.method=='POST':
        form = forms.N3ProductoForm(request.POST,instance=n3producto)
    else:
        form = forms.N3ProductoForm(instance=n3producto)
    return N3Producto_save_all(request,form,'inv/invN3Producto/modal_update.html')

@login_required
def N3Producto_Imagen(request,cod):
    reino(request)
    msr = models.N3Producto.objects.get(pk=cod)
    det = inlineformset_factory(models.N3Producto,models.N3ProductoImagen,fields=('ruta','nota',),extra=1)
    if request.method == 'POST':
        formset = det(request.POST,request.FILES,instance=msr)
        print(request.FILES)
        if formset.is_valid():
            formset.save()
            return redirect('N3Producto_Imagen',cod=msr.pk)
    formset = det(instance=msr)
    return render(request,'inv/invN3Producto/N3Producto_Imagen.html',{'formset':formset})

@login_required
def N3Producto_Eliminar(request,cod):
    reino(request)
    data = dict()
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    data['producto'] = models.N3Producto.objects.get(id_n3 = cod)
    if request.method == 'POST':
        producto = models.N3Producto.objects.get(id_n3 = cod)
        item = models.N4Item.objects.filter(producto__id_n3 = cod).count()
        if item == 0 :
            producto.delete()
        else:
            messages.warning(request,'Producto tiene items asociados no se puede eliminar')
        return redirect('N3Producto_Listar')
    else:
        return render(request,'inv/invN3Producto/N3Producto_Eliminar.html',data)

@login_required
def N3Producto_csv(request):
    tabla =  models.N3Producto.objects.all().order_by('id_n3')
    rows = ([ i.id_n3 , i.descripcion , i.familia, i.medida,i.codfabrica,i.sac,i.minimo,i.maximo,i.descontinuado,i.entero,i.naturaleza,i.exorubro ] for i in tabla)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    x = list(writer.writerow(['Codigo', 'Descripcion','Familia','Unidad de Medida','Codigo Fabrica','Sac','Minimo','Maximo','Descontinuado','En Partes?','Naturaleza','Rubro Exoneracion']))
    y = list(((writer.writerow(row) for row in rows)))
    z = x + y
    response = StreamingHttpResponse(z,content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename = "N3Producto.csv"'
    return response

# ---------------------------------------------------------------------
#          MARCA ITEM
# ---------------------------------------------------------------------
@login_required
def MarcaItem_list(request):
    reino(request)
    return render(request,'inv/invMarcaItem/MarcaItem_List.html',{
        'marcaitem':models.MarcaItem.objects.all(),
        'suc':LoggedInUser.objects.get(user=request.user)})

@login_required
def MarcaItem_save_all(request,form,template_name):
    reino(request)
    data = dict()
    suc = LoggedInUser.objects.get(user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            # conecciones.insertar_marcaitem('MA',form.cleaned_data['siglas'])
            data['form_is_valid'] = True
            marcaitem = models.MarcaItem.objects.all()
            data['Pantalla_List']= render_to_string('inv/invMarcaItem/MarcaItem_List_Details.html',{'marcaitem':marcaitem,'suc':suc})
        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def MarcaItem_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.MarcaItemForm(request.POST,request.FILES)
    else:
        form = forms.MarcaItemForm()
    return MarcaItem_save_all(request,form,'inv/invMarcaItem/modal_create.html')

@login_required
def MarcaItem_Editar(request,cod):
    reino(request)
    marcaitem = get_object_or_404(models.MarcaItem,siglas=cod)
    if request.method=='POST':
        form = forms.MarcaItemForm(request.POST,request.FILES,instance=marcaitem)
    else:
        form = forms.MarcaItemForm(instance=marcaitem)
    return MarcaItem_save_all(request,form,'inv/invMarcaItem/modal_update.html')

@login_required
def MarcaItem_Eliminar(request,cod):
    reino(request)
    if cod != 'GEN':
        data = dict()
        data['suc'] = LoggedInUser.objects.get(user=request.user)
        data['marca'] =  models.MarcaItem.objects.get(siglas = cod)
        if request.method == 'POST':
            marca = models.MarcaItem.objects.get(siglas = cod)
            item = models.N4Item.objects.filter(marca__siglas = cod).count()
            if item == 0:
                marca.delete()
            else:
                messages.warning(request,'La marca tiene items asociados no se puede eliminar')
            return redirect('MarcaItem_Listar')
            # return render(request,'inv/invMarcaItem/MarcaItem_List.html',{'marcaitem':models.MarcaItem.objects.all(),'suc':LoggedInUser.objects.get(user=request.user)})
        else:
            return render(request,'inv/invMarcaItem/MarcaItem_Eliminar.html',data)
    else:
        raise PermissionDenied()

# ---------------------------------------------------------------------
#          N4 ITEM
# ---------------------------------------------------------------------

@login_required
def N4Item_list(request):
    reino(request)
    data = dict()
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    suc = LoggedInUser.objects.get(user=request.user)
    if request.method == 'POST':
        form = forms.DescontinuadoForm(request.POST)
        if form.is_valid():
            data['form'] = form         
            if form.cleaned_data['rubro'] == None:# si el rubro esta vacio Listar todoso los item con el estado indicado
                select = form.cleaned_data['descontinuado']
                if select == 'A':#Activos
                    data['n4item']= models.N4Item.objects.annotate(existencias_sucursal = Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal=suc.sucursal))).filter(descontinuado='N').order_by('producto__familia__rubro').order_by('producto__familia').order_by('producto')
                if select == 'D':#Descontinuados
                    data['n4item']= models.N4Item.objects.annotate(existencias_sucursal = Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal=suc.sucursal))).filter(descontinuado='S').order_by('producto__familia__rubro')
                if select == 'T':#Ambos
                    data['n4item']= models.N4Item.objects.annotate(existencias_sucursal = Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal=suc.sucursal))).all().order_by('producto__familia__rubro')
            elif form.cleaned_data['familia'] == None:# si el rubro lleno y familia vacia !--listar todos los item de ese rubro--!
                rubro = form.cleaned_data['rubro']
                select = form.cleaned_data['descontinuado']
                if select == 'A':
                    data['n4item']= models.N4Item.objects.annotate(existencias_sucursal = Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal=suc.sucursal))).filter(descontinuado='N').filter(producto__familia__rubro=rubro).order_by('producto__familia__rubro').order_by('producto__familia').order_by('producto')
                if select == 'D':
                    data['n4item']= models.N4Item.objects.annotate(existencias_sucursal = Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal=suc.sucursal))).filter(descontinuado='S').filter(producto__familia__rubro=rubro).order_by('producto__familia__rubro').order_by('producto__familia').order_by('producto')
                if select == 'T':
                    data['n4item']= models.N4Item.objects.annotate(existencias_sucursal = Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal=suc.sucursal))).filter(producto__familia__rubro=rubro).order_by('producto__familia__rubro').order_by('producto__familia').order_by('producto')
            elif form.cleaned_data['producto'] == None:#si el rubro y la familia esta lleno pero el producto vacio !-- Listar todos los item de esa familia --!
                familia = form.cleaned_data['familia']
                select = form.cleaned_data['descontinuado']
                if select == 'A':
                    data['n4item']= models.N4Item.objects.annotate(existencias_sucursal = Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal=suc.sucursal))).filter(descontinuado='N').filter(producto__familia=familia).order_by('producto__familia__rubro').order_by('producto__familia').order_by('producto')
                if select == 'D':
                    data['n4item']= models.N4Item.objects.annotate(existencias_sucursal = Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal=suc.sucursal))).filter(descontinuado='S').filter(producto__familia=familia).order_by('producto__familia__rubro').order_by('producto__familia').order_by('producto')
                if select == 'T':
                    data['n4item']= models.N4Item.objects.annotate(existencias_sucursal = Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal=suc.sucursal))).filter(producto__familia=familia).order_by('producto__familia__rubro').order_by('producto__familia').order_by('producto')
            else:# si todos los campos estan llenos !-- Filtrar todos los item de ese producto --!
                producto = form.cleaned_data['producto']
                select = form.cleaned_data['descontinuado']
                if select == 'A':
                    data['n4item']= models.N4Item.objects.annotate(existencias_sucursal = Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal=suc.sucursal))).filter(descontinuado='N').filter(producto=producto).order_by('producto__familia__rubro').order_by('producto__familia').order_by('producto')
                if select == 'D':
                    data['n4item']= models.N4Item.objects.annotate(existencias_sucursal = Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal=suc.sucursal))).filter(descontinuado='S').filter(producto=producto).order_by('producto__familia__rubro').order_by('producto__familia').order_by('producto')
                if select == 'T':
                    data['n4item']= models.N4Item.objects.annotate(existencias_sucursal = Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal=suc.sucursal))).filter(producto=producto).order_by('producto__familia__rubro').order_by('producto__familia').order_by('producto')
            
            if form.cleaned_data['tipo']!= 'T':  
                data['n4item'] = data['n4item'].filter(producto__naturaleza=form.cleaned_data['tipo'])
        else:
            print(form.errors)
    else:
        data['form']=forms.DescontinuadoForm()
        data['suc'] = LoggedInUser.objects.get(user=request.user)
        data['n4item']= models.N4Item.objects.annotate(existencias_sucursal = Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal=suc.sucursal))).filter(descontinuado = 'N')[:0]

    return render(request,'inv/invN4Item/N4Item_List.html',data)

@login_required
def N4Item_save_all(request,form,template_name):
    reino(request)
    data = dict()
    suc = LoggedInUser.objects.get(user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            if form.cleaned_data['preciomax'] >= form.cleaned_data['preciomin']:
                if form.cleaned_data['maximo'] >= form.cleaned_data['minimo']:
                    id_n4 = form.cleaned_data['id_n4']
                    i = models.N4Item.objects.filter(pk = id_n4).exists()
                    if i:
                        print('actualizacion')
                        form.save()
                    else:
                        print('insert')
                        form.save()
                        #creando las existencias en bodega
                        bodegas = models.Bodega.objects.all()
                        for bodega in bodegas:
                            p = models.ExistenciaBodega.objects.create(
                                item = models.N4Item.objects.get(pk = id_n4),
                                bodega = models.Bodega.objects.get(pk = bodega.pk),
                                cantidad = 0 
                            )
                        print('creo existencias')
                        #creamos su costo en item_costo
                        p = models.item_costo.objects.create(
                            item = models.N4Item.objects.get(pk = id_n4)
                        )
                        print('creo item costo')
                        #creamos su costo en item_costo historico
                        p = models.item_costo_historico.objects.create(
                            item = models.N4Item.objects.get(pk = id_n4)
                        )
                        print('creo item costo historico')


                    data['form_is_valid'] = True
                    data['Pantalla_List']= render_to_string('inv/invN4Item/N4Item_List_Details.html',{'n4item':models.N4Item.objects.all(),'suc':suc})
                else:
                    messages.warning(request,'la cantidad minima no puede ser mayor que su cantidad maxima')
                    data['form_is_valid'] = False
            else:
                messages.warning(request,'El precio minimo no debe ser mayor que su precio maximo')
                data['form_is_valid'] = False
        else:
            print(form.errors)
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def N4Item_Create(request):
    reino(request)
    if request.method=='POST':
        post = request.POST.copy()
        minimo = float(post['preciomin'])
        maximo = float(post['preciomax'])
        print(minimo)
        print(maximo)
        if minimo > maximo:
            data = dict()
            form = forms.N4ItemForm(request.POST,request.FILES)
            messages.warning(request, 'El precio Minimo no puede ser Mayor que el precio Maximo')
            data['form_is_valid'] = False
            data['html_form'] = render_to_string('inv/invN4Item/modal_create.html',{'form':form},request=request,)
            return JsonResponse(data)
        form = forms.N4ItemForm(request.POST,request.FILES)
    else:
        form = forms.N4ItemForm()
    return N4Item_save_all(request,form,'inv/invN4Item/modal_create.html')

@login_required
def N4Item_Editar(request,cod):
    reino(request)
    n4item = get_object_or_404(models.N4Item,pk=cod)
    if request.method=='POST':
        post = request.POST.copy()
        minimo = float(post['preciomin'])
        maximo = float(post['preciomax'])
        print(minimo)
        print(maximo)
        if minimo > maximo:
            data = dict()
            form = forms.N4ItemForm(request.POST,request.FILES,instance=n4item)
            messages.warning(request, 'El precio Minimo no puede ser Mayor que el precio Maximo')
            data['form_is_valid'] = False
            data['html_form'] = render_to_string('inv/invN4Item/modal_update.html',{'form':form},request=request,)
            return JsonResponse(data)
        form = forms.N4ItemForm(request.POST,request.FILES,instance=n4item)
    else:
        form = forms.N4ItemForm(instance=n4item)
    return N4Item_save_all(request,form,'inv/invN4Item/modal_update.html')

@login_required
def N4ItemKardex_list(request,cod):
    reino(request)
    data = dict()
    suc = LoggedInUser.objects.get(user=request.user)
    data['item'] = models.N4Item.objects.get(id_n4=cod)
    data['suc'] = suc
    
    if request.method == 'POST':
        form = forms.make_seleccionKardex(suc.sucursal.siglas,request)
        data['inicio'] = '1999-01-01'
        data['fin'] = '2999-12-31'
        if form.is_valid():
            data['inicio'] = form.cleaned_data['inicio']
            data['fin'] = form.cleaned_data['fin']
            if form.cleaned_data['inicio'] != '' and form.cleaned_data['fin'] != '':
                if form.cleaned_data['inicio'] > form.cleaned_data['fin']:
                    messages.warning(request,'la fecha fin no puede ser menor que la fecha de inicio')
                    return redirect('N4Item_Kardex',cod = cod)

                if form.cleaned_data['fin'] < form.cleaned_data['inicio']:
                    messages.warning(request,'la fecha inicio no puede ser mayor que la fecha fin')
                    return redirect('N4Item_Kardex',cod = cod)
            else:
                data['inicio'] = '1999-01-01'
                data['fin'] = '2999-12-31'


            select = form.cleaned_data['esglobal']
            #seleccionado la sucursal
            if select == 's':
                if form.cleaned_data['bodega'] == None:
                    data['filtro'] = 'Sucursal'

                    inicio = form.cleaned_data['inicio']
                    fin = form.cleaned_data['fin']

                    #Revisando los distintos casos de los campos de fecha
                    if inicio=='' and fin=='':
                        data['kardex'] = models.Kardex.objects.filter(sucursal = suc.sucursal,item = cod).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                        kardexFil = models.Kardex.objects.filter(item = cod).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                    elif inicio != '' and fin == '':
                        data['kardex'] = models.Kardex.objects.filter(sucursal = suc.sucursal,item = cod,fecha__gte= inicio).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                        kardexFil = models.Kardex.objects.filter(item = cod, fecha__gte=inicio ).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                    elif inicio == '' and fin != '':
                        data['kardex'] = models.Kardex.objects.filter(sucursal = suc.sucursal,item = cod,fecha__lte= fin).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                        kardexFil = models.Kardex.objects.filter(item = cod, fecha__lte=fin).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                    elif inicio != '' and fin != '':
                        data['kardex'] = models.Kardex.objects.filter(sucursal = suc.sucursal,item = cod,fecha__gte= inicio).filter(fecha__lte = fin).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                        kardexFil = models.Kardex.objects.filter(item = cod, fecha__gte=inicio ).filter(fecha__lte = fin).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')

                    data['fechas'] = kardexFil.order_by('fecha').values_list('fecha',flat=True).distinct()
                else:
                    #seleccionado el global
                    bodega = form.cleaned_data['bodega']
                    data['filtro'] = 'Bodega'
                    data['bod']= bodega.nombre
                    
                    inicio = form.cleaned_data['inicio']
                    fin = form.cleaned_data['fin']

                    #Revisando los distintos casos de los campos de fecha
                    if inicio=='' and fin=='':
                        data['kardex'] = models.Kardex.objects.filter(bodega = bodega,item = cod).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                        kardexFil = models.Kardex.objects.filter(item = cod).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                    elif inicio != '' and fin == '':
                        data['kardex'] = models.Kardex.objects.filter(bodega = bodega,item = cod,fecha__gte= inicio).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                        kardexFil = models.Kardex.objects.filter(item = cod, fecha__gte=inicio ).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                    elif inicio == '' and fin != '':
                        data['kardex'] = models.Kardex.objects.filter(bodega = bodega,item = cod,fecha__lte= fin).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                        kardexFil = models.Kardex.objects.filter(item = cod, fecha__lte=fin).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                    elif inicio != '' and fin != '':
                        data['kardex'] = models.Kardex.objects.filter(bodega = bodega,item = cod,fecha__gte= inicio).filter(fecha__lte = fin).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                        kardexFil = models.Kardex.objects.filter(item = cod, fecha__gte=inicio ).filter(fecha__lte = fin).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')

                    data['fechas'] = kardexFil.order_by('fecha').values_list('fecha',flat=True).distinct()

            #seleccionado el global
            elif select == 'g':
                data['filtro'] = 'Global'

                inicio = form.cleaned_data['inicio']
                fin = form.cleaned_data['fin']

                #Revisando los distintos casos de los campos de fecha
                if inicio=='' and fin=='':
                    data['kardex'] = models.Kardex.objects.filter(item = cod).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                    kardexFil = models.Kardex.objects.filter(item = cod).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                elif inicio != '' and fin == '':
                    data['kardex'] = models.Kardex.objects.filter(item = cod,fecha__gte= inicio).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                    kardexFil = models.Kardex.objects.filter(item = cod, fecha__gte=inicio ).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                elif inicio == '' and fin != '':
                    data['kardex'] = models.Kardex.objects.filter(item = cod,fecha__lte= fin).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                    kardexFil = models.Kardex.objects.filter(item = cod, fecha__lte=fin).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                elif inicio != '' and fin != '':
                    data['kardex'] = models.Kardex.objects.filter(item = cod,fecha__gte= inicio).filter(fecha__lte = fin).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
                    kardexFil = models.Kardex.objects.filter(item = cod, fecha__gte=inicio ).filter(fecha__lte = fin).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')

                data['fechas'] = kardexFil.order_by('fecha').values_list('fecha',flat=True).distinct()
        data['form'] = form
    else:
        
        data['inicio'] = '1999-01-01'
        data['fin'] = '2999-12-31'
        data['filtro'] = 'Sucursal'
        data['kardex'] = models.Kardex.objects.filter(sucursal = suc.sucursal,item = cod, fecha__gte=date.today()).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
        kardexFil = models.Kardex.objects.filter(item = cod, fecha__gte=date.today() ).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')
        data['fechas'] = kardexFil.order_by('fecha').values_list('fecha',flat=True).distinct()
        #cuando solo es get se muestra la pantalla vacia
        data['kardex'] = models.Kardex.objects.filter(sucursal = suc.sucursal,item = cod, fecha__gte=date.today()).exclude(sucursal__siglas = 'DU').order_by('fecha').order_by('referencia')[:0]
        data['form'] = forms.make_seleccionKardex(suc.sucursal.siglas,request)
    return render(request,'inv/invN4Item/Kardex_List.html',data)

@login_required
def N4Item_Obtener_Select(request,cod):
    reino(request)
    data = dict()
    print('entre')
    # if request.method == 'POST':
    data['items'] = models.N4Item.objects.filter(Q(id_n4__icontains=cod)|Q(id_n3__familia__descripcion__icontains=cod)|Q(id_n3__descripcion__icontains=cod)|Q(marca__marca__icontains=cod))
        # data['items'] = render_to_string('inv/invDevolucionMsr/DevolucionMsr_List_Select.html',{'item':item})
    return JsonResponse(data)

@login_required
def N4Item_combo(request,cod):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    msr = models.N4Item.objects.get(id_n4=cod)
    detform = forms.make_N4Item_combo_form(cod)
    det = inlineformset_factory(models.N4Item,models.N4ItemCombo,fk_name='combo',form=detform,extra=1)
    lineas = models.N4ItemCombo.objects.filter(combo=cod)
    if request.method == 'POST':
        formset = det(request.POST,instance=msr)
        if formset.is_valid():
            formset.save()
            return redirect('N4Item_Combo',cod=msr.id_n4)
        else:
            print(formset.errors)
            messages.warning(request,formset.errors)
    formset = det(instance=msr)
    return render(request,'inv/invN4Item/N4Item_Combo.html',{'formset':formset,'Item':msr,'suc':suc,'lineas':lineas})

@login_required
def N4Item_receta(request,cod):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    msr = models.N4Item.objects.get(id_n4=cod)
    detform = forms.make_N4Item_receta_form(cod)
    det = inlineformset_factory(models.N4Item,models.N4ItemReceta,fk_name='receta',form=detform,extra=1)
    lineas = models.N4ItemCombo.objects.filter(combo=cod)
    if request.method == 'POST':
        formset = det(request.POST,instance=msr)
        if formset.is_valid():
            formset.save()
            return redirect('N4Item_Receta',cod=msr.id_n4)
        else:
            print(formset.errors)
            messages.warning(request,formset.errors)
    formset = det(instance=msr)
    return render(request,'inv/invN4Item/N4Item_Receta.html',{'formset':formset,'Item':msr,'suc':suc,'lineas':lineas})

@login_required
def N4Item_costo(request,cod):
    reino(request)
    data = dict()

    data['suc'] = LoggedInUser.objects.get(user=request.user)
    data['item'] = models.N4Item.objects.get(id_n4=cod)
    costo = models.item_costo.objects.get(item = cod)

    data['costo'] = costo
    if request.method=='POST':
        form = forms.ItemCostoForm(request.POST,request.FILES,instance=data['item'])
        if form.is_valid():
            form.save()
        data['form'] = form
    else:
        print('entre')
        form = forms.ItemCostoForm(instance=costo)
        data['form'] = form
    return render(request,'inv/invN4Item/N4Item_Costo.html',data)

@login_required
def N4Item_Eliminar(request,cod):
    reino(request)
    data = dict()
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    data['item'] = models.N4Item.objects.get(id_n4 = cod)
    if request.method == 'POST':
        data['suc'] = LoggedInUser.objects.get(user=request.user)
        precios = models.N4ItemXPrecio.objects.filter(item = cod)
        existencias = models.ExistenciaBodega.objects.filter(item = cod)
        kardex = models.Kardex.objects.filter(item=cod)
        costo = models.item_costo.objects.filter(item=cod)
        costo_historico = models.item_costo_historico.objects.filter(item = cod)
        item = models.N4Item.objects.get(id_n4 = cod)
        movimientos = models.Kardex.objects.filter(item=cod).count()
        if movimientos == 1:
            # eliminando las filas
            precios.delete()
            existencias.delete()
            kardex.delete()
            costo.delete()
            costo_historico.delete()
            item.delete()
            return redirect('N4Item_Listar')
        else:
            messages.warning(request,'El item ya tiene movimientos en el sistema no se puede Eliminar')
            return redirect('N4Item_Listar')
    else:
        return render(request,'inv/invN4Item/N4Item_Eliminar.html',data)

@login_required
def N4Item_csv(request):
    tabla =  models.N4Item.objects.all().order_by('id_n4')
    rows = ([i.producto.familia.pk+'.' +i.id_n4 , i.descripcion , i.producto , i.marca, i.preciomax, "'"+i.codanterior,i.codbarra,i.sac,i.exotipo,i.cantidad_impuesto,i.minimo,i.maximo,i.descontinuado,i.producto.exorubro ] for i in tabla)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    x = list(writer.writerow(['Codigo', 'Nota','Producto','Marca','Precio','Codigo Anterior','Codigo Barra','Sac','Tipo Exoneracion','Cantidad Impuesto','Minimo','Maximo','Descontinuado','Rubro de exoneracion']))
    y = list(((writer.writerow(row) for row in rows)))
    z = x + y
    response = StreamingHttpResponse(z,content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename = "N4Item.csv"'
    return response

@login_required
def N4Item_Kardex_Excel(request,cod,inicio,fin,filtro):
    tabla = models.Kardex.objects.raw('''
                                            select * from pruebas.inv_kardex
                                            where item_id = '%s'
                                            and fecha between '%s' and '%s'
                                            order by 
                                            Fecha,
                                            if(tipotransaccion = 'EE',1,
                                            if(tipotransaccion = 'EC',2,
                                            if(tipotransaccion = 'EA',3,
                                            if(tipotransaccion = 'ST',4,
                                            if(tipotransaccion = 'ET',5,
                                            if(tipotransaccion = 'SC',6,
                                            if(tipotransaccion = 'SA',7,
                                            if(tipoTransaccion = 'SS',8,9)/*Octavo if*/
                                            )/*Septimo if*/
                                            )/*Sexto if*/
                                            )/*Quinto if*/
                                            )/*Cuarto if*/
                                            )/*Tercer if*/
                                            )/*Segundo if*/
                                            )/*Primer if*/,
                                            referencia
                                    '''%(cod,inicio,fin))
    if filtro ==   'Global':
        rows = ([i.item.producto.familia.pk+'.'+i.item.id_n4 ,i.item, i.fecha , i.sucursal , i.bodega, i.referencia, i.tipotransaccion, i.entrada,i.salida,i.existencia,i.debe,i.haber,i.saldo,i.costounitario ] for i in tabla)
    elif filtro == 'Sucursal':
        rows = ([i.item.producto.familia.pk+'.'+i.item.id_n4 ,i.item, i.fecha , i.sucursal , i.bodega, i.referencia, i.tipotransaccion, i.entrada,i.salida,i.existenciasuc,i.debe,i.haber,i.saldosuc,i.costounitario ] for i in tabla)
    elif filtro == 'Bodega':
        rows = ([i.item.producto.familia.pk+'.'+i.item.id_n4 ,i.item, i.fecha , i.sucursal , i.bodega, i.referencia, i.tipotransaccion, i.entrada,i.salida,i.existenciabod,i.debe,i.haber,i.saldobod,i.costounitario ] for i in tabla)
    
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    x = list(writer.writerow(['Codigo','Descripcion', 'Fecha','Sucursal','Bodega','Referencia','Tipo ','Entrada','Salida','Existencia','Debe','Haber','Saldo','CU']))
    y = list(((writer.writerow(row) for row in rows)))
    z = x + y
    response = StreamingHttpResponse(z,content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename = "Kardex_.csv"'
    return response

@login_required
def N4Item_Consolidado(request):
    tabla =  models.N4Item.objects.annotate(CN=Sum('existenciabodega__cantidad')).annotate(
        MK=Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal__pk='MK'))).annotate(
        ES=Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal__pk='ES'))).annotate(
        CA=Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal__pk='14'))).annotate(
        MA=Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal__pk='MA'))).annotate(
        AG=Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal__pk='2A'))).annotate(
        LE=Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal__pk='LE'))
        ).all().order_by('id_n4')
    rows = ([i.producto.familia.pk+'.' +i.id_n4 , i.producto.familia.rubro.descripcion+' '+i.producto.familia.descripcion+' '+i.producto.descripcion+' '+i.descripcion ,i.preciomin,i.preciomax,i.CN,i.ES,i.MK,i.CA,i.MA,i.AG,i.LE  ] for i in tabla)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    x = list(writer.writerow(['Codigo', 'Descripcion','Precio Minimo','Precio Maximo','CN','ES','MK','14','MA','2A','LE']))
    y = list(((writer.writerow(row) for row in rows)))
    z = x + y
    response = StreamingHttpResponse(z,content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename = "Consolidado.csv"'
    return response

@login_required
def N4Item_Lista_Inventario(request):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)

    #obtenemos todos los items, las bodegas pertenecientes a la sucursal y la sucursal
    items = models.N4Item.objects.all().exclude(
        producto__naturaleza ='S').exclude(
        producto__naturaleza = 'P').exclude(
        producto__naturaleza = 'C'
        ).annotate(
        existencias_sucursal = Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal=suc.sucursal))
        )
    bodegas = models.Bodega.objects.filter(sucursal = suc.sucursal).order_by('nombre')
    sucursal = models.Sucursal.objects.get(siglas = suc.sucursal.siglas)

    #creamos el buffer para crear el csv
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)

    #declaramos la lista con la cual haremos el csv
    z = list()
    cabecera = ['Codigo','Codigo anterior','Descripcion',sucursal.nombre]
    for b in bodegas:
        cabecera.append(b.nombre+' Sistema')
        cabecera.append(b.nombre+' Real')
    z += list(writer.writerow(cabecera))

    for i in items:
        fila = []
        fila.append(i.producto.familia.pk+'.'+i.id_n4)#codigo
        fila.append( "'"+i.codanterior)#codigo anterior
        #descripcion
        fila.append(i.producto.familia.descripcion+' '+i.producto.descripcion+' '+i.descripcion)
        fila.append(i.existencias_sucursal)#Existencia en sucursal
        #sacamos sus existencias en bodega
        existenciasbodega = models.ExistenciaBodega.objects.filter(item = i,bodega__sucursal = suc.sucursal).order_by('bodega__nombre')
        for b in existenciasbodega:
            fila.append(b.cantidad)
            fila.append('0')
        z+= list(writer.writerow(fila))

    response = StreamingHttpResponse(z,content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename = "ListadeInventario.csv"'
    return response

@login_required
def N4Item_Consolidado_Costo(request):
    tabla =  models.N4Item.objects.annotate(CN=Sum('existenciabodega__cantidad')).annotate(
        MK=Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal__pk='MK'))).annotate(
        ES=Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal__pk='ES'))).annotate(
        CA=Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal__pk='14'))).annotate(
        MA=Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal__pk='MA'))).annotate(
        AG=Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal__pk='2A'))).annotate(
        LE=Sum('existenciabodega__cantidad',filter=Q(existenciabodega__bodega__sucursal__pk='LE'))).annotate(
        CU=Min('item_costo__costo')).all().order_by('id_n4')
    rows = ([i.producto.familia.pk+'.' +i.id_n4 , i.producto.familia.rubro.descripcion+' '+i.producto.familia.descripcion+' '+i.producto.descripcion+' '+i.descripcion,i.CU,i.preciomin,i.preciomax ,i.CN,i.ES,i.MK,i.CA,i.MA,i.AG,i.LE  ] for i in tabla)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    print('llegue')
    x = list(writer.writerow(['Codigo', 'Descripcion','CU','Precio Min','Precio Max','CN','ES','MK','14','MA','2A','LE']))
    y = list(((writer.writerow(row) for row in rows)))
    z = x + y
    response = StreamingHttpResponse(z,content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename = "Consolidado_Costo.csv"'
    return response


# ---------------------------------------------------------------------
#          N4 ITEM PRODUCCION
# ---------------------------------------------------------------------

@login_required
def N4Item_produccion_listar(request):
    reino(request)
    data = dict()
    data['suc']= LoggedInUser.objects.get(user=request.user)
    data['n4item'] = models.N4Item.objects.filter(producto__naturaleza = 'P')
    return render(request,'inv/invN4Item/N4Item_Produccion.html',data)

@login_required
def N4Item_produccion_historial(request):
    reino(request)
    data = dict()
    suc = LoggedInUser.objects.get(user=request.user)
    if request.method == 'POST':
        busquedaform = forms.BusquedafechasForm(request.POST)
        data['busqueda']  = busquedaform
        form = forms.make_cantidadForm(suc.sucursal.siglas,request)
        data['form'] = form
        if busquedaform.is_valid():
            print(busquedaform.cleaned_data['busqueda'])
            busqueda= busquedaform.cleaned_data['busqueda']
            fecha_ini = datetime.strptime(busquedaform.cleaned_data['fecha_inicio'],'%Y-%m-%d')
            fecha_fin = datetime.strptime(busquedaform.cleaned_data['fecha_fin'],'%Y-%m-%d')+ timedelta(days=1)
            if busqueda == 'TRUE':
                data['fecha_inicio'] = busquedaform.cleaned_data['fecha_inicio']
                data['fecha_fin'] = busquedaform.cleaned_data['fecha_fin']
                data['historial'] = models.N4ItemProduccion.objects.filter(fecha__gte=fecha_ini,fecha__lte=fecha_fin).order_by('-fecha')
            else:
                data['fecha_inicio'] = busquedaform.cleaned_data['fecha_inicio']
                data['fecha_fin'] = busquedaform.cleaned_data['fecha_fin']
                select =busquedaform.cleaned_data['rangos_especificos']
                if select == '1':
                    data['historial'] = models.N4ItemProduccion.objects.filter(fecha__gte=date.today()).order_by('-fecha')
                if select == '2':
                    data['historial'] = models.N4ItemProduccion.objects.filter(fecha__week=datetime.today().isocalendar()[1],fecha__year__gte=date.today().year).order_by('-fecha')
                if select == '3':
                    data['historial'] = models.N4ItemProduccion.objects.filter(fecha__month=date.today().month,fecha__year=date.today().year).order_by('-fecha')
        else:
            print(busquedaform.errors)
        if form.is_valid():
            # print('entraste')
            # obteniendo datos
            cabecera = form.cleaned_data['item']
            lineas = models.N4ItemReceta.objects.filter(receta = cabecera)
            cantidad = form.cleaned_data['cantidad']
            nota = form.cleaned_data['nota']
            bodegaO = form.cleaned_data['bodegaO']
            bodegaD = form.cleaned_data['bodegaD']
            today= date.today().strftime('%Y%m%d')
            numero = models.N4ItemProduccion.objects.filter(referencia__contains=today,item=cabecera).count()
            if numero==0:
                consecutivo='00001'
            else:
                consecutivo='{:0>5}'.format(numero+1)
            referencia =suc.sucursal.siglas+'-MP-'+today+'-'+consecutivo

            puede_producir = True

            for i in lineas:
                existencia = models.ExistenciaBodega.objects.get(item = i.item.id_n4, bodega = bodegaO)
                final = existencia.cantidad - (i.cantidad * cantidad)
                if final < 0:
                    messages.warning(request,'no se puede efectuar operacion, las existencias quedan negativas, del item: "%s", en la bodega: "%s", sus existencias actuales: "%s"'%(
                        i.item,
                        bodegaO,
                        existencia.cantidad
                        )
                    )
                    puede_producir = False
                    return redirect('N4Item_Historial')

            if puede_producir:
                # disminuyo las existencias
                for ingrediente in lineas:  
                    item = models.N4Item.objects.get(pk=ingrediente.item.pk)
                    existencia = models.ExistenciaBodega.objects.get(item=item,bodega = bodegaO)
                    existencia.cantidad = existencia.cantidad - (ingrediente.cantidad * cantidad)
                    existencia.save()
                    kardex = models.Kardex.objects.create(
                        referencia = referencia,
                        sucursal = suc.sucursal,
                        item = item,
                        salida = (ingrediente.cantidad * cantidad),
                        existencia = existencia.cantidad,
                        bodega = bodegaO,
                        tipotransaccion = 'SA'
                    )
                    

                    #restamos su vencimiento segun la cantidad que dice la receta por la unidades pedida en la produccion
                    cantidad2 = ingrediente.cantidad * cantidad
                    
                    while cantidad2 > 0:
                        vencimiento = models.N4ItemVencimiento.objects.filter(item =item).exclude(cantidad = 0).order_by('fecha_venc').first()
                        if vencimiento:
                            if cantidad2 > vencimiento.cantidad:
                                cantidad2 -= vencimiento.cantidad
                                vencimiento.cantidad = 0
                                vencimiento.fecha_cero = date.today().strftime('%Y-%m-%d')
                                vencimiento.save()
                            else:
                                vencimiento.cantidad -= cantidad2
                                cantidad2 = 0
                                vencimiento.save()
                        else:
                            cantidad2 = 0

                existencia = models.ExistenciaBodega.objects.get(item = cabecera,bodega = bodegaD)
                existencia.cantidad = existencia.cantidad + cantidad
                existencia.save()
                
                produccion = models.N4ItemProduccion.objects.create(
                    referencia   = referencia,
                    bodegao      = bodegaO,
                    bodegad      = bodegaD,
                    item         = models.N4Item.objects.get(pk = cabecera.id_n4),
                    cantidad     = cantidad,
                    nota         = nota,
                    fecha_venc   = form.cleaned_data['fecha_venc']
                )

                kardex = models.Kardex.objects.create(
                    referencia = referencia,
                    sucursal = suc.sucursal,
                    bodega  = bodegaD,
                    item = cabecera,
                    entrada = cantidad,
                    salida = 0,
                    debe = 0,
                    haber = 0,
                    saldo = 0,
                    costounitario = 0,
                    existencia = existencia.cantidad,
                    fecha_venc = form.cleaned_data['fecha_venc'].strftime('%Y-%m-%d'),
                    tipotransaccion = 'EA'
                )                

            #creamos o aumentamos la tupla en su registro de vencimiento
            existevencimiento = models.N4ItemVencimiento.objects.filter(item = models.N4Item.objects.get(pk = i.item.id_n4),referencia = referencia,fecha_venc = form.cleaned_data['fecha_venc'].strftime('%Y-%m-%d') ).exists()

            if existevencimiento:
                vencimiento = models.N4ItemVencimiento.objects.get(item = models.N4Item.objects.get(pk = i.item.id_n4),referencia = referencia,fecha_venc = form.cleaned_data['fecha_venc'].strftime('%Y-%m-%d'))
                vencimiento.cantidad = vencimiento.cantidad + i.cantidad
                vencimiento.fecha_cero ='.'
                vencimiento.save()
            else:
                c = models.N4ItemVencimiento.objects.create(
                    referencia = referencia,
                    item = cabecera,
                    fecha_venc = form.cleaned_data['fecha_venc'].strftime('%Y-%m-%d'),
                    cantidad = cantidad
                )


            return redirect('N4Item_Historial')
        else:
            # print('no pudiste entrar')
            print(form.errors)
    else:
        form = forms.make_cantidadForm(suc.sucursal.siglas,request)
        data['form'] = form
        data['busqueda'] = forms.BusquedafechasForm()
        data['historial'] = models.N4ItemProduccion.objects.filter(fecha__gte=date.today()).order_by('-fecha')
        data['fecha_inicio'] = date.today().strftime("%Y-%m-%d")
        data['fecha_fin'] = date.today().strftime("%Y-%m-%d")  
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    return render(request,'inv/invN4Item/N4Item_Produccion_historial.html',data)

@login_required
def N4Item_produccion_imprimir(request,cod,item):
    reino(request)
    data = dict()
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    data['msr'] = models.N4ItemProduccion.objects.get(pk= cod)
    data['det'] = models.Kardex.objects.filter(referencia=cod) 
    return render(request,'inv/invN4Item/produccion_impresion.html',data)

@login_required
def N4Item_produccion_detalle(request,cod,item):
    reino(request)
    data = dict()
    lineas = models.N4ItemReceta.objects.filter(receta = item)
    # data['kardex'] = models.Kardex.objects.filter(item__in=[ i.item for i in lineas ])
    data['form_is_valid'] = True
    data['html_form'] = render_to_string('inv/invN4Item/modal_produccion_kardex.html',
                                        {
                                            'kardex':models.Kardex.objects.filter(referencia=cod).filter(item__in=[ i.item for i in lineas ])
                                        },
                                        request=request,)
    return JsonResponse(data) 

# ---------------------------------------------------------------------
#          N4 ITEM COMBO
# ---------------------------------------------------------------------

@login_required
def N4ItemCombo_list(request):
    reino(request)
    return render(request,'inv/invN4ItemCombo/N4ItemCombo_List.html',{
        'n4itemcombo':models.N4ItemCombo.objects.all(),
        'suc':LoggedInUser.objects.get(user=request.user)})

@login_required
def N4ItemCombo_save_all(request,form,template_name):
    reino(request)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            n4itemcombo = models.N4ItemCombo.objects.all()
            data['Pantalla_List']= render_to_string('inv/invN4ItemCombo/N4ItemCombo_List_Details.html',{'n4itemcombo':n4itemcombo})
        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def N4ItemCombo_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.N4ItemComboForm(request.POST,request.FILES)
    else:
        form = forms.N4ItemComboForm()
    return N4ItemCombo_save_all(request,form,'inv/invN4ItemCombo/modal_create.html')

@login_required
def N4ItemCombo_Editar(request,cod):
    reino(request)
    n4itemcombo = get_object_or_404(models.N4ItemCombo,pk=cod)
    if request.method=='POST':
        form = forms.N4ItemComboForm(request.POST,request.FILES,instance=n4itemcombo)
    else:
        form = forms.N4ItemComboForm(instance=n4itemcombo)
    return N4ItemCombo_save_all(request,form,'inv/invN4itemCombo/modal_update.html')

# ---------------------------------------------------------------------
#          PRECIOS
# ---------------------------------------------------------------------
@login_required
def Precio_list(request):
    reino(request)
    return render(request,'inv/invPrecio/Precio_List.html',{
        'precio':models.Precio.objects.all(),
        'suc':LoggedInUser.objects.get(user=request.user)})

@login_required
def Precio_save_all(request,form,template_name):
    reino(request)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            id_precio = form.cleaned_data['id_precio']
            i = models.Precio.objects.filter(pk=id_precio).exists()
            if i:
                form.save()
            else:
                form.save()
                #actualizamos los precios de los item
                items = models.N4Item.objects.all()
                for item in items:
                    j = models.N4ItemXPrecio.objects.create(
                        item = models.N4Item.objects.get(pk = item.pk),
                        precio = models.Precio.objects.get(pk = id_precio),
                        valor = float(item.precio)
                    )
            data['form_is_valid'] = True
            data['Pantalla_List']= render_to_string('inv/invPrecio/Precio_List_Details.html',{'precio':models.Precio.objects.all()})
        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def Precio_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.PrecioForm(request.POST,request.FILES)
    else:
        form = forms.PrecioForm()
    return Precio_save_all(request,form,'inv/invPrecio/modal_create.html')

@login_required
def Precio_Editar(request,cod):
    reino(request)
    precio = get_object_or_404(models.Precio,pk=cod)
    if request.method=='POST':
        form = forms.PrecioForm(request.POST,request.FILES,instance=precio)
    else:
        form = forms.PrecioForm(instance=precio)
    return Precio_save_all(request,form,'inv/invPrecio/modal_update.html')

# ---------------------------------------------------------------------
#          N4 ITEM POR PRECIO
# ---------------------------------------------------------------------
@login_required 
def N4ItemXPrecio_busqueda(request):
    reino(request)
    data = dict()
    if request.method == 'POST':
        form = forms.BusquedaForm(request.POST)
        if form.is_valid():
            data['form'] = form
            n4itemxpreciobuscado = models.N4ItemXPrecio.objects.filter(item=form.cleaned_data['busqueda'])
            data['n4itemxpreciobuscado'] = n4itemxpreciobuscado
            data['suc']= LoggedInUser.objects.get(user=request.user)
    else:
            form = forms.BusquedaForm()
            data['n4itemxpreciobuscado'] = []
            data['form'] = form
            data['suc']= LoggedInUser.objects.get(user=request.user)
    return render(request,'inv/invN4ItemXPrecio/Busqueda.html',data)

@login_required
def N4ItemXPrecio_list(request,cod):
    reino(request)
    data= dict()
    data['n4itemxprecio'] = models.N4ItemXPrecio.objects.filter(item=cod);
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    data['item'] = models.N4Item.objects.get(pk=cod)
    return render(request,'inv/invN4ItemXPrecio/N4ItemXPrecio_List.html',data)
    
@login_required
def N4ItemXPrecio_save_all(request,form,template_name):
    reino(request)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            # data['Pantalla_List']= render_to_string('inv/invN4ItemXPrecio/N4ItemXPrecio_List_Details.html',{'n4itemxprecio':models.N4ItemXPrecio.objects.all()})
            data['Pantalla_List']= render_to_string('inv/invN4ItemXPrecio/N4ItemXPrecio_List_Details.html',{'n4itemxprecio':models.N4ItemXPrecio.objects.filter(item=form.cleaned_data['item'])})
        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def N4ItemXPrecio_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.N4ItemXPrecioForm(request.POST,request.FILES)
    else:
        form = forms.N4ItemXPrecioForm()
    return N4ItemXPrecio_save_all(request,form,'inv/invN4ItemXPrecio/modal_create.html')

@login_required
def N4ItemXPrecio_Editar(request,cod):
    reino(request)
    n4itemxprecio = get_object_or_404(models.N4ItemXPrecio,pk=cod)
    if request.method=='POST':
        form = forms.N4ItemXPrecioForm(request.POST,request.FILES,instance=n4itemxprecio)
    else:
        form = forms.N4ItemXPrecioForm(instance=n4itemxprecio)
    return N4ItemXPrecio_save_all(request,form,'inv/invN4ItemXPrecio/modal_update.html')

# ---------------------------------------------------------------------
#          MARCA VEHICULO
# ---------------------------------------------------------------------
@login_required
def MarcaVehiculo_list(request):
    reino(request)
    return render(request,'inv/invMarcaVehiculo/MarcaVehiculo_List.html',{
        'marcavehiculo':models.MarcaVehiculo.objects.all(),
        'suc':LoggedInUser.objects.get(user=request.user)})

@login_required
def MarcaVehiculo_save_all(request,form,template_name):
    reino(request)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            marcavehiculo = models.MarcaVehiculo.objects.all()
            data['Pantalla_List']= render_to_string('inv/invMarcaVehiculo/MarcaVehiculo_List_Details.html',{'marcavehiculo':marcavehiculo})
        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def MarcaVehiculo_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.MarcaVehiculoForm(request.POST,request.FILES)
    else:
        form = forms.MarcaVehiculoForm()
    return MarcaVehiculo_save_all(request,form,'inv/invMarcaVehiculo/modal_create.html')

@login_required
def MarcaVehiculo_Editar(request,cod):
    reino(request)
    marcavehiculo = get_object_or_404(models.MarcaVehiculo,siglas=cod)
    if request.method=='POST':
        form = forms.MarcaVehiculoForm(request.POST,request.FILES,instance=marcavehiculo)
    else:
        form = forms.MarcaVehiculoForm(instance=marcavehiculo)
    return MarcaVehiculo_save_all(request,form,'inv/invMarcaVehiculo/modal_update.html')

def MarcaVehiculo_Eliminar(request,cod):
    reino(request)
    if cod != 'NE':
        data = dict()
        data['suc'] = LoggedInUser.objects.get(user=request.user)
        data['marca'] = models.MarcaVehiculo.objects.get(siglas = cod)
        if request.method == 'POST':
            marca = models.MarcaVehiculo.objects.get(siglas = cod)
            modelo = models.ModeloVehiculo.objects.filter(marca__siglas = cod).count()
            if modelo == 0:
                marca.delete()
            else:
                messages.warning(request,'La marca del vehiculo esta asociado con un modelo no se puede eliminar')
            return redirect('MarcaVehiculo_Listar')
        else:
            return render(request,'inv/invMarcaVehiculo/MarcaVehiculo_Eliminar.html',data)
    else:
        raise PermissionDenied()

# ---------------------------------------------------------------------
#          TIPO DE VEHICULO
# ---------------------------------------------------------------------
@login_required
def TipoVehiculo_list(request):
    reino(request)
    return render(request,'inv/invTipoVehiculo/TipoVehiculo_List.html',{
        'tipovehiculo':models.TipoVehiculo.objects.all(),
        'suc':LoggedInUser.objects.get(user=request.user)})

@login_required
def TipoVehiculo_save_all(request,form,template_name):
    reino(request)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            tipovehiculo = models.TipoVehiculo.objects.all()
            data['Pantalla_List']= render_to_string('inv/invTipoVehiculo/TipoVehiculo_List_Details.html',{'tipovehiculo':tipovehiculo})
        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def TipoVehiculo_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.TipoVehiculoForm(request.POST,request.FILES)
    else:
        form = forms.TipoVehiculoForm()
    return TipoVehiculo_save_all(request,form,'inv/invTipoVehiculo/modal_create.html')

@login_required
def TipoVehiculo_Editar(request,cod):
    reino(request)
    tipovehiculo = get_object_or_404(models.TipoVehiculo,pk=cod)
    if request.method=='POST':
        form = forms.TipoVehiculoForm(request.POST,request.FILES,instance=tipovehiculo)
    else:
        form = forms.TipoVehiculoForm(instance=tipovehiculo)
    return TipoVehiculo_save_all(request,form,'inv/invTipoVehiculo/modal_update.html')

@login_required
def TipoVehiculo_Eliminar(request,cod):
    reino(request)
    if cod != '1':
        data = dict()
        data['tipo'] = models.TipoVehiculo.objects.get(pk=cod)
        data['suc'] = LoggedInUser.objects.get(user=request.user)
        if request.method == 'POST':
            tipo = models.TipoVehiculo.objects.get(pk=cod)
            modelo = models.ModeloVehiculo.objects.filter(tipo__id = cod).count()
            if modelo == 0:
                tipo.delete()
            else:
                messages.warning(request,'el tipo de vehiculo esta asociado a un modelo no se puede eliminar')
            return redirect('TipoVehiculo_Listar')
        else:
            return render(request,'inv/invTipoVehiculo/TipoVehiculo_Eliminar.html',data)
    else:
        raise PermissionDenied()

# ---------------------------------------------------------------------
#          MODELO DE VEHICULO
# ---------------------------------------------------------------------
@login_required
def ModeloVehiculo_list(request):
    reino(request)
    return render(request,'inv/invModeloVehiculo/ModeloVehiculo_List.html',{
        'modelovehiculo':models.ModeloVehiculo.objects.all(),
        'suc':LoggedInUser.objects.get(user=request.user)})

@login_required
def ModeloVehiculo_save_all(request,form,template_name):
    reino(request)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            modelovehiculo = models.ModeloVehiculo.objects.all()
            data['Pantalla_List']= render_to_string('inv/invModeloVehiculo/ModeloVehiculo_List_Details.html',{'modelovehiculo':modelovehiculo})
        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def ModeloVehiculo_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.ModeloVehiculoForm(request.POST,request.FILES)
    else:
        form = forms.ModeloVehiculoForm()
    return ModeloVehiculo_save_all(request,form,'inv/invModeloVehiculo/modal_create.html')

@login_required
def ModeloVehiculo_Editar(request,cod):
    reino(request)
    modelovehiculo = get_object_or_404(models.ModeloVehiculo,id_modelo=cod)
    if request.method=='POST':
        form = forms.ModeloVehiculoForm(request.POST,request.FILES,instance=modelovehiculo)
    else:
        form = forms.ModeloVehiculoForm(instance=modelovehiculo)
    return ModeloVehiculo_save_all(request,form,'inv/invModeloVehiculo/modal_update.html')

@login_required
def ModeloVehiculo_Eliminar(request,cod):
    reino(request)
    if cod != 'NE.NEE000':
        data = dict()
        data['modelo'] = models.ModeloVehiculo.objects.get(pk=cod)
        data['suc'] = LoggedInUser.objects.get(user=request.user)
        if request.method == 'POST':
            modelo = models.ModeloVehiculo.objects.get(pk=cod)
            modelo.delete()
            return redirect('ModeloVehiculo_Listar')
        else:
            return render(request,'inv/invModeloVehiculo/ModeloVehiculo_Eliminar.html',data)
    else:
        raise PermissionDenied()

# ---------------------------------------------------------------------
#          SUCURSALES
# ---------------------------------------------------------------------
@login_required
def Sucursal_list(request):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    sucursal = models.Sucursal.objects.filter(siglas= suc.sucursal.siglas)
    return render(request,'inv/invSucursal/Sucursal_List.html',{
        'sucursal':sucursal,
        'suc':suc })

@login_required
def Sucursal_save_all(request,form,template_name):
    reino(request)
    data = dict()
    suc = LoggedInUser.objects.get(user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            sucursal = models.Sucursal.objects.filter(siglas=suc.sucursal.siglas)
            data['Pantalla_List']= render_to_string('inv/invSucursal/Sucursal_List_Details.html',{'sucursal':sucursal})
        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def Sucursal_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.SucursalForm(request.POST,request.FILES)
    else:
        form = forms.SucursalForm()
    return Sucursal_save_all(request,form,'inv/invSucursal/modal_create.html')

@login_required
def Sucursal_Editar(request,cod):
    reino(request)
    sucursal = get_object_or_404(models.Sucursal,siglas=cod)
    if request.method=='POST':
        form = forms.SucursalForm(request.POST,request.FILES,instance=sucursal)
    else:
        form = forms.SucursalForm(instance=sucursal)
    return Sucursal_save_all(request,form,'inv/invSucursal/modal_update.html')


@login_required
def Sucursal_Saldo(request,cod):
    reino(request)
    sucursal = get_object_or_404(models.Sucursal,siglas=cod)
    if request.method=='POST':
        form = forms.SucursalForm(request.POST,request.FILES,instance=sucursal)
    else:
        form = forms.SucursalForm(instance=sucursal)
    return Sucursal_save_all(request,form,'inv/invSucursal/modal_saldo.html')

# ---------------------------------------------------------------------
#          BODEGAS
# ---------------------------------------------------------------------
@login_required
def Bodega_list(request):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    bodega = models.Bodega.objects.filter(sucursal=suc.sucursal)
    return render(request,'inv/invBodega/Bodega_List.html',{
        'bodega':bodega,
        'suc':suc})

@login_required
def Bodega_save_all(request,form,template_name):
    reino(request)
    data = dict()
    suc = LoggedInUser.objects.get(user=request.user)
    sigla = suc.sucursal.siglas
    if request.method == 'POST':
        if form.is_valid():
            ex = form.cleaned_data['id_bodega']
            i = models.Bodega.objects.filter(pk = ex).exists()
            form.save()
            if not i:
                items = models.N4Item.objects.all()
                for i in items:
                    k = models.ExistenciaBodega.objects.create(
                        bodega = models.Bodega.objects.get(pk = ex),
                        item = i,
                        cantidad = 0
                    )
            data['form_is_valid'] = True
            bodega = models.Bodega.objects.filter(sucursal=suc.sucursal)
            data['Pantalla_List']= render_to_string('inv/invBodega/Bodega_List_Details.html',{'bodega':bodega})
        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def Bodega_Create(request):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    sigla = suc.sucursal.siglas
    if request.method=='POST':
        post = request.POST.copy()
        post['sucursal'] = suc.sucursal.siglas
        post['id_bodega'] = suc.sucursal.siglas + post['siglas']
        form = forms.BodegaForm(post,request.FILES)
    else:
        form = forms.make_new_bodega(sigla)
    return Bodega_save_all(request,form,'inv/invBodega/modal_create.html')

@login_required
def Bodega_Editar(request,cod):
    reino(request)
    bodega = get_object_or_404(models.Bodega,pk=cod)
    suc = LoggedInUser.objects.get(user=request.user)
    sigla = suc.sucursal.siglas
    if request.method=='POST':
        form = forms.BodegaForm(request.POST,request.FILES,instance=bodega)
    else:
        form = forms.make_new_bodega(sigla)
        form = form(instance=bodega)
    return Bodega_save_all(request,form,'inv/invBodega/modal_update.html')

@login_required
def Bodega_Saldo(request,cod):
    reino(request)
    bodega = get_object_or_404(models.Bodega,pk=cod)
    suc = LoggedInUser.objects.get(user=request.user)
    sigla = suc.sucursal.siglas
    if request.method=='POST':
        form = forms.BodegaForm(request.POST,request.FILES,instance=bodega)
    else:
        form = forms.make_new_bodega(sigla)
        form = form(instance=bodega)
    return Bodega_save_all(request,form,'inv/invBodega/modal_saldo.html')

@login_required
def Bodega_Eliminar(request,cod):
    reino(request)
    bod =  get_object_or_404(models.Bodega,pk=cod)
    print(bod.siglas)
    if bod.siglas != 'TR' and bod.siglas !='CT' and bod.siglas !='TD' and bod.siglas !='DE':
        data = dict()
        data['bodega'] = get_object_or_404(models.Bodega,pk=cod)
        data['suc'] = LoggedInUser.objects.get(user = request.user)
        suc = LoggedInUser.objects.get(user = request.user)
        sigla = suc.sucursal.siglas
        if request.method == 'POST':
            exbodega = models.ExistenciaBodega.objects.filter(bodega = bod)
            for i in exbodega:
                if i.cantidad != 0:
                    messages.warning(request,'No se puede eliminar la bodega presenta existencias de "%s" en el item "%s"'%(
                                                i.cantidad,
                                                i.item
                                                )
                                            )
                    return redirect('Bodega_Listar')
            bod.delete()
            return redirect('Bodega_Listar')
        else:
            return render(request,'inv/invBodega/Bodega_Eliminar.html',data)
    else:
        raise PermissionDenied()

@login_required
def Bodega_CentroCosto(request):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    tabla =  models.Bodega.objects.annotate(sucExistencia=Sum('sucursal__existencia')).annotate(sucSaldo=Sum('sucursal__saldo')).filter(sucursal = suc.sucursal).order_by('id_bodega')
    sucursal = models.Sucursal.objects.get(siglas = suc.sucursal.siglas)
    rows = ([i.sucursal,i.id_bodega, i.nombre,i.existencia,i.saldo ] for i in tabla)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    x = list(writer.writerow(['Sucursal','Codigo','Nombre','Existencias','Saldo']))
    y = list(((writer.writerow(row) for row in rows)))
    t = list(writer.writerow(['Total:',sucursal.siglas,sucursal.nombre,sucursal.existencia,sucursal.saldo]))
    z = x + y
    z += t
    response = StreamingHttpResponse(z,content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename = "CentroCosto.csv"'
    return response

@login_required
def Bodega_CentroCosto_Global(request):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    sucursales = models.Sucursal.objects.all().exclude(siglas = 'DU')
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    z = list()
    z += list(writer.writerow(['Sucursal','Codigo','Nombre','Existencias','Saldo']))
    for s in sucursales:
        tabla =  models.Bodega.objects.annotate(sucExistencia=Sum('sucursal__existencia')).annotate(sucSaldo=Sum('sucursal__saldo')).filter(sucursal = s).order_by('id_bodega')
        rows = ([i.sucursal,i.id_bodega, i.nombre,i.existencia,i.saldo ] for i in tabla)
        x = list(((writer.writerow(row) for row in rows)))
        y = list(writer.writerow(['Total:',s.siglas,s.nombre,s.existencia,s.saldo]))
        z += x+y
    response = StreamingHttpResponse(z,content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename = "CentroCosto.csv"'
    return response

# ---------------------------------------------------------------------
#          EXISTENCIAS DE BODEGA
# ---------------------------------------------------------------------
@login_required
def ExistenciaBodega_list(request,item):
    reino(request)
    data = dict()
    suc = LoggedInUser.objects.get(user=request.user)
    data['item'] = models.N4Item.objects.get(id_n4=item)
    data['suc'] = suc
    data['existenciabodega'] = models.ExistenciaBodega.objects.filter(bodega__sucursal = suc.sucursal,item = item)
    data['exsucursales'] = models.Sucursal.objects.annotate(existencias = Sum('bodega__existenciabodega__cantidad',filter=Q(bodega__existenciabodega__item=item))).all().exclude(pk='DU')
    return render(request,'inv/invExistenciaBodega/ExistenciaBodega_List.html',data)

@login_required
def ExistenciaBodega_save_all(request,form,template_name):
    reino(request)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            existenciabodega = models.ExistenciaBodega.objects.all()
            data['Pantalla_List']= render_to_string('inv/invExistenciaBodega/ExistenciaBodega_List_Details.html',{'existenciabodega':existenciabodega})
        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def ExistenciaBodega_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.ExistenciaBodegaForm(request.POST,request.FILES)
    else:
        form = forms.ExistenciaBodegaForm()
    return ExistenciaBodega_save_all(request,form,'inv/invExistenciaBodega/modal_create.html')

@login_required
def ExistenciaBodega_Editar(request,cod):
    reino(request)
    existenciabodega = get_object_or_404(models.ExistenciaBodega,pk=cod)
    if request.method=='POST':
        form = forms.ExistenciaBodegaForm(request.POST,request.FILES,instance=existenciabodega)
    else:
        form = forms.ExistenciaBodegaForm(instance=existenciabodega)
    return ExistenciaBodega_save_all(request,form,'inv/invExistenciaBodega/modal_update.html')

# ---------------------------------------------------------------------
#          ESTADOS
# ---------------------------------------------------------------------
@login_required
def Estado_list(request):
    reino(request)
    return render(request,'inv/invEstado/Estado_List.html',{
        'estado':models.Estado.objects.all(),
        'suc':LoggedInUser.objects.get(user=request.user)})

@login_required
def Estado_save_all(request,form,template_name):
    reino(request)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            estado = models.Estado.objects.all()
            data['Pantalla_List']= render_to_string('inv/invEstado/Estado_List_Details.html',{'estado':estado})
        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def Estado_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.EstadoForm(request.POST,request.FILES)
    else:
        form = forms.EstadoForm()
    return Estado_save_all(request,form,'inv/invEstado/modal_create.html')

@login_required
def Estado_Editar(request,cod):
    reino(request)
    estado = get_object_or_404(models.Estado,pk=cod)
    if request.method=='POST':
        form = forms.EstadoForm(request.POST,request.FILES,instance=estado)
    else:
        form = forms.EstadoForm(instance=estado)
    return Estado_save_all(request,form,'inv/invEstado/modal_update.html')

# ---------------------------------------------------------------------
#          CENTRO DE COSTOS
# ---------------------------------------------------------------------
@login_required
def CentroCosto_list(request):
    reino(request)
    return render(request,'inv/invCentroCosto/CentroCosto_List.html',{
        'centrocosto':models.CentroCosto.objects.all(),
        'suc':LoggedInUser.objects.get(user=request.user)})

@login_required
def CentroCosto_save_all(request,form,template_name):
    reino(request)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            centrocosto = models.CentroCosto.objects.all()
            data['Pantalla_List']= render_to_string('inv/invCentroCosto/CentroCosto_List_Details.html',{'centrocosto':centrocosto})
        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def CentroCosto_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.CentroCostoForm(request.POST,request.FILES)
    else:
        form = forms.CentroCostoForm()
    return CentroCosto_save_all(request,form,'inv/invCentroCosto/modal_create.html')

@login_required
def CentroCosto_Editar(request,cod):
    reino(request)
    centrocosto = get_object_or_404(models.CentroCosto,pk=cod)
    if request.method=='POST':
        form = forms.CentroCostoForm(request.POST,request.FILES,instance=centrocosto)
    else:
        form = forms.CentroCostoForm(instance=centrocosto)
    return CentroCosto_save_all(request,form,'inv/invCentroCosto/modal_update.html')

# ---------------------------------------------------------------------
#          TIPO DE AJUSTES
# ---------------------------------------------------------------------
@login_required
def AjusteTipo_list(request):
    reino(request)
    return render(request,'inv/invAjusteTipo/AjusteTipo_List.html',{
        'ajustetipo':models.AjusteTipo.objects.all(),
        'suc':LoggedInUser.objects.get(user=request.user)})

@login_required
def AjusteTipo_save_all(request,form,template_name):
    reino(request)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            ajustetipo = models.justeTipo.objects.all()
            data['Pantalla_List']= render_to_string('inv/invAjusteTipo/AjusteTipo_List_Details.html',{'ajustetipo':ajustetipo})
        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def AjusteTipo_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.AjusteTipoForm(request.POST,request.FILES)
    else:
        form = forms.AjusteTipoForm()
    return AjusteTipo_save_all(request,form,'inv/invAjusteTipo/modal_create.html')

@login_required
def AjusteTipo_Editar(request,cod):
    reino(request)
    ajustetipo = get_object_or_404(models.AjusteTipo,pk=cod)
    if request.method=='POST':
        form = forms.AjusteTipoForm(request.POST,request.FILES,instance=ajustetipo)
    else:
        form = forms.AjusteTipoForm(instance=ajustetipo)
    return AjusteTipo_save_all(request,form,'inv/invAjusteTipo/modal_update.html')

# ---------------------------------------------------------------------
#          CONDICIONES PARA LA DEVOLUCION
# ---------------------------------------------------------------------

@login_required
def DevolucionCondicion_list(request):
    reino(request)
    return render(request,'inv/invDevolucionCondicion/DevolucionCondicion_List.html',{
        'devolucioncondicion':models.DevolucionCondicion.objects.all(),
        'suc':LoggedInUser.objects.get(user=request.user)})

@login_required
def DevolucionCondicion_save_all(request,form,template_name):
    reino(request)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            devolucioncondicion = models.DevolucionCondicion.objects.all()
            data['Pantalla_List']= render_to_string('inv/invDevolucionCondicion/DevolucionCondicion_List_Details.html',{'devolucioncondicion':devolucioncondicion})
        else:
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def DevolucionCondicion_Create(request):
    reino(request)
    if request.method=='POST':
        form = forms.DevolucionCondicionForm(request.POST,request.FILES)
    else:
        form = forms.DevolucionCondicionForm()
    return DevolucionCondicion_save_all(request,form,'inv/invDevolucionCondicion/modal_create.html')

@login_required
def DevolucionCondicion_Editar(request,cod):
    reino(request)
    devolucioncondicion = get_object_or_404(models.DevolucionCondicion,pk=cod)
    if request.method=='POST':
        form = forms.DevolucionCondicionForm(request.POST,request.FILES,instance=devolucioncondicion)
    else:
        form = forms.DevolucionCondicionForm(instance=devolucioncondicion)
    return DevolucionCondicion_save_all(request,form,'inv/invDevolucionCondicion/modal_update.html')

# ---------------------------------------------------------------------
#          DEVOLUCION
# ---------------------------------------------------------------------

@login_required
def Devolucion_busqueda(request):
    reino(request)
    data = dict()
    if request.method == 'POST':
        form = forms.BusquedaForm(request.POST)
        data['form'] = form
        devolucionbuscado = models.DevolucionMsr.objects.filter(item = form.cleaned_data['busqueda'])
        data['devolucionbuscado'] = devolucionbuscado
    else:
        form = forms.BusquedaForm()
        data['devolucionbuscado']=[]
        data['form'] = form
    return render(request,'inv/invDevolucionMsr/Busqueda.html',data)

@login_required
def DevolucionMsr_list(request):
    reino(request)
    data = dict()
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    if request.method=='POST':
        form = forms.BusquedafechasForm(request.POST)
        if form.is_valid():
            data['form'] = form
            busqueda= form.cleaned_data['busqueda']
            fecha_ini = datetime.strptime(form.cleaned_data['fecha_inicio'],'%Y-%m-%d')
            fecha_fin = datetime.strptime(form.cleaned_data['fecha_fin'],'%Y-%m-%d')+ timedelta(days=1)
            if busqueda == 'TRUE':
                data['fecha_inicio'] = form.cleaned_data['fecha_inicio']
                data['fecha_fin'] = form.cleaned_data['fecha_fin']
                data['devolucionmsr'] = models.DevolucionMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=fecha_ini,fecha__lte=fecha_fin).order_by('-fecha')
            else:
                data['fecha_inicio'] = form.cleaned_data['fecha_inicio']
                data['fecha_fin'] = form.cleaned_data['fecha_fin']
                select =form.cleaned_data['rangos_especificos']
                if select=='1':#seleccioname los del dia
                    data['devolucionmsr'] = models.DevolucionMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=date.today()).order_by('-fecha')
                if select == '2': #seleccioname los de la semana
                    data['devolucionmsr'] = models.DevolucionMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__week=datetime.today().isocalendar()[1],fecha__year__gte=date.today().year).order_by('-fecha')
                if select == '3': #seleccioname los del mes
                    data['devolucionmsr'] = models.DevolucionMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__month=date.today().month,fecha__year=date.today().year).order_by('-fecha')
    else:
        data['form']=forms.BusquedafechasForm()
        data['devolucionmsr']= models.DevolucionMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=date.today()).order_by('-fecha')
        data['fecha_inicio'] = date.today().strftime("%Y-%m-%d")
        data['fecha_fin'] = date.today().strftime("%Y-%m-%d")  
    return render(request,'inv/invDevolucionMsr/DevolucionMsr_List.html',data)

@login_required
def DevolucionMsr_save_all(request,form,template_name):
    reino(request)
    data = dict()
    suc = LoggedInUser.objects.get(user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            devolucionmsr = models.DevolucionMsr.objects.filter(sucursal= suc.sucursal,fecha__gte=date.today()).order_by('-fecha')
            data['Pantalla_List']= render_to_string('inv/invDevolucionMsr/DevolucionMsr_List_Details.html',{'devolucionmsr':devolucionmsr})
            # data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
        else:
            print('invalido')
            print(form.errors)
            data['form_is_valid'] = False
            # data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    param = dict()
    param['form'] = form        
    param['queryr'] = EntradaMercaderiaMsr.objects.filter(referencia__contains = suc.sucursal.siglas).filter(estado__id = 3)  
    param['queryf'] = Facturamsr.objects.filter(sucursal = suc.sucursal).filter(estado__id = 3)
    # print(param['queryf'])  
    data['html_form'] = render_to_string(template_name,param,request=request,)
    return JsonResponse(data)
    # return redirect('DevolucionMaestroDetalle',cod = form.cleaned_data['referencia'])

@login_required
def DevolucionMsr_Create(request):
    reino(request)
    if request.method=='POST':
        #copiamos el post para poder modificar sus valores
        post = request.POST.copy()
        today= date.today().strftime('%Y%m%d')
        suc = LoggedInUser.objects.get(user=request.user)
        post['sucursal']=suc.sucursal.siglas
        print(post['factura'] == '')
        # print(post['rem'])
        # print(post['factura'])
        # print('voy a probar con el post')
        if post['rem'] == '' and post['factura'] == '':
            data = dict()
            messages.warning(request, 'no ha seleccionado ninguna factura o rem para la devolucion.')
            form = forms.make_devolucion_msr_form(request,post)
            param = dict()
            param['form'] = form        
            param['queryr'] = EntradaMercaderiaMsr.objects.filter(estado__id = 3)      
            param['queryf'] = Facturamsr.objects.filter(estado__id = 3)        
            data['form_is_valid'] = False
            data['html_form'] = render_to_string('inv/invDevolucionMsr/modal_create.html',param,request=request,)
            return JsonResponse(data)
        else:
            #con este if generamos el consecutivo
            if post['rem']!= '':
                numero = models.DevolucionMsr.objects.filter(referencia__contains='SD',sucursal=suc.sucursal).filter(referencia__contains=today)
                if numero.count()==0:
                    consecutivo = '00001'
                else:
                    consecutivo = '{:0>5}'.format(numero.count()+1)
                post['referencia'] = suc.sucursal.siglas+'-SD-'+today+'-'+consecutivo

            elif post['factura']!='':
                numero = models.DevolucionMsr.objects.filter(referencia__contains='ED',sucursal=suc.sucursal).filter(referencia__contains=today)
                if numero.count()==0:
                    consecutivo = '00001'
                else:
                    consecutivo = '{:0>5}'.format(numero.count()+1)
                post['referencia'] = suc.sucursal.siglas+'-ED-'+today+'-'+consecutivo
            form = forms.DevolucionMsrForm(post)
    else:
        post = dict()
        print(post == {})
        form = forms.make_devolucion_msr_form(request,post)
    return DevolucionMsr_save_all(request,form,'inv/invDevolucionMsr/modal_create.html')

@login_required
def DevolucionMsr_Editar(request,cod):
    reino(request)
    devolucionmsr = get_object_or_404(models.DevolucionMsr,referencia=cod)
    if request.method=='POST':
        form = forms.DevolucionMsrForm(request.POST,request.FILES,instance=devolucionmsr)
    else:
        form = forms.DevolucionMsrForm(instance=devolucionmsr)
    return DevolucionMsr_save_all(request,form,'inv/invDevolucionMsr/modal_update.html')

@login_required
def DevolucionMaestroDetalle(request,cod):
    # variables para poder pintar la session de usuarios
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    msr = models.DevolucionMsr.objects.get(referencia=cod) 

    queryItem=models.N4Item.objects.all()
    queryBodega = models.Bodega.objects.filter(sucursal = suc.sucursal,id_bodega__contains= 'TR')
    detalle = models.N4Item.objects.all()

    if msr.rem == 'DU-EM-99999999-00001':
        entrada = True
        documento = EntradaMercaderiaMsr.objects.get(pk = 'DU-EM-99999999-00001')
    elif msr.factura == 'DU-SV-001':
        entrada = False
        documento = Facturamsr.objects.get(pk ='DU-SV-001')

    else:
        # verificamos si es devolucion de proveedor o de cliente para asi saber a que documento referenciarnos
        if msr.rem != 'REM-001' and msr.rem != None:
            documento = EntradaMercaderiaMsr.objects.get(referencia=msr.rem)
            detalle = EntradaMercaderiaDet.objects.filter(referencia = documento.referencia)
            entrada = True
        elif msr.factura != 'SF-001' and msr.factura != None:
            documento = Facturamsr.objects.get(referencia=msr.factura)
            detalle = Facturadet.objects.filter(referencia=documento.referencia)
            entrada = False
        #esto para filtrar los item y la bodega que aparecen en el documento
        #estoy cargando la lista de item que estan en el documento a una lista de qitem para luego realizar el queryset
        qitems = []
        for d in detalle:
            item = models.N4Item.objects.get(pk=d.item.id_n4)
            qitems.append(item.id_n4)
        queryItem=models.N4Item.objects.filter(pk__in=qitems)

    # construimos el formulario con los queryset de bodega y item para limitar solo estos al item
    detform = forms.make_devolucion_det_form(suc.sucursal.siglas,queryItem,queryBodega)
    det = inlineformset_factory(models.DevolucionMsr,models.DevolucionDettemp,form=detform,extra = 1)

    
    # comenzamos las validaciones cuando el request sea un POST
    if request.method == 'POST':
        formset = det(request.POST,instance = msr)
        if formset.is_valid():            
            for form in formset:
                if form.cleaned_data != {}:
                    if form.cleaned_data.get('item',False):
                        if form.cleaned_data['DELETE']:
                            if form.cleaned_data['id'] != None:
                                linea = models.DevolucionDettemp.objects.get(id = form.cleaned_data['id'].id )
                                linea.delete()
                        else:
                            if form.is_valid():

                                decimales = form.cleaned_data['cantidad']
                                item = form.cleaned_data['item']
                                if item.producto.entero == 'S':
                                    print(decimales)
                                    if float(decimales)-float(int(decimales)) > float(0):
                                        messages.warning(request,'No se puede efectuar operacion, el item : "%s" pertenece a un producto cuyos movimientos son enteros, no decimales'%(
                                            form.cleaned_data['item']
                                            )
                                        )
                                        return redirect('DevolucionMaestroDetalle',cod = msr.referencia)



                                if form.cleaned_data['cantidad'] <= 0:
                                    messages.warning(request,'No se puede efectuar operacion, el campo unidades del item : "%s" es igual o menor a "0"'%(
                                        form.cleaned_data['item']
                                        )
                                    )
                                    return redirect('DevolucionMaestroDetalle',cod = msr.referencia)

                                #sacamos la bodega transitoria de la sucursal
                                bodegatr = models.Bodega.objects.get(sucursal = suc.sucursal,id_bodega__contains='TR')
                                
                                #cuando es devolucion sin documento asociado
                                if msr.rem == 'DU-EM-99999999-00001' or msr.factura == 'DU-SV-001':
                                    existencia = models.ExistenciaBodega.objects.get(item = form.cleaned_data['item'],bodega = bodegatr)
                                    if entrada:
                                        final = existencia.cantidad - form.cleaned_data['cantidad']
                                    else:
                                        final = existencia.cantidad + form.cleaned_data['cantidad']
                                    if final < 0:
                                        messages.warning(request,'No se puede efectuar operacion, las existencias quedan en negativo del item : "%s" en la bodega: "%s", Existencias Actuales: "%s"'%(
                                            form.cleaned_data['item'],
                                            bodegatr,
                                            existencia.cantidad
                                            )
                                        )
                                        return redirect('DevolucionMaestroDetalle',cod = msr.referencia)
                                    else:
                                        #revisamos i tenemos registrado su dato
                                        exis = models.DevolucionDettemp.objects.filter(referencia = msr,bodega=bodegatr,item =form.cleaned_data['item'],estado = form.cleaned_data['estado']).exists()
                                        if exis:
                                            linea = models.DevolucionDettemp.objects.get(referencia = msr,bodega=bodegatr,item =form.cleaned_data['item'],estado = form.cleaned_data['estado'])
                                            linea.fecha_venc = form.cleaned_data['fecha_venc']
                                            linea.cantidad = form.cleaned_data['cantidad']
                                            linea.costo = form.cleaned_data['costo']
                                            linea.precio = form.cleaned_data['precio']
                                            linea.impuesto = form.cleaned_data['impuesto']
                                            linea.penalizacion = form.cleaned_data['penalizacion']
                                            linea.monto = form.cleaned_data['monto']
                                            linea.save()

                                        else:
                                            models.DevolucionDettemp.objects.create(
                                                referencia = msr,
                                                bodega = bodegatr,
                                                item = form.cleaned_data['item'],
                                                fecha_venc = form.cleaned_data['fecha_venc'],
                                                estado = form.cleaned_data['estado'],
                                                cantidad = form.cleaned_data['cantidad'],
                                                costo = form.cleaned_data['costo'],
                                                precio = form.cleaned_data['precio'],
                                                impuesto = form.cleaned_data['impuesto'],
                                                penalizacion = form.cleaned_data['penalizacion'],
                                                monto = form.cleaned_data['monto']
                                            )
                                #cuando tiene documento asociado
                                else:
                                    #buscamos la cantidad disponible que tiene la linea en el documento(entrada => TRUE =>  entradamercaderia)
                                    if entrada:
                                        cant = EntradaMercaderiaDet.objects.filter(referencia = msr.rem, item = form.cleaned_data['item']).aggregate(Sum('unidades'),Sum('devuelto'))
                                        # obtenemos la existencia que dice el sistema actualmente
                                        existencia = models.ExistenciaBodega.objects.get(item = form.cleaned_data['item'],bodega = bodegatr)
                                        final = existencia.cantidad - form.cleaned_data['cantidad']
                                    else:
                                        cant = Facturadet.objects.filter(referencia = msr.factura, item = form.cleaned_data['item']).aggregate(Sum('unidades'),Sum('devuelto'))
                                        # obtenemos la existencia que dice el sistema actualmente
                                        existencia = models.ExistenciaBodega.objects.get(item = form.cleaned_data['item'],bodega = bodegatr)
                                        final = existencia.cantidad + form.cleaned_data['cantidad']
                                    
                                    documento_cantidad = cant['unidades__sum']
                                    documento_devueltos = cant['devuelto__sum']
                                    disponible = documento_cantidad - documento_devueltos
                                    detdocum = models.DevolucionDettemp.objects.filter(referencia = msr,item = form.cleaned_data['item']).exclude(estado= form.cleaned_data['estado']).aggregate(Sum('cantidad'))
                                    if detdocum['cantidad__sum'] != None:
                                        sumatoria = detdocum['cantidad__sum']
                                    else:
                                        sumatoria = 0
                                    devolver = form.cleaned_data['cantidad'] + sumatoria
                                    #primero verificamos que la cantidad sea menor que lo que tiene disponible el documento
                                    if devolver <= disponible:
                                        #despues revisamos que su bodega no quede en negativo
                                        if final < 0:
                                            messages.warning(request,'No se puede efectuar operacion, las existencias quedan en negativo del item : "%s" en la bodega: "%s", Existencias Actuales: "%s"'%(
                                                form.cleaned_data['item'],
                                                bodegatr,
                                                existencia.cantidad
                                                )
                                            )
                                        else:
                                            #revisamos i tenemos registrado su dato
                                            exis = models.DevolucionDettemp.objects.filter(referencia = msr,bodega=bodegatr,item =form.cleaned_data['item'],estado = form.cleaned_data['estado']).exists()
                                            if exis:
                                                linea = models.DevolucionDettemp.objects.get(referencia = msr,bodega=bodegatr,item =form.cleaned_data['item'],estado = form.cleaned_data['estado'])
                                                linea.fecha_venc = form.cleaned_data['fecha_venc']
                                                linea.cantidad = form.cleaned_data['cantidad']
                                                linea.costo = form.cleaned_data['costo']
                                                linea.precio = form.cleaned_data['precio']
                                                linea.impuesto = form.cleaned_data['impuesto']
                                                linea.penalizacion = form.cleaned_data['penalizacion']
                                                linea.monto = form.cleaned_data['monto']
                                                linea.save()

                                            else:
                                                models.DevolucionDettemp.objects.create(
                                                    referencia = msr,
                                                    bodega = bodegatr,
                                                    item = form.cleaned_data['item'],
                                                    fecha_venc = form.cleaned_data['fecha_venc'],
                                                    estado = form.cleaned_data['estado'],
                                                    cantidad = form.cleaned_data['cantidad'],
                                                    costo = form.cleaned_data['costo'],
                                                    precio = form.cleaned_data['precio'],
                                                    impuesto = form.cleaned_data['impuesto'],
                                                    penalizacion = form.cleaned_data['penalizacion'],
                                                    monto = form.cleaned_data['monto']
                                                )
                                    else:
                                        messages.warning(request,'No se puede efectuar operacion, las unidades son mayores que las disponibles en el documento, item : "%s", disponibles del documento: "%s"'%(
                                            form.cleaned_data['item'],
                                            disponible
                                            )
                                        )
            return redirect('DevolucionMaestroDetalle',cod = msr.referencia)
        else:
            print(formset.errors)
            messages.warning(request,formset.errors)
    # inicializamos el formset y las lineas para cuando el request sea GET 
    lineas = models.DevolucionDet.objects.filter(referencia=cod)
    formset = det(instance = msr)
    return render(request,'inv/invDevolucionMsr/MaestroDetalle.html',{'formset':formset,'Devolucion':msr,'suc':suc,'documento':documento,'entrada':entrada,'lineas':lineas})

@login_required
def DevolucionFinalizar(request,cod):
    #para poder retornar a la lista de las devoluciones
    data = dict()
    data['form']=forms.BusquedafechasForm()
    data['fecha_inicio'] = date.today().strftime("%Y-%m-%d")
    data['fecha_fin'] = date.today().strftime("%Y-%m-%d")  
    suc = LoggedInUser.objects.get(user=request.user)
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    data['devolucionmsr']= models.DevolucionMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=date.today()).order_by('-fecha')
    
    #comenzamos por obtener la cabecera y el detalle que vamos a grabar
    maestro = models.DevolucionMsr.objects.get(pk=cod)
    detallestemp = models.DevolucionDettemp.objects.filter(referencia = cod)
    costo_t = 0
    precio_t = 0
    impuesto_t = 0
    penalizacion_t = 0
    monto_t = 0

    if detallestemp.count() == 0:
        messages.warning(request,'Para Grabar la Devolucion debe tener al menos una linea de detalle')
        return redirect('DevolucionMaestroDetalle',cod = maestro.referencia)

    

    #cuando la devolucion tiene documento asociado se aumenta los devueltos
    if maestro.rem != 'DU-EM-99999999-00001' and maestro.factura != 'DU-SV-001':
        # verificamos si es devolucion de proveedor o de cliente para asi saber a que documento referenciarnos
        if maestro.rem != 'REM-001' and maestro.rem != None:
            for i in detallestemp:
                documento = EntradaMercaderiaMsr.objects.get(referencia=maestro.rem)
                sumadocumento = EntradaMercaderiaDet.objects.filter(item = i.item,referencia = documento.referencia).aggregate(Sum('unidades'),Sum('devuelto'))
                detalledocumento = EntradaMercaderiaDet.objects.filter(item = i.item,referencia = documento.referencia)

                disponible = sumadocumento['unidades__sum'] - sumadocumento['devuelto__sum']
                dev = i.cantidad
                if disponible >= dev:
                    for j in detalledocumento:
                        if dev != 0:
                            disp_j = j.unidades - j.devuelto
                            if disp_j > dev:
                                j.devuelto += dev
                                dev = 0
                                j.save()
                            else:
                                dev -= disp_j
                                j.devuelto = j.unidades
                                j.save()
                else:
                    messages.warning(request,'Para Grabar la Devolucion debe tener items disponibles en el documento')
                    return redirect('DevolucionMaestroDetalle',cod = maestro.referencia)
                                
        elif maestro.factura != 'SF-001' and maestro.factura != None:

            for i in detallestemp:
                documento = Facturamsr.objects.get(referencia=maestro.factura)
                sumadocumento = Facturadet.objects.filter(item = i.item,referencia=documento.referencia).aggregate(Sum('unidades'),Sum('devuelto'))
                detalledocumento = Facturadet.objects.filter(item = i.item,referencia=documento.referencia)

                disponible = sumadocumento['unidades__sum'] - sumadocumento['devuelto__sum']
                dev = i.cantidad

                if disponible >= dev:
                    for j in detalledocumento:
                        if dev != 0:
                            disp_j = j.unidades - j.devuelto
                            if disp_j > dev:
                                j.devuelto += dev
                                dev = 0
                                j.save()
                            else:
                                dev -= disp_j
                                j.devuelto = j.unidades
                                j.save()
                else:
                    messages.warning(request,'Para Grabar la Devolucion debe tener al items disponibles en el documento')
                    return redirect('DevolucionMaestroDetalle',cod = maestro.referencia)
        






    if maestro.rem != 'REM-001' and maestro.rem != None:

        # devolucion de proveedor trayendo los datos de la REM
        puede_grabar = True
        for i in  detallestemp:
            if puede_grabar:
                existencia = models.ExistenciaBodega.objects.get(item = i.item,bodega = i.bodega)
                final = existencia.cantidad - i.cantidad
                if final < 0:
                    puede_grabar = False
                    messages.warning(request,'No se puede Grabar este documento, las existencias quedan en negativo del item : "%s" en la bodega: "%s", Existencias Actuales: "%s"'%(
                                    i.item,
                                    i.bodega,
                                    existencia.cantidad
                                    ))
                    print(i.referencia.referencia)
                    return redirect('DevolucionMaestroDetalle',cod = i.referencia.referencia)
                
        if puede_grabar:
            for i in  detallestemp:
                existencia = models.ExistenciaBodega.objects.get(item = i.item, bodega = i.bodega)
                cost       = i.costo
                imp        = i.impuesto
                mont       = i.costo + i.impuesto
                a = models.DevolucionDet.objects.create(
                    referencia   = models.DevolucionMsr.objects.get(referencia=cod),
                    bodega       = models.Bodega.objects.get(pk = i.bodega.id_bodega),
                    item         = models.N4Item.objects.get(pk = i.item.id_n4),
                    estado       = i.estado,
                    cantidad     = i.cantidad,
                    costo        = cost,    
                    precio       = cost,
                    impuesto     = imp,
                    penalizacion = i.penalizacion,
                    monto        = mont,
                    fecha_venc   = i.fecha_venc
                )
                costo_t = costo_t + cost
                precio_t = precio_t + cost
                impuesto_t = impuesto_t + imp
                penalizacion_t = 0
                monto_t += mont

                # Afecto la existencia en la bodega
                existencia.cantidad = existencia.cantidad - i.cantidad
                existencia.save()

                exsucursal = models.ExistenciaBodega.objects.filter(bodega__sucursal =suc.sucursal, item = i.item).aggregate(Sum('cantidad'))
                exglobal = models.ExistenciaBodega.objects.filter(item = i.item).aggregate(Sum('cantidad'))
                    
                # Creamos el registro en el Kardex
                k = models.Kardex.objects.create(
                    sucursal = suc.sucursal,
                    bodega   = i.bodega,
                    item = models.N4Item.objects.get(pk = i.item.id_n4),
                    referencia = cod,
                    salida = i.cantidad,
                    haber = cost,
                    tipotransaccion = 'SC',
                    fecha_venc =  datetime.strptime(i.fecha_venc,'%Y-%m-%d') if i.fecha_venc  else date.today().strftime('%Y-%m-%d'),
                    existenciabod = existencia.cantidad,
                    existenciasuc = exsucursal['cantidad__sum'],
                    existencia = exglobal['cantidad__sum']
                )
                
                #restamos su vencimiento
                cantidad = i.cantidad
                while cantidad > 0:
                    vencimiento = models.N4ItemVencimiento.objects.filter(item =models.N4Item.objects.get(pk=i.item.id_n4)).exclude(cantidad = 0).order_by('fecha_venc').first()
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

    elif maestro.factura != 'SF-001' and maestro.factura != None:
        #devolucion de cliente trayendo los datos de la factura
        for i in  detallestemp:
            existencia = models.ExistenciaBodega.objects.get(item = i.item, bodega = i.bodega)
            item_cost  = models.item_costo.objects.get(item = i.item.id_n4)
            mont = (i.precio + i.impuesto) - i.penalizacion
            a= models.DevolucionDet.objects.create(
                referencia   = models.DevolucionMsr.objects.get(referencia=cod),
                bodega       = models.Bodega.objects.get(pk = i.bodega.id_bodega),
                item         = models.N4Item.objects.get(pk = i.item.id_n4),
                estado       = i.estado,
                cantidad     = i.cantidad,
                costo        = i.costo,    
                precio       = i.precio,
                impuesto     = i.impuesto,
                penalizacion = i.penalizacion,
                monto        = mont,
                fecha_venc   = i.fecha_venc
            )
            costo_t = costo_t + i.costo
            precio_t = precio_t + i.precio
            impuesto_t = impuesto_t + i.impuesto
            penalizacion_t = penalizacion_t + i.penalizacion
            monto_t = monto_t + mont
            # Afecto la existencia en la bodega
            existencia.cantidad = existencia.cantidad + i.cantidad
            existencia.save()
            exsucursal = models.ExistenciaBodega.objects.filter(bodega__sucursal =suc.sucursal, item = i.item).aggregate(Sum('cantidad'))
            exglobal = models.ExistenciaBodega.objects.filter(item = i.item).aggregate(Sum('cantidad'))
            # me falta incorporar el costo
            k = models.Kardex.objects.create(
                sucursal = suc.sucursal,
                bodega   = i.bodega,
                item = models.N4Item.objects.get(pk = i.item.id_n4),
                referencia =cod,
                entrada = i.cantidad,
                debe = i.costo,
                tipotransaccion = 'EA',
                fecha_venc = datetime.strptime(i.fecha_venc,'%Y-%m-%d') if i.fecha_venc  else date.today().strftime('%Y-%m-%d'),
                existenciabod = existencia.cantidad,
                existenciasuc = exsucursal['cantidad__sum'],
                existencia = exglobal['cantidad__sum']
            )

            if i.fecha_venc:
                #creamos o aumentamos la tupla en su registro de vencimiento
                existevencimiento = models.N4ItemVencimiento.objects.filter(item = models.N4Item.objects.get(pk = i.item.id_n4),referencia = cod,fecha_venc = datetime.strptime(i.fecha_venc,'%Y-%m-%d') ).exists()

                if i.fecha_venc:
                    if existevencimiento:
                        vencimiento = models.N4ItemVencimiento.objects.get(item = models.N4Item.objects.get(pk = i.item.id_n4),referencia = cod,fecha_venc = datetime.strptime(i.fecha_venc,'%Y-%m-%d'))
                        vencimiento.cantidad = vencimiento.cantidad + i.cantidad
                        vencimiento.fecha_cero ='.'
                        vencimiento.save()
                    else:
                        c = models.N4ItemVencimiento.objects.create(
                            referencia = cod,
                            item = models.N4Item.objects.get(pk = i.item.id_n4),
                            fecha_venc = datetime.strptime(i.fecha_venc,'%Y-%m-%d'),
                            cantidad = i.cantidad
                        )

    








    #borramos el temporal porque el item ya se grabo
    detallestemp.delete()
    #cambiamos el estado de la cabecera de la devolucion y ponemos los totales obtenidos
    maestro.estado = models.Estado.objects.get(pk=1)
    maestro.costo_total = costo_t
    maestro.precio_total = precio_t
    maestro.impuesto_total = impuesto_t
    maestro.penalizacion_total = penalizacion_t
    maestro.monto_total = monto_t
    maestro.save()
    #volvemos a la lista de los documentos del dia
    return redirect('DevolucionMsr_Listar')

@login_required
def DevolucionImpreso(request,cod):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    devolucionmsr = models.DevolucionMsr.objects.get(referencia=cod)
    if devolucionmsr.estado.id == 4:
        devoluciondet= models.DevolucionDettemp.objects.filter(referencia=cod).extra(select={'total':'costo * cantidad',})
    else:
        devoluciondet= models.DevolucionDet.objects.filter(referencia=cod).extra(select={'total':'costo * cantidad',})

    if(devoluciondet.count()!=0):
        tot = 0.0
        imp = 0.0
        sto = 0.0
        if(devolucionmsr.referencia.find('ED')>=0):
            tipo  = 'CLIENTE'
            valor = True
            documento = Facturamsr.objects.get(referencia=devolucionmsr.factura)
            for l in devoluciondet:
                tot +=  (l.precio * l.cantidad) + l.impuesto - l.penalizacion
                sto +=  l.precio
        else:
            tipo = 'PROVEEDOR'
            valor = False
            documento = EntradaMercaderiaMsr.objects.get(referencia=devolucionmsr.rem)
            for l in devoluciondet:
                sto +=  l.costo
                imp +=  l.impuesto
                tot +=  l.costo + l.impuesto 
        return render(request,'inv/invDevolucionMsr/DevolucionImpresion.html',{
            'suc':suc,
            'msr':devolucionmsr,
            'det':devoluciondet,
            'tipo':tipo,
            'valor':valor,
            'documento':documento,
            'tot':tot,
            'imp': imp,
            'sto': sto
            })
    else:
        if(devolucionmsr.referencia.find('ED')>=0):
            tipo  = 'CLIENTE'
            valor = True
        else:
            tipo = 'PROVEEDOR'
            valor = False
        return render(request,'inv/invDevolucionMsr/DevolucionNoDetalle.html',{'suc':suc,'msr':devolucionmsr,'tipo':tipo,'valor':valor})

# ---------------------------------------------------------------------
#          TRASLADOS
# ---------------------------------------------------------------------
#ACCIONES CON LAS CABECERAS
@login_required
def TrasladoMsr_list(request):
    reino(request)
    data = dict()
    data['suc'] = LoggedInUser.objects.get(user= request.user)
    if request.method=='POST':
        form = forms.BusquedafechasForm(request.POST)
        if form.is_valid():
            data['form'] = form
            busqueda= form.cleaned_data['busqueda']
            fecha_ini = datetime.strptime(form.cleaned_data['fecha_inicio'],'%Y-%m-%d')
            fecha_fin = datetime.strptime(form.cleaned_data['fecha_fin'],'%Y-%m-%d')+ timedelta(days=1)
            if busqueda == 'TRUE':
                data['fecha_inicio'] = form.cleaned_data['fecha_inicio']
                data['fecha_fin'] = form.cleaned_data['fecha_fin']
                data['trasladomsr'] = models.TrasladoMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=fecha_ini,fecha__lte=fecha_fin,referencia__contains='MT').order_by('-fecha')
            else:
                data['fecha_inicio'] = form.cleaned_data['fecha_inicio']
                data['fecha_fin'] = form.cleaned_data['fecha_fin']
                select =form.cleaned_data['rangos_especificos']
                if select=='1':#seleccioname los del dia
                    data['trasladomsr'] = models.TrasladoMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=date.today(),referencia__contains='MT').order_by('-fecha')
                if select == '2': #seleccioname los de la semana
                    data['trasladomsr'] = models.TrasladoMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__week=datetime.today().isocalendar()[1],fecha__year__gte=date.today().year,referencia__contains='MT').order_by('-fecha')
                if select == '3': #seleccioname los del mes
                    data['trasladomsr'] = models.TrasladoMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__month=date.today().month,fecha__year=date.today().year,referencia__contains='MT').order_by('-fecha')
    else:
        data['form']=forms.BusquedafechasForm()
        data['trasladomsr']= models.TrasladoMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=date.today(),referencia__contains='MT').order_by('-fecha')
        data['fecha_inicio'] = date.today().strftime("%Y-%m-%d")
        data['fecha_fin'] = date.today().strftime("%Y-%m-%d")  
    return render(request,'inv/invTrasladoMsr/TrasladoMsr_List.html',data)

@login_required
def TrasladoMsr_save_all(request,form,template_name):
    reino(request)
    data = dict()
    suc = LoggedInUser.objects.get(user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()    
            data['form_is_valid'] = True
            trasladomsr = models.TrasladoMsr.objects.filter(sucursal= suc.sucursal,fecha__gte=date.today()).order_by('-fecha')
            data['Pantalla_List']= render_to_string('inv/invTrasladoMsr/TrasladoMsr_List_Details.html',{'trasladomsr':trasladomsr})
        else:
            print(form.errors)
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def TrasladoMsr_Create(request):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    if request.method=='POST':
        #copiamos el post para poder modificar sus valores
        post = request.POST.copy()
        today = date.today().strftime('%Y%m%d')
        post['sucursal']=suc.sucursal.siglas
        numero = models.TrasladoMsr.objects.filter(referencia__contains=today,sucursal=suc.sucursal,sucursalD=post['sucursalD'])
        if numero.count()==0:
            consecutivo = '01'
        else:
            consecutivo = '{:0>2}'.format(numero.count()+1)
        post['referencia']=suc.sucursal.siglas+'-MT-'+today+'-'+consecutivo+'-'+post['sucursalD']
        form = forms.TrasladoMsrForm(post,request.FILES)
    else:
        # form = forms.TrasladoMsrForm()
        form = forms.make_traslado_msr_form(suc.sucursal.siglas)
    return TrasladoMsr_save_all(request,form,'inv/invTrasladoMsr/modal_create.html')

@login_required
def TrasladoMsr_Editar(request,cod):
    reino(request)
    trasladomsr = get_object_or_404(models.TrasladoMsr,referencia=cod)
    if request.method=='POST':
        form = forms.TrasladoMsrForm(request.POST,request.FILES,instance=trasladomsr)
    else:
        form = forms.TrasladoMsrForm(instance=trasladomsr)
    return TrasladoMsr_save_all(request,form,'inv/invTrasladoMsr/modal_update.html')

#TrasladoMaestroDetalle es Equivalente a el Maestro detalle de los envios
@login_required
def TrasladoMaestroDetalle(request,cod):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    msr = models.TrasladoMsr.objects.get(referencia=cod)
    detform = forms.make_traslado_det_form(suc.sucursal.siglas)
    det = inlineformset_factory(models.TrasladoMsr,models.TrasladoDettemp, form=detform,extra = 1)
    lineas = models.TrasladoDet.objects.filter(referencia=cod)
    if request.method == 'POST':
        formset = det(request.POST,instance = msr)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data!= {}:
                    print(form)
                    if form.cleaned_data.get('bodegaO',False) and form.cleaned_data.get('item',False):
                        if form.cleaned_data['DELETE']:
                            if form.cleaned_data['id'] != None:
                                linea = models.TrasladoDettemp.objects.get(id = form.cleaned_data['id'].id)
                                linea.delete()
                        else:
                            if form.is_valid():

                                decimales = form.cleaned_data['cantidad']
                                item = form.cleaned_data['item']
                                if item.producto.entero == 'S':
                                    print(decimales)
                                    if float(decimales)-float(int(decimales)) > float(0):
                                        messages.warning(request,'No se puede efectuar operacion, el item : "%s" pertenece a un producto cuyos movimientos son enteros, no decimales'%(
                                            form.cleaned_data['item']
                                            )
                                        )
                                        return redirect('TrasladoMaestroDetalle',cod = msr.referencia)


                                sucursalD = msr.sucursalD
                                bodegaTR = models.Bodega.objects.get(sucursal = sucursalD,id_bodega__contains='TR')
                                form.cleaned_data['bodegaD'] = bodegaTR
                                form.cleaned_data['bodegaD_id']= bodegaTR.id_bodega
                                existencia = models.ExistenciaBodega.objects.get(bodega = form.cleaned_data['bodegaO'], item = form.cleaned_data['item'])
                                final = existencia.cantidad - form.cleaned_data['cantidad']
                                if final < 0:
                                    messages.warning(request,'No se puede efectuar operacion, las unidades son mayores que el documento, item : "%s" en la bodega: "%s", Existencia en bodega: "%s"'%(
                                        form.cleaned_data['item'],
                                        form.cleaned_data['bodegaO'],
                                        existencia.cantidad
                                        )
                                    )
                                elif form.cleaned_data['cantidad'] == 0:
                                    messages.warning(request,'No se puede efectuar operacion, las unidades escritas son "0", item : "%s" en la bodega: "%s"'%(
                                        form.cleaned_data['item'],
                                        form.cleaned_data['bodegaO']
                                        )
                                    )
                                else:
                                    existe = models.TrasladoDettemp.objects.filter(item = form.cleaned_data['item'].id_n4, referencia = msr,bodegaD = bodegaTR,bodegaO = form.cleaned_data['bodegaO']).exists()
                                    if existe:
                                        i = models.TrasladoDettemp.objects.get(item = form.cleaned_data['item'].id_n4, referencia = msr,bodegaD = bodegaTR,bodegaO = form.cleaned_data['bodegaO'])
                                        i.bodegaO = form.cleaned_data['bodegaO']
                                        i.bodegaD = bodegaTR
                                        i.item = models.N4Item.objects.get(pk = form.cleaned_data['item'].id_n4)
                                        i.cantidad = float(form.cleaned_data['cantidad'])
                                        i.costo = float(0)
                                        i.estado = models.Estado.objects.get(estado_desc = form.cleaned_data['estado'].estado_desc)
                                        i.save()
                                    else:
                                        i = models.TrasladoDettemp.objects.create(
                                            referencia = msr,
                                            bodegaO = form.cleaned_data['bodegaO'],
                                            bodegaD = bodegaTR,
                                            item  = models.N4Item.objects.get(pk = form.cleaned_data['item'].id_n4),
                                            cantidad = float(form.cleaned_data['cantidad']),
                                            costo = float(0),
                                            estado = models.Estado.objects.get(estado_desc= form.cleaned_data['estado'].estado_desc)
                                        )
            return redirect('TrasladoMaestroDetalle',cod = msr.referencia)
        else:
            print(formset.errors)
            messages.warning(request,formset.errors)
    formset = det(instance = msr)
    return render(request,'inv/invTrasladoMsr/MaestroDetalle.html',{'formset':formset,'Traslado':msr,'suc':suc,'lineas':lineas})

@login_required
def RecepcionAprobacion(request,cod,bodegao,bodegad,item,boton):
    reino(request)
    print(boton)
    data = dict()
    aprobar = models.TrasladoDet.objects.get(referencia__pk=cod,bodegaO__pk=bodegao,bodegaD__pk=bodegad,item__pk=item)
    
    if boton == '1':
        aprobado = models.Estado.objects.get(estado_desc='Aprobado')
    else:
        aprobado = models.Estado.objects.get(estado_desc='Devuelto')
    
    aprobar.estado = aprobado
    aprobar.save()
    return redirect('TrasladoRecepcion',cod = cod)
    
@login_required
def TrasladoRecepcionar(request,cod):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    msr = models.TrasladoMsr.objects.get(referencia=cod)
    lineas = models.TrasladoDet.objects.filter(referencia=cod)
    return render(request,'inv/invTrasladoMsr/Recepcionar.html',{'Traslado':msr,'suc':suc,'lineas':lineas})

@login_required
def RecepcionTraslado(request):
    reino(request)
    data = dict()
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    if request.method=='POST':
        form = forms.BusquedafechasForm(request.POST)
        if form.is_valid():
            data['form'] = form
            busqueda = form.cleaned_data['busqueda']
            fecha_ini = datetime.strptime(form.cleaned_data['fecha_inicio'],'%Y-%m-%d')
            fecha_fin = datetime.strptime(form.cleaned_data['fecha_fin'],'%Y-%m-%d')+ timedelta(days=1)
            if busqueda == 'TRUE':
                data['fecha_inicio'] = form.cleaned_data['fecha_inicio']
                data['fecha_fin'] = form.cleaned_data['fecha_fin']
                data['recepciones'] = models.TrasladoMsr.objects.filter(sucursalD = data['suc'].sucursal,referencia__contains = 'MT',fecha__gte=fecha_ini,fecha__lte=fecha_fin).order_by('-fecha')
            else:
                data['fecha_inicio'] = form.cleaned_data['fecha_inicio']
                data['fecha_fin'] = form.cleaned_data['fecha_fin']
                select =form.cleaned_data['rangos_especificos']

                if select=='1':#seleccioname los del dia
                    data['recepciones'] = models.TrasladoMsr.objects.filter(sucursalD = data['suc'].sucursal,referencia__contains = 'MT',fecha__gte=date.today())
                if select == '2': #seleccioname los de la semana
                    data['recepciones'] = models.TrasladoMsr.objects.filter(sucursalD = data['suc'].sucursal,referencia__contains = 'MT',fecha__week=datetime.today().isocalendar()[1],fecha__year__gte=date.today().year).order_by('-fecha')
                if select == '3': #seleccioname los del mes
                    data['recepciones'] = models.TrasladoMsr.objects.filter(sucursalD = data['suc'].sucursal,referencia__contains = 'MT',fecha__month=date.today().month,fecha__year=date.today().year).order_by('-fecha')
    
    else:
        data['form']=forms.BusquedafechasForm()
        data['recepciones'] = models.TrasladoMsr.objects.filter(sucursalD = data['suc'].sucursal,referencia__contains = 'MT',fecha__gte=date.today())
        data['fecha_inicio'] = date.today().strftime("%Y-%m-%d")
        data['fecha_fin'] = date.today().strftime("%Y-%m-%d")  
    return render(request,'inv/invTrasladoMsr/Recepcion.html',data)

@login_required
def TrasladoFinalizar(request,cod):
    #para poder retornar a la lista de las devoluciones
    reino(request)
    data = dict()
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    data['form']=forms.BusquedafechasForm()
    data['trasladomsr']= models.TrasladoMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=date.today()).order_by('-fecha')
    data['fecha_inicio'] = date.today().strftime("%Y-%m-%d")
    data['fecha_fin'] = date.today().strftime("%Y-%m-%d")

    #comenzamos por obtener la cabecera y el detalle que vamos a grabar
    maestro = models.TrasladoMsr.objects.get(pk=cod)
    detallestemp = models.TrasladoDettemp.objects.filter(referencia = cod)
    
    if detallestemp.count() == 0:
        messages.warning(request,'Para Grabar el envio debe tener al menos una linea de detalle')
        return redirect('TrasladoMaestroDetalle',cod = maestro.referencia)

    puede_grabar = True

    if puede_grabar:
        for i in detallestemp:
            existencia = models.ExistenciaBodega.objects.get(item= i.item,bodega = i.bodegaO)
            final = existencia.cantidad - i.cantidad
            if final < 0 :
                puede_grabar = False
                messages.warning(request,'No se puede Grabar este documento, las existencias quedan en negativo del item : "%s" en la bodega: "%s", Existencias Actuales: "%s"'%(
                    i.item,
                    i.bodegaO,
                    existencia.cantidad
                    )
                )
                return redirect('TrasladoMaestroDetalle',cod = i.referencia.referencia)
    if puede_grabar:
        for i in  detallestemp:
            # item_docum = EntradaMercaderiaDet.objects.get(referencia=maestro.rem,item=i.item.id_n4)
            item_cost  = models.item_costo.objects.get(item = i.item.id_n4)
            existenciaO = models.ExistenciaBodega.objects.get(item = i.item,bodega = i.bodegaO)
            existenciaD = models.ExistenciaBodega.objects.get(item = i.item,bodega = i.bodegaD)
            # mont       = float(item_docum.costo)*float(i.cantidad)
            a= models.TrasladoDet.objects.create(
                referencia   = models.TrasladoMsr.objects.get(referencia=cod),
                bodegaO       = models.Bodega.objects.get(pk = i.bodegaO.id_bodega),
                bodegaD       = models.Bodega.objects.get(pk = i.bodegaD.id_bodega),
                item          = models.N4Item.objects.get(pk = i.item.id_n4),  
                cantidad      = i.cantidad,
                recepcionado  = 0,# se queda en cero porque se quieren que revise los item que estan recibiendo
                costo         = i.costo,
                estado        = models.Estado.objects.get(pk=i.estado.id)
            )
            existenciaO.cantidad = existenciaO.cantidad - i.cantidad
            existenciaD.cantidad = existenciaD.cantidad + i.cantidad
            k = models.Kardex.objects.create(
                sucursal = maestro.sucursal,
                bodega   = i.bodegaO,
                item = models.N4Item.objects.get(pk = i.item.id_n4),
                referencia = cod,
                salida = i.cantidad,
                haber = i.costo,
                existencia = existencia.cantidad,
                tipotransaccion = 'ST',
                bodega_fin = i.bodegaD
            )
            existenciaO.save()
            existenciaD.save()


        #borramos el temporal porque el item ya se grabo
        detallestemp.delete()
        #cambiamos el estado del traslado a en espera
        maestro.estado = models.Estado.objects.get(pk=5)
        maestro.save()
        print(maestro.sucursalD.siglas)
        print(cod)
    #volvemos a la lista de los documentos del dia
    return redirect('TrasladoMsr_Listar')

@login_required
def Recepcion_Finalizar(request,cod):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    msr = models.TrasladoMsr.objects.get(pk = cod)
    lineas = models.TrasladoDet.objects.filter(referencia = msr)

    for linea in lineas:
        decimales = linea.recepcionado
        if linea.item.producto.entero == 'S':
            print(decimales)
            if float(decimales)-float(int(decimales)) > float(0):
                messages.warning(request,'No se puede efectuar operacion, el item : "%s" pertenece a un producto cuyos movimientos son enteros, no decimales'%(
                    linea.item
                    )
                )
                return redirect('TrasladoRecepcion',cod = msr.referencia)
    
    for linea in lineas:
        if linea.recepcionado > linea.cantidad:
            messages.warning(request,'el item: "%s" que va a la bodega:"%s" tiene el campo recepcionado en "%s" lo cual es mayor a la unidades que estan enviando, cambien el campo recepcionado a igual o menor valor que las unidades'%(
                linea.item,
                linea.bodegaD,
                linea.recepcionado
                )
            )
            return redirect('TrasladoRecepcion',cod = msr.referencia)
        if linea.recepcionado < 0:
            messages.warning(request,'el item: "%s" que va a la bodega:"%s" tiene el campo recepcionado en "%s" el cual es negativo, cambie su campo a un valor positivo'%(
                linea.item,
                linea.bodegaD,
                linea.recepcionado
                )
            )
            return redirect('TrasladoRecepcion',cod = msr.referencia)

    #viendo si hay que crear una devolucion es decir que encontremos una linea en devolver
    devolver = False
    for linea in lineas:
        diferencia = linea.cantidad - linea.recepcionado
        if diferencia != 0:
            devolver = True

    #esta variable es para crear el documento de devolucion de traslado
    refe = ''
    if devolver:
        today = date.today().strftime('%Y%m%d')
        numero = models.TrasladoMsr.objects.filter(referencia__contains=today,sucursal=suc.sucursal)
        if numero.count()==0:
            consecutivo = '01'
        else:
            consecutivo = '{:0>2}'.format(numero.count()+1)
        refe = msr.sucursalD.siglas+'-MT-'+today+'-'+consecutivo+'-'+msr.sucursal.siglas
        #creamos la cabecera de la devolucion del traslados
        j = models.TrasladoMsr.objects.create(
            referencia = refe,
            nota = 'devolucion de items de sucursal',
            sucursal = msr.sucursalD,
            sucursalD = msr.sucursal,
            estado = models.Estado.objects.get(pk=5)#En Espera
        )
    #grabando el detalle del envio en el kardex 
    for linea in lineas:
        #sin importar el estado de la linea solo resta crear su kardex de la entrada por traslado   
        k = models.Kardex.objects.create(
            sucursal = suc.sucursal,
            bodega = linea.bodegaD,
            item = models.N4Item.objects.get(pk=linea.item.id_n4),
            referencia = cod,
            entrada = linea.cantidad,
            debe = linea.costo,
            existencia = 0,
            tipotransaccion = 'ET'
        )

        #creando el detalle de la devolucion del traslado con los item que no esten aprobados
        diferencia = linea.cantidad - linea.recepcionado
        if diferencia != 0:
            #devolvemos sus existencias
            existenciaO = models.ExistenciaBodega.objects.get(item=linea.item,bodega = linea.bodegaO)
            existenciaD = models.ExistenciaBodega.objects.get(item=linea.item,bodega = linea.bodegaD)

            #Recordar que el recepcionado es la cantidad devuelta tal cual es
            existenciaO.cantidad = existenciaO.cantidad + diferencia
            existenciaD.cantidad = existenciaD.cantidad - diferencia

            j = models.TrasladoDet.objects.create(
                referencia = models.TrasladoMsr.objects.get(pk=refe),
                bodegaO = linea.bodegaD,
                bodegaD = linea.bodegaO,
                item = linea.item,
                cantidad = diferencia,
                recepcionado = diferencia,
                costo = 0,
                estado = models.Estado.objects.get(pk=4)# en espera
            )
            k = models.Kardex.objects.create(
                sucursal = suc.sucursal,
                bodega   = linea.bodegaD,
                item = models.N4Item.objects.get(pk=linea.item.id_n4),
                referencia = refe,
                salida = diferencia,
                haber = 0,
                existencia = 0,
                tipotransaccion = 'ST'
            )
            existenciaO.save()
            existenciaD.save()
    #aprobamos el documento que esta finalizando
    msr.estado = models.Estado.objects.get(pk = 1)
    msr.save()
    return redirect('TrasladoMsr_Recepcion')

@login_required
def TrasladoImpreso(request,cod):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    trasladomsr = models.TrasladoMsr.objects.get(referencia=cod)
    trasladodet= models.TrasladoDet.objects.filter(referencia=cod)
    
    if trasladomsr.estado.id == 4:
        trasladodet= models.TrasladoDettemp.objects.filter(referencia=cod).extra(select={'total':'costo * cantidad',})
    else:
        trasladodet= models.TrasladoDet.objects.filter(referencia=cod).extra(select={'total':'costo * cantidad',})

    if(trasladodet.count()!=0):
        return render(request,'inv/invTrasladoMsr/TrasladoImpresion.html',{'suc':suc,'msr':trasladomsr,'det':trasladodet})
    else:
        return render(request,'inv/invTrasladoMsr/TrasladoNoDetalle.html',{'suc':suc,'msr':trasladomsr})


# ---------------------------------------------------------------------
#          MOVIMIENTOS LOCALES
# ---------------------------------------------------------------------
@login_required
def Locales_Listar(request):
    data = dict()
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    data['suc'] = LoggedInUser.objects.get(user= request.user)
    if request.method=='POST':
        form = forms.BusquedafechasForm(request.POST)
        if form.is_valid():
            data['form'] = form
            busqueda= form.cleaned_data['busqueda']
            fecha_ini = datetime.strptime(form.cleaned_data['fecha_inicio'],'%Y-%m-%d')
            fecha_fin = datetime.strptime(form.cleaned_data['fecha_fin'],'%Y-%m-%d')+ timedelta(days=1)
            if busqueda == 'TRUE':
                data['fecha_inicio'] = form.cleaned_data['fecha_inicio']
                data['fecha_fin'] = form.cleaned_data['fecha_fin']
                data['trasladomsr'] = models.TrasladoMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=fecha_ini,fecha__lte=fecha_fin,referencia__contains='MU').order_by('-fecha')
            else:
                data['fecha_inicio'] = form.cleaned_data['fecha_inicio']
                data['fecha_fin'] = form.cleaned_data['fecha_fin']
                select =form.cleaned_data['rangos_especificos']
                if select=='1':#seleccioname los del dia
                    data['trasladomsr'] = models.TrasladoMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=date.today(),referencia__contains='MU').order_by('-fecha')
                if select == '2': #seleccioname los de la semana
                    data['trasladomsr'] = models.TrasladoMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__week=datetime.today().isocalendar()[1],fecha__year__gte=date.today().year,referencia__contains='MU').order_by('-fecha')
                if select == '3': #seleccioname los del mes
                    data['trasladomsr'] = models.TrasladoMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__month=date.today().month,fecha__year=date.today().year,referencia__contains='MU').order_by('-fecha')
    else:
        data['form']=forms.BusquedafechasForm()
        data['trasladomsr']= models.TrasladoMsr.objects.filter(sucursal=data['suc'].sucursal,referencia__contains='MU',fecha__gte=date.today()).order_by('-fecha')
        data['fecha_inicio'] = date.today().strftime("%Y-%m-%d")
        data['fecha_fin'] = date.today().strftime("%Y-%m-%d")  

    return render(request,'inv/invTrasladoMsr/Locales_List.html',data)

@login_required
def Locales_Create(request):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    if request.method=='POST':
        print('realizo el post')
        #copiamos el post para poder modificar sus valores
        post = request.POST.copy()
        today = date.today().strftime('%Y%m%d')
        post['sucursal']=suc.sucursal.siglas
        post['sucursalD']=suc.sucursal.siglas
        numero = models.TrasladoMsr.objects.filter(referencia__contains=today,sucursal=suc.sucursal,sucursalD=suc.sucursal)
        if numero.count()==0:
            consecutivo = '00001'
        else:
            consecutivo = '{:05}'.format(numero.count()+1)
        post['referencia']=suc.sucursal.siglas+'-MU-'+today+'-'+consecutivo
        form = forms.TrasladoMsrForm(post,request.FILES)
    else:
        print('no fue un post')
        # form = forms.TrasladoMsrForm()
        form = forms.make_traslado_msr_form2(suc.sucursal.siglas)
    return TrasladoMsr_save_all(request,form,'inv/invTrasladoMsr/Locales_create.html')

@login_required
def LocalesMaestroDetalle(request,cod):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    msr = models.TrasladoMsr.objects.get(referencia=cod)
    detform = forms.make_traslado_det_form2(suc.sucursal.siglas)
    det = inlineformset_factory(models.TrasladoMsr,models.TrasladoDettemp, form=detform,extra = 1)
    lineas = models.TrasladoDet.objects.filter(referencia=cod)
    if request.method == 'POST':
        formset = det(request.POST,instance = msr)
        if formset.is_valid():
            for form in formset:
                 if form.cleaned_data!= {}:
                    if form.is_valid():
                        if form.cleaned_data['DELETE']:
                            linea = models.TrasladoDettemp.objects.get(id = form.cleaned_data['id'].id)
                            linea.delete()
                        else:

                            decimales = form.cleaned_data['cantidad']
                            item = form.cleaned_data['item']
                            if item.producto.entero == 'S':
                                print(decimales)
                                if float(decimales)-float(int(decimales)) > float(0):
                                    messages.warning(request,'No se puede efectuar operacion, el item : "%s" pertenece a un producto cuyos movimientos son enteros, no decimales'%(
                                        form.cleaned_data['item']
                                        )
                                    )
                                    return redirect('LocalesMaestroDetalle',cod = msr.referencia)

                            sucursalD = msr.sucursalD
                            existencia = models.ExistenciaBodega.objects.get(bodega = form.cleaned_data['bodegaO'], item = form.cleaned_data['item'])

                            #primero validamos las existencias en todos los subformularios
                            Existenciass = float(0)
                            Item = form.cleaned_data['item'].id_n4
                            Origen = form.cleaned_data['bodegaO'].siglas
                            for subform in formset:
                                if subform.cleaned_data!= {}:
                                    i = subform.cleaned_data['item'].id_n4
                                    j = subform.cleaned_data['bodegaO'].siglas
                                    if Item == i and Origen == j :
                                        # print('debo sumar solo los item iguales')
                                        Existenciass = Existenciass + float(subform.cleaned_data['cantidad'])

                            final = round(existencia.cantidad - Existenciass,2)
                            print(final)
                            if final < 0:
                                messages.warning(request,'No se puede efectuar operacion, las unidades son mayores que el documento, item : "%s" en la bodega: "%s", Existencia en bodega: "%s"'%(
                                    form.cleaned_data['item'],
                                    form.cleaned_data['bodegaO'],
                                    existencia.cantidad
                                    )
                                )
                            elif form.cleaned_data['cantidad'] == 0:
                                messages.warning(request,'No se puede efectuar operacion, las unidades escritas son "0", item : "%s" en la bodega: "%s"'%(
                                    form.cleaned_data['item'],
                                    form.cleaned_data['bodegaO']
                                    )
                                )
                            else:
                                print('voy a guardar')
                                existe = models.TrasladoDettemp.objects.filter(item = form.cleaned_data['item'].id_n4,bodegaO = form.cleaned_data['bodegaO'],bodegaD = form.cleaned_data['bodegaD'], referencia = msr).exists()
                                print(existe)
                                if existe:
                                    i = models.TrasladoDettemp.objects.get(item = form.cleaned_data['item'].id_n4,bodegaO = form.cleaned_data['bodegaO'],bodegaD = form.cleaned_data['bodegaD'], referencia = msr)
                                    i.bodegaO = form.cleaned_data['bodegaO']
                                    i.bodegaD = form.cleaned_data['bodegaD']
                                    i.item = models.N4Item.objects.get(pk = form.cleaned_data['item'].id_n4)
                                    i.cantidad = float(form.cleaned_data['cantidad'])
                                    i.costo = float(0)
                                    i.estado = models.Estado.objects.get(estado_desc = form.cleaned_data['estado'].estado_desc)
                                    i.save()
                                else:
                                    i = models.TrasladoDettemp.objects.create(
                                        referencia = msr,
                                        bodegaO = form.cleaned_data['bodegaO'],
                                        bodegaD = form.cleaned_data['bodegaD'],
                                        item  = models.N4Item.objects.get(pk = form.cleaned_data['item'].id_n4),
                                        cantidad = float(form.cleaned_data['cantidad']),
                                        # costo = float(form.cleaned_data['costo']),
                                        costo = float(0),
                                        estado = models.Estado.objects.get(estado_desc= form.cleaned_data['estado'].estado_desc)
                                    )
            return redirect('LocalesMaestroDetalle',cod = msr.referencia)
        else:
            print(formset.errors)
            messages.warning(request,formset.errors)
    formset = det(instance = msr)
    return render(request,'inv/invTrasladoMsr/LocalesMaestroDetalle.html',{'formset':formset,'Traslado':msr,'suc':suc,'lineas':lineas})

@login_required
def LocalesFinalizar(request,cod):

    #para poder retornar a la lista de las devoluciones
    reino(request)
    data = dict()
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    data['form']=forms.BusquedafechasForm()
    data['trasladomsr']= models.TrasladoMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=date.today()).order_by('-fecha')
    data['fecha_inicio'] = date.today().strftime("%Y-%m-%d")
    data['fecha_fin'] = date.today().strftime("%Y-%m-%d")

    #comenzamos por obtener la cabecera y el detalle que vamos a grabar
    maestro = models.TrasladoMsr.objects.get(pk=cod)
    detallestemp = models.TrasladoDettemp.objects.filter(referencia = cod)

    if detallestemp.count() == 0:
        messages.warning(request,'No se puede grabar el movimiento local, para grabarlo al menos inserte una linea en el registro')
        return redirect('LocalesMaestroDetalle',cod = maestro.referencia)



    puede_grabar = True

    if puede_grabar:
        for i in detallestemp:
            existencia = 0
            item = i.item.id_n4
            origen = i.bodegaO.siglas
            for j in detallestemp:
                if item == j.item.id_n4 and origen == i.bodegaO.siglas:
                    existencia = existencia + j.cantidad
            existenciabodega = models.ExistenciaBodega.objects.get(item= i.item,bodega = i.bodegaO)
            final = existenciabodega.cantidad - existencia


            if final < 0 :
                puede_grabar = False
                messages.warning(request,'No se puede Grabar este documento, las existencias quedan en negativo del item : "%s" en la bodega: "%s", Existencias Actuales: "%s"'%(
                    i.item,
                    i.bodegaO,
                    existencia.cantidad
                    )
                )
                return redirect('LocalesMaestroDetalle',cod = i.referencia.referencia)
    if puede_grabar:
        for i in  detallestemp:
            # item_docum = EntradaMercaderiaDet.objects.get(referencia=maestro.rem,item=i.item.id_n4)
            item_cost  = models.item_costo.objects.get(item = i.item.id_n4)
            existenciaO = models.ExistenciaBodega.objects.get(item = i.item,bodega = i.bodegaO)
            existenciaD = models.ExistenciaBodega.objects.get(item = i.item,bodega = i.bodegaD)
            # mont       = float(item_docum.costo)*float(i.cantidad)
            a= models.TrasladoDet.objects.create(
                referencia   = models.TrasladoMsr.objects.get(referencia=cod),
                bodegaO       = models.Bodega.objects.get(pk = i.bodegaO.id_bodega),
                bodegaD       = models.Bodega.objects.get(pk = i.bodegaD.id_bodega),
                item          = models.N4Item.objects.get(pk = i.item.id_n4),  
                cantidad      = i.cantidad,
                costo         = i.costo,
                estado        = models.Estado.objects.get(pk=1)
            )
            existenciaO = models.ExistenciaBodega.objects.get(item = i.item,bodega = i.bodegaO)
            existenciaO.cantidad = existenciaO.cantidad - i.cantidad
            existenciaO.save()
            existenciaD = models.ExistenciaBodega.objects.get(item = i.item,bodega = i.bodegaD)
            existenciaD.cantidad = existenciaD.cantidad + i.cantidad
            existenciaD.save()
            l = models.Kardex.objects.create(
                sucursal = maestro.sucursal,
                bodega = i.bodegaO,
                item = models.N4Item.objects.get(pk = i.item.id_n4), 
                referencia = cod,
                entrada = 0,
                salida = i.cantidad,
                debe = 0,
                haber = i.costo,
                existencia = item_cost.existencia,
                tipotransaccion = 'ST',
                bodega_fin = i.bodegaD
            )
            j = models.Kardex.objects.create(
                sucursal = maestro.sucursal,
                bodega = i.bodegaD,
                item = models.N4Item.objects.get(pk = i.item.id_n4),
                referencia = cod,
                entrada = i.cantidad,
                salida = 0,
                debe = i.costo,
                haber = 0,
                existencia = item_cost.existencia,
                tipotransaccion = 'ET'
            )


        #borramos el temporal porque el item ya se grabo
        detallestemp.delete()
        #cambiamos el estado del traslado a en espera
        maestro.estado = models.Estado.objects.get(pk=1)
        maestro.save()
        print(maestro.sucursalD.siglas)
        print(cod)
    #volvemos a la lista de los documentos del dia
    return redirect('LocalesListar')


# ---------------------------------------------------------------------
#          AJUSTES
# ---------------------------------------------------------------------

@login_required
def AjusteMsr_Busqueda(request):
    reino(request)
    data = dict()
    if request.method == 'POST':
        form = forms.BusquedaForm(request.POST)
        if form.is_valid():
            data['form'] = form
            ajustebuscado = models.AjusteMsr.objects.filter(referencia=form.cleaned_data['busqueda'])
            data['ajustebuscado'] = ajustebuscado
            data['suc']= LoggedInUser.objects.get(user=request.user)
    else:
            form = forms.BusquedaForm()
            data['ajustebuscado'] = []
            data['form'] = form
            data['suc']= LoggedInUser.objects.get(user=request.user)
    return render(request,'inv/invAjusteMsr/Busqueda.html',data)

@login_required
def AjusteMsr_list(request):
    reino(request)
    data = dict()
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    if request.method=='POST':
        form = forms.BusquedafechasForm(request.POST)
        if form.is_valid():
            data['form'] = form
            busqueda= form.cleaned_data['busqueda']
            fecha_ini = datetime.strptime(form.cleaned_data['fecha_inicio'],'%Y-%m-%d')
            fecha_fin = datetime.strptime(form.cleaned_data['fecha_fin'],'%Y-%m-%d')+ timedelta(days=1)
            if busqueda == 'TRUE':
                data['fecha_inicio'] = form.cleaned_data['fecha_inicio']
                data['fecha_fin'] = form.cleaned_data['fecha_fin']
                data['ajustemsr'] = models.AjusteMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=fecha_ini,fecha__lte=fecha_fin).filter(Q(referencia__icontains = 'SA' )|Q( referencia__icontains='EA')).order_by('-fecha')
            else:
                data['fecha_inicio'] = form.cleaned_data['fecha_inicio']
                data['fecha_fin'] = form.cleaned_data['fecha_fin']
                select =form.cleaned_data['rangos_especificos']
                if select=='1':#seleccioname los del dia
                    data['ajustemsr'] = models.AjusteMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=date.today()).filter(Q(referencia__icontains = 'SA' )|Q( referencia__icontains='EA')).order_by('-fecha')
                if select == '2': #seleccioname los de la semana
                    data['ajustemsr'] = models.AjusteMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__week=datetime.today().isocalendar()[1],fecha__year__gte=date.today().year).filter(Q(referencia__icontains = 'SA' )|Q( referencia__icontains='EA')).order_by('-fecha')
                if select == '3': #seleccioname los del mes
                    data['ajustemsr'] = models.AjusteMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__month=date.today().month,fecha__year=date.today().year).filter(Q(referencia__icontains = 'SA' )|Q( referencia__icontains='EA')).order_by('-fecha')
    else:
        data['form']=forms.BusquedafechasForm()
        data['ajustemsr']= models.AjusteMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=date.today()).filter(Q(referencia__icontains = 'SA' )|Q( referencia__icontains='EA')).order_by('-fecha').order_by('referencia')    
        data['fecha_inicio'] = date.today().strftime("%Y-%m-%d")
        data['fecha_fin'] = date.today().strftime("%Y-%m-%d")            
    return render(request,'inv/invAjusteMsr/AjusteMsr_List.html',data)

@login_required
def AjusteMsr_save_all(request,form,template_name):
    reino(request)
    data = dict()
    suc = LoggedInUser.objects.get(user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            ajustemsr = models.AjusteMsr.objects.filter(sucursal= suc.sucursal,fecha__gte=date.today()).filter(Q(referencia__icontains = 'SA' )|Q( referencia__icontains='EA')).order_by('-fecha')
            data['Pantalla_List']= render_to_string('inv/invAjusteMsr/AjusteMsr_List_Details.html',{'ajustemsr':ajustemsr})
        else:
            print(form.errors)
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def AjusteMsr_Create(request):
    reino(request)
    if request.method=='POST':
        #copiamos el post para poder modificar sus valores
        post = request.POST.copy()
        today= date.today().strftime('%Y%m%d')
        suc = LoggedInUser.objects.get(user=request.user)
        post['sucursal'] = suc.sucursal.siglas
        #con este if modificamos el tipo de consecutivo
        if post['ajuste']=='1':#ajuste de Salida
            numero = models.AjusteMsr.objects.filter(referencia__contains=today,sucursal=suc.sucursal).filter(Q(referencia__icontains = 'SA' )|Q( referencia__icontains='EA')).filter(referencia__contains='SA')
            if numero.count()==0:
                consecutivo='00001'
            else:
                consecutivo='{:0>5}'.format(numero.count()+1)
            post['referencia']=suc.sucursal.siglas+'-SA-'+today+'-'+consecutivo
        elif post['ajuste']=='2':#ajuste de entrada
            numero = models.AjusteMsr.objects.filter(referencia__contains=today,sucursal=suc.sucursal).filter(Q(referencia__icontains = 'SA' )|Q( referencia__icontains='EA')).filter(referencia__contains='EA')
            if numero.count()==0:
                consecutivo='00001'
            else:
                consecutivo='{:0>5}'.format(numero.count()+1)
            post['referencia']=suc.sucursal.siglas+'-EA-'+today+'-'+consecutivo        
        form = forms.AjusteMsrForm(post,request.FILES)
    else:
        form = forms.AjusteMsrForm()
    return AjusteMsr_save_all(request,form,'inv/invAjusteMsr/modal_create.html')

@login_required
def AjusteMsr_Editar(request,cod):
    reino(request)
    ajustemsr = get_object_or_404(models.AjusteMsr,referencia=cod)
    if request.method=='POST':
        form = forms.AjusteMsrForm(request.POST,request.FILES,instance=ajustemsr)
    else:
        form = forms.AjusteMsrForm(instance=ajustemsr)
    return AjusteMsr_save_all(request,form,'inv/invAjusteMsr/modal_update.html')

@login_required
def AjusteMaestroDetalle(request,cod):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    msr = models.AjusteMsr.objects.get(referencia=cod)
    detform = forms.make_ajuste_det_form(suc.sucursal.siglas)
    det = inlineformset_factory(models.AjusteMsr,models.AjusteDettemp,form=detform,extra=1)
    lineas = models.AjusteDet.objects.filter(referencia=cod)
    if msr.ajuste.tipo_mov == 'S':
        # print('salida')
        salida = True
    else:
        # print('entrada')
        salida = False
    if request.method == 'POST':
        formset = det(request.POST,instance=msr)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data != {}:
                    if form.cleaned_data.get('bodega',False) and form.cleaned_data.get('item',False):
                        if form.cleaned_data['DELETE']:
                            if form.cleaned_data['id'] != None:
                                linea = models.AjusteDettemp.objects.get(id =form.cleaned_data['id'].id)
                                linea.delete()
                        else:
                            if form.is_valid():
                                
                                decimales = form.cleaned_data['cantidad']
                                item = form.cleaned_data['item']
                                if item.producto.entero == 'S':
                                    print(decimales)
                                    if float(decimales)-float(int(decimales)) > float(0):
                                        messages.warning(request,'No se puede efectuar operacion, el item : "%s" pertenece a un producto cuyos movimientos son enteros, no decimales'%(
                                            form.cleaned_data['item']
                                            )
                                        )
                                        return redirect('AjusteMaestroDetalle',cod=msr.referencia)


                                if salida:#solo si es de salida validamos su exisencia
                                    existencia = models.ExistenciaBodega.objects.get(item = form.cleaned_data['item'],bodega = form.cleaned_data['bodega'])
                                    final = existencia.cantidad - form.cleaned_data['cantidad']
                                    if final < 0:
                                        messages.warning(request,'No se puede efectuar la operacion, las existencias quedan en negativo, del item: "%s" en la bodega: "%s", existencias actuales: "%s"'%(
                                            form.cleaned_data['item'],
                                            form.cleaned_data['bodega'],
                                            existencia.cantidad
                                            )
                                        )
                                        return redirect('AjusteMaestroDetalle',cod=msr.referencia)
                                    form.save()
            return redirect('AjusteMaestroDetalle',cod=msr.referencia)
        else:
            print(formset.errors)
            messages.warning(request,formset.errors)
    formset = det(instance=msr)
    return render(request,'inv/invAjusteMsr/MaestroDetalle.html',{'formset':formset,'Ajuste':msr,'suc':suc,'lineas':lineas})

@login_required
def AjusteImpreso(request,cod):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    ajustemsr = models.AjusteMsr.objects.get(referencia=cod)
    ajustedet= models.AjusteDet.objects.filter(referencia=cod)
    
    if ajustemsr.estado.id == 4:
        ajustedet= models.AjusteDettemp.objects.filter(referencia=cod)
    else:
        ajustedet= models.AjusteDet.objects.filter(referencia=cod)

    if(ajustedet.count()!=0):
        return render(request,'inv/invAjusteMsr/AjusteImpresion.html',{'suc':suc,'msr':ajustemsr,'det':ajustedet})
    else:
        return render(request,'inv/invAjusteMsr/AjusteNoDetalle.html',{'suc':suc,'msr':ajustemsr})

@login_required
def AjusteFinalizar(request,cod):
    
    #para poder retornar a la lista de las devoluciones
    reino(request)
    data = dict()
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    suc = LoggedInUser.objects.get(user = request.user)
    data['form']=forms.BusquedafechasForm()
    data['ajustemsr']= models.AjusteMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=date.today()).filter(Q(referencia__icontains = 'SA' )|Q( referencia__icontains='EA')).order_by('-fecha')    
    data['fecha_inicio'] = date.today().strftime("%Y-%m-%d")
    data['fecha_fin'] = date.today().strftime("%Y-%m-%d") 
    
    #comenzamos por obtener la cabecera y el detalle que vamos a grabar
    maestro = models.AjusteMsr.objects.get(pk=cod)
    detallestemp = models.AjusteDettemp.objects.filter(referencia = cod)

    if detallestemp.count() == 0:
        messages.warning(request,'No se puede finalizar el ajuste sin antes ingresar al menos una linea en su detalle')
        return redirect('AjusteMaestroDetalle',cod= maestro.referencia)


    if maestro.ajuste.tipo_mov == 'S':
        salida = True
    else:
        salida = False
    #validar que las existencias no queden en negativo
    if  salida:
        puede_grabar = False
    else:
        puede_grabar = True
    
    # verificando que ninguno de los ajustes de salida deje en negativo las existencias
    if salida:
        for i in detallestemp:
            existencia = models.ExistenciaBodega.objects.get(item = i.item, bodega = i.bodega)
            final = existencia.cantidad - i.cantidad
            if final < 0:
                puede_grabar = False
                messages.warning('no se puede efectuar operacion, las existencias quedan negativas, del item: "%s", en la bodega: "%s", sus existencias actuales: "%s"'%(
                    i.item,
                    i.bodega,
                    existencia.cantidad
                    )
                )
                return redirect('AjusteMaestroDetalle',cod = cod)
        puede_grabar = True
    print(puede_grabar)
    if puede_grabar:
        #Ajuste sin costo trayendo el costo de la tabla item_costo
        for i in  detallestemp:
            existencia = models.ExistenciaBodega.objects.get(item = i.item.id_n4, bodega = i.bodega.id_bodega)
            item_cost  = models.item_costo.objects.get(item = i.item.id_n4)
            costo_total = float(i.cantidad)*float(item_cost.costo)
            a= models.AjusteDet.objects.create(
                referencia   = maestro,
                bodega       = models.Bodega.objects.get(pk = i.bodega.id_bodega),
                item         = models.N4Item.objects.get(pk = i.item.id_n4),
                cantidad     = i.cantidad,
                costo        = costo_total,
                fecha_venc   = i.fecha_venc if i.fecha_venc else '.'
            )
            if salida:
                existencia.cantidad = existencia.cantidad - i.cantidad
                existencia.save()

                exsucursal = models.ExistenciaBodega.objects.filter(bodega__sucursal =suc.sucursal, item = i.item).aggregate(Sum('cantidad'))
                exglobal = models.ExistenciaBodega.objects.filter(item = i.item).aggregate(Sum('cantidad'))

                k = models.Kardex.objects.create(
                    sucursal = suc.sucursal,
                    bodega = i.bodega,
                    item = models.N4Item.objects.get(pk = i.item.id_n4),
                    referencia = cod,
                    salida = i.cantidad,
                    haber = costo_total,
                    tipotransaccion = 'SA',
                    existenciabod = existencia.cantidad,
                    existenciasuc = exsucursal['cantidad__sum'],
                    existencia = exglobal['cantidad__sum']
                )

                #restamos su vencimiento
                cantidad = i.cantidad
                while cantidad > 0:
                    vencimiento = models.N4ItemVencimiento.objects.filter(item =models.N4Item.objects.get(pk=i.item.id_n4)).exclude(cantidad = 0).order_by('fecha_venc').first()
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

            else:
                existencia.cantidad = existencia.cantidad + i.cantidad
                existencia.save()

                exsucursal = models.ExistenciaBodega.objects.filter(bodega__sucursal =suc.sucursal, item = i.item).aggregate(Sum('cantidad'))
                exglobal = models.ExistenciaBodega.objects.filter(item = i.item).aggregate(Sum('cantidad'))
                k = models.Kardex.objects.create(
                    sucursal = suc.sucursal,
                    bodega = i.bodega,
                    item = models.N4Item.objects.get(pk = i.item.id_n4),
                    referencia = cod,
                    entrada = i.cantidad,
                    debe = costo_total,
                    fecha_venc = datetime.strptime(i.fecha_venc,'%Y-%m-%d') if i.fecha_venc else date.today().strftime('%Y-%m-%d'),
                    tipotransaccion = 'EA',
                    existenciabod = existencia.cantidad,
                    existenciasuc = exsucursal['cantidad__sum'],
                    existencia = exglobal['cantidad__sum']
                )

                if i.fecha_venc:
                    #creamos o aumentamos la tupla en su registro de vencimiento
                    existevencimiento = models.N4ItemVencimiento.objects.filter(item = models.N4Item.objects.get(pk = i.item.id_n4),referencia = cod,fecha_venc = datetime.strptime(i.fecha_venc,'%Y-%m-%d') ).exists()

                    if i.fecha_venc:
                        if existevencimiento:
                            vencimiento = models.N4ItemVencimiento.objects.get(item = models.N4Item.objects.get(pk = i.item.id_n4),referencia = cod,fecha_venc = datetime.strptime(i.fecha_venc,'%Y-%m-%d'))
                            vencimiento.cantidad = vencimiento.cantidad + i.cantidad
                            vencimiento.fecha_cero ='.'
                            vencimiento.save()
                        else:
                            c = models.N4ItemVencimiento.objects.create(
                                referencia = cod,
                                item = models.N4Item.objects.get(pk = i.item.id_n4),
                                fecha_venc = datetime.strptime(i.fecha_venc,'%Y-%m-%d'),
                                cantidad = i.cantidad
                            )

        #borramos el temporal porque el item ya se grabo
        detallestemp.delete()
        #cambiamos el estado de la cabecera de la devolucions
        maestro.estado = models.Estado.objects.get(pk=1)
        maestro.save()

    #volvemos a la lista de los documentos del dia
    return redirect('AjusteMsr_Listar')

# ---------------------------------------------------------------------
#          AJUSTES CONTABLES
# ---------------------------------------------------------------------

@login_required
def AjusteCMsr_Busqueda(request):
    reino(request)
    data = dict()
    if request.method == 'POST':
        form = forms.BusquedaForm(request.POST)
        if form.is_valid():
            data['form'] = form
            ajustebuscado = models.AjusteMsr.objects.filter(referencia=form.cleaned_data['busqueda'])
            data['ajustebuscado'] = ajustebuscado
            data['suc']= LoggedInUser.objects.get(user=request.user)
    else:
            form = forms.BusquedaForm()
            data['ajustebuscado'] = []
            data['form'] = form
            data['suc']= LoggedInUser.objects.get(user=request.user)
    return render(request,'inv/invAjusteMsr/Busqueda.html',data)

@login_required
def AjusteCMsr_list(request):
    reino(request)
    data = dict()
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    if request.method=='POST':
        form = forms.BusquedafechasForm(request.POST)
        if form.is_valid():
            data['form'] = form
            busqueda= form.cleaned_data['busqueda']
            fecha_ini = datetime.strptime(form.cleaned_data['fecha_inicio'],'%Y-%m-%d')
            fecha_fin = datetime.strptime(form.cleaned_data['fecha_fin'],'%Y-%m-%d')+ timedelta(days=1)
            if busqueda == 'TRUE':
                data['fecha_inicio'] = form.cleaned_data['fecha_inicio']
                data['fecha_fin'] = form.cleaned_data['fecha_fin']
                data['ajustemsr'] = models.AjusteMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=fecha_ini,fecha__lte=fecha_fin).filter(Q(referencia__icontains = 'SC' )|Q( referencia__icontains='EC')).order_by('-fecha').order_by('referencia')
            else:
                data['fecha_inicio'] = form.cleaned_data['fecha_inicio']
                data['fecha_fin'] = form.cleaned_data['fecha_fin']
                select =form.cleaned_data['rangos_especificos']
                if select=='1': #seleccioname los del dia
                    data['ajustemsr'] = models.AjusteMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=date.today()).filter(Q(referencia__icontains = 'SC' )|Q( referencia__icontains='EC')).order_by('-fecha').order_by('referencia')
                if select == '2': #seleccioname los de la semana
                    data['ajustemsr'] = models.AjusteMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__week=datetime.today().isocalendar()[1],fecha__year__gte=date.today().year).filter(Q(referencia__icontains = 'SC' )|Q( referencia__icontains='EC')).order_by('-fecha').order_by('referencia')
                if select == '3': #seleccioname los del mes
                    data['ajustemsr'] = models.AjusteMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__month=date.today().month,fecha__year=date.today().year).filter(Q(referencia__icontains = 'SC' )|Q( referencia__icontains='EC')).order_by('-fecha').order_by('referencia')
    else:
        data['form']=forms.BusquedafechasForm()
        data['ajustemsr']= models.AjusteMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=date.today()).filter(Q(referencia__icontains = 'SC' )|Q( referencia__icontains='EC')).order_by('-fecha').order_by('referencia')
        data['fecha_inicio'] = date.today().strftime("%Y-%m-%d")
        data['fecha_fin'] = date.today().strftime("%Y-%m-%d")            
    return render(request,'inv/invAjusteMsr/AjusteCMsr_List.html',data)

@login_required
def AjusteCMsr_save_all(request,form,template_name):
    reino(request)
    data = dict()
    suc = LoggedInUser.objects.get(user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            ajustemsr = models.AjusteMsr.objects.filter(sucursal= suc.sucursal,fecha__gte=date.today()).filter(Q(referencia__icontains = 'SC' )|Q( referencia__icontains='EC')).order_by('-fecha')
            data['Pantalla_List']= render_to_string('inv/invAjusteMsr/AjusteCMsr_List_Details.html',{'ajustemsr':ajustemsr})
        else:
            print(form.errors)
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name,{'form':form},request=request,)
    return JsonResponse(data)

@login_required
def AjusteCMsr_Create(request):
    reino(request)
    if request.method=='POST':
        #copiamos el post para poder modificar sus valores
        post = request.POST.copy()
        today= date.today().strftime('%Y%m%d')
        suc = LoggedInUser.objects.get(user=request.user)
        post['sucursal'] = suc.sucursal.siglas
        #con este if modificamos el tipo de consecutivo
        if post['ajuste']=='1':#ajuste de Salida
            numero = models.AjusteMsr.objects.filter(referencia__contains=today,sucursal=suc.sucursal).filter(Q(referencia__icontains = 'SC' )|Q( referencia__icontains='EC')).filter(referencia__contains='SC')
            if numero.count()==0:
                consecutivo='00001'
            else:
                consecutivo='{:0>5}'.format(numero.count()+1)
            post['referencia']=suc.sucursal.siglas+'-SC-'+today+'-'+consecutivo
        elif post['ajuste']=='2':#ajuste de entrada
            numero = models.AjusteMsr.objects.filter(referencia__contains=today,sucursal=suc.sucursal).filter(Q(referencia__icontains = 'SC' )|Q( referencia__icontains='EC')).filter(referencia__contains='EC')
            if numero.count()==0:
                consecutivo='00001'
            else:
                consecutivo='{:0>5}'.format(numero.count()+1)
            post['referencia']=suc.sucursal.siglas+'-EC-'+today+'-'+consecutivo           
        form = forms.AjusteMsrForm(post,request.FILES)
    else:
        form = forms.AjusteMsrForm()
    return AjusteCMsr_save_all(request,form,'inv/invAjusteMsr/Cmodal_create.html')

@login_required
def AjusteCMsr_Editar(request,cod):
    reino(request)
    ajustemsr = get_object_or_404(models.AjusteMsr,referencia=cod)
    if request.method=='POST':
        form = forms.AjusteMsrForm(request.POST,request.FILES,instance=ajustemsr)
    else:
        form = forms.AjusteMsrForm(instance=ajustemsr)
    return AjusteCMsr_save_all(request,form,'inv/invAjusteMsr/Cmodal_update.html')

@login_required
def AjusteCMaestroDetalle(request,cod):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    msr = models.AjusteMsr.objects.get(referencia=cod)
    detform = forms.make_ajuste_det_form(suc.sucursal.siglas)
    det = inlineformset_factory(models.AjusteMsr,models.AjusteDettemp,form=detform,extra=1)
    lineas = models.AjusteDet.objects.filter(referencia=cod)
    if msr.ajuste.tipo_mov == 'S':
        # print('Salida')
        salida = True
    else:
        # print('Entrada')
        salida = False
    if request.method == 'POST':
        formset = det(request.POST,instance=msr)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data != {}:
                    if form.cleaned_data.get('bodega',False) and form.cleaned_data.get('item',False):
                        if form.cleaned_data['DELETE']:
                            if form.cleaned_data['id'] != None:
                                linea = models.AjusteDettemp.objects.get(id = form.cleaned_data['id'].id)
                                linea.delete()
                        else:
                            if form.is_valid():

                                decimales = form.cleaned_data['cantidad']
                                item = form.cleaned_data['item']
                                if item.producto.entero == 'S':
                                    print(decimales)
                                    if float(decimales)-float(int(decimales)) > float(0):
                                        messages.warning(request,'No se puede efectuar operacion, el item : "%s" pertenece a un producto cuyos movimientos son enteros, no decimales'%(
                                            form.cleaned_data['item']
                                            )
                                        )
                                        return redirect('AjusteCMaestroDetalle',cod=msr.referencia)

                                if salida:
                                    #solo si es de salida validamos su exisencia
                                    existencia = models.ExistenciaBodega.objects.get(item = form.cleaned_data['item'],bodega = form.cleaned_data['bodega'])
                                    final = existencia.cantidad - form.cleaned_data['cantidad']
                                    if final < 0 :
                                                messages.warning(request,'No se puede efectuar la operacion, las existencias quedan en negativo, del item: "%s" en la bodega: "%s", existencias actuales: "%s"'%(
                                                    form.cleaned_data['item'],
                                                    form.cleaned_data['bodega'],
                                                    existencia.cantidad
                                                    )
                                                )
                                                return redirect('AjusteCMaestroDetalle',cod=msr.referencia)

                                if form.cleaned_data['costo'] == None:
                                            messages.warning(request,'No se puede efectuar la operacion, el costo debe tener una valor, del item: "%s" en la bodega: "%s"'%(
                                                form.cleaned_data['item'],
                                                form.cleaned_data['bodega']
                                                )
                                            )
                                            return redirect('AjusteCMaestroDetalle',cod=msr.referencia)
                                form.save()
            return redirect('AjusteCMaestroDetalle',cod=msr.referencia)
        else:
            print(formset.errors)
            messages.warning(request,formset.errors)
    formset = det(instance=msr)
    return render(request,'inv/invAjusteMsr/CMaestroDetalle.html',{'formset':formset,'Ajuste':msr,'suc':suc,'lineas':lineas})

@login_required
def AjusteCImpreso(request,cod):
    reino(request)
    suc = LoggedInUser.objects.get(user=request.user)
    ajustemsr = models.AjusteMsr.objects.get(referencia=cod)
    ajustedet= models.AjusteDet.objects.filter(referencia=cod)
    
    if ajustemsr.estado.id == 4:
        ajustedet= models.AjusteDettemp.objects.filter(referencia=cod)
    else:
        ajustedet= models.AjusteDet.objects.filter(referencia=cod)

    if(ajustedet.count()!=0):
        return render(request,'inv/invAjusteMsr/AjusteImpresion.html',{'suc':suc,'msr':ajustemsr,'det':ajustedet})
    else:
        return render(request,'inv/invAjusteMsr/AjusteNoDetalle.html',{'suc':suc,'msr':ajustemsr})

@login_required
def AjusteCFinalizar(request,cod):

    #para poder retornar a la lista de las devoluciones
    reino(request)
    data = dict()
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    suc = LoggedInUser.objects.get(user = request.user)
    data['form']=forms.BusquedafechasForm()
    data['ajustemsr']= models.AjusteMsr.objects.filter(sucursal=data['suc'].sucursal,fecha__gte=date.today()).filter(Q(referencia__icontains = 'SC' )|Q( referencia__icontains='EC')).order_by('-fecha')    
    data['fecha_inicio'] = date.today().strftime("%Y-%m-%d")
    data['fecha_fin'] = date.today().strftime("%Y-%m-%d") 

    #comenzamos por obtener la cabecera y el detalle que vamos a grabar
    maestro = models.AjusteMsr.objects.get(pk=cod)
    detallestemp = models.AjusteDettemp.objects.filter(referencia = cod)

    
    if detallestemp.count() == 0:
        messages.warning(request,'No se puede finalizar el ajuste de costo sin antes ingresar al menos una linea en su detalle')
        return redirect('AjusteCMaestroDetalle',cod= maestro.referencia)



    #verificamos el tipo de ajuste con el que estamos tratando
    if maestro.ajuste.tipo_mov == 'S':
        salida = True
    else:
        salida = False
    # para validar que las existencias no queden en negativo
    if salida:
        puede_grabar = False
    else:
        puede_grabar = True
    # Verificando que ninguno de los ajustes de salida deje en negativo las existencias
    if salida:
        for i in detallestemp:
            existencia = models.ExistenciaBodega.objects.get(item = i.item, bodega = i.bodega)
            final = existencia.cantidad - i.cantidad
            if final < 0:
                puede_grabar = False
                messages.warning(request,'no se puede efectuar operacion, las existencias quedan negativas, del item: "%s", en la bodega: "%s", sus existencias actuales: "%s"'%(
                    i.item,
                    i.bodega,
                    existencia.cantidad
                    )
                )
                return redirect('AjusteCMaestroDetalle',cod)
        puede_grabar = True
    if puede_grabar:
        # Ajuste contable se debe respetar el costo que dice la contabilidad
        for i in  detallestemp:
            existencia = models.ExistenciaBodega.objects.get(item = i.item.id_n4, bodega = i.bodega.id_bodega)
            a = models.AjusteDet.objects.create(
                referencia   = models.AjusteMsr.objects.get(referencia=cod),
                bodega       = models.Bodega.objects.get(pk = i.bodega.id_bodega),
                item         = models.N4Item.objects.get(pk = i.item.id_n4),
                cantidad     = i.cantidad,
                costo        = i.costo
            )
            if salida:
                existencia.cantidad = existencia.cantidad - i.cantidad
                existencia.save()

                exsucursal = models.ExistenciaBodega.objects.filter(bodega__sucursal =suc.sucursal, item = i.item).aggregate(Sum('cantidad'))
                exglobal = models.ExistenciaBodega.objects.filter(item = i.item).aggregate(Sum('cantidad'))
                k = models.Kardex.objects.create(
                    sucursal = suc.sucursal,
                    bodega = i.bodega,
                    item = models.N4Item.objects.get(pk = i.item.id_n4),
                    referencia = cod,
                    salida = i.cantidad,
                    haber = i.costo,
                    tipotransaccion = 'SC',
                    existenciabod = existencia.cantidad,
                    existenciasuc = exsucursal['cantidad__sum'],
                    existencia = exglobal['cantidad__sum']
                )
                #restamos su vencimiento
                cantidad = i.cantidad
                while cantidad > 0:
                    vencimiento = models.N4ItemVencimiento.objects.filter(item =models.N4Item.objects.get(pk=i.item.id_n4)).exclude(cantidad = 0).order_by('fecha_venc').first()
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
            else:
                existencia.cantidad = existencia.cantidad + i.cantidad
                existencia.save()
                exsucursal = models.ExistenciaBodega.objects.filter(bodega__sucursal =suc.sucursal, item = i.item).aggregate(Sum('cantidad'))
                exglobal = models.ExistenciaBodega.objects.filter(item = i.item).aggregate(Sum('cantidad'))
                k = models.Kardex.objects.create(
                    sucursal = suc.sucursal,
                    bodega = i.bodega,
                    item = models.N4Item.objects.get(pk = i.item.id_n4),
                    referencia = cod,
                    entrada = i.cantidad,
                    debe = i.costo,
                    fecha_venc = datetime.strptime(i.fecha_venc,'%Y-%m-%d') if i.fecha_venc else date.today().strftime('%Y-%m-%d'),
                    tipotransaccion = 'EC',
                    existenciabod = existencia.cantidad,
                    existenciasuc = exsucursal['cantidad__sum'],
                    existencia = exglobal['cantidad__sum']
                )

                if i.fecha_venc:
                    #creamos o aumentamos la tupla en su registro de vencimiento
                    existevencimiento = models.N4ItemVencimiento.objects.filter(item = models.N4Item.objects.get(pk = i.item.id_n4),referencia = cod,fecha_venc = datetime.strptime(i.fecha_venc,'%Y-%m-%d') ).exists()

                    if existevencimiento:
                        vencimiento = models.N4ItemVencimiento.objects.get(item = models.N4Item.objects.get(pk = i.item.id_n4),referencia = cod,fecha_venc = datetime.strptime(i.fecha_venc,'%Y-%m-%d'))
                        vencimiento.cantidad = vencimiento.cantidad + i.cantidad
                        vencimiento.fecha_cero ='.'
                        vencimiento.save()
                    else:
                        c = models.N4ItemVencimiento.objects.create(
                            referencia = cod,
                            item = models.N4Item.objects.get(pk = i.item.id_n4),
                            fecha_venc = datetime.strptime(i.fecha_venc,'%Y-%m-%d'),
                            cantidad = i.cantidad
                        )


        #borramos el temporal porque el item ya se grabo
        detallestemp.delete()
        #cambiamos el estado de la cabecera de la devolucions
        maestro.estado = models.Estado.objects.get(pk=1)
        maestro.save()
    #volvemos a la lista de los documentos del dia
    return redirect('AjusteMsrC_Listar')

# ---------------------------------------------------------------------
#          AJUSTES CONTABLES
# ---------------------------------------------------------------------
@login_required
def Vencidos_inicial(request):
    reino(request)
    data= dict()
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    if request.method=='POST':
        form = forms.BusquedafechasForm(request.POST)
        if form.is_valid():
            data['form'] = form
            busqueda= form.cleaned_data['busqueda']
            fecha_ini = datetime.strptime(form.cleaned_data['fecha_inicio'],'%Y-%m-%d')
            fecha_fin = datetime.strptime(form.cleaned_data['fecha_fin'],'%Y-%m-%d')+ timedelta(days=1)
            if busqueda == 'TRUE':
                data['fecha_inicio'] = form.cleaned_data['fecha_inicio']
                data['fecha_fin'] = form.cleaned_data['fecha_fin']
                data['vencidos'] = models.N4ItemVencimiento.objects.filter(fecha_venc__gte=fecha_ini,fecha_venc__lte=fecha_fin).order_by('-fecha_venc').order_by('referencia')
            else:
                data['fecha_inicio'] = form.cleaned_data['fecha_inicio']
                data['fecha_fin'] = form.cleaned_data['fecha_fin']
                select =form.cleaned_data['rangos_especificos']
                if select=='1': #seleccioname los del dia
                    data['vencidos'] = models.N4ItemVencimiento.objects.filter(fecha_venc=date.today()).order_by('-fecha_venc').order_by('referencia')
                if select == '2': #seleccioname los de la semana
                    data['vencidos'] = models.N4ItemVencimiento.objects.filter(fecha_venc__week=datetime.today().isocalendar()[1],fecha_venc__year__gte=date.today().year).order_by('-fecha_venc').order_by('referencia')
                if select == '3': #seleccioname los del mes
                    data['vencidos'] = models.N4ItemVencimiento.objects.filter(fecha_venc__month=date.today().month,fecha_venc__year=date.today().year).order_by('-fecha_venc').order_by('referencia')
    else:
        data['form']=forms.BusquedafechasForm()
        data['vencidos']= models.N4ItemVencimiento.objects.filter(fecha_venc=date.today()).order_by('-fecha_venc').order_by('referencia')
        data['fecha_inicio'] = date.today().strftime("%Y-%m-%d")
        data['fecha_fin'] = date.today().strftime("%Y-%m-%d")          
    return render(request,'inv/invN4Item/ListarVencidos.html',data)

