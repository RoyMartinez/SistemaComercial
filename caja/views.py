import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponse
from . import models as tabla, forms as formulario
from usuarios.models import LoggedInUser
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from panel.views import list_tc, list_movimiento

@login_required
def principal(request):
    return render(request, 'caja/cajabase.html', {'suc':LoggedInUser.objects.get(user=request.user)})

# ---------------------------------------------------------------------
#          VENTANA TIPO DE CAMBIO
# ---------------------------------------------------------------------
@login_required
def tipocambio(request):
    tc = tabla.TipoCambio.objects.all()
    return render(request, 'caja/tipocambio.html', {'tc':tc, 'suc':LoggedInUser.objects.get(user=request.user)})

class NuevoCambio(BSModalCreateView):
    template_name = 'caja/nuevotc.html'
    form_class = formulario.FormTipoCambio
    success_message = 'Se ha insertado un nuevo registro'
    success_url = reverse_lazy(list_tc)

class EditarCambio(BSModalUpdateView):
    model = tabla.TipoCambio
    template_name = 'caja/edit_tc.html'
    form_class = formulario.FormTipoCambio
    success_message = 'Registros actualizados'
    success_url = reverse_lazy(tipocambio)

# ---------------------------------------------------------------------
#          VENTANA CAJAS
# ---------------------------------------------------------------------
@login_required
def listar_caja(request):
    return render(request, 'caja/cajas.html', {
        'caja':tabla.Cajas.objects.all(), 'suc':LoggedInUser.objects.get(user=request.user) })

class NuevoCaja(BSModalCreateView):
    template_name = 'caja/nuevocaja.html'
    form_class = formulario.FormCajas
    success_message = 'Se ha insertado un nuevo registro'
    success_url = reverse_lazy(listar_caja)

class EditarCaja(BSModalUpdateView):
    model = tabla.Cajas
    template_name = 'caja/edit_caja.html'
    form_class = formulario.FormCajas
    success_message = 'Registros actualizados'
    success_url = reverse_lazy(listar_caja)

# ---------------------------------------------------------------------
#          VENTANA TIPO DE MOVIMIENTOS
# ---------------------------------------------------------------------

class NuevoMovimiento(BSModalCreateView):
    template_name = 'caja/nuevo_movimiento.html'
    form_class = formulario.FormTipoMovimiento
    success_message = 'Se ha insertado un nuevo registro'
    success_url = reverse_lazy(list_movimiento)

class EditarMovimiento(BSModalUpdateView):
    model = tabla.TipoMovimiento
    template_name = 'caja/edit_tm.html'
    form_class = formulario.FormTipoMovimiento
    success_message = 'Registros actualizados'
    success_url = reverse_lazy(list_movimiento)

# ---------------------------------------------------------------------
#          VENTANA REGISTROS
# ---------------------------------------------------------------------
@login_required
def registros_list(request):
    hoy = datetime.date.today()
    registros = tabla.Registros.objects.filter(fecha__gte=hoy)
    if request.method == 'POST':
        form = formulario.FormFiltroRegistros(request.POST)
        if form.is_valid():
            rango = form.cleaned_data['intervalo']
            if rango == 'ayer':
                final = hoy - datetime.timedelta(days=1)
                registros =  tabla.Registros.objects.filter(fecha__range=(final,hoy))
            elif rango == 'semana':
                final = hoy - datetime.timedelta(days=7)
                registros =  tabla.Registros.objects.filter(fecha__range=(final,hoy))
            elif rango == 'mes':
                final = hoy - datetime.timedelta(days=30)
                registros =  tabla.Registros.objects.filter(fecha__range=(final,hoy))
            else:
                pass
    else:
        form = formulario.FormFiltroRegistros()
    return render(request, 'caja/registros.html', {
        'registros': registros, 'suc':LoggedInUser.objects.get(user=request.user),
        'caja': tabla.Cajas.objects.all(),
        })