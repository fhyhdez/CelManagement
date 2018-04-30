#encoding:utf-8 
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import Group
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.forms.extras.widgets import SelectDateWidget


from django.contrib.auth.models import User
from django.db.models import Q

from djCell.apps.almacen.models import AlmacenEquipo, AlmacenExpres, AlmacenAccesorio, AlmacenFicha
from djCell.apps.catalogos.models import Estado, Ciudad, Colonia, CP, Zona
from djCell.apps.clientes.models import ClienteFacturacion, ClienteServicio, Mayorista
from djCell.apps.comisiones.models import Comision
from djCell.apps.contabilidad.models import Nomina, TipoCuenta, CuentaEmpleado, HistorialEmpleado, Metas, Caja, Gastos,LineaCredito, HistLCredito, Cuenta
from djCell.apps.corteVta.models import TipoGastoSucursal, GastosSucursal, CorteVenta, DiferenciasCorte
from djCell.apps.movimientos.models import TipoMovimiento, Movimiento, ListaEquipo, ListaExpres, ListaAccesorio, ListaFichas, TransferenciaSaldo
from djCell.apps.personal.models import Area, Puesto, Empleado, Permiso, Usuario
from djCell.apps.portabilidades.models import EstadoPortabilidad, Portabilidad,FlexeoEquipo
from djCell.apps.productos.models import TiempoGarantia,Estatus,Marca,Gama,DetallesEquipo,Equipo,TipoIcc,DetallesExpres,Expres,Secciones,MarcaAccesorio,DetallesAccesorio,EstatusAccesorio,Accesorio, NominacionFicha,EstatusFicha,Ficha,  TiempoAire, HistorialPreciosEquipos,HistorialPreciosAccesorios
from djCell.apps.servicios.models import TipoReparacion, EstadoReparacion,Reparacion, EquipoReparacion, HistorialClienteReparacion
from djCell.apps.sucursales.models import EstadoSucursal, TipoSucursal, Sucursal, VendedorSucursal
from djCell.apps.ventas.models import EstadoVenta, Venta,VentaEquipo,VentaExpres,VentaAccesorio,VentaFichas,VentaRecarga,VentaPlan,Renta, Cancelaciones, VentaMayoreo,TipoPago, Anticipo

class addReparacionForm(ModelForm):
	
	class Meta:
		model = Reparacion

	def __init__(self,  *args, **kwargs):
		super(addReparacionForm, self).__init__(*args, **kwargs)
		self.fields['tipoReparacion'].label='Tipo de Reparacion'

class updReparacion(ModelForm):

	class Meta:
		model = Reparacion
		exclude = ('tipoReparacion',)

	def __init__(self,  *args, **kwargs):
		super(updReparacion, self).__init__(*args, **kwargs)
		self.fields['activo'].widget.attrs={'title':'Desactivar para que no aparezca mas en el catalogo'}
	
class addClienteServicioForm(forms.Form):
	nombre 		= forms.CharField(max_length=180,required=True, help_text='Nombre Completo')
	direccion 	= forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	colonia 	= forms.CharField(max_length=180,required=True)
	ciudad  	= forms.CharField(max_length=100,required=True)
	estado 		= forms.ChoiceField(required=True,choices=[(c.id, c.estado) for c in Estado.objects.all()], help_text='Elija el estado correspondiente a la colonia y ciudad')


