from django.db import models
from djCell.apps.catalogos.models import Ciudad,CP,Colonia, Estado
from djCell.apps.sucursales.models import Sucursal
from datetime import datetime, timedelta

# Clientes
class ClienteServicio(models.Model):
	nombre 		= models.CharField(max_length=180)
	direccion 	= models.TextField()
	colonia 	= models.ForeignKey(Colonia)
	ciudad  	= models.ForeignKey(Ciudad)
	sucursal 	= models.ForeignKey(Sucursal)
	fxIngreso	= models.DateTimeField(auto_now=True)
	tipoCliente = models.CharField(max_length=180)
	folio 		= models.CharField(max_length=80, unique=True)
	def __unicode__(self):
		cliente ="%s %s - %s - %s - %s"%(self.nombre, self.direccion, self.fxIngreso.strftime("%d-%m-%Y"), self.sucursal.nombre, self.tipoCliente)
		return cliente

	class Meta:
		ordering = ['-fxIngreso','folio','sucursal','nombre']

class ClienteFacturacion(models.Model):
	rfc 	= models.CharField(max_length=15, unique=True)
	razonSocial = models.CharField(max_length=255)
	direccion 	= models.TextField()
	colonia 	= models.ForeignKey(Colonia)
	ciudad 		= models.ForeignKey(Ciudad)
	cp 			= models.ForeignKey(CP)
	estado 		= models.ForeignKey(Estado)
	fxIngreso	= models.DateTimeField(auto_now=True) #add feb.14
	def __unicode__(self):
		cliente="%s - %s "%(self.rfc.upper(), self.razonSocial.title())
		return cliente

	class Meta:
		ordering = ['-fxIngreso','razonSocial','rfc']

class Mayorista(models.Model):
	cliente 		= models.ForeignKey(ClienteFacturacion, unique=True)
	descuentoFichas = models.DecimalField(max_digits=10,decimal_places=2, blank=True, null=True)
	descuentoRecargas = models.DecimalField(max_digits=10,decimal_places=2, blank=True, null=True)
	telefono = models.CharField(max_length=200, null=True, blank=True)
	def __unicode__(self):
		cliente ="%s - %s (%)Fichas: %s (%)Recargas: % %s"%(self.cliente.rfc, self.cliente.razonSocial, self.descuentoFichas, self.descuentoRecargas)
		return cliente

	class Meta:
		ordering = ['cliente']

		