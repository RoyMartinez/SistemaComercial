import datetime
from .widgets import BootstrapDateTimePickerInput
from django.forms.widgets import SelectDateWidget
from django import forms
from bootstrap_modal_forms.forms import BSModalForm
from . import models
from vta.models import Facturamsr
from com.models import EntradaMercaderiaMsr

class RubroForm(BSModalForm):
    class Meta:
        model = models.N1Rubro
        fields='__all__'
    
class FamiliaForm(BSModalForm):
    class Meta:
        model = models.N2Familia
        fields='__all__'
    def __init__(self, *args, **kwargs):
        super(FamiliaForm, self).__init__(*args, **kwargs)
        self.fields['id_n2'].widget.attrs.update({'readonly':True})

class N1RubroForm(forms.ModelForm):
    class Meta:
        model = models.N1Rubro
        fields = '__all__'

class N2FamiliaForm(forms.ModelForm):
     class Meta:
        model = models.N2Familia
        fields ='__all__' 

class ExoRubroForm(forms.ModelForm):
     class Meta:
        model = models.ExoRubro
        fields ='__all__' 
        
class UmForm(forms.ModelForm):
    class Meta:
        model = models.Um
        fields = '__all__'
        
class N3ProductoForm(forms.ModelForm):
    rubro = forms.ModelChoiceField(queryset=models.N1Rubro.objects.all(),required = False)
    id_n3 = forms.CharField(label='OEM',max_length = 251)
    # familia = forms.CharField(widget = forms.Select(choices = []))
    class Meta:
        model = models.N3Producto
        fields = '__all__'
        
class CodigoFabricaForm(forms.ModelForm):
    class Meta:
        model = models.CodigoFabrica
        fields = '__all__'        

class N3ProductoImagenForm(forms.ModelForm):
    class Meta:
        model = models.N3ProductoImagen
        fields = '__all__'

class MarcaItemForm(forms.ModelForm):
    class Meta:
        model = models.MarcaItem
        fields = '__all__'
        
class N4ItemForm(forms.ModelForm):
    rubro = forms.ModelChoiceField(queryset=models.N1Rubro.objects.all(),required = False)
    familia = forms.ModelChoiceField(queryset=models.N2Familia.objects.all(),required = False)
    preciomax = forms.FloatField(label='Precio Maximo')
    preciomin = forms.FloatField(label='Precio Minimo')
    descripcion = forms.CharField(label='Nota',max_length = 100,required = False)
    class Meta:
        model = models.N4Item
        fields= '__all__'
        """
        widgets={
            'Id' : forms.TextInput(attrs={'class':'form-control','ReadOnly':'True'}),
            'N3' : forms.Select(attrs={'class':'form-control','onchange':'completarcampo()'}),
        }
        """

class N4ItemImagenForm(forms.ModelForm):
    class Meta:
        model = models.N4ItemImagen
        fields = '__all__'

#para generar el formulario
def make_N4Item_combo_form(cod):
    query = models.N4Item.objects.all().exclude(id_n4=cod)
    from django import forms
    class N4ItemComboForm(forms.ModelForm):
        item = forms.ModelChoiceField(queryset=query)
        class Meta:
            model = models.N4ItemCombo
            fields = '__all__'
            # exclude = ['costo',]
    return N4ItemComboForm

class N4ItemComboForm(forms.ModelForm):
    class Meta:
        model = models.N4ItemCombo
        fields = '__all__'

def make_N4Item_receta_form(cod):
    query = models.N4Item.objects.all().exclude(id_n4=cod).exclude(producto__naturaleza = 'C')
    from django import forms
    class N4ItemRecetaForm(forms.ModelForm):
        item = forms.ModelChoiceField(queryset=query)
        class Meta:
            model = models.N4ItemReceta
            fields = '__all__'
    return  N4ItemRecetaForm

class N4ItemRecetaForm(forms.ModelForm):
    class Meta:
        model = models.N4ItemReceta
        fields = '__all__'

class PrecioForm(forms.ModelForm):
    class Meta:
        model = models.Precio
        fields = '__all__'

class N4ItemXPrecioForm(forms.ModelForm):
    class Meta:
        model = models.N4ItemXPrecio
        fields = '__all__'
    
class BusquedaForm(forms.Form):
    busqueda = forms.CharField(max_length=20)

class MarcaVehiculoForm(forms.ModelForm):
    class Meta:
        model = models.MarcaVehiculo
        fields = '__all__'

class TipoVehiculoForm(forms.ModelForm):
    class Meta:
        model = models.TipoVehiculo
        fields = '__all__'

class ModeloVehiculoForm(forms.ModelForm):
    class Meta:
        model = models.ModeloVehiculo
        fields = '__all__'

