#encoding:utf-8 
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import Group
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField, TextInput
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.forms.extras.widgets import SelectDateWidget
from django.db.models import Q

from django.contrib.auth.models import User
from djCell.apps.activaciones.models import TipoActivacion, ActivacionEquipo, ActivacionExpress, ActivacionPlan
from djCell.apps.productos.models import TiempoGarantia,Estatus,Marca,Gama,DetallesEquipo,Equipo,TipoIcc,DetallesExpres,Expres, Secciones,MarcaAccesorio,DetallesAccesorio,EstatusAccesorio,Accesorio, NominacionFicha,EstatusFicha,Ficha,  TiempoAire
from djCell.apps.sucursales.models import EstadoSucursal, TipoSucursal, Sucursal, VendedorSucursal
from djCell.apps.personal.models import Area, Puesto, Empleado, Permiso, Usuario

#consultas


#Activacion de equipos
class addActivacionEquipoForm(ModelForm):
	
	class Meta:
		model = ActivacionEquipo
		exclude = ('usuario','fxActivacion','sucursal', 'equipo')
	
	def __init__(self,  *args, **kwargs):
		super(addActivacionEquipoForm, self).__init__(*args, **kwargs)
		self.fields['empleado'].queryset = Empleado.objects.filter(Q(puesto__puesto__icontains='encargado') | Q(puesto__puesto__icontains='vendedor'))
		self.fields['tipoActivacion'].queryset = TipoActivacion.objects.filter(Q(tipo__icontains='Kit') | Q(tipo__icontains='Tip')| Q(tipo__icontains='Pag. G.')| Q(tipo__icontains='Otros'))
		self.fields['tipoActivacion'].label='Tipo de Activacion'

#"/activaciones/equipo/buscar - Buscar y actualizar equipo para activacion"
class consEquipo(forms.Form):
	imei 	= forms.DecimalField(required=True)
	icc 	= forms.DecimalField(required=True)
	noCell 	= forms.DecimalField(required=True)

	def __init__(self,  *args, **kwargs):
		super(consEquipo, self).__init__(*args, **kwargs)
		self.fields['noCell'].label='No de Asignado'
		self.fields['noCell'].widget.attrs={'placeholder':'2381234567'}
		self.fields['imei'].widget.attrs={'readonly': True, 'size':25}
		self.fields['icc'].widget.attrs={'readonly': True, 'size':25}
	

#"Activacion de express"
class addActivacionExpressForm(ModelForm):
	
	class Meta:
		model = ActivacionExpress
		exclude = ('usuario','fxActivacion','sucursal', 'express')

	def __init__(self,  *args, **kwargs):
		super(addActivacionExpressForm, self).__init__(*args, **kwargs)
		self.fields['empleado'].queryset = Empleado.objects.filter(Q(puesto__puesto__icontains='encargado') | Q(puesto__puesto__icontains='vendedor'))
		self.fields['tipoActivacion'].queryset = TipoActivacion.objects.filter(Q(tipo__icontains='Express') | Q(tipo__icontains='Virgen')| Q(tipo__icontains='Otros'))
		self.fields['tipoActivacion'].label='Tipo de Activacion'

#"/activaciones/express/buscar"
class consExpres(forms.Form):
	icc 	= forms.DecimalField(required=True)
	noCell 	= forms.DecimalField(required=True)

	def __init__(self,  *args, **kwargs):
		super(consExpres, self).__init__(*args, **kwargs)
		self.fields['noCell'].label='No de Asignado'
		self.fields['noCell'].widget.attrs={'placeholder':'2381234567'}
		self.fields['icc'].widget.attrs={'readonly': True, 'size':25}

#"/activaciones/reporte -Reporte de activaciones"
class reporteFecha(forms.Form):
	fxInicio 	= forms.DateField(required=True)
	fxFinal 	= forms.DateField(required=False)

	def __init__(self,  *args, **kwargs):
		super(reporteFecha, self).__init__(*args, **kwargs)
		self.fields['fxInicio'].label='Inicio'
		self.fields['fxFinal'].label='Final'
		self.fields['fxInicio'].widget=SelectDateWidget()
		self.fields['fxFinal'].widget=SelectDateWidget()
		self.fields['fxInicio'].widget.attrs={'title': 'Fecha de consulta inicial','type':'Date'}
		self.fields['fxFinal'].widget.attrs={'title': 'Fecha de consulta final'}
	#'''


class reporteCompleto(forms.Form):
	#fxInicio 	= forms.DateField(required=True)
	#fxFinal 	= forms.DateField(required=False)
	tipoActivacion = forms.ChoiceField(widget=forms.RadioSelect, choices=[(c.tipo, c.tipo) for c in TipoActivacion.objects.all()], required=True)

	def __init__(self,  *args, **kwargs):
		super(reporteCompleto, self).__init__(*args, **kwargs)
		self.fields['tipoActivacion'].label='Tipo de Activacion'
