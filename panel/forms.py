from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from bootstrap_modal_forms.forms import BSModalForm
from inv.models import ExoRubro

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','password1','password2']

class FormExoFormula(BSModalForm):
    class Meta:
        model = ExoRubro
        fields = '__all__'

class FormExo(forms.Form):
    opciones = forms.CharField()

