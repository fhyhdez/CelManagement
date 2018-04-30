from django.db import models
from django.contrib.auth.models import User
from djCell.apps.sucursales.models import Sucursal
from djCell.apps.personal.models import Empleado
from djCell.apps.productos.models import Equipo, Expres
from djCell.apps.planes.models import Plan, Solicitud


class TipoActivacion(models.Model):
	tipo        = models.CharField(max_length=80)
	def __unicode__(self):
		return self.tipo

	class Meta:
		ordering = ['tipo']

class ActivacionEquipo(models.Model):
	equipo 			= models.ForeignKey(Equipo)
	tipoActivacion 	= models.ForeignKey(TipoActivacion)
	fxActivacion 	= models.DateTimeField(auto_now=True)
	usuario 		= models.ForeignKey(User) #quien lo activo en telcel
	empleado 		= models.ForeignKey(Empleado) #empleado que hizo la venta activa
	sucursal 		= models.ForeignKey(Sucursal)
	def __unicode__(self):
		equipoActivado="%s %s"%(self.equipo, self.tipoActivacion)
		return equipoActivado

	class Meta:
		ordering = ['-fxActivacion','tipoActivacion','equipo','empleado','sucursal']

class ActivacionExpress(models.Model):
	express 		= models.ForeignKey(Expres)
	tipoActivacion 	= models.ForeignKey(TipoActivacion)
	fxActivacion 	= models.DateTimeField(auto_now=True)
	usuario  		= models.ForeignKey(User) #quien lo activo en telcel
	empleado 		= models.ForeignKey(Empleado) #empleado que hizo la venta activa
	sucursal 		= models.ForeignKey(Sucursal)
	def __unicode__(self):
		expresActivado="%s %s"%(self.express, self.tipoActivacion)
		return expresActivado

	class Meta:
		ordering = ['-fxActivacion','tipoActivacion','express','empleado','sucursal']

class ActivacionPlan(models.Model):
	equipo 			= models.ForeignKey(Equipo, null=True, blank=True)
	plan 			= models.ForeignKey(Plan)
	solicitud 		= models.ForeignKey(Solicitud)
  	sucursal 		= models.ForeignKey(Sucursal)
  	fxAutorizacion 	= models.DateTimeField(auto_now=True)
  	ejecutivo 		= models.ForeignKey(Empleado)
  	form_act 		= models.CharField(max_length=80)
	difEquipo 		= models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)
  	difContado 		= models.CharField(max_length=80, null=True, blank=True)
  	finanMeses 		= models.IntegerField( null=True, blank=True)
  	numGratis 		= models.CharField(max_length=80, blank=True)
  	lada  			= models.IntegerField()
  	actSno  		= models.CharField(max_length=20)
  	noActcliente 	= models.CharField(max_length=20)
	hraCdom  		= models.CharField(max_length=80)
  	hraRef  		= models.CharField(max_length=80)
  	fxActivacion 	= models.DateTimeField(auto_now=True)
  	def __unicode__(self):
		activacionPlan="%s || %s -- %s %s || %s"%(self.plan, self.sucursal.nombre, self.ejecutivo.curp, self.ejecutivo.nombre, self.fxActivacion)
		return activacionPlan

	class Meta:
		ordering = ['-fxActivacion','plan','equipo','ejecutivo']