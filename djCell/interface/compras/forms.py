#encoding:utf-8 
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import Group
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField, TextInput
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.forms.extras.widgets import SelectDateWidget

from django.db.models import Q

from django.contrib.auth.models import User
from djCell.apps.almacen.models import AlmacenEquipo, AlmacenExpres, AlmacenAccesorio, AlmacenFicha
from djCell.apps.auditoria.models import ArqueoCaja
from djCell.apps.catalogos.models import Ciudad,CP,Colonia, Estado
from djCell.apps.contabilidad.models import CuentaEmpleado, HistorialEmpleado, Caja, Gastos,LineaCredito, HistLCredito
from djCell.apps.corteVta.models import GastosSucursal, CorteVenta, DiferenciasCorte
from djCell.apps.credito.models import EstadoSubdistribuidor, EstadoCredito, Subdistribuidor, Credito, HistorialSubdistribuidor
from djCell.apps.garantiasuc.models import EstadoGarantia, Garantia
from djCell.apps.mensajes.models import SolicitudNuevoProducto 
from djCell.apps.movimientos.models import TipoMovimiento, Movimiento, ListaEquipo, ListaExpres, ListaAccesorio, ListaFichas, TransferenciaSaldo
from djCell.apps.papeletas.models import Papeleta
from djCell.apps.personal.models import Empleado, Usuario
from djCell.apps.productos.models import TiempoGarantia,Estatus,Marca,Gama,DetallesEquipo,Equipo,TipoIcc,DetallesExpres,Expres, Secciones,MarcaAccesorio,DetallesAccesorio,EstatusAccesorio,Accesorio, NominacionFicha,EstatusFicha,Ficha,  TiempoAire
from djCell.apps.proveedor.models import Proveedor, FormaPago,  Factura
from djCell.apps.recargas.models import Monto,Recarga,SaldoSucursal, HistorialSaldo, SaldoStock
from djCell.apps.stocks.models import StockEquipo, StockExpres, StockAccesorio, StockFicha
from djCell.apps.sucursales.models import EstadoSucursal, TipoSucursal, Sucursal, VendedorSucursal
from djCell.apps.ventas.models import EstadoVenta, Venta,VentaEquipo,VentaExpres,VentaAccesorio,VentaFichas,VentaRecarga,VentaPlan,Renta, Cancelaciones, VentaMayoreo,TipoPago
from djCell.apps.clientes.models import ClienteFacturacion, ClienteServicio, Mayorista

from datetime import datetime, timedelta
anterior = datetime.now().date().year - 10
ielactual = datetime.now().date().year

#"Nueva factura o nota de compra"
class addFacturaForm(ModelForm):

	class Meta:
		model = Factura
		exclude =('usuario','fxIngreso')
	def __init__(self,  *args, **kwargs):
		super(addFacturaForm, self).__init__(*args, **kwargs)
		self.fields['conFactura'].label='¿La compra contiene Factura?'
		self.fields['conFactura'].help_text='Activar si contiene Factura obligatoria'
		self.fields['fxFactura'].label='Fecha de la Factura'
		self.fields['fxFactura'].widget=SelectDateWidget()
		self.fields['formaPago'].label='Forma de Pago'
		self.fields['subTotal'].label='Sub-Total'
		self.fields['montoTotal'].label='Total'
		#self.fields['tipoFactura'].label='Tipo de Factura'
		self.fields['observacion'].required=False

#"Agregar equipos a Factura"
class addDetallesEquipoForm(ModelForm):
	class Meta:
		model = DetallesEquipo
	def __init__(self,  *args, **kwargs):
		super(addDetallesEquipoForm, self).__init__(*args, **kwargs)
		self.fields['gama'].label='Gamma del Equipo'
		self.fields['tiempoGarantia'].label='Tiempo de Garantia'
		self.fields['precioMenudeo'].label='Precio al Publico'
		self.fields['precioMayoreo'].label='Precio de Mayoreo'


class DetallesEquipoForm(ModelForm):
	class Meta:
		model = DetallesEquipo
		exclude = ('gama','tiempoGarantia', 'marca', 'modelo', 'color')
	def __init__(self,  *args, **kwargs):
		super(DetallesEquipoForm, self).__init__(*args, **kwargs)
		self.fields['precioMenudeo'].label='Precio al Publico'
		self.fields['precioMayoreo'].label='Precio de Mayoreo'

	
