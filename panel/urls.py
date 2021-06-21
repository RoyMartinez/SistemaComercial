from django.urls import path
from . import views

urlpatterns=[
    path('inicio/', views.principal, name='configuracion'),
    path('registro/', views.register, name='nuevo_usuario'),
    path('usuarios/', views.cuentas, name='cuentas_usuario'),
    
    path('configuracion/ventas/condicion/', views.condicion, name='conf_condicion'),
    path('configuracion/ventas/formapago/', views.forma_pago, name='conf_formapago'),
    path('configuracion/ventas/vendedores/', views.vendedor, name='conf_vendedor'),
    # Modulo CAJA
    path('configuracion/caja/naturaleza/', views.listar_naturaleza, name='conf_naturaleza'),
    path('configuracion/caja/tipo/cambio/', views.list_tc, name='conf_tipocambio'),
    path('configuracion/caja/tipo/movimiento/', views.list_movimiento, name='conf_movimiento'),
    # MODULO VENTAS
    path('configuracion/ventas/exoformula', views.exoformula, name='conf_exoformula'),
    path('configuracion/ventas/exoformula/nuevo/', views.NewExoFormula.as_view(), name='conf_newexof'),
]