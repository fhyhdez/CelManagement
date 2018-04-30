from django.db import models
from djCell.apps.clientes.models import ClienteServicio
from djCell.apps.sucursales.models import Sucursal
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class TipoReparacion(models.Model):
	tipo = models.CharField(max_length=80)
	def __unicode__(self):
		return self.tipo

	class Meta:
		ordering = ['tipo']

class EstadoReparacion(models.Model):
	estado = models.CharField(max_length=80)
	comisionReparacion = models.DecimalField(max_digits=10,decimal_places=2)
	def __unicode__(self):
		return self.estado

	class Meta:
		ordering = ['estado']

class Reparacion(models.Model):
	tipoReparacion = models.ForeignKey(TipoReparacion)
	descripcion	= models.CharField(max_length=80, unique=True)
	monto 		= models.DecimalField(max_digits=10,decimal_places=2)
	activo 	= models.BooleanField(default=True)
	def __unicode__(self):
		reparacion="%s %s %s"%(self.tipoReparacion.tipo, self.descripcion, self.monto)
		return reparacion

	class Meta:
		ordering = ['tipoReparacion__tipo','descripcion']

class EquipoReparacion(models.Model):
	marcaModelo = models.CharField(max_length=180)
	imei 		= models.CharField(max_length=20)# se quito el unique
	falla 		= models.TextField()
	observacion = models.TextField(null=True, blank=True) #condiciones de entrega
	cliente 	= models.ForeignKey(ClienteServicio)
	conCosto 	= models.BooleanField(default=True)
	reparacion 	= models.ForeignKey(Reparacion)
	anticipo 	= models.DecimalField(max_digits=10,decimal_places=2)
	sucursal 	= models.ForeignKey(Sucursal)
	estado 		= models.ForeignKey(EstadoReparacion)
	fxIngreso 	= models.DateTimeField(auto_now=True)
	fxRevision	= models.DateTimeField(null=True,blank=True)#ultima fecha de revision 24feb
	pagado 		= models.BooleanField(default=False)
	def __unicode__(self):
		equipoReparacion="%s %s %s %s %s %s"%(self.cliente.nombre, self.cliente.direccion,self.marcaModelo, self.imei, self.falla, self.estado.estado )
		return equipoReparacion

	class Meta:
		ordering = ['-fxIngreso','sucursal__nombre','marcaModelo']

class HistorialClienteReparacion(models.Model):
	fxAbono 	= models.DateTimeField(auto_now=True)
	equipoReparacion = models.ForeignKey(EquipoReparacion)
	abono 		= models.DecimalField(max_digits=10,decimal_places=2)
	def __unicode__(self):
		grrr="%s %s - %s - $%s - %s"%(self.equipoReparacion.marcaModelo, self.equipoReparacion.imei, self.equipoReparacion.cliente.nombre, self.abono, self.fxAbono.strftime("%d-%m-%Y"))
		return grrr

	class Meta:
		ordering = ['-fxAbono','equipoReparacion__sucursal__nombre' ,'equipoReparacion__marcaModelo']

class comisionesReparacion(models.Model):
	usuario 	= models.ForeignKey(User) #quien lo registro
	reparacion  = models.ForeignKey(EquipoReparacion)
	def __unicode__(self):
		r="%s - %s "%(self.usuario,self.reparacion)
		return r

	class Meta:
		ordering = ['usuario','reparacion']
			