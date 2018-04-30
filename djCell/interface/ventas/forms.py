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
from djCell.apps.productos.models import TiempoGarantia,Estatus,Marca,Gama,DetallesEquipo,Equipo,TipoIcc,DetallesExpres,Expres, Secciones,MarcaAccesorio,DetallesAccesorio,EstatusAccesorio,Accesorio, NominacionFicha,EstatusFicha,Ficha,  TiempoAire, HistorialPreciosEquipos,HistorialPreciosAccesorios,HistorialPreciosExpres
from djCell.apps.proveedor.models import Proveedor, FormaPago,  Factura
from djCell.apps.recargas.models import Monto,Recarga,SaldoSucursal, HistorialSaldo, SaldoStock
from djCell.apps.servicios.models import TipoReparacion, EstadoReparacion,Reparacion, EquipoReparacion, HistorialClienteReparacion
from djCell.apps.stocks.models import StockEquipo, StockExpres, StockAccesorio, StockFicha
from djCell.apps.sucursales.models import EstadoSucursal, TipoSucursal, Sucursal, VendedorSucursal
from djCell.apps.ventas.models import EstadoVenta, Venta,VentaEquipo,VentaExpres,VentaAccesorio,VentaFichas,VentaRecarga,VentaPlan,Renta, Cancelaciones, VentaMayoreo,TipoPago, Anticipo


class reporteCompleto(forms.Form):
	fxInicio 	= forms.DateField(required=True)
	fxFinal 	= forms.DateField(required=False)
	tipoActivacion = forms.ChoiceField(widget=forms.RadioSelect, choices=[(c.tipo, c.tipo) for c in TipoActivacion.objects.all()], required=True)

	def __init__(self,  *args, **kwargs):
		super(reporteCompleto, self).__init__(*args, **kwargs)
		self.fields['fxInicio'].label='Inicio'
		self.fields['fxFinal'].label='Final'
		self.fields['fxInicio'].widget=SelectDateWidget()
		self.fields['fxFinal'].widget=SelectDateWidget()
		self.fields['fxInicio'].widget.attrs={'title': 'Fecha de consulta inicial'}
		self.fields['fxFinal'].widget.attrs={'title': 'Fecha de consulta final'}
		self.fields['tipoActivacion'].label='Tipo de Activacion'

class addEvento(forms.Form):
	nombre 		= forms.CharField(max_length=180,required=True, help_text='Nombre del Evento')
	direccion 	= forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	colonia 	= forms.CharField(max_length=180,required=True)
	ciudad  	= forms.CharField(max_length=100,required=True)
	estado 		= forms.ChoiceField(required=True,choices=[(c.id, c.estado) for c in Estado.objects.all()], help_text='Elija el estado correspondiente a la colonia y ciudad')
	cp 			= forms.DecimalField(required=True,max_digits=5,decimal_places=0,help_text='Ejemplo: 75700, Sólo 5 digitos')
	zona    	= forms.ChoiceField(choices=[(c.id, c.zona ) for c in Zona.objects.all().order_by('zona')], help_text='Elija la Zona del Evento')
	zona2 		= forms.CharField(max_length=100, required=False, help_text='Agregue Aqui, si la zona no existe.')
	encargado 	= forms.ChoiceField(required=True,choices=[(c.id, c.curp +' - '+ c.nombre +' '+c.aPaterno+' '+c.aMaterno) for c in Empleado.objects.filter(Q(puesto__puesto__icontains='encargado') | Q(puesto__puesto__icontains='vendedor'))], help_text='Elija el nuevo encargado del Evento')
	noCelOfi 	= forms.CharField(max_length=15,required=False)
	
	def __init__(self,  *args, **kwargs):
		super(addEvento, self).__init__(*args, **kwargs)
		self.fields['noCelOfi'].label='No. de Celular de oficina (Opcional)'
		self.fields['encargado'].widget.attrs = {'title':'Vendedores sin asignar Sucursal como encargados'}
		self.fields['zona2'].label='¿Nueva Zona?'

class AmonestacionForm(ModelForm):
		 
	class Meta:
		model = Amonestacion
		exclude =('fxAmonestacion',)
	
	def __init__(self,  *args, **kwargs):
		super(AmonestacionForm, self).__init__(*args, **kwargs)
		self.fields['empleado'].queryset = Empleado.objects.filter(Q(puesto__puesto__icontains='encargado') | Q(puesto__puesto__icontains='vendedor'))
		self.fields['tipoAmonestacion'].label='Tipo de Amonestacion'

