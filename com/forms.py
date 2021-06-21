import datetime
from bootstrap_modal_forms.forms import BSModalForm
from django import forms
#from django_select2.forms import Select2Widget, Select2MultipleWidget, HeavySelect2Widget
from . import models
from inv.models import Bodega, N4Item
from usuarios.models import LoggedInUser
from vta.models import Cliente

class ProveedorForm(BSModalForm):
    class Meta:
        model = models.Proveedor
        fields = '__all__'

class CotizacionMsrForm(BSModalForm):
    class Meta:
        model = models.CotizacionMsr
        exclude = ['finalizado', 'referencia']





class CotizacionDetForm(forms.ModelForm):
    item = forms.ModelChoiceField(queryset =models.N4Item.objects.exclude(producto__naturaleza='C').exclude(producto__naturaleza='S').exclude(producto__naturaleza='P'))
    class Meta:
        model = models.CotizacionDet
        fields = '__all__'    

class ProformaMsrForm(BSModalForm):
    class Meta:
        model = models.ProformaMsr
        exclude = ['finalizado', 'referencia','importado']

    def __init__(self, *args, **kwargs):
        super(ProformaMsrForm, self).__init__(*args, **kwargs)
        self.suc = LoggedInUser.objects.get(user=self.request.user)
        self.fields['cotizacion'] = forms.ModelChoiceField(queryset=models.CotizacionMsr.objects.filter(finalizado=True, referencia__contains=self.suc.sucursal.pk).order_by('-fecha'))
        self.fields['cotizacion'].required = False

class ProformaDetForm(forms.ModelForm):
    item = forms.ModelChoiceField(queryset =models.N4Item.objects.exclude(producto__naturaleza='C').exclude(producto__naturaleza='S').exclude(producto__naturaleza='P'))
    class Meta:
        model = models.ProforDet
        fields = '__all__'
        exclude = ['referencia']

class OrdenCompraMsrForm(BSModalForm):
    class Meta:
        model = models.OrdenCompraMsr
        exclude = ['estado', 'referencia', 'importado','recibido' ]

    def __init__(self, *args, **kwargs):
        super(OrdenCompraMsrForm, self).__init__(*args, **kwargs)
        self.suc = LoggedInUser.objects.get(user=self.request.user)
        self.fields['proforma'] = forms.ModelChoiceField(queryset=models.ProformaMsr.objects.filter(finalizado=True, referencia__contains=self.suc.sucursal.pk).order_by('-fecha'))
        self.fields['cliente'] = forms.ModelChoiceField(queryset=Cliente.objects.filter(tipo='C'))
        self.fields['cliente'].label = 'Cooperativa a exonerar'
        self.fields['proforma'].required = False
        self.fields['cliente'].required = False

class OrdenCompraDetForm(forms.ModelForm):
    class Meta:
        model = models.OrdenCompraDet
        #fields = '__all__'
        exclude = ['fecha_venc']

    def __init__(self, *args, **kwargs):
        super(OrdenCompraDetForm, self).__init__(*args, **kwargs)
        self.fields['unidades'].label = 'Cantidad'

class EntradaMercaderiaMsrForm(forms.ModelForm):
    validez = forms.IntegerField()
    bodega = forms.CharField(required=False, widget=forms.Select(choices=[]))
    detalle = forms.CharField()
    class Meta:
        model = models.EntradaMercaderiaMsr
        exclude = ['estado', 'referencia', 'fecha_vencimiento', 'proveedor', 'cliente']

class EmList(forms.Form):
    cmboc = forms.CharField(max_length=50)

def make_devolucion_det_form(sigla):
    class DevolucionDetalleForm(forms.ModelForm):
        x = forms.ModelChoiceField(queryset=models.Bodega.objects.filter(sucursal=sigla))
        class Meta:
            model = models.EntradaMercaderiaDet
            fields = '__all__'
    return DevolucionDetalleForm


def make_orden_compra_det():
    class CotizacionDetForm(forms.ModelForm):
        item = forms.ModelChoiceField(queryset =models.N4Item.objects.exclude(producto__naturaleza='C').exclude(producto__naturaleza='S').exclude(producto__naturaleza='P'))
        class Meta:
            model = models.CotizacionDet
            # fields = '__all__'    
            exclude = ['fecha_venc' ,'despachado']
    return CotizacionDetForm