class addEquipoForm(ModelForm):
	class Meta:
		model = Equipo
		
	def __init__(self, *args, **kwargs):
		super(addEquipoForm,self).__init__(*args,**kwargs)
		self.fields['accesorioEqu'].label='Accesorios de Equipo'
		self.fields['accesorioEqu'].widget.attrs['rows']='3'
		self.fields['accesorioEqu'].widget.attrs['cols']='15'
		self.fields['importeFactura'].label='Precio de Factura'

class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
    
'''#
class addObservacionEquipoForm(ModelForm):
	class Meta:
		model = ObservacionEquipo
		exclude = ('fecha','equipo', 'usuario')

	def __init__(self, *args, **kwargs):
		super(addObservacionEquipoForm,self).__init__(*args,**kwargs)
		self.fields['observ'].label='Observaciones del Equipo'
#'''

#"Agregar accesorios"
class addDetallesAccesorioForm(ModelForm):
	class Meta:
		model = DetallesAccesorio
		fields = ('folio', 'seccion','marca','descripcion','precioMenudeo', 'precioMayoreo')
	def __init__(self, *args, **kwargs):
		super(addDetallesAccesorioForm,self).__init__(*args,**kwargs)
		self.fields['precioMenudeo'].label='Precio Publico'
		self.fields['precioMayoreo'].label='Precio Mayoreo'

class DetallesAccesorioForm(ModelForm):
	class Meta:
		model = DetallesAccesorio
		exclude= ('marca', 'descripcion', 'seccion')
	def __init__(self, *args, **kwargs):
		super(DetallesAccesorioForm,self).__init__(*args,**kwargs)
		self.fields['precioMenudeo'].label='Precio Publico'
		self.fields['precioMayoreo'].label='Precio Mayoreo'

class MarcaAccesorioForm(forms.ModelForm):
    class Meta:
        model = MarcaAccesorio

class addAccesorioForm(ModelForm):
	class Meta:
		model = Accesorio
		exclude = ('sucursal','productoFacturado','estatusAccesorio')
'''	
class addObservacionAccesorioForm(ModelForm):
	class Meta:
		model = ObservacionAccesorio
		exclude=('fecha','accesorio','usuario')
	def __init__(self, *args, **kwargs):
		super(addObservacionAccesorioForm,self).__init__(*args,**kwargs)
		self.fields['observ'].label='Observaciones del Accesorio'
#'''

#"Agregar express"
class addDetallesExpresForm(ModelForm):

	class Meta:
		model = DetallesExpres
		exclude = ('descripcion','tipoIcc')
	def __init__(self, *args, **kwargs):
		super(addDetallesExpresForm,self).__init__(*args, **kwargs)
		self.fields['tiempoGarantia'].label='Tiempo de Garantia'
		self.fields['precioMenudeo'].label='Precio al Publico'
		self.fields['precioMayoreo'].label='Precio de Mayoreo'

class addExpresForm(ModelForm):
	
	class Meta:
		model = Expres
		exclude = ('estatus','sucursal','productoFacturado')
	
	def __init__(self, *args, **kwargs):
		super(addExpresForm,self).__init__(*args,**kwargs)
		self.fields['importeFactura'].label='Precio de Factura'

'''
class addObservacionExpresForm(ModelForm):
	
	class Meta:
		model = ObservacionExpres
		exclude=('fecha','expres','usuario')

	def __init__(self, *args, **kwargs):
		super(addObservacionExpresForm,self).__init__(*args,**kwargs)
		self.fields['observ'].label='Observaciones de la Expres'
#'''

#"Agregar fichas"

class addFichaForm(ModelForm):
	
	class Meta:
		model = Ficha
		exclude =('estatusFicha','productoFacturado','sucursal')

	def __init__(self, *args, **kwargs):
		super(addFichaForm,self).__init__(*args,**kwargs)
		self.fields['precioFac'].label='Precio de Factura'