class SucursalForm(forms.ModelForm):
    class Meta:
        model = models.Sucursal
        fields = '__all__'

def make_new_bodega(sigla):
    from django import forms
    class BodegaCreatedForm(forms.ModelForm):
        # sucursal = forms.ModelChoiceField(queryset=models.Sucursal.objects.filter(siglas=sigla))
        class Meta:
            model = models.Bodega
            fields = '__all__'
    return BodegaCreatedForm

class BodegaForm(forms.ModelForm):
    class Meta:
        model = models.Bodega
        fields = '__all__'

class ExistenciaBodegaForm(forms.ModelForm):
    class Meta:
        model = models.ExistenciaBodega
        fields = '__all__'

class EstadoForm(forms.ModelForm):
    class Meta:
        model = models.Estado
        fields = '__all__'

class CentroCostoForm(forms.ModelForm):
    class Meta:
        model = models.CentroCosto
        fields = '__all__'

class AjusteTipoForm(forms.ModelForm):
    class Meta:
        model = models.AjusteTipo
        fields = '__all__'

class DevolucionCondicionForm(forms.ModelForm):
    class Meta:
        model = models.DevolucionCondicion
        fields = '__all__'

def make_devolucion_msr_form(request,post):
    from django import forms
    class DevolucionMsrForm(forms.ModelForm):
        # queryf = Facturamsr.objects.filter(estado__id = 3)
        # queryr = EntradaMercaderiaMsr.objects.filter(estado__id = 3)
        # factura = forms.ModelChoiceField(queryset=queryf,required = False)
        # rem = forms.ModelChoiceField(queryset=queryr,required= False)
        class Meta:
            model = models.DevolucionMsr
            fields = '__all__'

        # def __init__(self,*args,**kwargs):
        #     super(DevolucionMsrForm,self).__init__(*args,**kwargs)
        #     self.fields['rem']=forms.ModelChoiceField(queryset=self.queryr,required = False)
        #     self.fields['factura']=forms.ModelChoiceField(queryset=self.queryf,required = False)

    if request.method == 'POST':
        return DevolucionMsrForm(post)
    else:
        return DevolucionMsrForm()


class DevolucionMsrForm(forms.ModelForm):
    # fecha = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'], widget=BootstrapDateTimePickerInput())
    class Meta:
        model = models.DevolucionMsr
        fields = '__all__'

#para generar el formulario
def make_devolucion_det_form(sigla,queryItem,queryBodega):
    from django import forms
    class DevolucionDetalleForm(forms.ModelForm):
        item = forms.ModelChoiceField(queryset=queryItem)
        bodega = forms.ModelChoiceField(queryset=queryBodega,required = False)
        class Meta:
            model = models.DevolucionDettemp
            fields = '__all__'
    return DevolucionDetalleForm

class DevolucionDetForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        print('esto quiere decir que si obtiene la variable')
        query = models.Bodega.objects.filter(sucursal = 'MA')
        super().__init__(*args, **kwargs)
        self.fields['bodega'] = forms.ModelChoiceField(queryset=query)
    class Meta:
        model = models.DevolucionDet
        fields = '__all__'

class AjusteMsrForm(forms.ModelForm):
    # fecha_venc = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'], widget=BootstrapDateTimePickerInput())
    class Meta:
        model = models.AjusteMsr
        fields =[
            'referencia', 
            'nota',
            'sucursal',
            'estado',
            'centro_costo',
            'ajuste',
        ]
        # fields = '__all__'

#para generar el formulario
def make_ajuste_det_form(sigla):
    from django import forms
    class AjusteDetalleForm(forms.ModelForm):
        bodega = forms.ModelChoiceField(queryset=models.Bodega.objects.filter(sucursal=sigla))
        class Meta:
            model = models.AjusteDettemp
            fields = '__all__'
    return AjusteDetalleForm

class AjusteDetForm(forms.ModelForm):
    class Meta:
        model = models.AjusteDet
        fields = '__all__'

#para generar el formulario de maestro de traslado
def make_traslado_msr_form(_sigla):
    query = models.Sucursal.objects.all().exclude(siglas = _sigla).exclude(siglas='DU')
    from django import forms
    class TrasladoMaestroForm(forms.ModelForm):
        sucursalD = forms.ModelChoiceField(queryset=query)
        class Meta:
            model = models.TrasladoMsr
            fields = '__all__'
    return TrasladoMaestroForm


def make_traslado_msr_form2(_sigla):
    query = models.Sucursal.objects.all().exclude(siglas='DU')
    from django import forms
    class TrasladoMaestroForm(forms.ModelForm):
        class Meta:
            model = models.TrasladoMsr
            fields = '__all__'
    return TrasladoMaestroForm

