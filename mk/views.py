import csv
from bootstrap_modal_forms.generic import BSModalDeleteView
from datetime import date, timedelta
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from vta.apoyo import calculo
#from vta.models import Facturamsr, Facturadet, Vendedores
#from vta.forms import Form_factura
from inv.models import TempCatalogo, Sucursal, Estado, N4Item, ExoTipo, ExistenciaBodega
from vta.apoyo import reino

#Variable global
articulos = ExistenciaBodega.objects.filter(cantidad__gt=0) \
    .filter(bodega__sucursal='ES') \
    .values('item__id_n4','item__descripcion','item__producto__familia__descripcion','item__producto__familia__rubro__descripcion') \
    .annotate(Sum('cantidad'))

@login_required
def menu_mk(request):
    reino(request)
    return render(request, 'fenimarket/indice.html')
"""
@login_required
def facturar(request):
    regusuario = User.objects.get(username=request.user)
    usuario_vendedor = Vendedores.objects.get(pk=request.user.id)
    if request.method == "GET":
        form = Form_factura()
        a = calculo(regusuario)
    else:
        form = Form_factura(request.POST)
        if form.is_valid():
            tempo = TempCatalogo.objects.filter(usuario=regusuario)
            if tempo:
                a = calculo(regusuario)
                numero = Facturamsr.objects.filter(sucursal='MK').count()
                f = Facturamsr.objects.create(
                    referencia = 'A0000' + str(numero+1),
                    formapago = form.cleaned_data['formapago'],
                    sucursal = Sucursal.objects.get(pk='MK'),
                    fechavencimiento = date.today() + timedelta(days=30),
                    cliente = form.cleaned_data['cliente'],
                    vendedor = usuario_vendedor,
                    estado = Estado.objects.get(pk=4),
                    preciofinaltotal = a['subtotal'] + a['iva'],
                    descuentotal = form.cleaned_data['descuentotal'],
                    impuestototal = a['iva'],
                    impreso = 0
                )
                for i in a['tempo']:
                    Facturadet.objects.create(
                        referencia = Facturamsr.objects.get(pk=f.pk),
                        bodega = Sucursal.objects.get(pk='MK'),
                        item = N4Item.objects.get(pk=i.articulo.id_n4),
                        unidades = i.cantidad,
                        preciofinal = i.factor,
                        descuento = 0,
                        impuesto = i.cantidad * i.articulo.precio * i.articulo.impuesto,
                        costo = 0,
                        tipoexo = Exotipo.objects.get(pk='G'),
                        comercializacion = 1
                    )
                tempo.delete()
                return HttpResponseRedirect(reverse('vta_facturacion', args=[f.pk]))
            else:
                return HttpResponse('<h1>Debe ingresar al menos un item</h1>')
    return render(request, 'fenimarket/factura.html', {'form':form, 'tempo':a['tempo'], 'subtotal':a['subtotal'], 'iva':a['iva'], 'total':a['subtotal'] + a['iva']})    
"""
def buscador_fact(request):
    return render(request, 'fenimarket/buscador.html')

@login_required
def catalogo(request):
     return render(request, 'fenimarket/catalogo.html')

@login_required
def consumo(request):
    return render(request, 'fenimarket/consumo.html')

@login_required
def inventario(request):
    return render(request, 'fenimarket/inventario.html',{'inv':articulos})

class item_delete(BSModalDeleteView):
    model = TempCatalogo
    template_name = 'cartera/cliente_delete.html'
    success_message = 'Hola Mundo'
    success_url = reverse_lazy('mk_facturar')

class Echo:
    def write(self, value):
        return value

@login_required
def some_streaming_csv_view(request):
    rows = ([i['item__n3__familia__rubro__descripcion'], i['item__n3__familia__descripcion'], 
            i['item__id_n4'], i['item__descripcion'], i['cantidad__sum']] for i in articulos)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename = "archivo.csv"'
    return response
