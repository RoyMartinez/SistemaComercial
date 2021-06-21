from django.urls import path
from . import views, ajax, models

urlpatterns = [
    path('',views.vta_principal, name='vta_principal'),
    # ------- Uniones ----------
    path('union/', views.cat_union, name='vta_union'),
    path('union/editar/<slug:pk>', views.Editar_union.as_view(), name='vta_union_editar'),
    path('union/eliminar/<int:pk>/', views.DeleteUnion.as_view(), name='vta_union_eliminar'),
    # ------- Cooperativa ----------
    path('cooperativa/', views.cat_cooperativa, name='vta_cooperativa'),
    path('cooperativa/editar/<int:pk>', views.Editar_cooperativa.as_view(), name='vta_coop_edit'),
    # ------- Membresia ----------
    path('membresia/', views.membresia, name='vta_membresia'),
    path('membresia/editar/<int:pk>', views.Editar_membresia.as_view(), name='vta_membresia_editar'),
    path('membresia/delete/<int:pk>', views.DeleteMembresia.as_view(), name='vta_membresia_delete'),
    # ------- Otras Cosas -----------
    path('colores/', views.color, name='vta_colores'),
    path('catalogo/<int:borra>/', views.catalogo, name='vta_catalogo'),
    # ------- Facturación -----------
    path('facturar/<int:borra>/', views.facturar, name='vta_facturar'),
    path('facturar/caja/<int:valor>/', views.caja, name='vta_facturarcaja'),
    path('facturar/administracion/', views.admon_fact, name='vta_admon_fact'),
    path('proforma/administracion/', views.proforma_admon, name='vta_admon_prof'),
    path('facturar/quitar/<int:item_id>/', views.quitar_items, name='vta_quitar_item'),
    path('factura/detalle/<slug:pk>', views.Detalle_fact.as_view(), name='vta_fact_detalle'),
    path('factura/anular/<slug:pk>', views.Anular_factura.as_view(), name='vta_fact_anular'),
    path('incentivo/', views.incentivo, name='vta_incentivo'),
    path('incentivo/kardex/', views.incentivo_kardex, name='incentivo-kardex'),
    # ------- Clientes --------------
    path('cliente/nuevo/<int:origen>/', views.nuevo_cliente, name='vta_cliente_nuevo'),
    path('cliente/listado/<int:origen>/', views.listar_cliente, name='vta_cliente_listar'),
    path('cliente/editar/<str:cedula>/<int:origen>/', views.editar_cliente, name='vta_cliente_editar'),
    path('cliente/vehiculo/nuevo/<str:ced>/<int:origen>/', views.Nuevo_cliente_vehiculo.as_view(), name='vta_cliente_vehiculo'),
    path('cliente/direccion/nuevo/<str:ced>/<int:origen>/', views.NuevoClienteDireccion.as_view(), name='vta_cliente_direccion'),
    path('cliente/telefono/nuevo/<str:ced>/<int:origen>/', views.NuevoClienteTelefono.as_view(), name='vta_cliente_telefono'),
    path('cliente/vehiculo/eliminar/<str:pk>/<str:ced>/<int:origen>/', views.DelClienteVehiculo.as_view(), name='vta_clientevehiculo_delete'),
    path('cliente/direccion/eliminar/<str:pk>/<str:ced>/<int:origen>/', views.DelClienteDireccion.as_view(), name='vta_clientedireccion_delete'),
    path('cliente/telefono/eliminar/<str:pk>/<str:ced>/<int:origen>/', views.DelClienteTelefono.as_view(), name='vta_clientetelefono_delete'),
    path('cliente/exorubro/principal/', views.exorubro, name='vta_exorubro'),
    path('cliente/exorubro/ajuste/nuevo/', views.nuevoexoajuste, name='vta_nuevoexoajuste'),
    # ------- Vendedores ----------
    path('vendedores/', views.vendedor, name='vta_vendedor'),
    path('vendedores_check/<int:vendedor_id>', views.vendedor_check, name='vta_vendedor_check'),
    # ------- AJAX ----------
    path('ajax/cliente/<int:borra>/', ajax.obtener_cliente, name='vta_ajax_cliente'),
    path('ajax/cliente/reset/<int:borra>/', ajax.reset_cliente, name='vta_ajax_reset'),
    path('ajax/item/<int:borra>/', ajax.temporal_item, name='vta_ajax_item'),
    path('ajax/item/actualizar/<int:borra>/', ajax.actualizar_temp, name='vta_ajax_updateitem'),
    path('ajax/descuento/<int:borra>/', ajax.descuento, name='vta_ajax_descuento'),
    path('ajax/vehiculo/', ajax.obtener_marca, name='vta_ajax_modelos'),
    #path('ajax/exoneracion/impuesto/<int:borra>/', ajax.exoiva, name='vta_ajax_iva'),
    path('ajax/producto/<int:borra>/', ajax.producto_mk, name="mk_producto"),
    path('ajax/combo/modal/<int:borra>', ajax.armarcombo, name='vta_ajax_combo'),
    path('ajax/exo/cliente/ajuste/', ajax.exocliente, name='vta_ajax_exocliente'),
    path('ajax/exo/factura/cooperativa/<int:borra>/', ajax.cambiar_coop, name='vta_ajax_changecoop'),
    path('ajax/extra/descuento/verificar/acceso/', ajax.verificar_acceso, name='vta_ajax_acceso'),
    # ------- Reporte ----------
    path('facturar/proforma/<str:no_pro>', views.proforma, name='vta_proforma'),
    path('factura/voucher/<str:no_fact>', views.facturacion2, name='vta_facturacion'),
    path('reportes/rubro/', views.reporteria, name='vta_reporteria'),
    path('reporte/forma/pago/', views.rpt_formapago, name='vta_rptformapago'),
    path('reporte/arqueo/', views.rpt_arqueo, name='vta_arqueo'),
    path('reporte/general/ventas/', views.rpt_general, name='vta_rptgeneral'),
    path('reporte/general/ventas/imprimir/<str:tabla1>/', views.lpr_general, name='vta_lprgeneral'),
    path('reporte/general/ventas/csv/<str:tabla1>/', views.reporteg_csv, name='vta_csvgeneral'),
    path('reporte/ventas/items/', views.ventasxitem, name='vta_vtaxitem'),
    path('reporte/ventas/items/imprimir/<str:parametros>/', views.lpr_vtaitem, name='vta_lprvtaxitem'),
    path('reporte/ventas/items/csv/<str:parametros>/', views.itemxvta_csv, name='vta_csvixv')
]