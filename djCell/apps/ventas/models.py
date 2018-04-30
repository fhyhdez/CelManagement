from django.db import models
from djCell.apps.sucursales.models import Sucursal
from djCell.apps.planes.models import Plan
from djCell.apps.productos.models import Equipo,Expres,Accesorio,Ficha
from djCell.apps.recargas.models import Recarga
from djCell.apps.clientes.models import Mayorista
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class EstadoVenta(models.Model):
	estado = models.CharField(max_length=80)
	def __unicode__(self):
		return self.estado

	class Meta:
		ordering = ['estado']

class TipoPago(models.Model):
	tipo = models.CharField(max_length=80)
	def __unicode__(self):
		return self.tipo

	class Meta:
		ordering = ['tipo']
		

class Venta(models.Model):
	folioVenta 	= models.CharField(max_length=80, unique=True) #folio generado: V-suc-fecha-id
	fecha 		= models.DateTimeField(auto_now=True)
	sucursal 	= models.ForeignKey(Sucursal)
	usuario 	= models.ForeignKey(User) #quien hace la venta
	total 		= models.DecimalField(max_digits=10,decimal_places=2)
	tipoPago 	= models.ForeignKey(TipoPago)
	aceptada 	= models.BooleanField(default=True)
	mayoreo  	= models.BooleanField(default=False)
	credito  	= models.BooleanField(default=False)
	estado 		= models.ForeignKey(EstadoVenta)
	facturada 	= models.BooleanField(default=False)
	activa 		= models.BooleanField(default=True)
	def __unicode__(self):
		folio="%s --- %s"%(self.fecha.strftime("%d-%m-%Y"),self.folioVenta)
		return folio

	class Meta:
		ordering = ['-fecha','folioVenta','sucursal']

class VentaMayoreo(models.Model):
	folioVenta 		= models.ForeignKey(Venta)
	clienteMayoreo 	= models.ForeignKey(Mayorista)
	descuentoAplicado = models.DecimalField(max_digits=10,decimal_places=2)
	def __unicode__(self):
		return self.folioVenta.folioVenta

	class Meta:
		ordering = ['-folioVenta']

class Anticipo(models.Model):
	folioVenta 		= models.ForeignKey(Venta)
	tipoAnticipo 	= models.CharField(max_length=80) # apartado, servicio tecnico, planes, <- control interno
	observacion 	= models.TextField(null=True,blank=True)
	monto 			= models.DecimalField(max_digits=10,decimal_places=2)
	def __unicode__(self):
		return self.folioVenta.folioVenta

	class Meta:
		ordering = ['-folioVenta']
		

class VentaEquipo(models.Model):
	venta  		= models.ForeignKey(Venta)
	precVenta 	= models.DecimalField(max_digits=10,decimal_places=2)
	equipo 		= models.ForeignKey(Equipo)
	def __unicode__(self):
		ventaEquipo="%s %s"%(self.venta,self.equipo)
		return ventaEquipo

	class Meta:
		ordering = ['-venta']

class VentaExpres(models.Model):
	venta 		= models.ForeignKey(Venta)
	precVenta 	= models.DecimalField(max_digits=10,decimal_places=2)
	expres 		= models.ForeignKey(Expres)
	def __unicode__(self):
		ventaExpres="%s %s"%(self.venta,self.expres)
		return ventaExpres

	class Meta:
		ordering = ['-venta']

class VentaAccesorio(models.Model):
	venta 		= models.ForeignKey(Venta)
	precVenta 	= models.DecimalField(max_digits=10,decimal_places=2)
	accesorio 	= models.ForeignKey(Accesorio)
	def __unicode__(self):
		ventaAccesorio="%s %s"%(self.venta,self.accesorio)
		return ventaAccesorio

	class Meta:
		ordering = ['-venta']

class VentaFichas(models.Model):
	venta 		= models.ForeignKey(Venta)
	precVenta 	= models.DecimalField(max_digits=10,decimal_places=2)
	ficha 		= models.ForeignKey(Ficha)
	def __unicode__(self):
		ventaFicha="%s %s"%(self.venta,self.ficha)
		return ventaFicha
	class Meta:
		ordering = ['-venta']

class VentaRecarga(models.Model):
	venta 		= models.ForeignKey(Venta)
	precVenta 	= models.DecimalField(max_digits=10,decimal_places=2)
	recarga 	= models.ForeignKey(Recarga)
	def __unicode__(self):
		ventaRecarga="%s %s"%(self.venta,self.recarga)
		return ventaRecarga
	class Meta:
		ordering = ['-venta']

class VentaPlan(models.Model):
	venta 		= models.ForeignKey(Venta)
	precVenta 	= models.DecimalField(max_digits=10,decimal_places=2)
	plan 		= models.ForeignKey(Plan)
	observacion = models.TextField(null=True, blank=True) #pago de renta por adquirir plan
	def __unicode__(self):
		ventaPlan="%s %s"%(self.venta,self.plan.plan)
		return ventaPlan
	class Meta:
		ordering = ['-venta']

class Renta(models.Model):
	venta 		= models.ForeignKey(Venta)
	numeroReferencia = models.CharField(max_length=50)
	abono 		= models.DecimalField(max_digits=10,decimal_places=2)
	fecha 		= models.DateTimeField(auto_now=True)
	sucursal 	= models.ForeignKey(Sucursal)
	usuario 	= models.ForeignKey(User)
	observacion = models.TextField(null=True, blank=True) #banco etc
	def __unicode__(self):
		ventaRenta="%s %s"%(self.venta,self.numeroReferencia)
		return ventaRenta
	class Meta:
		ordering = ['-venta']

class Cancelaciones(models.Model):
	venta 		= models.ForeignKey(Venta)
	empleado 	= models.ForeignKey(User, null=True,blank=True) # quien autoriza la cancelacion
	fxCancelacion = models.DateTimeField(auto_now=True)
	activo 		= models.BooleanField(default=True)
	def __unicode__(self):
		cancelacion ="%s %s %s"%(self.venta.folioVenta, self.empleado, self.fxCancelacion.strftime("%d-%m-%Y"))
		return cancelacion
	class Meta:
		ordering = ['-venta']