'''	
class addObservacionFichasForm(ModelForm):
	
	class Meta:
		model = ObservacionFichas
		exclude=('ficha','fecha','usuario')

	def __init__(self, *args, **kwargs):
		super(addObservacionFichasForm,self).__init__(*args,**kwargs)
		self.fields['observ'].label='Observaciones de la Ficha'
#'''
#"Agregar Recargas"
class addTiempoAireForm(ModelForm):
	
	class Meta:
		model = TiempoAire

	def __init__(self, *args, **kwargs):
		super(addTiempoAireForm,self).__init__(*args,**kwargs)
		self.fields['precioFac'].label='Precio en Factura'

class MovimientoForm(ModelForm):
	class Meta:
		model = Movimiento
		exclude = ('fx_movimiento','sucursalOrigen','usuarioOrigen','usuarioDestino', 'tipoMovimiento', 'confirmacion')
	
	def __init__(self, *args, **kwargs):
		super(MovimientoForm,self).__init__(*args,**kwargs)
		self.fields['sucursalDestino'].label='Sucursal Destino'

class MovimientoDForm(ModelForm):
	class Meta:
		model = Movimiento
		exclude = ('fx_movimiento','usuarioOrigen','usuarioDestino', 'tipoMovimiento', 'confirmacion','sucursalDestino')

	def __init__(self,  *args, **kwargs):
		super(MovimientoDForm, self).__init__(*args, **kwargs)
		self.fields['sucursalOrigen'].queryset = Sucursal.objects.exclude(nombre='Almacen Central')
		self.fields['sucursalOrigen'].label='Sucursal Origen'
	

#"Agregar equipos"
	
class ListaEquipoForm(ModelForm):
	class Meta:
		model = ListaEquipo
		exclude = ('confirmacion','equipo')

#"Agregar accesorios"
class ListaAccesorioForm(ModelForm):
	class Meta:
		model = ListaAccesorio
		exclude = ('confirmacion','accesorio')


#"Agregar express"
class ListaExpresForm(ModelForm):
	class Meta:
		model = ListaExpres
		exclude = ('confirmacion','expres')
	

#"Agregar fichas"
class ListaFichasForm(ModelForm):
	class Meta:
		model = ListaFichas
		exclude = ('confirmacion','ficha')

class ListaFichasForm2(ModelForm):
	class Meta:
		model = ListaFichas
		exclude = ('confirmacion','movimiento')

#"Agregar Recargas"
class TransferenciaSaldoForm(ModelForm):
	class Meta:
		model = TransferenciaSaldo


class StockEquipoForm(ModelForm):
	class Meta:
		model = StockEquipo
	def __init__(self,  *args, **kwargs):
		super(StockEquipoForm, self).__init__(*args, **kwargs)
		self.fields['sucursal'].queryset = Sucursal.objects.all().order_by('nombre')
#"upd add Stocks accesorios"
class StockAccesorioForm(ModelForm):
	class Meta:
		model = StockAccesorio
	def __init__(self,  *args, **kwargs):
		super(StockAccesorioForm, self).__init__(*args, **kwargs)	
		self.fields['sucursal'].queryset = Sucursal.objects.all().order_by('nombre') 
	

#"upd- add Stocks express"
class StockExpresForm(ModelForm):
	class Meta:
		model = StockExpres
	def __init__(self,  *args, **kwargs):
		super(StockExpresForm, self).__init__(*args, **kwargs)
		self.fields['sucursal'].queryset = Sucursal.objects.all().order_by('nombre')

#"upd- add Stocks fichas"
class StockFichaForm(ModelForm): 
	class Meta:
		model = StockFicha
	def __init__(self,  *args, **kwargs):
		super(StockFichaForm, self).__init__(*args, **kwargs)
		self.fields['sucursal'].queryset = Sucursal.objects.all().order_by('nombre')

#" add - upd Stocks recargas"
class SaldoStockForm(ModelForm):
	class Meta:
		model = SaldoStock
	def __init__(self,  *args, **kwargs):
		super(SaldoStockForm, self).__init__(*args, **kwargs)
		self.fields['sucursal'].queryset = Sucursal.objects.all().order_by('nombre')


