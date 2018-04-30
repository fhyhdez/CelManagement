from django.db import models
from djCell.apps.personal.models import Empleado

class TipoAmonestacion(models.Model):
	tipo 	= models.CharField(max_length=80, unique=True)
	def __unicode__(self):
		return self.tipo

	class Meta:
		ordering = ['tipo']

class Amonestacion(models.Model):
	empleado 		= models.ForeignKey(Empleado)	
	tipoAmonestacion = models.ForeignKey(TipoAmonestacion)
	comentario 		= models.TextField(null=True,blank=True)
	fxAmonestacion = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		amonestacion ="%s %s %s %s %s %s"%(self.empleado.curp, self.empleado.nombre, self.empleado.aPaterno, self.empleado.aMaterno, self.tipoAmonestacion.tipo, self.comentario)
		return amonestacion

	class Meta:
		ordering = ['-fxAmonestacion', 'tipoAmonestacion','comentario','empleado']


class Sancion(models.Model):
	empleado 	= models.ForeignKey(Empleado)	
	descripcion	= models.TextField(null=True,blank=True)
	monto 		= models.DecimalField(max_digits=10,decimal_places=2)
	fxSancion	= models.DateTimeField(auto_now=True)
	def __unicode__(self):
		a ="%s %s %s %s %s %s"%(self.empleado.curp, self.empleado.nombre, self.empleado.aPaterno, self.empleado.aMaterno, self.descripcion, self.monto)
		return a

	class Meta:
		ordering = ['empleado','-fxSancion']