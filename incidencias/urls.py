from django.urls import path
from . import views

urlpatterns=[
    path('reporte/', views.reporte, name='inc_reporte'),
    path('reporte/nuevo/<str:cod>', views.reporte_new, name='inc_reporte_nuevo'),
    path('reporte/listas/<str:cod>', views.reporte_list, name='inc_reporte_lista'),
    #inicio de modulo de compras
    path('',views.index,name='inc_inicio'),
]