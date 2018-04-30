# -*- coding: utf-8 -*-
from django.db import models
from djCell.apps.personal.models import Empleado
from djCell.apps.proveedor.models import Proveedor
from djCell.apps.corteVta.models import CorteVenta
from django.contrib.auth.models import User
from datetime import datetime

class TipoCuenta(models.Model):
	tipo = models.CharField(max_length=80, unique=True)
	def __unicode__(self):
		return self.tipo

	class Meta:
		ordering = ['tipo']

class CuentaEmpleado(models.Model):
	folio 		= models.CharField(max_length=15)
	empleado 	= models.ForeignKey(Empleado)
	tipoCuenta 	= models.ForeignKey(TipoCuenta, verbose_name="Tipo de Cuenta")
	monto 		= models.DecimalField(max_digits=10,decimal_places=2)
	fxCreacion 	= models.DateTimeField(auto_now=True)
	observacion = models.TextField(null=True,blank=True, verbose_name="Observaciones")
	adeudo  = models.DecimalField(max_digits=10,decimal_places=2)
	def __unicode__(self):
		cuenta="%s %s %s || %s || %s || $%s || %s"%(self.empleado.nombre, self.empleado.aPaterno, self.empleado.aMaterno, self.empleado.curp,self.tipoCuenta.tipo, self.monto, self.fxCreacion.strftime("%d-%m-%Y"))
		return cuenta

	class Meta:
		ordering = ['-fxCreacion','folio','tipoCuenta__tipo','empleado__nombre','empleado__curp']

class HistorialEmpleado(models.Model):
	cuentaEmpleado 	= models.ForeignKey(CuentaEmpleado, verbose_name="Cuenta del Empleado")	
	descuento 		= models.DecimalField(max_digits=10,decimal_places=2)
	fxPago			= models.DateTimeField(auto_now=True)
	observacion 	= models.TextField(null=True,blank=True)
	def __unicode__(self):
		historialEmpleado="%s %s %s"%(self.cuentaEmpleado.empleado.curp,self.descuento, self.fxPago.strftime("%d-%m-%Y"))
		return historialEmpleado

	class Meta:
		ordering = ['-fxPago','cuentaEmpleado__folio','descuento']


class Nomina(models.Model):
	folio = models.CharField(max_length=50, null=True, blank=True)
	fxCreacion	= models.DateField(auto_now=True)
	descripcion = models.TextField()
	cerrar = models.BooleanField(default=False)#dato agregado para mejor control
	def __unicode__(self):
		nomina="%s"%(self.folio)
		return nomina

	class Meta:
		ordering = ['-fxCreacion','folio','descripcion']

class NominaEmpleado(models.Model):
	nomina = models.ForeignKey(Nomina)
	empleado 	= models.ForeignKey(Empleado)
	diasTrab 	= models.DecimalField(max_digits=10,decimal_places=2,default=0, verbose_name="Dias trabajados")
	salarioDia = models.DecimalField(max_digits=10,decimal_places=2, blank=True, null=True, default=0)
	bonoPuntualidad = models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True, default=0, verbose_name="Bono de Puntualidad")
	bonoProductividad= models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True, default=0, verbose_name="Bono de Productividad")
	bonoVales 		= models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True, default=0, verbose_name="Vales de Despensa")
	descuento 	= models.DecimalField(max_digits=10,decimal_places=2, default=0) # .ForeignKey(HistorialEmpleado) descuento de historial
	observacion 	= models.TextField(null=True,blank=True, default='')
	total = models.DecimalField(max_digits=10,decimal_places=2, blank=True, null=True, default=0)
	pagado 		= models.BooleanField(default=False)
	fxCreacion		= models.DateField(auto_now=True)
	fxPago 		= models.DateTimeField(null=True, blank=True)
	def __unicode__(self):
		nomina="%s || %s || %s %s %s "%(self.nomina.folio,self.empleado.curp,self.empleado.nombre, self.empleado.aPaterno, self.empleado.aMaterno)
		return nomina

	class Meta:
		ordering = ['-fxPago','-nomina__folio','empleado__curp','empleado__nombre']

class Metas(models.Model):
	empleado 	= models.ForeignKey(Empleado)
	metaEquipo 	= models.IntegerField()
	metaPlanes 	= models.IntegerField()
	metaServicios = models.IntegerField()
	def __unicode__(self):
		metas="%s %s %s %s %s %s %s"%(self.empleado.curp,self.empleado.nombre, self.empleado.aPaterno, self.empleado.aMaterno, self.metaEquipo, self.metaPlanes, self.metaServicios)
		return metas

	class Meta:
		ordering = ['empleado__nombre','empleado__curp','metaEquipo']

