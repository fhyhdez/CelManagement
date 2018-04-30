#encoding:utf-8 
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import Group
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.forms.extras.widgets import SelectDateWidget
from django.db.models import Q
import re
from datetime import datetime, timedelta
import time
from decimal import Decimal

from django.contrib.auth.models import User
from djCell.apps.activaciones.models import TipoActivacion, ActivacionEquipo, ActivacionExpress, ActivacionPlan
from djCell.apps.almacen.models import AlmacenEquipo, AlmacenExpres, AlmacenAccesorio, AlmacenFicha
from djCell.apps.amonestaciones.models import TipoAmonestacion, Amonestacion, Sancion
from djCell.apps.auditoria.models import ArqueoCaja
from djCell.apps.catalogos.models import Estado, Ciudad, Colonia, CP, Zona
from djCell.apps.clientes.models import ClienteFacturacion, ClienteServicio, Mayorista
from djCell.apps.comisiones.models import Comision
from djCell.apps.contabilidad.models import Nomina, TipoCuenta, CuentaEmpleado, HistorialEmpleado, Metas, Caja, Gastos,LineaCredito, HistLCredito, Cuenta
from djCell.apps.corteVta.models import TipoGastoSucursal, GastosSucursal, CorteVenta, DiferenciasCorte, VentasCorte
from djCell.apps.credito.models import EstadoSubdistribuidor, EstadoCredito, Subdistribuidor, Credito, HistorialSubdistribuidor
from djCell.apps.facturacion.models import Facturacion, EstadoFacturacion
from djCell.apps.garantiasuc.models import EstadoGarantia, Garantia
from djCell.apps.mensajes.models import EstadoMensaje, SolicitudNuevoProducto 
from djCell.apps.movimientos.models import TipoMovimiento, Movimiento, ListaEquipo, ListaExpres, ListaAccesorio, ListaFichas, TransferenciaSaldo
from djCell.apps.papeletas.models import TipoProducto, Papeleta
from djCell.apps.personal.models import Area, Puesto, Empleado, Permiso, Usuario
from djCell.apps.planes.models import EstadoSolicitud, Solicitud, TipoRelacion, Banco, Plan, DetallePlan, ServiciosPlan
from djCell.apps.portabilidades.models import EstadoPortabilidad, Portabilidad,FlexeoEquipo
from djCell.apps.productos.models import TiempoGarantia,Estatus,Marca,Gama,DetallesEquipo,Equipo,TipoIcc,DetallesExpres,Expres, Secciones,MarcaAccesorio,DetallesAccesorio,EstatusAccesorio,Accesorio, NominacionFicha,EstatusFicha,Ficha,  TiempoAire, HistorialPreciosEquipos,HistorialPreciosAccesorios,HistorialPreciosExpres
from djCell.apps.proveedor.models import Proveedor, FormaPago,  Factura
from djCell.apps.recargas.models import Monto,Recarga,SaldoSucursal, HistorialSaldo, SaldoStock
from djCell.apps.servicios.models import TipoReparacion, EstadoReparacion,Reparacion, EquipoReparacion, HistorialClienteReparacion
from djCell.apps.stocks.models import StockEquipo, StockExpres, StockAccesorio, StockFicha
from djCell.apps.sucursales.models import EstadoSucursal, TipoSucursal, Sucursal, VendedorSucursal
from djCell.apps.ventas.models import EstadoVenta, Venta,VentaEquipo,VentaExpres,VentaAccesorio,VentaFichas,VentaRecarga,VentaPlan,Renta, Cancelaciones, VentaMayoreo,TipoPago, Anticipo

class reporteCompleto(forms.Form):
	tipoActivacion = forms.ChoiceField(widget=forms.RadioSelect, choices=[(c.tipo, c.tipo) for c in TipoActivacion.objects.all()], required=True)
	vendido = forms.BooleanField(required=False)

	def __init__(self,  *args, **kwargs):
		super(reporteCompleto, self).__init__(*args, **kwargs)
		self.fields['tipoActivacion'].label='Tipo de Activacion'
		self.fields['vendido'].label='Mostrar: Activados sin Vender'
		self.fields['vendido'].widget.attrs={'title':'Producto que no tienen asignada una venta'}

class reporteFecha(forms.Form):
	fxInicio 	= forms.DateField(required=True)
	fxFinal 	= forms.DateField(required=False)

	def __init__(self,  *args, **kwargs):
		super(reporteFecha, self).__init__(*args, **kwargs)
		self.fields['fxInicio'].label='Inicio'
		self.fields['fxFinal'].label='Final'
		self.fields['fxInicio'].widget=SelectDateWidget()
		self.fields['fxFinal'].widget=SelectDateWidget()
		self.fields['fxInicio'].widget.attrs={'title': 'Fecha de consulta inicial'}
		self.fields['fxFinal'].widget.attrs={'title': 'Fecha de consulta final'}