class AddVentaCaja(forms.Form):
	folioVenta 	= forms.CharField(max_length=80)
	efectivo 	= forms.DecimalField(max_digits=10,decimal_places=2, required=True)
	total 		= forms.DecimalField(max_digits=10,decimal_places=2)

	def __init__(self,  *args, **kwargs):
		super(AddVentaCaja, self).__init__(*args, **kwargs)
		self.fields['folioVenta'].label='Folio'
		self.fields['folioVenta'].widget.attrs={'readonly':True,'size':40}
		self.fields['total'].widget.attrs={'readonly':True}
		
class AddVentaRecarga(forms.Form):
	rfolio = forms.BooleanField(required=False)
	folio 	= forms.CharField(max_length=40,required=False) #folio que retorna telcel por la recarga enviada, exampl: FE394848595
	montos 	= forms.ChoiceField(required=True,choices=[(c.id, c.monto ) for c in Monto.objects.all()])
	observaciones = forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}), required=False )
	
			
	def __init__(self,  *args, **kwargs):
		super(AddVentaRecarga, self).__init__(*args, **kwargs)
		self.fields['montos'].label='Monto'
		self.fields['rfolio'].label='¿Generar Folio?'
		self.fields['rfolio'].widget.attrs={'title':'Si no le proporcionan el folio, genere uno automaticamente, clic aqui!'}

class AddVentaPlan(ModelForm):

	class Meta:
		model = VentaPlan
		exclude = ('venta',)
	def __init__(self,  *args, **kwargs):
		super(AddVentaPlan, self).__init__(*args, **kwargs)
		self.fields['plan'].queryset = Plan.objects.filter(activo=True)
		self.fields['precVenta'].label='Deposito'

class AddRenta(ModelForm):

	class Meta:
		model= Renta
		exclude = ('venta','fecha','sucursal','usuario',)

	def __init__(self,  *args, **kwargs):
		super(AddRenta, self).__init__(*args, **kwargs)
		self.fields['numeroReferencia'].label='Numero de Referencia Bancario'

class addPapeleta(forms.Form):
	folioPapeleta = forms.CharField(max_length=80)
	nombre 	= forms.CharField(max_length=300)
	calle 	= forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	colonia 	= forms.CharField(max_length=180,required=True)
	cp 			= forms.DecimalField(required=True,max_digits=5,decimal_places=0,help_text='Ejemplo: 75700, Sólo 5 digitos')
	ciudad  	= forms.CharField(max_length=100,required=True)
	estado 		= forms.ChoiceField(required=True,choices=[(c.id, c.estado) for c in Estado.objects.all()])
	telPart = forms.CharField(max_length=20,required=False)
	telAsig = forms.CharField(max_length=10)
	esnImei = forms.CharField(max_length=30)
	dat 	= forms.CharField(max_length=10)
	tipoProducto = forms.ChoiceField(required=True,choices=[(c.id, c.tipo ) for c in TipoProducto.objects.all()])
	
	def __init__(self,  *args, **kwargs):
		super(addPapeleta, self).__init__(*args, **kwargs)
		self.fields['folioPapeleta'].label='Folio de Papeleta'
		self.fields['cp'].label='Codigo Postal'
		self.fields['telPart'].label='Telefono Particular'
		self.fields['telAsig'].label='No. Asignado'
		self.fields['esnImei'].label='ESN/IMEI'
		self.fields['dat'].label='DAT'
		self.fields['estado'].widget.attrs={'title':'Elija el estado correspondiente a la colonia y ciudad'}
		self.fields['tipoProducto'].label='Tipo de Activacion'

class AsignarMayorista(forms.Form):
	cliente = forms.ChoiceField(required=True,choices=[(c.id, c.cliente.rfc +' ' + c.cliente.razonSocial+' (%)Fichas: '+ str(c.descuentoFichas) +' (%)Rec.: '+ str(c.descuentoRecargas)  ) for c in Mayorista.objects.all()])
	
class addClienteServicioForm(forms.Form):
	nombre 		= forms.CharField(max_length=180,required=True, help_text='Nombre Completo')
	direccion 	= forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	colonia 	= forms.CharField(max_length=180,required=True)
	ciudad  	= forms.CharField(max_length=100,required=True)
	estado 		= forms.ChoiceField(required=True,choices=[(c.id, c.estado) for c in Estado.objects.all()], help_text='Elija el estado correspondiente a la colonia y ciudad')

