from django.urls import path
from . import views
from vta.ajax import guardarrem, actualizarrem, exorem, obtener_items, obtener_proveedor, cantidadrem, fechavencrem
urlpatterns=[
    #Proveedor
    path('proveedor/',views.Proveedor_list,name='com_proveedor'),
    path('proveedor/nuevo/',views.ProveedorNuevo.as_view(), name='com_proveedorNew'),
    path('proveedor/editar/<str:pk>/', views.ProveedorEditar.as_view(), name='com_proveedorEdit'),
    #Detalles de Proveedor
    path('proveedor/contacto/<str:cod>/',views.ProveedorContacto,name='com_proveedorContact'),
    path('proveedor/direccion/<str:cod>/',views.ProveedorDireccion,name='com_proveedorAddress'),
    #Cotizacion
    path('cotizacion/',views.Cotizacion_list, name='com_cotizacion'),
    path('cotizacion/nuevo/',views.CotizacionNuevo.as_view(), name='com_cotizacionNew'),
    path('cotizacion/editar/<str:pk>/', views.CotizacionEditar.as_view(), name='com_cotizacionEdit'),
    path('cotizacion/detalle/<str:cod>/',views.CotizacionDetalle, name='com_cotizacionDetail'),
    path('cotizacion/plantilla/descargar/', views.cotizacion_csv, name='com_cot_download'),
    #Proforma
    path('proforma/',views.Proforma_list,name='com_proforma'),
    path('proforma/nuevo/',views.ProformaNuevo.as_view(), name='com_proformaNew'),
    path('proforma/editar/<str:pk>/', views.ProformaEditar.as_view(), name='com_proformaEdit'),
    path('proforma/detalle/<str:cod>/',views.ProformaDetalle, name='com_proformaDetail'),
    path('proforma/plantilla/descargar/', views.proforma_csv, name='com_pro_download'),
    path('proforma/ajax/cotizacion/proveedor/', obtener_proveedor, name='com_ajax_proveedor'),
    #OrdenCompra
    path('orden/compra/',views.OrdenCompra_list, name='com_ordencompra'),
    path('orden/compra/nuevo/',views.OrdenCompraNuevo.as_view(), name='com_ordencompraNew'),
    path('orden/compra/editar/<str:pk>/', views.OrdenCompraEditar.as_view(), name='com_ordencompraEdit'),
    path('orden/compra/detalle/<str:cod>/',views.OrdenCompraDetalle, name='com_ordencompraDetail'),
    path('orden/compra/plantilla/descargar/', views.ordencompra_csv, name='com_oc_download'),
    #EntradaMercaderia
    path('entrada/mercaderia/nuevo/<str:orden>',views.nuevarem, name='com_em'),
    path('entrada/mercaderia/',views.EntradaMercaderia_list, name='com_emlist'),
    path('catalogo/', views.catalogo, name='com_catalogo'),
    path('ajax/mercaderia/entrada/temporal/<str:oc>/', guardarrem, name='ajax_rem'),
    path('ajax/mercaderia/actualizar/rem/', actualizarrem, name='ajax_update_rem'),
    path('ajax/mercaderia/actualizar/rem/exoneracion/', exorem, name='ajax_rem_exo'),
    path('ajax/mercaderia/actualizar/rem/fechavenc/', fechavencrem, name='ajax_actualiza_fecha_venc'),
    path('ajax/item/compras', obtener_items, name='ajax_item_com'),
    path('ajax/rem/cantidad/', cantidadrem, name='ajax_rem_cant'),
    
    #Finalizar documentos
    path('finalizar/documento/<str:cod>/', views.finalizar, name='com_finalizar'),
    path('rem/quitar/<int:item_id>/', views.quitar_items, name='com_quitar_item'),
    path('rem/imprimir/<str:cod>/', views.imprimir_em, name='com_imprimir'),
    #inicio de modulo de compras
    path('',views.index,name='com_inicio'),
]