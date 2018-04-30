from django.db import models
from django.contrib.auth.models import User
from djCell.apps.sucursales.models import Sucursal
from djCell.apps.productos.models import Equipo, Expres, Accesorio, Ficha
from django.db.models import Q
from datetime import datetime, timedelta

class TipoMovimiento(models.Model):
	nombre 		= models.CharField(max_length=80)
	def __unicode__(self):
		return self.nombre

	class Meta:
		ordering = ['nombre']

class Movimiento(models.Model):
	folio 			= models.CharField(max_length=20, unique=True)#ja ya meti mano de nuevo
	tipoMovimiento 	= models.ForeignKey(TipoMovimiento)
	fx_movimiento 	= models.DateTimeField(auto_now=True)
	sucursalOrigen 	= models.ForeignKey(Sucursal, related_name='sucursal_origen')
	sucursalDestino = models.ForeignKey(Sucursal, related_name='sucursal_destino')
	usuarioOrigen 	= models.ForeignKey(User, related_name='empleado_emisor') #el que envia
	usuarioDestino 	= models.ForeignKey(User, related_name='empleado_reseptor',null=True, blank=True) #en teoria el q recibe
	confirmacion = models.BooleanField(default=False)
	def __unicode__(self):
		movimiento="%s || %s: %s==>%s || fx:%s"%(self.folio, self.tipoMovimiento, self.sucursalOrigen.nombre, self.sucursalDestino.nombre, self.fx_movimiento.date())
		return movimiento

	class Meta:
		ordering = ['-fx_movimiento']

class ListaEquipo(models.Model):
	movimiento 	= models.ForeignKey(Movimiento, limit_choices_to=Q(confirmacion=False))
	equipo 		= models.ForeignKey(Equipo,limit_choices_to=~Q(estatus__estatus ='Vendido'))
	confirmacion = models.BooleanField(default=False)
	def __unicode__(self):
		equipoMov="%s %s"%(self.equipo, self.movimiento)
		return equipoMov

	class Meta:
		ordering = ['-movimiento__fx_movimiento','equipo__imei']


class ListaExpres(models.Model):
	movimiento 	= models.ForeignKey(Movimiento, limit_choices_to=Q(confirmacion=False))
	expres 		= models.ForeignKey(Expres)
	confirmacion = models.BooleanField(default=False)
	def __unicode__(self):
		expresMov="%s %s"%(self.expres, self.movimiento)
		return expresMov

	class Meta:
		ordering = ['-movimiento__fx_movimiento','expres__icc']

class ListaAccesorio(models.Model):
	movimiento 	= models.ForeignKey(Movimiento, limit_choices_to=Q(confirmacion=False))
	accesorio 	= models.ForeignKey(Accesorio)
	confirmacion = models.BooleanField(default=False)
	def __unicode__(self):
		accesorioMov="%s %s"%(self.accesorio, self.movimiento)
		return accesorioMov

	class Meta:
		ordering = ['-movimiento__fx_movimiento','accesorio__codigoBarras']

class ListaFichas(models.Model):
	movimiento  = models.ForeignKey(Movimiento, limit_choices_to=Q(confirmacion=False))
	ficha 		= models.ForeignKey(Ficha)
	confirmacion = models.BooleanField(default=False)
	def __unicode__(self):
		fichaMov="%s %s"%(self.ficha, self.movimiento)
		return fichaMov

	class Meta:
		ordering = ['-movimiento__fx_movimiento','ficha__folio']

class TransferenciaSaldo(models.Model):
	movimiento = models.ForeignKey(Movimiento, limit_choices_to=Q(confirmacion=False))#humm
	monto = models.DecimalField(max_digits=10,decimal_places=2) #monto
	observaciones = models.TextField(null=True, blank=True)#observaciones
	def __unicode__(self):
		return str(self.monto)

	class Meta:
		ordering = ['-movimiento__fx_movimiento','monto']