class addApartado(forms.Form):
	key = forms.CharField(max_length=255)
	cliente = forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	equipo 	= forms.ChoiceField(required=True,choices=[(c.id, c.marca.marca+' '+c.modelo+' '+c.color+' $'+str(c.precioMenudeo)) for c in DetallesEquipo.objects.all().order_by('marca')])
	observacion 	= forms.CharField(required=False, max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	anticipo = forms.DecimalField(max_digits=10,decimal_places=2, required=True)
	
	def __init__(self,  *args, **kwargs):
		super(addApartado, self).__init__(*args, **kwargs)
		self.fields['cliente'].widget.attrs={'readonly':True}
		self.fields['observacion'].widget.attrs={'title':'Puede poner las terminaciones del equipo si lo desea u otros datos que crea necesarios'}

class abonoApartado(forms.Form):
	key = forms.CharField(max_length=255)
	cliente = forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	equipo 	= forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	faltante = forms.DecimalField(max_digits=10,decimal_places=2)
	abonar = forms.DecimalField(max_digits=10,decimal_places=2, required=True)
	
	def __init__(self,  *args, **kwargs):
		super(abonoApartado, self).__init__(*args, **kwargs)
		self.fields['cliente'].widget.attrs={'readonly':True}
		self.fields['equipo'].widget.attrs={'readonly':True}
		self.fields['faltante'].widget.attrs={'readonly':True}

class liquidacionApartado(forms.Form):
	key = forms.CharField(max_length=255)
	key2 = forms.CharField(max_length=255)
	cliente = forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	equipo 	= forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	precio  = forms.DecimalField(max_digits=10,decimal_places=2)
	historial  = forms.DecimalField(max_digits=10,decimal_places=2)
	imei 	= forms.DecimalField(max_digits=15,decimal_places=0, required=True)
	faltante = forms.DecimalField(max_digits=10,decimal_places=2)
	abonar = forms.DecimalField(max_digits=10,decimal_places=2, required=True)
	
	def __init__(self,  *args, **kwargs):
		super(liquidacionApartado, self).__init__(*args, **kwargs)
		self.fields['cliente'].widget.attrs={'readonly':True}
		self.fields['equipo'].widget.attrs={'readonly':True}
		self.fields['equipo'].label='Equipo Apartado'
		self.fields['historial'].widget.attrs={'readonly':True}
		self.fields['faltante'].widget.attrs={'readonly':True}
		self.fields['imei'].label='Imei de equipo a liquidar'

class cancelacionApartado(forms.Form):
	key 	= forms.CharField(max_length=255)
	key2 	= forms.CharField(max_length=255)
	cliente = forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	equipo 	= forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	precio  = forms.DecimalField(max_digits=10,decimal_places=2)
	historial  	= forms.DecimalField(max_digits=10,decimal_places=2)
	folio 		= forms.DecimalField(max_digits=15,decimal_places=0, required=True)
	completar 	= forms.DecimalField(max_digits=15,decimal_places=2)
	
	def __init__(self,  *args, **kwargs):
		super(cancelacionApartado, self).__init__(*args, **kwargs)
		self.fields['cliente'].widget.attrs={'readonly':True}
		self.fields['equipo'].widget.attrs={'readonly':True}
		self.fields['equipo'].label='Equipo Apartado'
		self.fields['historial'].widget.attrs={'readonly':True}
		self.fields['folio'].label = 'Ficha (Folio)'
		
class nuevoProducto(forms.Form):
	producto 	= forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 40, 'rows': 10}) )
	
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
		self.fields['sucursal'].widget.attrs={'readonly':True}
		self.fields['totalVta'].label='Total de Ventas'
		self.fields['totalGastos'].label='Total de Gastos'
		self.fields['folioCorteVta'].widget.attrs={'readonly':True}
		self.fields['totalVta'].widget.attrs={'title':'Total del ventas realizadas','readonly':True}
		self.fields['totalGastos'].widget.attrs={'title':'Total de gastos realizados','readonly':True}
		self.fields['total'].widget.attrs={'title':'Total del corte','readonly':True}
		self.fields['observacion'].widget.attrs={'title':'Observaciones particulares'}

