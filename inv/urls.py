from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views
from . import documents
from . import ajax
# from . import conecciones
 
urlpatterns=[
    # para conectarme a otras sucursales
    # path('conectarse/', conecciones.conectando, name='conectar'),
    path('Centralizar', views.centralizar, name='Centralizacion'),
    path('Recalcular', views.recalculo, name='Recalculo'),
    #N1Rubro
    path('rubro/', views.rubro_listar, name='N1Rubro_Listar'),
    path('pdf/', documents.generar_pdf, name='Pdf_Listar'),
    path('rubro/nuevo/',views.N1RubroCreate.as_view(),name='vta_rubroNew'),
    path('rubro/nuevo2/',views.N1Rubro_Create,name='vta_rubroNew2'),
    path('rubro/editar/<str:pk>/', views.RubroEdit.as_view() ,name='N1Rubro_Editar'),
    path('rubro/editar2/<str:cod>/', views.N1Rubro_Editar ,name='N1Rubro_Editar2'),
    path('rubro/eliminar/<str:cod>/', views.N1Rubro_Eliminar ,name='N1Rubro_Eliminar'),
    path('rubro/csv/', views.N1Rubro_csv ,name='N1Rubro_Csv'),
    #N2Familia
    path('familia/',views.familia_listar, name='N2Familia_Listar'),
    path('familia/eliminar/<str:cod>/',views.N2Familia_Eliminar, name='N2Familia_Eliminar'),
    path('familia/nuevo/',views.FamiliaCreate.as_view(),name='vta_familiaNew'),
    path('familia/nuevo2/',views.N2Familia_Create,name='vta_familiaNew2'),
    path('familia/editar/<str:pk>/', views.FamiliaEdit.as_view(),name='N2Familia_Editar'), 
    path('familia/editar2/<str:cod>/', views.N2Familia_Editar,name='N2Familia_Editar2'), 
    path('familia/csv/', views.N2Familia_csv,name='N2Familia_Csv'), 
    path('producto/get_familias/',ajax.get_N2Familia,name='get_familias'),
    path('producto/get_familiasT/',ajax.get_N2FamiliaT,name='get_familiasT'),
    #ExoRubro
    path('exorubro/',views.ExoRubro_list,name='ExoRubro_Listar'),
    path('exorubro/nuevo/',views.ExoRubro_Create,name='ExoRubro_Crear'),
    path('exorubro/editar/<int:num>/',views.ExoRubro_Editar,name='ExoRubro_Editar'),
    #Unidad de Medida
    path('um/',views.Um_list,name='Um_Listar'),
    path('um/nuevo/',views.Um_Create, name='Um_Crear'),
    path('um/editar/<str:cod>/',views.UMEditar, name='Um_Editar'),
    path('um/eliminar/<str:cod>/',views.UM_Eliminar, name='Um_Eliminar'),
    #N3Producto
    path('producto/',views.N3Producto_list,name='N3Producto_Listar'),
    path('producto/nuevo/',views.N3Producto_Create,name='N3Producto_Crear'),
    path('producto/editar/<str:cod>/',views.N3Producto_Editar,name='N3Producto_Editar'),
    path('producto/eliminar/<str:cod>/',views.N3Producto_Eliminar,name='N3Producto_Eliminar'),
    path('producto/imagen/<str:cod>/',views.N3Producto_Imagen,name='N3Producto_Imagen'),
    path('producto/Codigo/Fabrica/<str:cod>',views.CodigoProducto,name='N3ProductoCodigoFabrica'),
    path('producto/csv/',views.N3Producto_csv,name='N3Producto_Csv'),
    path('producto/get_productos/',ajax.get_N3Producto,name='get_productos'),
    path('producto/get_productosT/',ajax.get_N3ProductoTerminado,name='get_productosT'),
    #MarcaItem
    path('marca/item/',views.MarcaItem_list,name='MarcaItem_Listar'),
    path('marca/item/nuevo/',views.MarcaItem_Create,name='MarcaItem_Crear'),
    path('marca/item/editar/<str:cod>/',views.MarcaItem_Editar,name='MarcaItem_Editar'),
    path('marca/item/eliminar/<str:cod>/',views.MarcaItem_Eliminar,name='MarcaItem_Eliminar'),
    #N4Item
    path('item/',views.N4Item_list,name='N4Item_Listar'),
    path('item/nuevo/',views.N4Item_Create,name='N4Item_Crear'),
    path('item/editar/<str:cod>/',views.N4Item_Editar,name='N4Item_Editar'),
    path('item/eliminar/<str:cod>/',views.N4Item_Eliminar,name='N4Item_Eliminar'),
    path('item/combo/<str:cod>/',views.N4Item_combo,name='N4Item_Combo'),
    path('item/receta/<str:cod>/',views.N4Item_receta,name='N4Item_Receta'),
    path('item/kardex/<str:cod>/',views.N4ItemKardex_list,name='N4Item_Kardex'),
    path('item/select/<str:cod>/',views.N4Item_Obtener_Select,name='N4Item_Select'),
    path('item/costo/<str:cod>/',views.N4Item_costo,name='N4Item_Costo'),
    path('item/produccion/',views.N4Item_produccion_listar,name='N4Item_Produccion'),
    path('item/produccion/historial/',views.N4Item_produccion_historial,name='N4Item_Historial'),
    path('item/produccion/kardex/<str:cod>/<str:item>/',views.N4Item_produccion_detalle,name='N4Item_Producir_kardex'),
    path('item/produccion/impresion/<str:cod>/<str:item>/',views.N4Item_produccion_imprimir,name='N4Item_Producir_imprimir'),
    path('item/csv/',views.N4Item_csv,name='N4Item_Csv'),
    path('item/consolidado/',views.N4Item_Consolidado,name='N4Item_Consolidado'),
    path('item/consolidado/Costo/',views.N4Item_Consolidado_Costo,name='N4Item_Consolidado_Costo'),
    path('item/lista/inventario/',views.N4Item_Lista_Inventario,name='N4Item_Lista_Inventario'),
    path('item/kardex/Excel/<str:cod>/<str:inicio>/<str:fin>/<str:filtro>/',views.N4Item_Kardex_Excel,name='Kardex_Excel'),
    path('producto/get_items/',ajax.get_N4Item,name='get_items'),
    #N4ItemCombo
    path('item/combo/',views.N4ItemCombo_list,name='N4ItemCombo_Listar'),
    path('item/combo/nuevo/',views.N4ItemCombo_Create,name='N4ItemCombo_Crear'),
    path('item/combo/editar/<str:cod>/',views.N4ItemCombo_Editar,name='N4ItemCombo_Editar'),
    #Precio
    path('precio/',views.Precio_list,name='Precio_Listar'),
    path('precio/nuevo/',views.Precio_Create,name='Precio_Crear'),
    path('precio/editar/<str:cod>/',views.Precio_Editar,name='Precio_Editar'),
    #N4ItemXPrecio
    path('itemxprecio/<str:cod>/',views.N4ItemXPrecio_list,name='N4ItemXPrecio_Listar'),
    path('itemxprecio/nuevo/',views.N4ItemXPrecio_Create,name='N4ItemXPrecio_Crear'),
    path('itemxprecio/editar/<str:cod>/',views.N4ItemXPrecio_Editar,name='N4ItemXPrecio_Editar'),
    path('itemxprecio/buscar/',views.N4ItemXPrecio_busqueda,name='N4ItemXPrecio_Buscar'),
    #MarcaVehiculo
    path('marca/vehiculo/',views.MarcaVehiculo_list,name='MarcaVehiculo_Listar'),
    path('marca/vehiculo/nuevo/',views.MarcaVehiculo_Create,name='MarcaVehiculo_Crear'),
    path('marca/vehiculo/editar/<str:cod>/',views.MarcaVehiculo_Editar,name='MarcaVehiculo_Editar'),
    path('marca/vehiculo/eliminar/<str:cod>/',views.MarcaVehiculo_Eliminar,name='MarcaVehiculo_Eliminar'),
    #TipoVehiculo
    path('tipo/vehiculo/',views.TipoVehiculo_list,name='TipoVehiculo_Listar'),
    path('tipo/vehiculo/nuevo/',views.TipoVehiculo_Create,name='TipoVehiculo_Crear'),
    path('tipo/vehiculo/editar/<str:cod>/',views.TipoVehiculo_Editar,name='TipoVehiculo_Editar'),
    path('tipo/vehiculo/eliminar/<str:cod>/',views.TipoVehiculo_Eliminar,name='TipoVehiculo_Eliminar'),
    #ModeloVehiculo
    path('modelo/vehiculo/',views.ModeloVehiculo_list,name='ModeloVehiculo_Listar'),
    path('modelo/vehiculo/nuevo/',views.ModeloVehiculo_Create,name='ModeloVehiculo_Crear'),
    path('modelo/vehiculo/editar/<str:cod>/',views.ModeloVehiculo_Editar,name='ModeloVehiculo_Editar'),
    path('modelo/vehiculo/eliminar/<str:cod>/',views.ModeloVehiculo_Eliminar,name='ModeloVehiculo_Eliminar'),
    #Sucursal
    path('sucursal/',views.Sucursal_list,name='Sucursal_Listar'),
    path('sucursal/nuevo/',views.Sucursal_Create,name='Sucursal_Crear'),
    path('sucursal/editar/<str:cod>/',views.Sucursal_Editar,name='Sucursal_Editar'),
    path('sucursal/Saldo/<str:cod>/',views.Sucursal_Saldo,name='Sucursal_Saldo'),
    #Bodega
    path('bodega/',views.Bodega_list,name='Bodega_Listar'),
    path('bodega/nuevo/',views.Bodega_Create,name='Bodega_Crear'),
    path('bodega/editar/<str:cod>/',views.Bodega_Editar,name='Bodega_Editar'),
    path('bodega/saldo/<str:cod>/',views.Bodega_Saldo,name='Bodega_Saldo'),
    path('bodega/eliminar/<str:cod>/',views.Bodega_Eliminar,name='Bodega_Eliminar'),
    path('bodega/centro/Costo/',views.Bodega_CentroCosto,name='Bodega_Centro_Costo'),
    path('bodega/centro/Costo/Global/',views.Bodega_CentroCosto_Global,name='Bodega_Centro_Costo_Global'),
    #ExistenciaBodega
    path('ExistenciaBodega/<str:item>',views.ExistenciaBodega_list,name='ExistenciaBodega_Listar'),
    path('existencia/bodega/nuevo/',views.ExistenciaBodega_Create,name='ExistenciaBodega_Crear'),
    path('existencia/bodega/editar/<str:cod>/',views.ExistenciaBodega_Editar,name='ExistenciaBodega_Editar'),
    #Estado
    path('estado/',views.Estado_list,name='Estado_Listar'),
    path('estado/nuevo/',views.Estado_Create,name='Estado_Crear'),
    path('estado/editar/<str:cod>/',views.Estado_Editar,name='Estado_Editar'),
    #CentroCosto
    path('centro/costo/',views.CentroCosto_list,name='CentroCosto_Listar'),
    path('centro/costo/nuevo/',views.CentroCosto_Create,name='CentroCosto_Crear'),
    path('centro/costo/editar/<str:cod>/',views.CentroCosto_Editar,name='CentroCosto_Editar'),
    #AjusteTipo
    path('ajuste/tipo/',views.AjusteTipo_list,name='AjusteTipo_Listar'),
    path('ajuste/tipo/nuevo/',views.AjusteTipo_Create,name='AjusteTipo_Crear'),
    path('ajuste/tipo/editar/<str:cod>/',views.AjusteTipo_Editar,name='AjusteTipo_Editar'),
    #DevolucionCondicion
    path('devolucion/condicion/',views.DevolucionCondicion_list,name='DevolucionCondicion_Listar'),
    path('devolucion/condicion/nuevo/',views.DevolucionCondicion_Create,name='DevolucionCondicion_Crear'),
    path('devolucion/condicion/editar/<str:cod>/',views.DevolucionCondicion_Editar,name='DevolucionCondicion_Editar'),
    #DevolucionMsr
    path('devolucion/maestro/',views.DevolucionMsr_list,name='DevolucionMsr_Listar'),
    path('devolucion/maestro/nuevo/',views.DevolucionMsr_Create,name='DevolucionMsr_Crear'),
    path('devolucion/maestro/editar/<str:cod>/',views.DevolucionMsr_Editar,name='DevolucionMsr_Editar'), 
    path('devolucion/finalizar/<str:cod>/',views.DevolucionFinalizar,name='DevolucionMsr_Finalizar'), 
    path('devolucion/imprimir/<str:cod>/',views.DevolucionImpreso,name='DevolucionMsr_Imprimir'), 
    #TraladoMsr
    path('traslado/maestro/',views.TrasladoMsr_list,name='TrasladoMsr_Listar'),
    path('traslado/maestro/nuevo/',views.TrasladoMsr_Create,name='TrasladoMsr_Crear'),
    path('traslado/maestro/Locales/nuevo/',views.Locales_Create,name='Locales_Crear'),
    path('traslado/maestro/editar/<str:cod>/',views.TrasladoMsr_Editar,name='TrasladoMsr_Editar'),
    path('traslado/imprimir/<str:cod>',views.TrasladoImpreso,name='TrasladoMsr_Imprimir'),
    path('traslado/finalizar/<str:cod>',views.TrasladoFinalizar,name='TrasladoMsr_Finalizar'),
    path('traslado/locales/finalizar/<str:cod>',views.LocalesFinalizar,name='Locales_Finalizar'),
    path('traslado/recepcion/',views.RecepcionTraslado,name='TrasladoMsr_Recepcion'),
    path('traslado/devolver/',ajax.actualiza_devolucion,name='Actualiza_Recepcion'),
    path('traslado/recepcion/<str:cod>/<str:bodegao>/<str:bodegad>/<str:item>/<str:boton>',views.RecepcionAprobacion,name='TrasladoMsr_Aprobacion'),
    #AjusteMsr
    path('ajuste/maestro/',views.AjusteMsr_list,name='AjusteMsr_Listar'),
    path('ajuste/maestro/nuevo/',views.AjusteMsr_Create,name='AjusteMsr_Crear'),
    path('ajuste/maestro/editar/<str:cod>/',views.AjusteMsr_Editar,name='AjusteMsr_Editar'),
    path('ajuste/imprimir/<str:cod>/',views.AjusteImpreso,name='AjusteMsr_Imprimir'),
    path('ajuste/finalizar/<str:cod>/',views.AjusteFinalizar,name='AjusteMsr_Finalizar'),
    path('ajuste/buscar/',views.AjusteMsr_Busqueda,name='AjusteMsr_Buscar'),
    #AjusteMsrcontable
    path('ajusteC/maestro/',views.AjusteCMsr_list,name='AjusteMsrC_Listar'),
    path('ajusteC/maestro/nuevo/',views.AjusteCMsr_Create,name='AjusteMsrC_Crear'),
    path('ajusteC/maestro/editar/<str:cod>/',views.AjusteCMsr_Editar,name='AjusteMsrC_Editar'),
    path('ajusteC/imprimir/<str:cod>/',views.AjusteCImpreso,name='AjusteMsrC_Imprimir'),
    path('ajusteC/finalizar/<str:cod>/',views.AjusteCFinalizar,name='AjusteMsrC_Finalizar'),
    path('ajusteC/buscar/',views.AjusteCMsr_Busqueda,name='AjusteMsrC_Buscar'),
    #maestro detalle
    path('ajuste/maestro/detalle/<str:cod>',views.AjusteMaestroDetalle,name='AjusteMaestroDetalle'),
    path('ajusteC/maestro/detalle/<str:cod>',views.AjusteCMaestroDetalle,name='AjusteCMaestroDetalle'),
    path('devolucion/maestro/detalle/<str:cod>',views.DevolucionMaestroDetalle,name='DevolucionMaestroDetalle'),
    path('traslado/maestro/detalle/<str:cod>',views.TrasladoMaestroDetalle,name='TrasladoMaestroDetalle'),
    path('locales/maestro/detalle/<str:cod>',views.LocalesMaestroDetalle,name='LocalesMaestroDetalle'),
    path('traslado/recepcionar/<str:cod>',views.TrasladoRecepcionar,name='TrasladoRecepcion'),
    path('traslado/recepcionar/Finalizar/<str:cod>',views.Recepcion_Finalizar,name='RecepcionFinalizar'),
    path('traslado/Locales/Listar/',views.Locales_Listar,name='LocalesListar'),
    path('vencimientos/Locales/Listar/',views.Vencidos_inicial,name='item_vencidos'),
    #Generales
    path('',views.index, name='inv_inicio'),
]

if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
