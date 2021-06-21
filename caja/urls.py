from django.urls import path
from . import views

urlpatterns = [
    path('',views.principal, name='caja_principal'),
    # ------- Tipo de cambio ----------
    path('tipo/cambio/', views.tipocambio, name='caja_tc'),
    path('tipo/cambio/nuevo/', views.NuevoCambio.as_view(), name='caja_tcnuevo'),
    path('tipo/cambio/editar/<int:pk>', views.EditarCambio.as_view(), name='caja_tcedit'),
    # ------- Cajas ----------
    path('cajas/', views.listar_caja, name='caja_caja'),
    path('cajas/nuevo/', views.NuevoCaja.as_view(), name='caja_cajanuevo'),
    path('cajas/editar/<slug:pk>', views.EditarCaja.as_view(), name='caja_cajaedit'),
    # ------- Movimientos ----------
    path('tipo/movimiento/nuevo/', views.NuevoMovimiento.as_view(), name='caja_movnuevo'),
    path('tipo/movimiento/editar/<slug:pk>', views.EditarMovimiento.as_view(), name='caja_movedit'),
    # ------- Movimientos ----------
    path('registros', views.registros_list, name='caja_reg'),
]