class addDetallePlan(ModelForm):
	
	class Meta:
		model= DetallePlan

  	def __init__(self,  *args, **kwargs):
		super(addDetallePlan, self).__init__(*args, **kwargs)
		self.fields['llamaPaga'].label='¿El que llama Paga?'	
	  	self.fields['recibePaga'].label='¿El que recibe Paga?'	
	  	self.fields['tarjCred'].label='¿Con Tarjeta de Credito?' 
	  	self.fields['pagoVent'].label='Pago en Ventanilla'	
	  	self.fields['plazoMin'].label='Plazo Minimo forzoso'	
	  	self.fields['plazoLibre'].label='Plazo Libre'	
	  	self.fields['minInc'].label='Minutos Incluidos'	
	  	self.fields['minAd'].label='Minutos Adicionales'	
	  	self.fields['pico'].label='$ Pico'	
	  	self.fields['noPico'].label='$ No Pico'	
	  	self.fields['minRoaming'].label='Minutos Roaming $'	
	  	self.fields['minNal'].label='Minutos de L.D. Nacional $'	
	  	self.fields['cargoFijo'].label='Cargo fijo Mensual'	
	  	self.fields['limConsumo'].label='Limite de Consumo Aproximado $'	
	  	self.fields['program'].label='Programacion $'	
	  	self.fields['enGarantia'].label='En Garantia $'	


class addPlan(ModelForm):

	class Meta:
		model = Plan
		exclude=('detallePlan','activo')
	
	def __init__(self,  *args, **kwargs):
		super(addPlan, self).__init__(*args, **kwargs)
		self.fields['plan'].label='Nombre del Nuevo Plan'
		self.fields['costo'].label='Costo $'
		self.fields['tiempoGarantia'].label='Tiempo en Garantia'
		self.fields['equiposGratis'].label='Describa los equipos Gratis'
		self.fields['comision'].label='Comision por plan'

class updReparacion(forms.Form):
	descripcion	= forms.CharField(max_length=80)
	monto 		= forms.DecimalField(max_digits=10,decimal_places=2)
	activo 	= forms.BooleanField(required=False)
	key = forms.IntegerField()
	def __init__(self,  *args, **kwargs):
		super(updReparacion, self).__init__(*args, **kwargs)
		self.fields['activo'].widget.attrs={'title':'Desactivar para que no aparezca mas en el catalogo'}
		self.fields['key'].widget = forms.HiddenInput()
		self.fields['descripcion'].widget.attrs={'size':80}

class addClienteServicioForm(forms.Form):
	nombre 		= forms.CharField(max_length=180,required=True, help_text='Nombre Completo')
	direccion 	= forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	colonia 	= forms.CharField(max_length=180,required=True)
	ciudad  	= forms.CharField(max_length=100,required=True)
	estado 		= forms.ChoiceField(required=True,choices=[(c.id, c.estado) for c in Estado.objects.all()], help_text='Elija el estado correspondiente a la colonia y ciudad')

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

class AmonestacionForm(ModelForm):
		 
	class Meta:
		model = Amonestacion
		exclude =('fxAmonestacion',)
	
	def __init__(self,  *args, **kwargs):
		super(AmonestacionForm, self).__init__(*args, **kwargs)
		self.fields['empleado'].queryset = Empleado.objects.filter(Q(puesto__puesto__icontains='encargado') | Q(puesto__puesto__icontains='vendedor'))
		self.fields['tipoAmonestacion'].label='Tipo de Amonestacion'

class setMetas(ModelForm):

	class Meta:
		model = Metas
		exclude = ('empleado',)
	
	def __init__(self,  *args, **kwargs):
		super(setMetas, self).__init__(*args, **kwargs)
		self.fields['metaEquipo'].label='Equipos'
		self.fields['metaPlanes'].label='Planes'
		self.fields['metaServicios'].label='Servicios'
		self.fields['metaEquipo'].widget.attrs={'style':'width:50%;'}
		self.fields['metaPlanes'].widget.attrs={'style':'width:50%;'}
		self.fields['metaServicios'].widget.attrs={'style':'width:50%;'}

class SancionForm(ModelForm):

	class Meta:
		model = Sancion
	def __init__(self,  *args, **kwargs):
		super(SancionForm, self).__init__(*args, **kwargs)
		self.fields['empleado'].queryset = Empleado.objects.filter(estadoEmpleado=True)



class AddUsuarioForm(ModelForm):
	
	class Meta:
		model = Usuario
		exclude = ('user',)

	def __init__(self,  *args, **kwargs):
		super(AddUsuarioForm, self).__init__(*args, **kwargs)
		self.fields['empleado'].queryset = Empleado.objects.filter(estadoEmpleado=True)
		self.fields['permiso'].queryset = Permiso.objects.all().exclude(nivel=0)

class AddUserForm(ModelForm):

	class Meta:
		model= User
		fields = ('username','email','password',)

	def __init__(self,  *args, **kwargs):
		super(AddUserForm, self).__init__(*args, **kwargs)
		self.fields['email'].label='Correo Electronico'
		self.fields['password'].widget = forms.PasswordInput()

class UpdUserForm(ModelForm):
	key = forms.CharField(max_length=100, widget =forms.HiddenInput )
	class Meta:
		model=User
		fields = ('password','is_active',)

	def __init__(self,  *args, **kwargs):
		super(UpdUserForm, self).__init__(*args, **kwargs)
		self.fields['password'].widget = forms.PasswordInput()

class UpdVendedorSucursalForm(ModelForm):

	class Meta:
		model= VendedorSucursal

	def __init__(self,  *args, **kwargs):
		super(UpdVendedorSucursalForm, self).__init__(*args, **kwargs)
		self.fields['empleado'].queryset = Empleado.objects.filter(estadoEmpleado=True)