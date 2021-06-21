import csv, io, datetime
from . import forms, models, conecciones
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q, Sum, ExpressionWrapper, F, FloatField
from django.forms import ModelForm, Form, modelformset_factory, inlineformset_factory
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse

# Create your views here.

@login_required
def inicio(request):
    data =  dict()
    data["titulo"] = "Inicio"
    return render(request,'aprobaciones/shared/Inicio.html',data)

@login_required
def oc_list(request):
    data =  dict()   
    data["titulo"] = "Orden de Compra"
    #data['compras'] = conecciones.OC_Buscar(request,'127.0.0.1','3306','root','','pruebas') 
    data['compras'] = conecciones.OC_Buscar(request,'192.168.10.12','3307','siscarcoop','ph5DrAr!ch','pruebas') 
    return render(request,'aprobaciones/oc/lista.html',data)    

@login_required
def oc_detalle(request,codigo):
    data = dict()
    #data['Maestro'] = conecciones.OC_Maestro(request,'127.0.0.1','3306','root','','pruebas',codigo)
    #data['Detalles'] = conecciones.OC_Detalle(request,'127.0.0.1','3306','root','','pruebas',codigo)
    data['Maestro'] = conecciones.OC_Maestro(request,'192.168.10.12','3307','siscarcoop','ph5DrAr!ch','pruebas',codigo)
    data['Detalles'] = conecciones.OC_Detalle(request,'192.168.10.12','3307','siscarcoop','ph5DrAr!ch','pruebas',codigo)
    return render(request,'aprobaciones/oc/detalle.html',data)    

@login_required
def oc_actualiza(request,codigo,estado):
    data = dict()
    #conecciones.OC_Actualizar(request,'127.0.0.1','3306','root','','pruebas',codigo,estado)
    conecciones.OC_Actualizar(request,'192.168.10.12','3307','siscarcoop','ph5DrAr!ch','pruebas',codigo,estado)
    return redirect('aprobaciones_oc_list')  

@login_required
def em_list(request):
    data =  dict()
    data["titulo"] = "Entrada Mercaderia"
    #data['entradas'] = conecciones.EM_Buscar(request,'127.0.0.1','3306','root','','pruebas')
    data['entradas'] = conecciones.EM_Buscar(request,'192.168.10.12','3307','siscarcoop','ph5DrAr!ch','pruebas')
    return render(request,'aprobaciones/em/lista.html',data)

@login_required
def em_detalle(request,codigo):
    data = dict()
    #data['Maestro'] = conecciones.EM_Maestro(request,'127.0.0.1','3306','root','','pruebas',codigo)
    #data['Detalles'] = conecciones.EM_Detalle(request,'127.0.0.1','3306','root','','pruebas',codigo)
    data['Maestro'] = conecciones.EM_Maestro(request,'192.168.10.12','3307','siscarcoop','ph5DrAr!ch','pruebas',codigo)
    data['Detalles'] = conecciones.EM_Detalle(request,'192.168.10.12','3307','siscarcoop','ph5DrAr!ch','pruebas',codigo)
    return render(request,'aprobaciones/em/detalle.html',data)    

@login_required
def em_actualiza(request,codigo,estado):
    data = dict()
    #conecciones.EM_Actualizar(request,'127.0.0.1','3306','root','','pruebas',codigo,estado)
    conecciones.EM_Actualizar(request,'192.168.10.12','3307','siscarcoop','ph5DrAr!ch','pruebas',codigo,estado)
    return redirect('aprobaciones_em_list')  

@login_required
def reporte_ventas(request):
    data =  dict()
    data['referencia'] = 'EM-20201231-00001'
    return render(request,'aprobaciones/reporteventas/lista.html',data)
