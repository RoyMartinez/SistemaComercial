from . import models as tabla
from django import forms


class FormRoc(forms.ModelForm):
    inicio = forms.DateField(required=False)
    fin=forms.DateField(required=False)
    class Meta:
        model = tabla.Roc
        exclude = ['vendedor','numero']
        
    def __init__(self, *args, **kwargs):
        super(FormRoc, self).__init__(*args, **kwargs)
        self['concepto'].required = False