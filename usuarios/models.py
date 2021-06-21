from django.db import models
from django.contrib.auth.models import User
from inv.models import Sucursal

class LoggedInUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='logged_in_user')
    session_key = models.CharField(max_length=32, null=True, blank=True)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, default='DU') #Asegurarse de que primero exista esta sucursal

    def __str__(self):
        return self.user.username