# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from djCell.apps.catalogos.models import Ciudad, CP, Colonia, Estado


#****************************************Empleados**************************************
class Area(models.Model):
	area=models.CharField(max_length=50, unique=True)
	def __unicode__(self):
		return self.area
	class Meta:
		ordering = ['area']

class Puesto(models.Model):
	puesto=models.CharField(max_length=50, unique=True)
	def __unicode__(self):
		return self.puesto.upper()

	class Meta:
		ordering = ['puesto']

class Empleado(models.Model):
	nombre 	= models.CharField(max_length=250)
	aPaterno 	= models.CharField(max_length=180)
	aMaterno 	= models.CharField(max_length=180)
	direccion 	= models.TextField()
	colonia 	= models.ForeignKey(Colonia)
	ciudad  	= models.ForeignKey(Ciudad)
	estado   	= models.ForeignKey(Estado)
	telefono 	= models.CharField(max_length=80)
	fxIngreso 	= models.DateTimeField(auto_now=True)
	fxNacimiento 	= models.DateField()
	curp 	= models.CharField(max_length=30, unique=True)
	puesto  	= models.ForeignKey(Puesto)
	area = models.ForeignKey(Area)
	salarioxDia 	= models.DecimalField(max_digits=10,decimal_places=2)
	estadoEmpleado 	= models.BooleanField()
	def __unicode__(self):
		empleado="%s %s %s || %s || %s"%(self.nombre.capitalize(), self.aPaterno.capitalize(), self.aMaterno.capitalize(), self.curp.upper(), self.puesto)
		return empleado
	class Meta:
		ordering = ['nombre','aPaterno','aMaterno','curp']

#***************************************************************************************


#***********************************Usuarios********************************************
class Permiso(models.Model):
	descripcion = models.CharField(max_length=50, unique=True)
	nivel = models.IntegerField()
	def __unicode__(self):
		argh ="%s"%(self.descripcion)
		return argh
	class Meta:
		ordering = ['nivel','descripcion']

class Usuario(models.Model):
	user = models.ForeignKey(User, unique=True) #, unique=True
	empleado = models.ForeignKey(Empleado, unique=True)
	permiso = models.ForeignKey(Permiso)
	def __unicode__(self):
		return self.user.username

	class Meta:
		ordering = ['user__username','permiso','empleado']
#*************************************************************************************** 