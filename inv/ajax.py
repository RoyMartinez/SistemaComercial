from django.http import JsonResponse
from . import models


def actualiza_devolucion(request):
    codigo = request.GET.get('id') 
    valor = request.GET.get('value') 
    print('entre')
    print(valor)
    linea = models.TrasladoDet.objects.get(pk = codigo)
    linea.recepcionado = float(valor);
    linea.save()
    respuesta={}
    respuesta['ok']='ok'
    return JsonResponse(respuesta)


def get_N2Familia(request):
    rubro_id = request.GET.get('rubro_id')
    familias = models.N2Familia.objects.none()
    options = '<option value="" selected="selected">---------</option>'
    if rubro_id:
        familias = models.N2Familia.objects.filter(rubro__id_n1=rubro_id)   
    for familia in familias:
        options += '<option value="%s">%s</option>' % (
            familia.pk,
            familia
        )
    response = {}
    response['familias'] = options
    return JsonResponse(response)

def get_N3Producto(request):
    familia_id = request.GET.get('familia_id')
    productos = models.N3Producto.objects.none()
    options = '<option value="" selected="selected">---------</option>'
    if familia_id:
        productos = models.N3Producto.objects.filter(familia__id_n2 = familia_id)
    for producto in productos:
        options += '<option value="%s">%s</option>' % (
            producto.pk,
            producto
        )
    response = {}
    response['productos'] = options
    return JsonResponse(response)

def get_N2FamiliaT(request):
    rubro_id = request.GET.get('rubro_id')
    familias = models.N2Familia.objects.none()
    options = '<option value="" selected="selected">---------</option>'
    if rubro_id:
        familias = models.N2Familia.objects.filter(rubro__id_n1=rubro_id).filter(n3producto__naturaleza__in=['P'])
    for familia in familias:
        options += '<option value="%s">%s</option>' % (
            familia.pk,
            familia
        )
    response = {}
    response['familias'] = options
    return JsonResponse(response)

def get_N3ProductoTerminado(request):
    familia_id = request.GET.get('familia_id')
    productos = models.N3Producto.objects.none()
    options = '<option value="" selected="selected">---------</option>'
    if familia_id:
        productos = models.N3Producto.objects.filter(familia__id_n2 = familia_id).filter(naturaleza='P')
    for producto in productos:
        options += '<option value="%s">%s</option>' % (
            producto.pk,
            producto
        )
    response = {}
    response['productos'] = options
    return JsonResponse(response)

def get_N4Item(request):
    producto_id = request.GET.get('producto_id')
    items = models.N4Item.objects.none()
    options = '<option value="" selected="selected">---------</option>'
    if producto_id:
        items = models.N4Item.objects.filter(producto__id_n3 = producto_id)
    for item in items:
        options += '<option value="%s">%s</option>' % (
            item.pk,
            item
        )
    response = {}
    response['items'] = options
    return JsonResponse(response)