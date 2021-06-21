from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from inv.models import Sucursal
from usuarios.models import LoggedInUser
from .forms import SucursalForm

@login_required
def inicio(request):
    #u = User.objects.get(username=request.user)
    #s = Sucursal.objects.filter(usuarios__pk=u.pk).order_by('nombre')
    s = Sucursal.objects.filter(usuarios=request.user).order_by('nombre')
    if request.method =="POST":
        form = SucursalForm(request.POST)
        if form.is_valid():
            sesion = LoggedInUser.objects.get(user=request.user)
            sesion.sucursal = Sucursal.objects.get(nombre=form.cleaned_data['sucursal'])
            sesion.save()
    else:
        form = SucursalForm()
    suc = LoggedInUser.objects.get(user=request.user)
    return render(request, 'demostracion/menu.html',{'form':form, 'sucursal':s, 'suc':suc.sucursal})