class vtaReparacion(forms.Form):
	key 	= forms.CharField(max_length=20)
	cliente 	= forms.CharField(max_length=180)
	marcaModelo = forms.CharField(max_length=180)
	imei 		= forms.CharField(max_length=20)
	falla		= forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}))
	observacion = forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}))
	anticipo 	= forms.DecimalField(decimal_places=2,max_digits=10,required=True)
	reparacion 	= forms.ChoiceField(required=True,choices=[(c.id, c.tipoReparacion.tipo +' - '+c.descripcion+' $'+str(c.monto) ) for c in Reparacion.objects.filter(activo=True).order_by('descripcion')])

	
	def __init__(self,  *args, **kwargs):
		super(vtaReparacion, self).__init__(*args, **kwargs)
		self.fields['marcaModelo'].label=' Marca / Modelo de Equipo'
		self.fields['key'].widget = forms.HiddenInput()
		self.fields['cliente'].widget.attrs={'readonly':True}
		self.fields['observacion'].label='Entrega Equipo con...'
		self.fields['observacion'].widget.attrs={'title':'Estado en el que entrega el equipo a flexear'}

class updCostoPorta(forms.Form):
	key = forms.IntegerField()
	cliente 	= forms.CharField(max_length=180)
	marcaModelo = forms.CharField(max_length=180)
	imei 		= forms.CharField(max_length=20)
	falla 		= forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	observacion = forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	edoActual 	= forms.CharField(max_length=180)
	estado 		= forms.ChoiceField(required=True,choices=[(c.id, c.estado) for c in EstadoReparacion.objects.filter(Q(estado__icontains='Listo - Por enviar/Serv. Tecnico')| Q(estado__icontains='Por Entregar a Cliente')| Q(estado__icontains='Entregado a Cliente')| Q(estado__icontains='Cancelado por el Cliente') )])
	
	def __init__(self,  *args, **kwargs):
		super(updCostoPorta, self).__init__(*args, **kwargs)
		self.fields['marcaModelo'].label=' Marca / Modelo de Equipo'
		self.fields['key'].widget = forms.HiddenInput()
		self.fields['cliente'].widget.attrs={'readonly':True}
		self.fields['marcaModelo'].widget.attrs={'readonly':True}
		self.fields['imei'].widget.attrs={'readonly':True}
		self.fields['edoActual'].label='Estado Actual del Equipo'
		self.fields['estado'].widget.attrs={'title':'Indicar estado actual del equipo en servicio tecnico'}

class updPorta(forms.Form):
	key = forms.CharField(max_length=100)
	cliente = forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5})  )
	actualmente = forms.CharField(max_length=100)
	estado = forms.ChoiceField(choices=[(c.id, c.estado) for c in EstadoPortabilidad.objects.filter(Q(estado='En Sucursal - Sin enviar')|Q(estado='Enviado a Mesa de Control')|Q(estado='Por entregar a Cliente - Sucursal')|Q(estado='Entregado')|Q(estado='Cancelado'))], required=True)
	
	def __init__(self,  *args, **kwargs):
		super(updPorta, self).__init__(*args, **kwargs)
		self.fields['estado'].widget.attrs={'title':'Nuevo estado para el seguimiento de la Portabilidad'}
		self.fields['cliente'].widget.attrs={'readonly':True}
		self.fields['actualmente'].widget.attrs={'readonly':True}
	

class addAbonoReparacion(forms.Form):
	key = forms.CharField(max_length=255)
	cliente 	= forms.CharField(max_length=200)
	equipo = forms.CharField(max_length=180)
	fxIngreso  	= forms.CharField(max_length=32)
	reparacion 	= forms.CharField(max_length=200)
	costoRep 	= forms.DecimalField(max_digits=10,decimal_places=2)
	anticipos 	= forms.DecimalField(max_digits=10,decimal_places=2)
	faltante 	= forms.DecimalField(max_digits=10,decimal_places=2)
	abonar 		= forms.DecimalField(max_digits=10,decimal_places=2, required= True)

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

