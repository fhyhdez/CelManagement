from django.db import models

from djCell.apps.catalogos.models import Ciudad,CP,Colonia, Estado
from djCell.apps.ventas.models import Venta
from djCell.apps.clientes.models import ClienteFacturacion
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class EstadoSubdistribuidor(models.Model):
	estado = models.CharField(max_length=80, unique=True)
	def __unicode__(self):
		return self.estado

	class Meta:
		ordering = ['estado']

class Subdistribuidor(models.Model):
	cliente 	= models.ForeignKey(ClienteFacturacion)
	limCredito 	= models.DecimalField(max_digits=10,decimal_places=2)
	fxIngreso 	= models.DateTimeField(auto_now=True) #fatyma was here
	edo 		= models.ForeignKey(EstadoSubdistribuidor)
	telefono = models.CharField(max_length=200, null=True, blank=True)
	def __str__(self):
		cliente ="%s --- %s"%(self.cliente.razonSocial,self.cliente.rfc)
		return cliente

	class Meta:
		ordering = ['-fxIngreso','cliente']

class EstadoCredito(models.Model):
	estado 		= models.CharField(max_length=80)
	def __unicode__(self):
		return self.estado

	class Meta:
		ordering = ['estado']

class Credito(models.Model):
	folioc 		= models.CharField(max_length=80) #generar clave CR-AAMMDD-INT_Cred
	subdist 	= models.ForeignKey(Subdistribuidor)
	venta 		= models.ForeignKey(Venta, related_name='venta_a_credito')
	totalvta 	= models.DecimalField(max_digits=10,decimal_places=2) #guardar el monto de venta
	plazo 		= models.IntegerField()
	fxCredito 	= models.DateTimeField(auto_now=True) #fecha del credito
	edo 		= models.ForeignKey(EstadoCredito) #pagado, no pagado, retrasado, puntual, default Nuevo Credito
	observacion = models.TextField(null=True, blank=True)
	def __unicode__(self):
		credSubdist ="%s - %s --- %s . %s . %s"%(self.subdist, self.venta.folioVenta, self.totalvta, self.fxCredito.strftime("%d-%m-%Y %X"), self.edo.estado)
		return credSubdist

	class Meta:
		ordering = ['-fxCredito','subdist','folioc']

class HistorialSubdistribuidor(models.Model):
	credito = models.ForeignKey(Credito)
	abono 	= models.DecimalField(max_digits=10,decimal_places=2)
	fxAbono = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		historial="%s %s %s"%(self.credito, self.abono, self.fxAbono.strftime("%d-%m-%Y %X"))
		return historial

	class Meta:
		ordering = ['-fxAbono','credito','abono']