class updGratisFlexeo(forms.Form):
	key 	= forms.IntegerField()
	cliente 	= forms.CharField(max_length=180)
	marcaModelo 	= forms.CharField(max_length=150)
	observaciones 	= forms.CharField(max_length=255,required=True, widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	fxCliente 	= forms.DateField(required=False)
	edoActual 	= forms.CharField(max_length=180)
	estado 		= forms.ChoiceField(required=True,choices=[(c.id, c.estado) for c in EstadoReparacion.objects.filter(Q(estado__icontains='En Revision - Serv. Tecnico') | Q(estado__icontains='Listo - Por enviar/Serv. Tecnico')| Q(estado__icontains='Por Entregar a Cliente')| Q(estado__icontains='Entregado a Cliente')| Q(estado__icontains='Cancelado por el Cliente') )])
	
	def __init__(self,  *args, **kwargs):
		super(updGratisFlexeo, self).__init__(*args, **kwargs)
		self.fields['marcaModelo'].label=' Marca / Modelo de Equipo'
		self.fields['fxCliente'].label='Fecha de Entrega a Cliente'
		self.fields['key'].widget = forms.HiddenInput()
		self.fields['cliente'].widget.attrs={'readonly':True}
		self.fields['marcaModelo'].widget.attrs={'readonly':True}
		self.fields['fxCliente'].widget= SelectDateWidget()
		self.fields['edoActual'].label='Estado Actual del Equipo'
		self.fields['edoActual'].widget.attrs={'readonly':True}
		self.fields['estado'].widget.attrs={'title':'Indicar estado actual del equipo en servicio tecnico'}


class updCostoPorta(forms.Form):
	key = forms.IntegerField()
	cliente 	= forms.CharField(max_length=180)
	marcaModelo = forms.CharField(max_length=180)
	imei 		= forms.CharField(max_length=20)
	falla 		= forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	observacion = forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	edoActual 	= forms.CharField(max_length=180)
	estado 		= forms.ChoiceField(required=True,choices=[(c.id, c.estado) for c in EstadoReparacion.objects.filter(Q(estado__icontains='En Revision - Serv. Tecnico') | Q(estado__icontains='Listo - Por enviar/Serv. Tecnico')| Q(estado__icontains='Por Entregar a Cliente')| Q(estado__icontains='Entregado a Cliente')| Q(estado__icontains='Cancelado por el Cliente') )])
	
	def __init__(self,  *args, **kwargs):
		super(updCostoPorta, self).__init__(*args, **kwargs)
		self.fields['marcaModelo'].label=' Marca / Modelo de Equipo'
		self.fields['key'].widget = forms.HiddenInput()
		self.fields['cliente'].widget.attrs={'readonly':True}
		self.fields['marcaModelo'].widget.attrs={'readonly':True}
		self.fields['imei'].widget.attrs={'readonly':True}
		self.fields['edoActual'].label='Estado Actual del Equipo'
		self.fields['estado'].widget.attrs={'title':'Indicar estado actual del equipo en servicio tecnico'}

class addAbonoReparacion(forms.Form):
	key = forms.IntegerField()
	cliente 	= forms.CharField(max_length=200)
	equipo = forms.CharField(max_length=180)
	fxIngreso  	= forms.CharField(max_length=32)
	reparacion 	= forms.CharField(max_length=200)
	costoRep 	= forms.DecimalField(max_digits=10,decimal_places=2)
	anticipos 	= forms.DecimalField(max_digits=10,decimal_places=2)
	faltante 		= forms.DecimalField(max_digits=10,decimal_places=2)
	abonar 		= forms.DecimalField(max_digits=10,decimal_places=2)

	def __init__(self,  *args, **kwargs):
		super(addAbonoReparacion, self).__init__(*args, **kwargs)
		self.fields['key'].widget = forms.HiddenInput()
		self.fields['fxIngreso'].label='Fecha de Ingreso'
		self.fields['costoRep'].label='Costo de la Reparacion'
		self.fields['cliente'].widget.attrs={'readonly':True}
		self.fields['equipo'].widget.attrs={'readonly':True}
		self.fields['fxIngreso'].widget.attrs={'readonly':True}
		self.fields['reparacion'].widget.attrs={'readonly':True}
		self.fields['costoRep'].widget.attrs={'readonly':True}
		self.fields['anticipos'].widget.attrs={'readonly':True}
		self.fields['faltante'].widget.attrs={'readonly':True}

#
class vtaGratisFlexeo(forms.Form):
	key 	= forms.CharField(max_length=20)
	cliente = forms.CharField(max_length=180)
	noaportar = forms.DecimalField(max_digits=10,decimal_places=0,required=True)
	marcaModelo 	= forms.CharField(max_length=150)
	observaciones 	= forms.CharField(max_length=255,required=True, widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	
	def __init__(self,  *args, **kwargs):
		super(vtaGratisFlexeo, self).__init__(*args, **kwargs)
		self.fields['marcaModelo'].label=' Marca / Modelo /IMEI de Equipo'
		self.fields['noaportar'].label='No. A Portar'
		self.fields['key'].widget = forms.HiddenInput()
		self.fields['cliente'].widget.attrs={'readonly':True}
		self.fields['observaciones'].label='Entrega el Equipo con...'
		self.fields['observaciones'].widget.attrs={'title':'Estado en el que entrega el equipo a flexear'}
		

class vtaCostoPorta(forms.Form):
	key 	= forms.CharField(max_length=20)
	cliente 	= forms.CharField(max_length=180)
	noaportar = forms.DecimalField(max_digits=10,decimal_places=0,required=True)
	marcaModelo = forms.CharField(max_length=180)
	imei 		= forms.CharField(max_length=20)
	observacion = forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	anticipo 	= forms.DecimalField(decimal_places=2,max_digits=10,required=True)
	reparacion 	= forms.ChoiceField(required=True,choices=[(c.id, c.tipoReparacion.tipo +' - '+c.descripcion+' $'+str(c.monto) ) for c in Reparacion.objects.filter(tipoReparacion__tipo__icontains='Flexeos',activo=True).order_by('descripcion')])

	
	def __init__(self,  *args, **kwargs):
		super(vtaCostoPorta, self).__init__(*args, **kwargs)
		self.fields['marcaModelo'].label=' Marca / Modelo de Equipo'
		self.fields['noaportar'].label='No. A Portar'
		self.fields['key'].widget = forms.HiddenInput()
		self.fields['cliente'].widget.attrs={'readonly':True}
		self.fields['observacion'].label='Entrega Equipo con...'
		self.fields['observacion'].widget.attrs={'title':'Estado en el que entrega el equipo a flexear'}
		

class vtaReparacion(forms.Form):
	key 	= forms.CharField(max_length=20)
	cliente 	= forms.CharField(max_length=180)
	marcaModelo = forms.CharField(max_length=180,required=True)
	imei 		= forms.CharField(max_length=20,required=True)
	falla		= forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}))
	observacion = forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}))
	anticipo 	= forms.DecimalField(decimal_places=2,max_digits=10,required=True)
	reparacion 	= forms.ChoiceField(required=True,choices=[(c.id, c.tipoReparacion.tipo +' - '+c.descripcion+' $'+str(c.monto) ) for c in Reparacion.objects.filter(tipoReparacion__tipo__icontains='Flexeos',activo=True).order_by('descripcion')])

	
	def __init__(self,  *args, **kwargs):
		super(vtaReparacion, self).__init__(*args, **kwargs)
		self.fields['marcaModelo'].label=' Marca / Modelo de Equipo'
		self.fields['key'].widget = forms.HiddenInput()
		self.fields['cliente'].widget.attrs={'readonly':True}
		self.fields['observacion'].label='Entrega Equipo con Accesorios?'
		self.fields['observacion'].widget.attrs={'title':'Estado en el que entrega el equipo a flexear'}

