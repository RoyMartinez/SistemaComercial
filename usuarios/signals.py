from django.contrib.auth import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import LoggedInUser
from inv.models import Sucursal

@receiver(user_logged_in)
def on_user_logged_in(sender, request, **kwargs):
    #a = Sucursal.objects.get(pk='DU')
    LoggedInUser.objects.get_or_create(user=kwargs.get('user'))

@receiver(user_logged_out)
def on_user_logged_out(sender, **kwargs):
    LoggedInUser.objects.filter(user=kwargs.get('user')).delete()