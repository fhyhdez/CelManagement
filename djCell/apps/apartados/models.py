from django.db import models
from django.contrib.auth.models import User
from djCell.apps.personal.models import Empleado
from djCell.apps.sucursales.models import Sucursal
from djCell.apps.productos.models import DetallesEquipo
from djCell.apps.clientes.models import ClienteServicio
from djCell.apps.ventas.models import Venta
from datetime import datetime, timedelta

class EstadoApartado(models.Model):
	estado = models.CharField(max_length=80, unique=True)
	def __unicode__(self):
		return self.estado

	class Meta:
		ordering = ['estado']

class Apartado(models.Model):
	clienteApartado = models.ForeignKey(ClienteServicio)
	equipo 			= models.ForeignKey(DetallesEquipo)
	observacion 	= models.TextField(null=True,blank=True)
	precioEquipo 	= models.DecimalField(max_digits=10,decimal_places=2) # precio actual del equipo
	fxApartado 		= models.DateTimeField(auto_now=True)
	pagado = models.BooleanField(default=False)
	estado = models.ForeignKey(EstadoApartado)
	def __unicode__(self):
		apartado ="%s %s %s %s %s"%(self.equipo.detallesEquipo.marca.marca,self.equipo.detallesEquipo.modelo, self.equipo.imei, self.clienteApartado.nombre, self.monto)
		return apartado

	class Meta:
		ordering = ['-fxApartado','clienteApartado','equipo']

class HistorialApartado(models.Model):
	apartado 	= models.ForeignKey(Apartado)
	abono 		= models.DecimalField(max_digits=10,decimal_places=2)
	tipo 		= models.CharField(max_length=20)
	fxAbono 	= models.DateTimeField(auto_now=True)
	def __unicode__(self):
		historialApartado ="%s %s %s"%(self.apartado.clienteApartado.nombre, self.abono, self.fxAbono.strftime("%d%m%Y"))
		return historialApartado

	class Meta:
		ordering = ['-fxAbono','tipo']