#para generar el formulario
def make_traslado_det_form(sigla):
    # query = models.Estado.objects.filter(estado_desc__contains='Proceso')
    from django import forms
    class TrasladoDetalleForm(forms.ModelForm):
        bodegaO = forms.ModelChoiceField(queryset=models.Bodega.objects.filter(sucursal=sigla))
        # estado = forms.ModelChoiceField(queryset=query)
        class Meta:
            model = models.TrasladoDettemp
            fields = '__all__'
    return TrasladoDetalleForm

# esta es la que ocupo para traslados locales
def make_traslado_det_form2(sigla):
    # query = models.Estado.objects.filter(estado_desc__contains='Proceso')
    from django import forms
    class TrasladoDetalleForm(forms.ModelForm):
        bodegaO = forms.ModelChoiceField(queryset=models.Bodega.objects.filter(sucursal=sigla))
        bodegaD = forms.ModelChoiceField(queryset=models.Bodega.objects.filter(sucursal=sigla))
        # estado = forms.ModelChoiceField(queryset=query)
        class Meta:
            model = models.TrasladoDettemp
            fields = '__all__'
    return TrasladoDetalleForm


class TrasladoMsrForm(forms.ModelForm):
    # fecha = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'], widget=BootstrapDateTimePickerInput())
    class Meta:
        model = models.TrasladoMsr
        fields = '__all__'

class TrasladoDetForm(forms.ModelForm):
    class Meta:
        model = models.TrasladoDet
        fields = '__all__'

class BusquedafechasForm(forms.Form):
    busqueda =  forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','ReadOnly':'True'}))
    fecha_inicio = forms.CharField(widget=forms.DateInput())
    fecha_fin =forms.CharField(widget=forms.DateInput())
    rangos_especificos = forms.ChoiceField(widget=forms.Select,choices=[('1','Dia de hoy'),('2','Esta semana'),('3','Este mes')])


class DescontinuadoForm(forms.Form):
    rubro = forms.ModelChoiceField(queryset = models.N1Rubro.objects.filter(),required=False)
    familia = forms.ModelChoiceField(queryset = models.N2Familia.objects.filter(),required=False)
    producto = forms.ModelChoiceField(queryset=models.N3Producto.objects.filter(),required=False)
    tipo = forms.ChoiceField(widget=forms.Select,choices=[('T','Todos'),('U','Unico'),('E','Elemento'),('S','Servicio'),('P','Procesado'),('C','Combo')])
    descontinuado = forms.ChoiceField(widget=forms.Select,choices=[('A','Activos'),('D','Descontinuados'),('T','Ambos')])

def make_seleccionKardex(siglas,request):
    from django import forms
    class SeleccionKardexForm(forms.Form):
        esglobal = forms.ChoiceField(widget=forms.Select,choices=[('s','Sucursal'),('g','Global')])
        bodega = forms.ModelChoiceField(queryset = models.Bodega.objects.filter(sucursal__siglas = siglas),required=False)
        inicio = forms.CharField(widget=forms.DateInput(),required=False)
        fin =forms.CharField(widget=forms.DateInput(),required=False)
    if request.method == 'POST':
        return SeleccionKardexForm(request.POST)
    else:
        return SeleccionKardexForm()


def make_cantidadForm(siglas,request):
    from django import forms
    class cantidadForm(forms.Form):
        rubro = forms.ModelChoiceField(queryset = models.N1Rubro.objects.filter(n2familia__n3producto__naturaleza__in=['P']))
        familia = forms.ModelChoiceField(queryset = models.N2Familia.objects.filter(n3producto__naturaleza__in=['P']))
        producto = forms.ModelChoiceField(queryset=models.N3Producto.objects.filter(naturaleza='P'))
        item = forms.ModelChoiceField(queryset=models.N4Item.objects.filter(producto__naturaleza='P'))
        bodegaO = forms.ModelChoiceField(queryset=models.Bodega.objects.filter(sucursal__siglas=siglas))
        bodegaD = forms.ModelChoiceField(queryset=models.Bodega.objects.filter(sucursal__siglas=siglas))
        cantidad =  forms.IntegerField(min_value=1)
        fecha_venc = forms.DateTimeField()
        nota = forms.CharField(widget= forms.TextInput(attrs={'class':'form-control'}))
    if request.method == 'POST':
        return cantidadForm(request.POST)
    else:
        return cantidadForm()

class cantidadForm(forms.ModelForm):
    cantidad =  forms.IntegerField(widget=forms.TextInput(attrs={'class':'form-control'}))
    nota = forms.CharField(widget= forms.TextInput(attrs={'class':'form-control'}))
    class Meta:
        model = models.N4Item
        fields = '__all__'

class ItemCostoForm(forms.ModelForm):
    class Meta:
        model = models.item_costo
        fields = '__all__'


