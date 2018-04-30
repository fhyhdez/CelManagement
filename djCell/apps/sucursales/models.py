from django.db import models
from djCell.apps.catalogos.models import Ciudad, CP, Colonia, Zona
from djCell.apps.personal.models import Empleado

class EstadoSucursal(models.Model):
	estado = models.CharField(max_length=80)
	def __unicode__(self):
		return self.estado

	class Meta:
		ordering = ['estado']

class TipoSucursal(models.Model):
	tipo = models.CharField(max_length=80)
	def __unicode__(self):
		return self.tipo

	class Meta:
		ordering = ['tipo']

class Sucursal(models.Model):
	tipoSucursal = models.ForeignKey(TipoSucursal)
	nombre 		 = models.CharField(max_length=100, unique=True)
	encargado 	 = models.ForeignKey(Empleado)
	noCelOfi 	 = models.CharField(max_length=15, null=True, blank=True)
	direccion 	 = models.TextField()
	colonia 	 = models.ForeignKey(Colonia)
	cp 			 = models.ForeignKey(CP)
	ciudad 		 = models.ForeignKey(Ciudad)
	zona    	 = models.ForeignKey(Zona)
	estado  	 = models.ForeignKey(EstadoSucursal)
	def __unicode__(self):
		sucursal="%s - %s - %s"%( self.nombre, self.tipoSucursal.tipo, self.zona.zona )
		return sucursal

	class Meta:
		ordering = ['zona__zona' ,'nombre']

class VendedorSucursal(models.Model):
	empleado = models.ForeignKey(Empleado, unique=True) #SE RESTRINGE EL EMPLEADO PARA UNA SOLA SUCURSAL
	sucursal = models.ForeignKey(Sucursal)
	def __unicode__(self):
		vendedores="%s %s %s || %s ||%s || %s ||%s"%( self.empleado.nombre, self.empleado.aPaterno, self.empleado.aMaterno,self.empleado.curp, self.empleado.puesto.puesto, self.sucursal.zona.zona, self.sucursal.nombre)
		return vendedores

	class Meta:
		ordering = ['sucursal__nombre' ,'empleado']
