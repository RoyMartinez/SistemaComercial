"""infact3 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inicio/', include('demostracion.urls')),
    path('inventario/', include('inv.urls')),
    path('compras/', include('com.urls')),
    path('ventas/', include('vta.urls')),
    path('fenimarket/', include('mk.urls')),
    path('caja/',include('caja.urls')),
    path('panel/',include('panel.urls')),
    path('contabilidad/',include('conta.urls')),
    path('cartera/',include('cartera.urls')),
    path('aprobaciones/',include('aprobaciones.urls')),
    path('incidencias/',include('incidencias.urls')),
    path('',LoginView.as_view(template_name='usuarios/login.html'),name='login'),
    path('salir', LogoutView.as_view(template_name='usuarios/logout.html'), name='salir'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)