class vtaReparacionSW(forms.Form):
	key 	= forms.CharField(max_length=20)
	cliente 	= forms.CharField(max_length=180)
	marcaModelo = forms.CharField(max_length=180,required=True)
	imei 		= forms.CharField(max_length=20,required=True)
	falla		= forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}))
	observacion = forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}))
	anticipo 	= forms.DecimalField(decimal_places=2,max_digits=10,required=True)
	reparacion 	= forms.ChoiceField(required=True,choices=[(c.id, c.tipoReparacion.tipo +' - '+c.descripcion+' $'+str(c.monto) ) for c in Reparacion.objects.filter(tipoReparacion__tipo__icontains='Carga',activo=True).order_by('descripcion')])

	
	def __init__(self,  *args, **kwargs):
		super(vtaReparacionSW, self).__init__(*args, **kwargs)
		self.fields['marcaModelo'].label=' Marca / Modelo de Equipo'
		self.fields['key'].widget = forms.HiddenInput()
		self.fields['cliente'].widget.attrs={'readonly':True}
		self.fields['observacion'].label='Entrega Equipo con Accesorios?'
		self.fields['observacion'].widget.attrs={'title':'Estado en el que entrega el equipo para carga de software'}

class vtaReparacionFis(forms.Form):
	key 	= forms.CharField(max_length=20)
	cliente 	= forms.CharField(max_length=180)
	marcaModelo = forms.CharField(max_length=180,required=True)
	imei 		= forms.CharField(max_length=20,required=True)
	falla		= forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}))
	observacion = forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}))
	anticipo 	= forms.DecimalField(decimal_places=2,max_digits=10,required=True)
	reparacion 	= forms.ChoiceField(required=True,choices=[(c.id, c.tipoReparacion.tipo +' - '+c.descripcion+' $'+str(c.monto) ) for c in Reparacion.objects.filter(tipoReparacion__tipo__icontains='Reparacion Fisica',activo=True).order_by('descripcion')])

	
	def __init__(self,  *args, **kwargs):
		super(vtaReparacionFis, self).__init__(*args, **kwargs)
		self.fields['marcaModelo'].label=' Marca / Modelo de Equipo'
		self.fields['key'].widget = forms.HiddenInput()
		self.fields['cliente'].widget.attrs={'readonly':True}
		self.fields['observacion'].label='Entrega Equipo con Accesorios?'
		self.fields['observacion'].widget.attrs={'title':'Estado en el que entrega el equipo con fallas fisicas'}
	
