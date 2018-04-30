from django.db import models
from django.contrib.auth.models import User
from djCell.apps.sucursales.models import Sucursal
from djCell.apps.personal.models import Empleado
from djCell.apps.productos.models import Equipo, Expres, Accesorio, Ficha
from datetime import datetime, timedelta

class ArqueoCaja(models.Model):
	fxArqueo 		= models.DateTimeField(auto_now=True)
	sucursal 		= models.ForeignKey(Sucursal)
	vendedor 		= models.ForeignKey(User)# usuario en tienda, sesion activa
	# tipo de empleado (auditor, analista, contador, admingral), no inicia sesion solo se verifica sus datos
	auditor 		= models.ForeignKey(Empleado) 
	totalCaja 		= models.DecimalField(max_digits=10,decimal_places=2)
	totalArqueo 	= models.DecimalField(max_digits=10,decimal_places=2)
	difArqueo 		= models.DecimalField(max_digits=10,decimal_places=2)
	addCtaEmpleado	= models.BooleanField(default=True)
	observaciones 	= models.TextField(null=True,blank=True)
	def __unicode__(self):
		arqueo="%s %s"%(self.sucursal, self.fxArqueo.strftime("%d-%m-%Y"))
		return arqueo

	class Meta:
		ordering = ['-fxArqueo','sucursal','vendedor','difArqueo']

class Inventario(models.Model):
	folio 	= models.CharField(max_length=200) #folio generado aud-suc-fecha-id
	fxInicio 	= models.DateTimeField(auto_now=True)
	fxFinal 	= models.DateTimeField(auto_now=True)
	sucursal 	= models.ForeignKey(Sucursal)
	difEquipo 	= models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True, default=0)
	difExpres 	= models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True, default=0)
	difFicha 	= models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True, default=0)
	difAccesorio 	= models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True, default=0)
	difOtros 	= models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True, default=0) #se quito apartado por accesorio
	difStreet 	= models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True, default=0)
	sancion 	= models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True, default=0)
	descSancion = models.TextField(null=True,blank=True) #descripcion de la sancion
	elevado 	= models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True, default=1)
	determina 	= models.ForeignKey(User)
	observaciones 	= models.TextField(null=True,blank=True)
	terminada = models.BooleanField(default=False) # fin de inventario fisico
	cerrado = models.BooleanField(default=False) # fin de la auditoria - aqui es cuando se determina
	def __unicode__(self):
		auditoria ="%s || %s"%(self.folio, self.sucursal.nombre)
		return auditoria

	class Meta:
		ordering = ['-fxFinal','sucursal','determina']

class InventarioAuditores(models.Model):
	inventario = models.ForeignKey(Inventario, null=True, blank=True)
	auditor    = models.ForeignKey(Empleado)
	turno	   = models.BooleanField(default=False)

	def __unicode__(self):
		auditoria ="%s <--- %s"%(self.inventario, self.auditor)
		return auditoria


class InvEquipo(models.Model):
	inventario 	= models.ForeignKey(Inventario)
	equipo 		= models.ForeignKey(Equipo)
	existe 		= models.BooleanField(default=False)
	accesorios	= models.BooleanField(default=False)
	observacion = models.TextField(blank=True, null=True)
	revisado	= models.BooleanField(default=False)
	fxRevision 	=models.DateTimeField(auto_now=True)
	def __unicode__(self):
		item="%s %s"%(self.inventario.folio,self.equipo)
		return item

	class Meta:
		ordering = ['-fxRevision','inventario','revisado','equipo']

class InvExpres(models.Model):
	inventario 	= models.ForeignKey(Inventario)
	expres  	= models.ForeignKey(Expres)
	existe 		= models.BooleanField(default=False)
	observacion = models.TextField(blank=True, null=True)
	revisado	= models.BooleanField(default=False)
	fxRevision 	=models.DateTimeField(auto_now=True)
	def __unicode__(self):
		item="%s %s"%(self.inventario.folio,self.expres.icc)
		return item

	class Meta:
		ordering = ['-fxRevision','inventario','revisado','expres']

class InvAccesorio(models.Model):
	inventario 	= models.ForeignKey(Inventario)
	accesorio 	= models.ForeignKey(Accesorio)
	existe 		= models.BooleanField(default=False)
	observacion = models.TextField(blank=True, null=True)
	revisado	= models.BooleanField(default=False)
	fxRevision 	=models.DateTimeField(auto_now=True)
	def __unicode__(self):
		item="%s %s"%(self.inventario.folio,self.accesorio.codigoBarras)
		return item

	class Meta:
		ordering = ['-fxRevision','inventario','revisado','accesorio']

class InvFicha(models.Model):
	inventario 	= models.ForeignKey(Inventario)
	ficha 		= models.ForeignKey(Ficha)
	existe 		= models.BooleanField(default=False)
	observacion = models.TextField(blank=True, null=True)
	revisado	= models.BooleanField(default=False)
	fxRevision 	=models.DateTimeField(auto_now=True)
	def __unicode__(self):
		item="%s %s"%(self.inventario.folio,self.ficha.folio)
		return item

	class Meta:
		ordering = ['-fxRevision','inventario','revisado','ficha']