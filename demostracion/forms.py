from django import forms
from usuarios.models import LoggedInUser

class SucursalForm(forms.ModelForm):
    class Meta:
        model = LoggedInUser
        fields = ['sucursal']