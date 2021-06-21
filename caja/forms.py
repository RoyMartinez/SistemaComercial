from django import forms
from bootstrap_modal_forms.forms import BSModalForm
from . import models as tabla

class FormTipoCambio(BSModalForm):
    class Meta:
        model = tabla.TipoCambio
        fields = '__all__'

class FormCajas(BSModalForm):
    class Meta:
        model = tabla.Cajas
        fields = '__all__'

class FormTipoMovimiento(BSModalForm):
    class Meta:
        model = tabla.TipoMovimiento
        fields = '__all__'

class FormRegistros(forms.ModelForm): #Lo ocupo despues de la facturacion
    class Meta:
        model = tabla.Registros
        fields =['nio_in', 'usd_in', 'nio_out', 'usd_out', 'voucher', 'tarjeta']

class FormFiltroRegistros(forms.Form):
    intervalo = forms.CharField()