class addGarantia(forms.Form):
	key 	= forms.CharField(max_length=20)
	key2 	= forms.CharField(max_length=20)
	cliente 		= forms.CharField(max_length=255, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
	equipo 		= forms.CharField(max_length=255, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
	falla 		= forms.CharField(max_length=255, required=True, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
	observacion = forms.CharField(max_length=255, required=True, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
	
	def __init__(self,  *args, **kwargs):
		super(addGarantia, self).__init__(*args, **kwargs)
		self.fields['key'].widget = forms.HiddenInput()
		self.fields['cliente'].widget.attrs={'readonly':True}
		self.fields['equipo'].widget.attrs={'readonly':True}
		self.fields['observacion'].label='Ingresa Equipo con...'
		self.fields['observacion'].widget.attrs={'title':'Indique Accesorios o especificar estado del equipo actualmente','placeholder':'Ej.Equipo sin accesorios'}

class updGarantiaS(forms.Form):
	key = forms.IntegerField()
	papeleta 	= forms.CharField(max_length=100)
	equipo 		= forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 3}) )
	falla 		= forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	actualmente = forms.CharField(max_length=250)
	estado 		= forms.ChoiceField(required=True,choices=[(c.id, c.estado) for c in EstadoGarantia.objects.filter(Q(estado__icontains='En Sucursal - Sin enviar') | Q(estado__icontains='Enviado a Almacen')| Q(estado__icontains='Por entregar a Cliente - Sucursal')| Q(estado__icontains='Entregado')| Q(estado__icontains='Cancelado'))])

	def __init__(self,  *args, **kwargs):
		super(updGarantiaS, self).__init__(*args, **kwargs)
		self.fields['papeleta'].widget.attrs={'readonly':True}
		self.fields['equipo'].widget.attrs={'readonly':True}
		self.fields['falla'].widget.attrs={'readonly':True}

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

class addVendedor(forms.Form):
	usuario = forms.CharField(max_length=100, required=True)

	def __init__(self,  *args, **kwargs):
		super(addVendedor, self).__init__(*args, **kwargs)
		self.fields['usuario'].widget.attrs={'title':'Ingrese el nombre de usuario del empleado que registra'}

anterior = datetime.now().date().year - 100
ielactual = datetime.now().date().year - 15
MY_CHOICES = (('Masculino', 'Masculino'),('Femenino', 'Femenino'))

#se realizo la upd de curps por combo
class addSolicitud(forms.Form):
	a = forms.BooleanField(required=False)
	fxSolicitud = forms.CharField(max_length=50)
	canalVta 	= forms.CharField(max_length=50, required=True)
	folioSisAct = forms.CharField(max_length=50,required=False)
	lineaSolicitadas = forms.CharField(max_length=20,required=True)
	vendedor 	= forms.ChoiceField(required=True, choices=[(c.curp, c.aPaterno+' '+c.aMaterno+' '+c.nombre+' '+c.curp ) for c in Empleado.objects.filter(estadoEmpleado=True).order_by('curp')])
	subdist 	= forms.CharField(max_length=80, required=True)
	diTelcel 	= forms.BooleanField(required=False) # si o no
	lineaReferencia = forms.CharField(max_length=30,required=False)
	b = forms.BooleanField(required=False)
	fxConsultaBuro 		= forms.CharField(max_length=50,required=False)
	folioConsultaBuro 	= forms.CharField(max_length=50,required=False)
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
	def __init__(self,  *args, **kwargs):
		super(addSolicitud, self).__init__(*args, **kwargs)
		#a
		self.fields['fxSolicitud'].label='Fecha de Solicitud'
		self.fields['fxSolicitud'].widget.attrs={'readonly':True}
		self.fields['canalVta'].label='Canal de Venta'
		self.fields['folioSisAct'].label='Folio SISACT'
		self.fields['lineaSolicitadas'].label='Lineas Solicitadas'
		self.fields['vendedor'].label='Curp Vendedor'
		self.fields['subdist'].label='Subdistribuidor'
		self.fields['diTelcel'].label='Cliente TELCEL'
		self.fields['diTelcel'].widget.attrs={'title':'Seleccione o marque la casilla, si es cliente TELCEL'}
		self.fields['lineaReferencia'].label='Linea Referencia'
		#b
		self.fields['fxConsultaBuro'].label='Fecha consulta BC'
		self.fields['fxConsultaBuro'].widget.attrs={'readonly':True}
		self.fields['folioConsultaBuro'].label='Folio Consulta BC'
		self.fields['folioConsultaBuro'].widget.attrs={'readonly':True}
		self.fields['observacionSolicitud'].label='Observaciones'
		self.fields['observacionSolicitud'].widget.attrs={'readonly':True}
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
		
class updSolicitudPlan(forms.Form):
	a = forms.BooleanField(required=False)
	fxSolicitud = forms.CharField(max_length=50)
	canalVta 	= forms.CharField(max_length=50, required=True)
	folioSisAct = forms.CharField(max_length=50,required=False)
	lineaSolicitadas = forms.CharField(max_length=20,required=True)
	vendedor 	= forms.ChoiceField(required=True, choices=[(c.curp, c.aPaterno+' '+c.aMaterno+' '+c.nombre+' '+c.curp ) for c in Empleado.objects.filter(estadoEmpleado=True).order_by('curp')])
	subdist 	= forms.CharField(max_length=80, required=True)
	diTelcel 	= forms.BooleanField(required=False) # si o no
	lineaReferencia = forms.CharField(max_length=30,required=False)
	b = forms.BooleanField(required=False)
	fxConsultaBuro 		= forms.CharField(max_length=50,required=False)
	folioConsultaBuro 	= forms.CharField(max_length=50,required=False)
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
	estadoS 	= forms.ChoiceField(required=True, choices=[(c.id, c.estado) for c in EstadoSolicitud.objects.filter(Q(estado='En Sucursal - Sin Enviar')|Q(estado='Enviado a Planes T.')|Q(estado='Cancelado')|Q(estado='Entregado'))])
	
	def __init__(self,  *args, **kwargs):
		super(updSolicitudPlan, self).__init__(*args, **kwargs)
		#a
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
		self.fields['fxConsultaBuro'].widget.attrs={'readonly':True}
		self.fields['folioConsultaBuro'].label='Folio Consulta BC'
		self.fields['folioConsultaBuro'].widget.attrs={'readonly':True}
		self.fields['observacionSolicitud'].label='Observaciones'
		self.fields['observacionSolicitud'].widget.attrs={'readonly':True}
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


class addRfc(forms.Form):
	folio = forms.CharField(max_length=80)
	#datos facturacion
	nomRazon 	= forms.CharField(max_length=80,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5})  )
	sexo 		= forms.ChoiceField(choices=MY_CHOICES, required=True)
	rfc 		= forms.CharField(max_length=15, required=True, help_text='Formato: [ABCD-AAMMDD-OM1]')
	nomRep 		= forms.CharField(max_length=250,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5})  )
	profesion 	= forms.CharField(max_length=180,required=False)
	ocupacion 	= forms.CharField(max_length=180,required=True)
	cargo 		= forms.CharField(max_length=180,required=True)
	direcc 		= forms.CharField(max_length=255, widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	telPart 	= forms.CharField(max_length=20, required=False)
	telOfi 		= forms.CharField(max_length=20, required=False)
	refPersonal = forms.CharField(max_length=250,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}))
	telRefpers 	= forms.CharField(max_length=20,required=False )
	tipoIdent 	= forms.CharField(max_length=20,required=False )
	noIdent 	= forms.CharField(max_length=50,required=False )
	
	def __init__(self,  *args, **kwargs):
		super(addRfc, self).__init__(*args, **kwargs)
		self.fields['folio'].widget.attrs={'readonly':True}
		self.fields['nomRazon'].label='Nombre o Razon Social'
		self.fields['nomRep'].label='Nombre del Representante'
		self.fields['direcc'].label='Direccion'
		self.fields['telPart'].label='Tel. Particular'
		self.fields['telOfi'].label='Tel. Oficina'
		self.fields['refPersonal'].label='Referencia Personal'
		self.fields['telRefpers'].label='Tel.de la Referencia'
		self.fields['tipoIdent'].label='Tipo de Identificacion'
		self.fields['noIdent'].label='No. De Identificacion'

