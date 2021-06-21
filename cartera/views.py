import datetime
from bootstrap_modal_forms.generic import BSModalReadView, BSModalCreateView, BSModalDeleteView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Min, Max, Sum
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from vta.models import Cliente as venta_cliente, ClienteTelefono, ClienteDireccion, Vendedores
from vta.forms import Form_cliente, Form_cliente_direccion, Form_cliente_telefono
from vta.apoyo import reino
from . import forms as formulario, models as tablac

@login_required
def principal(request):
    reino(request)
    return render(request, 'cartera/cartera_index.html', {})

@login_required
def recibos(request):
    reino(request)
    cliente=venta_cliente.objects.exclude(tipo='C').order_by('nombres')
    limite=saldo=0
    cuenta=customer=None
    hoy=datetime.date.today()
    fecha1=fecha2=hoy.strftime("%Y-%m-%d")
    if request.method=='POST':
        form = formulario.FormRoc(request.POST)
        if form.is_valid():
            c = form.cleaned_data['cliente']
            cantidad = float(form.cleaned_data['cantidad'])
            concepto = form.cleaned_data['concepto']
            cuenta= tablac.EstadoCuenta.objects.filter(cliente=c).order_by('-pk')
            customer=cliente.get(pk=c.pk)
            if 'btn_buscar' in request.POST:
                limite=customer.limite_credito
                saldo=customer.saldo
                if cuenta:
                    x1=cuenta.aggregate(Min('fecha'))
                    x2=cuenta.aggregate(Max('fecha'))
                    fecha1=x1['fecha__min'].strftime("%Y-%m-%d")
                    fecha2=x2['fecha__max'].strftime("%Y-%m-%d")               
            elif 'btn_grabar' in request.POST:
                if cantidad == 0 or concepto=='':
                    messages.warning(request,'Revise que la cantidad sea mayor que cero o el concepto no este vacio')
                else:
                    numero = tablac.Roc.objects.filter(tipo=form.cleaned_data['tipo']).count() + 1
                    numero = form.cleaned_data['tipo'] + '-'  +  '{:0>3}'.format(numero)
                    debe=haber=0
                    roc = tablac.Roc.objects.create(numero=numero, tipo=form.cleaned_data['tipo'],
                        cliente=c, cantidad=cantidad, concepto=concepto, 
                        vendedor=Vendedores.objects.get(pk=request.user.id))
                    ecuenta = cuenta.aggregate(sdebe = Sum('debe'), shaber=Sum('haber'))
                    debito = float(ecuenta['sdebe']) if ecuenta['sdebe'] else 0
                    credito = float(ecuenta['shaber']) if ecuenta['shaber'] else 0
                    limite = float(customer.limite_credito)
                    if roc.tipo == 'NC':
                        haber=roc.cantidad
                        saldo = float(limite) + debito - credito - float(roc.cantidad)
                    else:
                        debe=roc.cantidad
                        saldo = float(limite) + debito - credito + float(roc.cantidad)
                    tablac.EstadoCuenta.objects.create(cliente=c, referencia=roc.pk, 
                        descripcion='roc.concepto',debe=debe, haber=haber, saldo=saldo)
                    customer.saldo=saldo
                    customer.save()
                    messages.success(request,'Recibo aplicado')
                    return HttpResponseRedirect(reverse('cartera_recibos'))
            elif 'btn_filtrar' in request.POST:
                a=form.cleaned_data['inicio']
                b=form.cleaned_data['fin']
                if a <= b:
                    cuenta=cuenta.filter(fecha__range=(a,b))
                    fecha1=a.strftime("%Y-%m-%d")
                    fecha2=b.strftime("%Y-%m-%d")
                else: 
                    messages.warning(request,'La fecha final no puede ser inferior a la fecha de inicio')
            else:
               pass
    else:
        form = formulario.FormRoc()
    return render(request, 'cartera/roc.html', {'cliente':cliente, 'form':form, 'cuenta':cuenta,
        'limite':limite, 'saldo':saldo, 'c':customer, 'fecha1':fecha1, 'fecha2':fecha2 })