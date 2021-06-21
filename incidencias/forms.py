from django import forms
from . import models

class documentoMsrForm(forms.ModelForm):
    class Meta:
        model = models.documentoMsr
        fields = '__all__'

class documentoDetForm(forms.ModelForm):
    class Meta:
        model = models.documentoDet
        fields = '__all__'