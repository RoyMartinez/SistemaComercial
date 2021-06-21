from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django.forms import ModelForm
from bootstrap_modal_forms.forms import BSModalForm
from . import models as tabla
from inv.models import ExoRubro

class Form_union(BSModalForm):
    class Meta:
        model = tabla.Uniones
        fields = '__all__'

class Frm_union(forms.ModelForm):
    class Meta:
        model = tabla.Uniones
        fields= ['nombre',]

    def __init__(self, *args, **kwargs):
        super(Frm_union, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class':'form-control form-control-sm'})

class Form_vendedor(forms.ModelForm):
    nombre = forms.CharField(max_length=30)
    apellidos = forms.CharField(max_length=150)
    class Meta:
        model = tabla.Vendedores
        fields = '__all__'

class Form_cooperativa(forms.ModelForm):
    class Meta:
        model = tabla.Cooperativa
        fields = '__all__'   

class Form_cooperativaUpdate(BSModalForm):
    class Meta:
        model = tabla.Cooperativa
        fields = '__all__'

class Form_membresia(forms.ModelForm):
    class Meta:
        model = tabla.Membresia
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(Form_membresia, self).__init__(*args, **kwargs)
        for i in self.fields:
            self.fields[i].widget.attrs.update({'class':'form-control form-control-sm'})

class Form_membresiaUpdate(BSModalForm):
    class Meta:
        model = tabla.Membresia
        fields = '__all__'

class Form_cliente(forms.ModelForm):
    telefono1 = forms.CharField(required = False, widget = forms.Select(choices=[]))
    direccion1 = forms.CharField(required = False, widget = forms.Select(choices=[]))
    class Meta:
        model = tabla.Cliente
        exclude = ['tipo']

    def __init__(self, *args, **kwargs):
        super(Form_cliente, self).__init__(*args, **kwargs)
        for i in self.fields:
            self.fields[i].widget.attrs.update({'class':'form-control'})    
            if self.fields[i].label == 'Limite credito':
                self.fields[i].widget.attrs.update({'class':'form-control', 'min':'0'})
            elif self.fields[i].label == 'Saldo':
                self.fields[i].widget.attrs.update({'class':'form-control', 'readonly':'readonly'})
            elif self.fields[i].label == 'Descuento':
                self.fields[i].widget.attrs.update({'class':'form-control', 'min':'0'})

class Form_cliente_direccion(BSModalForm):
    class Meta:
        model = tabla.ClienteDireccion
        fields = ['cliente','direccion']

class Form_cliente_telefono(BSModalForm):
    class Meta:
        model = tabla.ClienteTelefono
        fields = ['cliente','operador','telefono']

class Form_factura(forms.ModelForm):

    class Meta:
        model = tabla.InstanciaFactMsr
        fields = ['formapago','cliente','descuentotal','nombre','cct', 'monto_cct','impuestototal', 'extradescuento', 'cooperativa', 'preciofinaltotal']
    def __init__(self, *args, **kwargs):
        super(Form_factura, self).__init__(*args, **kwargs)
        self.fields['formapago'].widget.attrs.update({'class':'form-control form-control-sm'})
        self.fields['cliente'].widget.attrs.update({'class':'form-control form-control-sm'})
        self.fields['descuentotal'].widget.attrs.update({'readonly':True, 'value':0, 'class':'form-control form-control-sm'})
        self.fields['impuestototal'].widget.attrs.update({'value':0, 'class':'form-control form-control-sm', 'readonly':True})
        self.fields['cct'].widget.attrs.update({'class':'form-control form-control-sm prevenir', 'placeholder':'No. CCT'})
        self.fields['monto_cct'].widget.attrs.update({'value':0, 'class':'form-control form-control-sm prevenir'})
        
class Form_colores(forms.ModelForm):
    class Meta:
        model = tabla.ClienteVehiculoColor
        fields = ['codigo','descripcion']
    
    def __init__(self,*args,**kwargs):
        super(Form_colores,self).__init__(*args, **kwargs)
        self.fields['codigo'].widget.attrs.update({'class':'form-control', 'type':'color'})

class Form_clientevehiculo(BSModalForm):
    class Meta:
        model = tabla.ClienteVehiculo
        fields = '__all__'

class FormClienteTelefono(BSModalForm):
    class Meta:
        model = tabla.ClienteTelefono
        fields = '__all__'

class FormClienteDireccion(BSModalForm):
    class Meta:
        model = tabla.ClienteDireccion
        fields = '__all__'

class Form_exorubro(forms.Form):
    cooperativa = forms.CharField(required = False, widget = forms.Select(choices=[]))
    rubro = forms.CharField(required = False, widget = forms.Select(choices=[]))
    origen = forms.CharField(required = False, widget = forms.Select(choices=[]))
    destino = forms.CharField(required = False, widget = forms.Select(choices=[]))
    cantidad = forms.FloatField()
    precio = forms.FloatField()
    costo = forms.FloatField()

class FormFiltrado(forms.Form):
    cooperativa = forms.CharField(required=False, widget=forms.Select(choices=[]))
    cliente = forms.CharField(required=False, widget=forms.Select(choices=[]))
    rubro = forms.CharField(required=False, widget=forms.Select(choices=[]))


"""
    def __init__(self, *args, **kwargs):
        c = kwargs.pop('coop', None)
        coop = tabla.Cliente.objects.get(pk=c).cooperativa.get(segmento='1')
        cliente = tabla.Cliente.objects.filter(cooperativa=coop).get(tipo='C')
        b = tabla.ExoRubroCliente.objects.filter(cliente=cliente.pk)
        super(Form_exorubro, self).__init__(*args, **kwargs)
        self.fields['rubro'] = forms.ModelChoiceField(
            queryset=ExoRubro.objects.filter(nombre__in=[i.rubro for i in b]))
"""


class Form_admon_fact(forms.Form):
    fecha = forms.DateField()

class FormAdmonProf(forms.Form):
    referencia = forms.CharField()

class Form_factura_anular(BSModalForm):
    class Meta:
        model = tabla.Facturamsr
        fields = ['estado',]

class FormCatalogo(forms.Form):
    buscar = forms.CharField()

class FormArqueo(forms.Form):
    fecha = forms.DateField()
    vendedor = forms.CharField()

class FormGeneral(forms.Form):
    fecha = forms.DateField()
    vendedor = forms.CharField()
    rango= forms.IntegerField()
    tipo = forms.IntegerField()

class FormVtaItem(forms.Form):
    fecha = forms.DateField()
    rango = forms.IntegerField()

class FormIncentivo(forms.ModelForm):
    class Meta:
        model = tabla.IncentivoMsr
        fields = ['cliente', 'ajuste', 'monto']
