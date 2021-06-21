from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.N1Rubro)
admin.site.register(models.N2Familia)
admin.site.register(models.N3Producto)
admin.site.register(models.N4Item)
admin.site.register(models.ExoTipo) # = [Grabado, Exonerado, Excento]