class addServiciosPlan(forms.Form):
	folio = forms.CharField(max_length=100)
	servicioRequiere = forms.CharField(required=True ,max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )

	def __init__(self,  *args, **kwargs):
		super(addServiciosPlan, self).__init__(*args, **kwargs)
		self.fields['folio'].widget.attrs={'readonly':True}
		self.fields['servicioRequiere'].label='Servicio que solicita'
		self.fields['servicioRequiere'].widget.attrs={'title':'Explique el servicio que requiere el cliente'}

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
		
#---------------------------------
class addFactVenta(forms.Form):
	key = forms.CharField(max_length=255)
	rfc = forms.CharField(max_length=15, help_text='Formato: [ABCD-AAMMDD-OM1]', required=True)
	folio = forms.CharField(max_length=20,required=True)
	

class itemFactura(forms.Form):
	key = forms.CharField(max_length=255)
	tipo = forms.CharField(max_length=100)
	descripcion = forms.CharField(max_length=255)
	facturar = forms.BooleanField()
	def __init__(self,  *args, **kwargs):
		super(itemFactura, self).__init__(*args, **kwargs)
		self.fields['key'].widget = forms.HiddenInput()
		self.fields['tipo'].widget.attrs = {'readonly':True}
		self.fields['descripcion'].widget.attrs = {'readonly':True}
		self.fields['facturar'].widget.attrs = {'title':'Marque la casilla para Indicar que se facturo'}

		
		