#--------------------fatyma was here --------------------------->
class addCliente(forms.Form):
	rfc 	= forms.CharField(max_length=15, required=True, help_text='Formato: [ABCD-AAMMDD-OM1]',initial='ABCD-AAMMDD-OM1')
	razonSocial = forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	direccion 	= forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	cp 			= forms.DecimalField(max_digits=5, decimal_places=0,required=True,help_text='Ejemplo: 75700, Sólo 5 digitos')
	colonia 	= forms.CharField(max_length=180,required=True)
	ciudad  	= forms.CharField(max_length=100,required=True)
	estado 		= forms.ChoiceField(required=True,choices=[(c.id, c.estado) for c in Estado.objects.all()], help_text='Elija el estado correspondiente a la colonia y ciudad')
	
	def __init__(self,  *args, **kwargs):
		super(addCliente, self).__init__(*args, **kwargs)
		self.fields['razonSocial'].label='Nombre o Razon Social'
		self.fields['rfc'].widget.attrs={'title':'Si el cliente ya se encuentra,el rfc del cliente se asignara'}


class addMayorista(ModelForm):
	conrfc = forms.BooleanField(required= False,initial=True, help_text='Desmarque la casilla para generar un RFC provisional.')
	class Meta:
		model = Mayorista
		exclude = ('cliente',)

	def __init__(self,  *args, **kwargs):
		super(addMayorista, self).__init__(*args, **kwargs)
		self.fields['descuentoRecargas'].label='Descuento en Recargas (%)'
		self.fields['descuentoFichas'].label='Descuento en Fichas (%)'
		self.fields['conrfc'].label='El cliente tiene RFC?'
		self.fields['conrfc'].widget.attrs={'title':'Desmarque la casilla para señalar que no cuenta con rfc y se asignara uno provisional'}
		

class addSubdistribuidor(ModelForm):
	
	class Meta:
		model = Subdistribuidor
		exclude = ('cliente','fxIngreso')

	def __init__(self,  *args, **kwargs):
		super(addSubdistribuidor, self).__init__(*args, **kwargs)
		self.fields['limCredito'].label='Limite de Credito $'
		self.fields['edo'].label='Cliente es'

class updCliente(forms.Form):
	key = forms.IntegerField()
	rfc 	= forms.CharField(max_length=15,required=True)
	razonSocial = forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	direccion 	= forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	cp 			= forms.DecimalField(max_digits=5, decimal_places=0,required=True,help_text='Ejemplo: 75700, Sólo 5 digitos')
	colonia 	= forms.CharField(max_length=180,required=True)
	ciudad  	= forms.CharField(max_length=100,required=True)
	estado 		= forms.ChoiceField(required=True,choices=[(c.id, c.estado) for c in Estado.objects.all()], help_text='Elija el estado correspondiente a la colonia y ciudad')
	
	def __init__(self,  *args, **kwargs):
		super(updCliente, self).__init__(*args, **kwargs)
		self.fields['razonSocial'].label='Nombre o Razon Social'
		self.fields['rfc'].widget.attrs={'title':'Si el cliente ya se encuentra,el rfc del cliente se asignara'}

class updMayorista(forms.Form):
	descuentoFichas = forms.DecimalField(max_digits=10,decimal_places=2, required=True)
	descuentoRecargas = forms.DecimalField(max_digits=10,decimal_places=2, required=True)
	
	def __init__(self,  *args, **kwargs):
		super(updMayorista, self).__init__(*args, **kwargs)
		self.fields['descuentoRecargas'].label='Descuento en Recargas (%)'
		self.fields['descuentoFichas'].label='Descuento en Fichas (%)'

class updSubdistribuidor(forms.Form):
	limCredito 	= forms.DecimalField(max_digits=10,decimal_places=2, required=True)
	edo 		= forms.ChoiceField(required=True,choices=[(c.id, c.estado) for c in EstadoSubdistribuidor.objects.all()])
	
	def __init__(self,  *args, **kwargs):
		super(updSubdistribuidor, self).__init__(*args, **kwargs)
		self.fields['limCredito'].label='Limite de Credito $'
		self.fields['edo'].label='Cliente es'

