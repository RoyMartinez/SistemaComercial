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

@login_required
def consecutivo_informe(suc):
    today = date.today().strftime('%Y%m%d')
    numero = models.documentoMsr.objects.filter(referencia__contains=today)
    if numero.count()==0:
        consecutivo = '001'
    else:
        consecutivo = '{:0>3}'.format(numero.count()+1)
    referencia =suc.sucursal.siglas+'-'+today+'-'+consecutivo
    return referencia