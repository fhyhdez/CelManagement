#encoding:utf-8 
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import Group
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.forms.extras.widgets import SelectDateWidget
from django.db.models import Q
from datetime import datetime, timedelta

from djCell.apps.personal.models import Empleado, Usuario
from djCell.apps.contabilidad.models import Nomina, NominaEmpleado, TipoCuenta, CuentaEmpleado, HistorialEmpleado, Metas, Caja, Gastos,LineaCredito, HistLCredito, Cuenta, CuentaHistorial, HistorialCaja
from djCell.apps.personal.models import Area, Puesto
from djCell.apps.sucursales.models import VendedorSucursal
from djCell.apps.proveedor.models import Proveedor
from djCell.apps.clientes.models import ClienteFacturacion
from djCell.apps.facturacion.models import Facturacion
from djCell.apps.auditoria.models import Inventario, InventarioAuditores
from djCell.apps.sucursales.models import EstadoSucursal, TipoSucursal, Sucursal, VendedorSucursal
from djCell.apps.catalogos.models import Estado, Ciudad, Colonia, CP, Zona
# "Seccion de Nomina">Nomina


# "Empleados">Empleados
anterior = datetime.now().date().year - 100
ielactual = datetime.now().date().year - 15
#contabilidad/nomina/empleados/nuevo" "Agregar Nuevo Empleado">Nuevo
class EmpleadoForm(ModelForm):
	class Meta:
		model = Empleado
		exclude = ('colonia','ciudad')
	def __init__(self,  *args, **kwargs):
		super(EmpleadoForm, self).__init__(*args, **kwargs)
		#self.fields['colonia'] = forms.CharField(max_length=100,required=True)
		#self.fields['ciudad'] = forms.CharField(max_length=100,required=True)
		self.fields['puesto'].queryset = Puesto.objects.all()
		self.fields['area'].queryset = Area.objects.all()
		self.fields['aPaterno'].label='Apellido Paterno'
		self.fields['aMaterno'].label='Apellido Materno'
		self.fields['fxNacimiento'].label='Fecha de Nacimiento'
		self.fields['curp'].label='CURP'
		self.fields['salarioxDia'].label='Salario por Dia'
		self.fields['estadoEmpleado'].label='Empleado Activo'
		self.fields['fxNacimiento'].widget=SelectDateWidget(years=range(anterior,ielactual))

class VendedorSucursalForm(ModelForm):
	class Meta:
		model = VendedorSucursal
		exclude=('empleado',)
    
class ColoniaCiudad(forms.Form):
	colonia 	= forms.CharField(max_length=180,required=True)
	ciudad  	= forms.CharField(max_length=100,required=True)
		
#contabilidad/nomina/empleados/reporte" "Consulta y reporte de Empleados">Reporte

# "Estados de cuenta de empleados">Estados Cta

#contabilidad/nomina/empleados/estado_cta/agregar" "Agregar nuevo estado de cuenta a empleado">Agregar
class CuentaEmpleadoForm(ModelForm):
	class Meta:
		model = CuentaEmpleado
		exclude = ('fxCreacion','adeudo', 'folio')
	
	def __init__(self,  *args, **kwargs):
		super(CuentaEmpleadoForm, self).__init__(*args, **kwargs)
		self.fields['empleado'].queryset = Empleado.objects.all().order_by('curp')
		self.fields['tipoCuenta'].queryset = TipoCuenta.objects.all().order_by('tipo')

class HistorialEmpleadoForm(ModelForm):

	class Meta:
		model = HistorialEmpleado 
		exclude =('fxPago',)
	
	def __init__(self,  *args, **kwargs):
		super(HistorialEmpleadoForm, self).__init__(*args, **kwargs)
		self.fields['cuentaEmpleado'].queryset = CuentaEmpleado.objects.None()

#contabilidad/nomina/empleados/estado_cta/historial" "Consulta y reporte de estados de cuenta de empleados">Historial




#contabilidad/nomina/usuarios" "Consulta y reporte de usuarios existentes">Usuarios

#contabilidad/nomina/nueva_nomina" "Nueva nomina">Nueva Nomina
class NominaForm(ModelForm):

	class Meta:
		model = Nomina
		exclude = ('folio','cerrar')

class NominaEmpleadoForm(forms.ModelForm):
	class Meta:
		model = NominaEmpleado
		exclude =('salarioDia', 'total', 'fxPago', 'pagado', 'folio')
	
	def __init__(self,  *args, **kwargs):
		super(NominaEmpleadoForm, self).__init__(*args, **kwargs)
		self.fields['empleado'].queryset = Empleado.objects.all().order_by('curp')
    




class CuentaForm(forms.ModelForm):
	class Meta:
		model = Cuenta

