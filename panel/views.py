from bootstrap_modal_forms.generic import BSModalCreateView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserRegisterForm, FormExoFormula, FormExo
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from inv.models import ExoRubro, Precio
from vta.models import Condicion, Forma_pago, Vendedores, Membresia
from caja.models import Naturaleza, TipoCambio, TipoMovimiento

@login_required
def principal(request):
    if request.user.is_staff:
        return render(request, 'panel/inicio.html')
    else: 
        raise PermissionDenied()

@login_required
def cuentas(request):
    u = User.objects.all()
    return render(request,'panel/usuarios.html', {'usuarios':u})

@login_required
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cuentas_usuario')
    else:
        form = UserRegisterForm()
    return render(request,'usuarios/register.html',{'form':form})

@login_required
def cambiar_contra(request):
    if request.method == 'POST':
        pass

@login_required
def exoformula(request):
    if request.user.is_staff:
        tabla = ExoRubro.objects.all().order_by('pk')
        if request.method == "POST":
            form = FormExo(request.POST)
            if form.is_valid():
                arreglo = list(form.cleaned_data['opciones'].split(','))
                for j in ExoRubro.objects.exclude(pk=1).order_by('pk'):
                        j.unidades = False
                        j.costo = False
                        j.precio = False
                        j.save()
                for i in arreglo:             
                    x = ExoRubro.objects.get(pk=int(i[1]))
                    if i[0] == 'u':
                        x.unidades=True
                        x.save()
                    elif i[0] == 'c':
                        x.costo = True
                        x.save()
                    else:
                        x.precio = True
                        x.save()
                return HttpResponseRedirect(reverse('conf_exoformula'))
        else:
            form = FormExo()
        return render(request, 'panel/exoformula.html',{'tabla':tabla})
    else:
        raise PermissionDenied()   

class NewExoFormula(BSModalCreateView):
    template_name = 'panel/venta/new_exof.html'
    form_class = FormExoFormula
    #success_message = 'Datos grabados correctamente'
    success_url = reverse_lazy(exoformula)
   
@login_required
def condicion(request):
    if request.user.is_staff:
        return render(request, 'panel/condicion.html', {'tabla':Condicion.objects.all().order_by('nombre'),})
    else:
        raise PermissionDenied()

@login_required
def forma_pago(request):
    if request.user.is_staff:
        pago = Forma_pago.objects.all().order_by('nombre')
        return render(request, 'panel/formapago.html', {'pago':pago,})
    else:
        raise PermissionDenied()

@login_required
def vendedor(request):
    if request.user.is_staff:
        vendedor = Vendedores.objects.all().order_by('identificacion__username')
        return render(request, 'panel/vendedores.html', {'vendedores':vendedor,})
    else:
        raise PermissionDenied()

# ---------------------------------------------------------------------
#          VENTANA CAJA
# ---------------------------------------------------------------------

@login_required
def listar_naturaleza(request):
    return render(request, 'panel/caja/naturaleza.html', {'tabla': Naturaleza.objects.all()})

@login_required
def list_tc(request):
    return render(request, 'panel/caja/tipocambio.html', {'tabla':TipoCambio.objects.all().order_by('-pk')})

@login_required
def list_movimiento(request):
    return render (request, 'panel/caja/movimiento.html', {'tabla': TipoMovimiento.objects.all() })


