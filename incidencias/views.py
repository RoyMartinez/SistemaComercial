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
from . import models, forms, funciones
from vta.apoyo import reino
from usuarios.models import LoggedInUser
from django.db.models import Q,Sum,Min
from django.db import transaction
from django.contrib import messages 
from django.core.exceptions import PermissionDenied

# indice del app de reportes
@login_required
def index(request):
    reino(request)
    data = {}
    data['suc'] = LoggedInUser.objects.get(user=request.user)
    return render(request,'incidencias/incidenciasBase.html',data)

#mostrar los distintos reportes que tenemos
@login_required
def reporte(request):
    reino(request)
    data = {}
    data['suc']:LoggedInUser.objects.get(user=request.user)
    data['informes'] = models.catInforme.objects.all()
    return render(request,'incidencias/reporte/opcion.html',data)

#crear un nuevo reporte
@login_required
def reporte_new(request,cod):
    reino(request)
    data = {}
    data['suc']=LoggedInUser.objects.get(user=request.user)
    data['informe'] = models.catInforme.objects.get(pk = cod)
    data['seccion'] = models.catSeccion.objects.filter(informe = cod)
    if request.method=='POST':
        #copiamos el post para poder modificar sus valores
        post = request.POST.copy()
        post['referencia'] = funciones.consecutivo_informe(data['suc'])
        form = forms.documentoMsrForm(post)
        if form.is_valid():            
            messages.warning(request,'informe listo en la creacion referencia: '+post['referencia'])
            return redirect('inc_reporte')
        else:
            print(form.errors)
        data['form'] = forms.documentoMsrForm()
    else:
        data['form'] = forms.documentoMsrForm()

    return render(request,'incidencias/reporte/nuevo.html',data)




#listar todos los reportes de un tipo
@login_required
def reporte_list(request,cod):
    reino(request)
    data = {}
    data['suc']:LoggedInUser.objects.get(user=request.user)
    data['informes'] = models.catInforme.objects.all()
    return render(request,'incidencias/reporte/lista.html',data)

