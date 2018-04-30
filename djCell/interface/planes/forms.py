#encoding:utf-8 
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import Group
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.forms.extras.widgets import SelectDateWidget
from django.db.models import Q
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from djCell.apps.activaciones.models import TipoActivacion, ActivacionEquipo, ActivacionExpress, ActivacionPlan
from djCell.apps.almacen.models import AlmacenEquipo, AlmacenExpres, AlmacenAccesorio, AlmacenFicha
from djCell.apps.apartados.models import EstadoApartado, Apartado, HistorialApartado
from djCell.apps.amonestaciones.models import TipoAmonestacion, Amonestacion
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
from djCell.apps.productos.models import TiempoGarantia,Estatus,Marca,Gama,DetallesEquipo,Equipo, TipoIcc,DetallesExpres,Expres,Secciones,MarcaAccesorio,DetallesAccesorio,EstatusAccesorio,Accesorio, NominacionFicha,EstatusFicha,Ficha,  TiempoAire, HistorialPreciosEquipos,HistorialPreciosAccesorios,HistorialPreciosExpres
from djCell.apps.proveedor.models import Proveedor, FormaPago,  Factura
from djCell.apps.recargas.models import Monto,Recarga,SaldoSucursal, HistorialSaldo, SaldoStock
from djCell.apps.servicios.models import TipoReparacion, EstadoReparacion,Reparacion, EquipoReparacion, HistorialClienteReparacion
from djCell.apps.stocks.models import StockEquipo, StockExpres, StockAccesorio, StockFicha
from djCell.apps.sucursales.models import EstadoSucursal, TipoSucursal, Sucursal, VendedorSucursal
from djCell.apps.ventas.models import EstadoVenta, Venta,VentaEquipo,VentaExpres,VentaAccesorio,VentaFichas,VentaRecarga,VentaPlan,Renta, Cancelaciones, VentaMayoreo,TipoPago, Anticipo

anterior = datetime.now().date().year - 100
ielactual = datetime.now().date().year - 15
MY_CHOICES = (('Masculino', 'Masculino'),('Femenino', 'Femenino'))
MY_CHOICES2 = (('', '-------'),('Libre', 'Libre'),('Forzoso','Forzoso'))
MY_CHOICES3 = (('', '-------'),('Si', 'Si'),('No','No'))

