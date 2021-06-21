from django.urls import path
from . import views
urlpatterns=[
    path('EntradaMercaderia/',views.em_list,name='aprobaciones_em_list'),#entrada de mercaderia
    path('EntradaMercaderia/<str:codigo>/',views.em_detalle,name='aprobaciones_em_detalle'),#entrada de mercaderia
    path('EntradaMercaderia/Actualiza/<str:codigo>/<str:estado>/',views.em_actualiza,name='aprobaciones_em_actualiza'),#entrada de mercaderia
    path('OrdenCompra/',views.oc_list,name='aprobaciones_oc_list'),#ordenes de compra
    path('OrdenCompra/<str:codigo>/',views.oc_detalle,name='aprobaciones_oc_detalle'),#ordenes de compra
    path('OrdenCompra/Actualiza/<str:codigo>/<str:estado>/',views.oc_actualiza,name='aprobaciones_oc_actualiza'),#ordenes de compra
    path('ReporteVentas/Siscarcoop/',views.reporte_ventas,name='aprobaciones_rv_siscarcoop'),#reporte de ventas
    path('',views.inicio, name='aprobaciones_inicio'),
]