from django.urls import path
from . import views


urlpatterns=[
    path('',views.principal, name="cartera_inicio"),
    path('roc/nuevo/', views.recibos, name='cartera_recibos'),
]