class updSolicitudPlanP(forms.Form):
	a = forms.BooleanField(required=False)
	fxSolicitud = forms.CharField(max_length=50)
	canalVta 	= forms.CharField(max_length=50, required=True)
	folioSisAct = forms.CharField(max_length=50,required=False)
	lineaSolicitadas = forms.CharField(max_length=20,required=True)
	vendedor 	= forms.CharField(max_length=50, required=True)
	subdist 	= forms.CharField(max_length=80, required=True)
	diTelcel 	= forms.BooleanField(required=False) # si o no
	lineaReferencia = forms.CharField(max_length=30,required=False)
	b = forms.BooleanField(required=False)
	fxConsultaBuro 		= forms.CharField(max_length=50,required=True)
	folioConsultaBuro 	= forms.CharField(max_length=50,required=True)
	observacionSolicitud = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
	cep = forms.BooleanField(required=False)
	nombre 		= forms.CharField(max_length=255, required=True)
  	aPat 		= forms.CharField(max_length=255, required=True)
  	aMat 		= forms.CharField(max_length=255, required=True)
  	fxNac 		= forms.DateField()#max_length=50, 
  	nacionalidad = forms.CharField(max_length=180, required=True)
  	email 		= forms.EmailField(required=False)
  	tipoIdentif = forms.CharField(max_length=180, required=True)
  	folIdent 	= forms.CharField(required=False, max_length=100)
  	formPago 	= forms.ChoiceField(required=True, choices=[(c.id, c.forma) for c in FormaPago.objects.all()])
  	banco 		= forms.CharField(max_length=80, required=False)
  	numTc 		= forms.CharField(max_length=180, required=False)
	d = forms.BooleanField(required=False)
	calleP 		= forms.CharField(max_length=255, required=True, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
  	noextP 		= forms.CharField(max_length=50)
  	nointP 		= forms.CharField(max_length=50,required=False)
  	coloniaP 	= forms.CharField(max_length=180,required=True)
  	cpP 		= forms.DecimalField(required=True,max_digits=5,decimal_places=0,help_text='Ejemplo: 75700, Sólo 5 digitos')
  	calle1P 	= forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
  	calle2P 	= forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
  	ciudadP 	= forms.CharField(max_length=180,required=True)
  	countryP 	= forms.ChoiceField(required=True,choices=[(c.id, c.estado) for c in Estado.objects.all()])
  	telP 		= forms.CharField(max_length=20,required=False)
  	refDomP 	= forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
	e = forms.BooleanField(required=False)
	puesto 		= forms.CharField(max_length=180,required=True)
  	antiguedad 	= forms.IntegerField(required=True)
  	ingresomens = forms.DecimalField(max_digits=10,decimal_places=2,required=True)
  	empNegocio 	= forms.CharField(max_length=180,required=False)
  	giro 		= forms.CharField(max_length=180,required=False)
	f = forms.BooleanField(required=False)
	ecalle 		= forms.CharField(max_length=255,required=True, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
  	enoext 		= forms.CharField(max_length=50, required=True)
  	enoint 		= forms.CharField(max_length=50,required=False)
  	ecolonia 	= forms.CharField(max_length=180,required=True)
  	ecp 		= forms.DecimalField(required=True,max_digits=5,decimal_places=0,help_text='Ejemplo: 75700, Sólo 5 digitos')
  	ecalle1 	= forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
  	ecalle2 	= forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
  	eciudad 	= forms.CharField(max_length=180,required=True)
  	ecountry 	= forms.ChoiceField(required=True,choices=[(c.id, c.estado) for c in Estado.objects.all()])
  	etel 		= forms.CharField(max_length=20,required=False)
  	eextension 	= forms.CharField(max_length=10,required=False)
	g = forms.BooleanField(required=False)
	numautos	= forms.IntegerField(required=False)
  	modelo		= forms.CharField(max_length=80,required=False)
  	casaPropia	= forms.BooleanField(required=False) #si o no
  	casaValor	= forms.DecimalField(max_digits=10,decimal_places=2,required=False)
  	renta		= forms.DecimalField(max_digits=10,decimal_places=2,required=False)
	h = forms.BooleanField(required=False)
	banco1 		= forms.CharField(max_length=80, required=False)
	ctaBanco1 	= forms.CharField(max_length=50, required=False)
	telBanco1 	= forms.CharField(max_length=20, required=False)
	banco2 		= forms.CharField(max_length=80, required=False)
	ctaBanco2 	= forms.CharField(max_length=50, required=False)
	telBanco2 	= forms.CharField(max_length=20, required=False)
	banco1Comercial = forms.CharField(max_length=80, required=False)
	ctaBanco1Comercial = forms.CharField(max_length=50, required=False)
	telBanco1Comercial = forms.CharField(max_length=20, required=False)
	banco2Comercial = forms.CharField(max_length=80, required=False)
	ctaBanco2Comercial = forms.CharField(max_length=50, required=False)
	telBanco2Comercial = forms.CharField(max_length=20, required=False)
	nombreApellidos1 = forms.CharField(max_length=250, required=True, widget=forms.Textarea(attrs={'cols': 30, 'rows': 3}))
	direccRef1	= forms.CharField(max_length=255, required=True, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
	telOfiRef1	= forms.CharField(max_length=10, required=True)
	tipoRef1 	= forms.ChoiceField(required=True,choices=[(c.id, c.tipo) for c in TipoRelacion.objects.all()])
	nombreApellidos2 = forms.CharField(max_length=250, required=False, widget=forms.Textarea(attrs={'cols': 30, 'rows': 3}))
	direccRef2	= forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
	telOfiRef2	= forms.CharField(max_length=10, required=False)
	tipoRef2 	= forms.ChoiceField(required=False,choices=[(c.id, c.tipo) for c in TipoRelacion.objects.all()])
	nombreApellidos3 = forms.CharField(max_length=250, required=False, widget=forms.Textarea(attrs={'cols': 30, 'rows': 3}))
	direccRef3	= forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
	telOfiRef3	= forms.CharField(max_length=10, required=False)
	tipoRef3 	= forms.ChoiceField(required=False,choices=[(c.id, c.tipo) for c in TipoRelacion.objects.all()])
	j = forms.BooleanField(required=False)
	equipoSolicitado = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
	planS 		= forms.ChoiceField(required=True,choices=[(c.id, c.plan+' $ '+str(c.costo)) for c in Plan.objects.filter(activo=True).order_by('plan')])
	observacion =  forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
	folio 		= forms.CharField(max_length=100)
	estadoS 	= forms.ChoiceField(required=True, choices=[(c.id, c.estado) for c in EstadoSolicitud.objects.filter(Q(estado='En Tramite')| Q(estado='Aceptado')| Q(estado='No Aceptado')| Q(estado='Cancelado')| Q(estado='Activado - Sin Entregar')|Q(estado='Enviado a Sucursal')| Q(estado='Enviado a Cliente')| Q(estado='Entregado'))])
	
	def __init__(self,  *args, **kwargs):
		super(updSolicitudPlanP, self).__init__(*args, **kwargs)
		self.fields['fxSolicitud'].label='Fecha de Solicitud'
		self.fields['fxSolicitud'].widget.attrs={'readonly':True}
		self.fields['canalVta'].label='Canal de Venta'
		self.fields['folioSisAct'].label='Folio SISACT'
		self.fields['lineaSolicitadas'].label='Lineas Solicitadas'
		self.fields['vendedor'].label='Curp Vendedor'
		self.fields['vendedor'].widget.attrs={'readonly':True}
		self.fields['subdist'].label='Subdistribuidor'
		self.fields['diTelcel'].label='Cliente TELCEL'
		self.fields['diTelcel'].widget.attrs={'title':'Seleccione o marque la casilla, si es cliente TELCEL'}
		self.fields['lineaReferencia'].label='Linea Referencia'
		#b
		self.fields['fxConsultaBuro'].label='Fecha consulta BC'
		self.fields['fxConsultaBuro'].widget=SelectDateWidget()
		self.fields['folioConsultaBuro'].label='Folio Consulta BC'
		self.fields['observacionSolicitud'].label='Observaciones'
		#c
		self.fields['aPat'].label='Apellido Paterno'
	  	self.fields['aMat'].label='Apellido Materno'
	  	self.fields['fxNac'].label='Fecha de Nacimiento'
	  	self.fields['fxNac'].widget=SelectDateWidget(years=range(anterior,ielactual))
	  	self.fields['email'].label='E-mail'
	  	self.fields['tipoIdentif'].label='Tipo de Identificacion'
	  	self.fields['folIdent'].label='Folio de Identificacion'
	  	self.fields['formPago'].label='Forma de Pago'
	  	self.fields['numTc'].label='Numero de Tarjeta de Credito'
		#d
		self.fields['calleP'].label='Calle'
	  	self.fields['noextP'].label='No. Exterior'
	  	self.fields['nointP'].label='No. Interior'
	  	self.fields['coloniaP'].label='Colonia'
	  	self.fields['cpP'].label='Codigo Postal'
	  	self.fields['calle1P'].label='Entre la Calle'
	  	self.fields['calle2P'].label='Y la Calle'
	  	self.fields['ciudadP'].label='Ciudad'
	  	self.fields['countryP'].label='Estado'
	  	self.fields['telP'].label='(Lada)Telefono = 10 Digitos'
	  	self.fields['refDomP'].label='Referencias del Domicilio'
		#e
		self.fields['ingresomens'].label='Ingreso Mensual'
	  	self.fields['empNegocio'].label='Empresa o Negocio'
		#f
		self.fields['ecalle'].label='Calle'
	  	self.fields['enoext'].label='No. Exterior'
	  	self.fields['enoint'].label='No. Interior'
	  	self.fields['ecolonia'].label='Colonia'
	  	self.fields['ecp'].label='Codigo Postal'
	  	self.fields['ecalle1'].label='Entre la Calle'
	  	self.fields['ecalle2'].label='Y la Calle'
	  	self.fields['eciudad'].label='Ciudad'
	  	self.fields['ecountry'].label='Estado'
	  	self.fields['etel'].label='(Lada)Telefono = 10 Digitos'
	  	self.fields['eextension'].label='Extension'
		#g 
		self.fields['numautos'].label='No. de Autos'
	  	self.fields['modelo'].label='Modelo(Año)'
	  	self.fields['casaPropia'].label='Casa Propia'
	  	self.fields['casaValor'].label='Propia Indique el valor Aproximado'
	  	self.fields['renta'].label='Renta Indique Monto'
		#h 
		self.fields['banco1'].label='Banco (1)'
		self.fields['ctaBanco1'].label='Cuenta'
		self.fields['telBanco1'].label='(Lada)Telefono = 10 Digitos'
		self.fields['banco2'].label='Banco (2)'
		self.fields['ctaBanco2'].label='Cuenta'
		self.fields['telBanco2'].label='(Lada)Telefono = 10 Digitos'
		self.fields['banco1Comercial'].label='Banco Comercial (1)'
		self.fields['ctaBanco1Comercial'].label='Cuenta'
		self.fields['telBanco1Comercial'].label='(Lada)Telefono = 10 Digitos'
		self.fields['banco2Comercial'].label='Banco Comercial (2)'
		self.fields['ctaBanco2Comercial'].label='Cuenta'
		self.fields['telBanco2Comercial'].label='(Lada)Telefono = 10 Digitos'
		self.fields['nombreApellidos1'].label='(Referencia 1)Nombre y Apellidos'
		self.fields['direccRef1'].label='Direccion'
		self.fields['telOfiRef1'].label='(Lada)Telefono = 10 Digitos'
		self.fields['tipoRef1'].label='Relacion'
		self.fields['nombreApellidos2'].label='(Referencia 2)Nombre y Apellidos'
		self.fields['direccRef2'].label='Direccion'
		self.fields['telOfiRef2'].label='(Lada)Telefono = 10 Digitos'
		self.fields['tipoRef2'].label='Relacion'
		self.fields['nombreApellidos3'].label='(Referencia 3)Nombre y Apellidos'
		self.fields['direccRef3'].label='Direccion'
		self.fields['telOfiRef3'].label='(Lada)Telefono = 10 Digitos'
		self.fields['tipoRef3'].label='Relacion'
		#j 
		self.fields['equipoSolicitado'].label='Equipo que solicita'
		self.fields['planS'].label='Plan Solicitado'
		self.fields['estadoS'].label='Estado del Tramite de la Solicitud'
		self.fields['folio'].widget.attrs={'readonly':True}

class updEstadoPlan(forms.Form):
	estadoS 	= forms.ChoiceField(required=True,choices=[(c.id, c.estado) for c in EstadoSolicitud.objects.filter(Q(estado='En Tramite')| Q(estado='Aceptado')| Q(estado='No Aceptado')| Q(estado='Cancelado')|Q(estado='Activado - Sin Entregar')| Q(estado='Enviado a Sucursal')| Q(estado='Enviado a Cliente')| Q(estado='Entregado'))])
	def __init__(self,  *args, **kwargs):
		super(updEstadoPlan, self).__init__(*args, **kwargs)
		self.fields['estadoS'].label=''

	
class activacionEquipo(forms.Form):
	imei 	= forms.DecimalField(required=True)
	noCell 	= forms.DecimalField(required=True)

	def __init__(self,  *args, **kwargs):
		super(activacionEquipo, self).__init__(*args, **kwargs)
		self.fields['noCell'].label='No de Asignado'
		self.fields['noCell'].widget.attrs={'placeholder':'2381234567'}
		self.fields['imei'].widget.attrs={'readonly': True, 'size':25}

class addActivacionPlan(forms.Form):
	plan 		= forms.ChoiceField(required=True,choices=[(c.id, c.plan+' $ '+str(c.costo)) for c in Plan.objects.filter(activo=True).order_by('plan')])
	solicitud 	= forms.CharField(max_length=80, help_text='Escriba el folio de la solicitud')
	form_act 	= forms.ChoiceField(required=True, choices=MY_CHOICES2)
	difEquipo 	= forms.DecimalField(max_digits=10,decimal_places=2,required=False)
	difContado 	= forms.DecimalField(max_digits=10,decimal_places=2,required=False)
	finanMeses 	= forms.IntegerField(required=False)
	numGratis 	= forms.CharField(max_length=80,required=True)
	lada		= forms.IntegerField(required=True)
	actSno		= forms.ChoiceField(required=True, choices=MY_CHOICES3)
	noActcliente 	= forms.CharField(max_length=20,required=True)
	hraCdom		= forms.CharField(max_length=80,required=True)
	hraRef		= forms.CharField(max_length=80,required=True)

	def __init__(self,  *args, **kwargs):
		super(addActivacionPlan, self).__init__(*args, **kwargs)
		self.fields['form_act'].label='Forma de Activacion' 
		self.fields['difEquipo'].label='Diferencia de Equipo' 
		self.fields['difContado'].label='Diferencia de contado' 
		self.fields['finanMeses'].label='Financiamiento a meses' 
		self.fields['numGratis'].label='Numeros gratis del Cliente (Anotar 1)' 
		self.fields['lada'].label='Lada para Activar el Plan'	
		self.fields['actSno'].label='Si se va a ¿activar con su mismo numero?'
		self.fields['noActcliente'].label='Anote aqui el No. del Cliente(Existente / Nuevo) que activa'
		self.fields['hraCdom'].label='Horario en que el Cliente se Encuentra en el Domicilio'	
		self.fields['hraRef'].label='Horario para hablarle a Referencias'	


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
class updPorta(forms.Form):
	key = forms.CharField(max_length=100)
	cliente = forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5})  )
	actualmente = forms.CharField(max_length=100)
	estado = forms.ChoiceField(choices=[(c.id, c.estado) for c in EstadoPortabilidad.objects.filter(Q(estado='En Tramite - Mesa de Control')|Q(estado='Activado por Entregar')|Q(estado='Enviado a Sucursal'))], required=True)
	
	def __init__(self,  *args, **kwargs):
		super(updPorta, self).__init__(*args, **kwargs)
		self.fields['estado'].widget.attrs={'title':'Nuevo estado para el seguimiento de la Portabilidad'}
		self.fields['cliente'].widget.attrs={'readonly':True}
		self.fields['actualmente'].widget.attrs={'readonly':True}
	
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
#'''