class updGarantia(forms.Form):
	key = forms.IntegerField()
	papeleta 	= forms.CharField(max_length=100)
	equipo 		= forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 3}) )
	falla 		= forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	fxAlmacen 	= forms.DateField(help_text='Fecha de Ingreso A almacen', required=True)
	fxCAC 		= forms.DateField(help_text='Fecha de atencion en CAC', required=False)
	observacion = forms.CharField(max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}),required=False )
	estado 		= forms.ChoiceField(required=True,choices=[(c.id, c.estado) for c in EstadoGarantia.objects.filter(Q(estado__icontains='En revision - Almacen') | Q(estado__icontains='Enviado a CAC')| Q(estado__icontains='Listo - Por enviar a Suc.')| Q(estado__icontains='Enviado a Sucursal'))])

	def __init__(self,  *args, **kwargs):
		super(updGarantia, self).__init__(*args, **kwargs)
		self.fields['fxCAC'].label='Fecha de Envio a CAC'
		self.fields['fxAlmacen'].label='Fecha de Ingreso a Almacen'
		self.fields['estado'].label='Seguimiento del equipo en Garantia'
		self.fields['papeleta'].widget.attrs={'readonly':True}
		self.fields['equipo'].widget.attrs={'readonly':True}
		self.fields['fxAlmacen'].widget= SelectDateWidget()
		self.fields['fxCAC'].widget= SelectDateWidget()

class addAbonoCredito(forms.Form):
	key 	= forms.IntegerField()
	subdistribuidor = forms.CharField(max_length=255)
	credito = forms.CharField(max_length=180)
	fxCredito  	= forms.CharField(max_length=32)
	totalvta 	= forms.DecimalField(max_digits=10,decimal_places=2)
	anticipos 	= forms.DecimalField(max_digits=10,decimal_places=2)
	faltante 	= forms.DecimalField(max_digits=10,decimal_places=2)
	abonar 		= forms.DecimalField(max_digits=10,decimal_places=2)

	def __init__(self,  *args, **kwargs):
		super(addAbonoCredito, self).__init__(*args, **kwargs)
		self.fields['key'].widget = forms.HiddenInput()
		self.fields['fxCredito'].label='Fecha del Credito'
		self.fields['totalvta'].label='Total de la venta a Credito'
		self.fields['subdistribuidor'].widget.attrs={'readonly':True}
		self.fields['credito'].widget.attrs={'readonly':True}
		self.fields['totalvta'].widget.attrs={'readonly':True}
		self.fields['anticipos'].widget.attrs={'readonly':True}
		self.fields['faltante'].widget.attrs={'readonly':True}

class AddVentaCaja(forms.Form):
	folioVenta 	= forms.CharField(max_length=80) #folio generado: V-suc-fecha-id
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

class AsignarMayorista(forms.Form):
	cliente = forms.ChoiceField(required=True,choices=[(c.id, c.cliente.rfc +' ' + c.cliente.razonSocial+' (%)Fichas: '+ str(c.descuentoFichas) +' (%)Rec.: '+ str(c.descuentoRecargas)  ) for c in Mayorista.objects.all()])

class AddVentaCredito(forms.Form):
	folioVenta 	= forms.CharField(max_length=80) 
	anticipo	= forms.DecimalField(max_digits=10,decimal_places=2, required=True)
	plazo 		= forms.IntegerField(required=True)
	observacion = forms.CharField(required=False, max_length=255,widget=forms.Textarea(attrs={'cols': 20, 'rows': 3}) )
	total 		= forms.DecimalField(max_digits=10,decimal_places=2)

	def __init__(self,  *args, **kwargs):
		super(AddVentaCredito, self).__init__(*args, **kwargs)
		self.fields['folioVenta'].label='Folio'
		self.fields['folioVenta'].widget.attrs={'readonly':True,'size':40}
		self.fields['total'].widget.attrs={'readonly':True}

class AsignarACredito(forms.Form):
	cliente = forms.ChoiceField(required=True,choices=[(c.id, c.cliente.rfc +' ' + c.cliente.razonSocial+' Limite: '+str(c.limCredito) ) for c in Subdistribuidor.objects.all()])
	
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

class addSecciones(ModelForm):

	class Meta:
		model=Secciones
		
class ProveedorForm(forms.ModelForm):
	class Meta:
		model = Proveedor