class GastosForm(forms.ModelForm):
	class Meta:
		model = Gastos
	def __init__(self,  *args, **kwargs):
		super(GastosForm, self).__init__(*args, **kwargs)
		
		self.fields['fxGasto'].widget=SelectDateWidget()

class HistorialCajaForm(forms.ModelForm):
	class Meta:
		model = HistorialCaja
		exclude =('caja', 'abono')

class CuentaHistorialForm(forms.ModelForm):
	class Meta:
		model = CuentaHistorial
		exclude = ('deposito',)

class ProveedorForm(forms.ModelForm):
	rfc = forms.CharField(max_length=15,required=True,label='RFC' ,help_text='Formato: [ABCD-AAMMDD-OM1]',initial='ABCD-AAMMDD-OM1')
	class Meta:
		model = Proveedor


class LineaCreditoForm(forms.ModelForm):
	class Meta:
		model = LineaCredito
		exclude = ('deuda', 'pagado')

class HistLCreditoForm(forms.ModelForm):
	class Meta:
		model = HistLCredito

class InventarioAuditoresForm(forms.ModelForm):
	class Meta:
		model = InventarioAuditores
	def __init__(self,  *args, **kwargs):
		super(InventarioAuditoresForm, self).__init__(*args, **kwargs)
		_queryset =Usuario.objects.filter(Q(permiso__nivel=2)|Q(permiso__nivel=3)|Q(permiso__nivel=4))
		#self.fields['auditor'].queryset = Empleado.objects.filter(Q(puesto__puesto__icontains='Analista de Contabilidad') | Q(puesto__puesto__icontains='Auditores') | Q(puesto__puesto__icontains='conta'))
		empleados =[]
		for x in _queryset:
			empleados.append( [x.empleado.id, str(x.empleado)])
		self.fields['auditor'].choices = empleados


class ClienteFacturacionForm(forms.Form):
	rfc 		= forms.CharField(max_length=180,required=True, help_text='Formato: [ABCD-AAMMDD-OM1]',initial='ABCD-AAMMDD-OM1')
	razonSocial	= forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	direccion 	= forms.CharField(max_length=255,required=True,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	colonia 	= forms.CharField(max_length=180,required=True)
	ciudad  	= forms.CharField(max_length=100,required=True)
	cp 			= forms.DecimalField(required=True,max_digits=5,decimal_places=0,help_text='Ejemplo: 75700, Sólo 5 digitos')
	estado 		= forms.ChoiceField(required=True,choices=[(c.id, c.estado) for c in Estado.objects.all()], help_text='Elija el estado correspondiente a la colonia y ciudad')
	def __init__(self,*args,**kwargs):
		super(ClienteFacturacionForm,self).__init__(*args,**kwargs)
		self.fields['razonSocial'].label='Nombre de Persona Fisica o Moral'
		self.fields['cp'].label='Codigo Postal'


class FacturacionForm(forms.ModelForm):
	class Meta:
		model = Facturacion
		exclude = ('clienteFacturacion', 'totalvta')

class FacturacionAGranel(forms.Form):
	rfc = forms.CharField(max_length=15, help_text='Formato: [ABCD-AAMMDD-OM1]', required=True)
	folio = forms.CharField(max_length=20,required=True)


class InventarioForm(forms.ModelForm):
	class Meta:
		model = Inventario
		exclude = ('folio', 'difEquipo', 'difExpres', 'difFicha', 'difAccesorio', 'difApartados', 'difStreet', 'determina', 'terminada', 'cerrado', 'elevado', 'difOtros', 'sancion', 'descSancion')


class addSucursal(forms.Form):
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
	tipo 		= forms.ChoiceField(choices=[(c.id, c.tipo ) for c in TipoSucursal.objects.all().order_by('tipo')], help_text='Elija el Tipo de Sucursal')
	
	def __init__(self,  *args, **kwargs):
		super(addSucursal, self).__init__(*args, **kwargs)
		self.fields['noCelOfi'].label='No. de Celular de oficina (Opcional)'
		self.fields['encargado'].widget.attrs = {'title':'Vendedores sin asignar Sucursal como encargados'}
		self.fields['zona2'].label='¿Nueva Zona?'

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

class conSucursal(forms.Form):
	sucursal = forms.ChoiceField(required=True,choices=[(c.id, c.nombre) for c in Sucursal.objects.all().order_by('nombre')])


class VerificacionForm(forms.Form):
	totalCorte = forms.DecimalField(required=True,max_digits=12,decimal_places=2)
	observacion	= forms.CharField(max_length=255,required=False,widget=forms.Textarea(attrs={'cols': 20, 'rows': 5}) )
	def __init__(self,  *args, **kwargs):
		super(VerificacionForm, self).__init__(*args, **kwargs)
		self.fields['totalCorte'].label='Total del Corte'
		self.fields['observacion'].label='Observacion'