class Caja(models.Model):
	nombre 	= models.CharField(max_length=100)
	saldo 		= models.DecimalField(max_digits=10,decimal_places=2, default=0)
	def __unicode__(self):
		return self.saldo

	class Meta:
		ordering = ['saldo']

class HistorialCaja(models.Model):
	caja = models.ForeignKey(Caja)
	fxIngreso 	= models.DateTimeField(auto_now=True)
	monto 		= models.DecimalField(max_digits=10,decimal_places=2)
	descripcion = models.TextField()
	abono 		= models.BooleanField()
	def __unicode__(self):
		caja="%s %s"%(self.fxIngreso.strftime("%d-%m-%Y"), self.monto)
		return caja

	# d = today.strftime("%d%m%Y") 
	class Meta:
		ordering = ['-fxIngreso','monto']

class Gastos(models.Model):
	#proveedor 	= models.ForeignKey(Proveedor) # se quita porque no lo usa
	folioNota 	= models.CharField(max_length=80, verbose_name="Folio de la Nota")
	descripcion = models.CharField(max_length=80, verbose_name="Descripcion del pago")
	fxGasto 	= models.DateField(verbose_name="Fecha del Gasto")
	fxRegistro 	= models.DateTimeField(auto_now=True)
	monto 		= models.DecimalField(max_digits=10,decimal_places=2)
	observacion = models.TextField(null=True, blank=True, verbose_name="Observaciones extras")
	def __unicode__(self):
		gastos="%s %s $%s %s"%(self.folioNota, self.fxGasto.strftime("%d-%m-%Y"), self.monto,self.observacion )
		return gastos
	
	class Meta:
		ordering = ['-fxGasto','descripcion','monto']

# Polizas - ingresos y egresos
class Cuenta(models.Model):
	cuenta 		= models.CharField(max_length=180)
	nocuenta 	= models.CharField(max_length=80, unique=True, verbose_name="No. de Cuenta")
	saldo = models.DecimalField(max_digits=10,decimal_places=2, default=0)
	observacion = models.TextField(null=True,blank=True)
	fxIngreso 	= models.DateTimeField(auto_now=True)
	def __unicode__(self):
		cta ="%s %s"%(self.cuenta, self.nocuenta)
		return cta

class EstadoPoliza(models.Model):
	estado = models.CharField(max_length=30, unique=True)
	def __unicode__(self):
		return self.estado
			
	class Meta:
		ordering = ['estado']

class CuentaHistorial(models.Model): # para manejo de cheques o bancos
	cheque 		= models.DecimalField(decimal_places=0, max_digits=10, unique=True) # se agrega para control interno
	poliza 		= models.IntegerField(null=True,blank=True) #agregado control interno
	noReferencia 	= models.CharField(max_length=80, unique=True, verbose_name="Descripcion")
	fecha 		= models.DateTimeField(auto_now=True)
	cuenta 		= models.ForeignKey(Cuenta)
	proveedor 	= models.ForeignKey(Proveedor, null=True, blank=True)
	concepto 	= models.CharField(max_length=250)
	cantidad	= models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
	deposito	= models.BooleanField(default=True)
	estado		= models.ForeignKey(EstadoPoliza) # confirmado o cancelado
	def __unicode__(self):
		return self.noReferencia
	
	class Meta:
		ordering = ['-fecha','cheque']

# Linea de Credito
class LineaCredito(models.Model):
	proveedor 	= models.ForeignKey(Proveedor)
	notaCredito = models.CharField(max_length=80, verbose_name="Nota del Credito")
	total 		= models.DecimalField(max_digits=10,decimal_places=2)
	fxCredito 	= models.DateTimeField(auto_now=True)
	deuda 		= models.DecimalField(max_digits=10,decimal_places=2, default=0)
	pagado 		= models.BooleanField(default=False)
	def __unicode__(self):
		lineaCredito ="%s - %s || Nota: %s - $ %s || %s "%(self.proveedor.rfc, self.proveedor.nombre, self.notaCredito, self.total, self.fxCredito.strftime("%d-%m-%Y"))
		return lineaCredito
	
	class Meta:
		ordering = ['-fxCredito','proveedor']

class HistLCredito(models.Model):
	lineaCredito = models.ForeignKey(LineaCredito, verbose_name="Linea de Credito")
	abono 		= models.DecimalField(max_digits=10,decimal_places=2)
	fxAbono 	= models.DateTimeField(auto_now=True)
	observacion = models.TextField(blank=True, null=True)
	def __unicode__(self):
		historialCredito ="%s %s %s %s"%(self.lineaCredito.proveedor.rfc, self.lineaCredito.proveedor.nombre, self.abono, self.fxAbono.strftime("%d-%m-%Y"))
		return historialCredito
	
	class Meta:
		ordering = ['-fxAbono','lineaCredito__notaCredito']
