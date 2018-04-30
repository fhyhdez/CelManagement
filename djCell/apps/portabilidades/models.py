from django.db import models
from djCell.apps.catalogos.models import Ciudad,CP,Colonia, Estado
from djCell.apps.clientes.models import ClienteServicio
from djCell.apps.sucursales.models import Sucursal
from djCell.apps.servicios.models import EstadoReparacion
from datetime import datetime, timedelta

class EstadoPortabilidad(models.Model):
	estado = models.CharField(max_length=80)
	def __unicode__(self):
		return self.estado
	class Meta:
		ordering = ['estado']

class Portabilidad(models.Model):
	cliente 	= models.ForeignKey(ClienteServicio)
	noaPortar 	= models.CharField(max_length=80)#*** modificado
	flexearEquipo = models.BooleanField(default=False)
	fxIngreso 	= models.DateField(auto_now=True)
	estado 		= models.ForeignKey(EstadoPortabilidad)
	sucursal 	= models.ForeignKey(Sucursal)
	fxRevision	= models.DateTimeField(null=True,blank=True)# ultima fecha de revision
	def __unicode__(self):
		portabilidad="%s %s %s %s"%( self.cliente.nombre, self.cliente.direccion, self.noaPortar, self.fxIngreso.strftime("%d-%m-%Y"))
		return portabilidad

	class Meta:
		ordering = ['-fxIngreso','cliente__nombre']

class FlexeoEquipo(models.Model):
	portabilidad 	= models.ForeignKey(Portabilidad)
	marcaModelo 	= models.CharField(max_length=150)
	observaciones 	= models.TextField(null=True, blank=True)
	fxSucursal 	= models.DateTimeField(auto_now=True) #entregado a sucursal
	fxTecnico 	= models.DateTimeField(null=True,blank=True) #entregado a tecnico
	fxCliente 	= models.DateTimeField(null=True,blank=True) #entregado cliente- flexeo realizado
	estado 		= models.ForeignKey(EstadoReparacion)# 22 feb
	fxRevision	= models.DateTimeField(null=True,blank=True)# ultima fecha de revision
	def __unicode__(self):
		return str(self.portabilidad.cliente)

	class Meta:
		ordering = ['-fxSucursal','portabilidad__cliente__nombre']
		