class AddVentaCaja(forms.Form):
	folioVenta 	= forms.CharField(max_length=80)
	efectivo 	= forms.DecimalField(max_digits=10,decimal_places=2, required=True)
	total 		= forms.DecimalField(max_digits=10,decimal_places=2)

	def __init__(self,  *args, **kwargs):
		super(AddVentaCaja, self).__init__(*args, **kwargs)
		self.fields['folioVenta'].label='Folio'
		self.fields['folioVenta'].widget.attrs={'readonly':True,'size':40}
		self.fields['total'].widget.attrs={'readonly':True}

class addGastosSucursal(ModelForm):

	class Meta:
		model= GastosSucursal
		exclude =('fxGasto','sucursal','usuario','corteVenta')

	def __init__(self,  *args, **kwargs):
		super(addGastosSucursal, self).__init__(*args, **kwargs)
		self.fields['tipoGasto'].label='Tipo de Gasto'
		self.fields['observacion'].widget.attrs={'title':'Puede especificar quien autoriza o empleados involucrados por el tipo de gasto.'}
		self.fields['gasto'].label='$Monto del Gasto'

class updCorteVenta(forms.Form):
	folioCorteVta 	= forms.CharField(max_length=80)
	sucursal 		= forms.CharField(max_length=80)
	totalVta 		= forms.DecimalField(max_digits=10,decimal_places=2)
	totalGastos 	= forms.DecimalField(max_digits=10,decimal_places=2)
	total 			= forms.DecimalField(max_digits=10,decimal_places=2)
	observacion 	= forms.CharField(required=False,max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 3}))

	def __init__(self,  *args, **kwargs):
		super(updCorteVenta, self).__init__(*args, **kwargs)
		self.fields['folioCorteVta'].label='Folio'
		self.fields['totalVta'].label='Total de Ventas'
		self.fields['totalGastos'].label='Total de Gastos'
		self.fields['folioCorteVta'].widget.attrs={'readonly':True}
		self.fields['totalVta'].widget.attrs={'title':'Total del ventas realizadas','readonly':True}
		self.fields['totalGastos'].widget.attrs={'title':'Total de gastos realizados','readonly':True}
		self.fields['total'].widget.attrs={'title':'Total del corte','readonly':True}
		self.fields['observacion'].widget.attrs={'title':'Observaciones particulares'}

class addArqueoCaja(forms.Form):
	vendedor 		= forms.CharField(max_length=255)
	auditor 		= forms.CharField(max_length=255)
	totalCaja 		= forms.DecimalField(max_digits=10,decimal_places=2)
	totalArqueo 	= forms.DecimalField(required=True,max_digits=10,decimal_places=2)
	observaciones 	= forms.CharField(required=False,max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 3}))

	def __init__(self,  *args, **kwargs):
		super(addArqueoCaja, self).__init__(*args, **kwargs)
		self.fields['totalCaja'].label='Total Caja'
		self.fields['totalArqueo'].label='$Efectivo al Momento'
		self.fields['totalCaja'].widget.attrs={'title':'Total del ventas realizadas','readonly':True}
		self.fields['auditor'].label='Nombre de Usuario'
		self.fields['auditor'].widget.attrs={'title':'Solo usuarios: Administrador, Contador,Audito, Analista','readonly':True}
		self.fields['vendedor'].widget.attrs={'title':'Total del corte','readonly':True}
		self.fields['observaciones'].widget.attrs={'title':'Observaciones particulares'}