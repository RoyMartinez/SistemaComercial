from django.contrib import admin
from . import models as tabla

# Register your models here.
admin.site.register(tabla.Vendedores)
admin.site.register(tabla.Forma_pago)
admin.site.register(tabla.Condicion)
admin.site.register(tabla.Membresia)