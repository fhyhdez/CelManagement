from django.db import models
from django.contrib.auth.models import User
from djCell.apps.sucursales.models import Sucursal
from djCell.apps.productos.models import Equipo, Expres, Accesorio, Ficha

class AlmacenEquipo(models.Model):
	sucursal 	= models.ForeignKey(Sucursal)
	equipo 		= models.ForeignKey(Equipo)
	estado 		= models.BooleanField() #existencia
	fxTransf 	=models.DateTimeField(auto_now=True)
	def __unicode__(self):
		sucuEquipo="%s %s"%(self.sucursal.nombre,self.equipo)
		return sucuEquipo

	class Meta:
		ordering = ['-fxTransf','sucursal','equipo']

class AlmacenExpres(models.Model):
	sucursal  	= models.ForeignKey(Sucursal)
	expres  	= models.ForeignKey(Expres)
	estado 		= models.BooleanField()
	fxTransf 	=models.DateTimeField(auto_now=True)
	def __unicode__(self):
		sucuExp="%s %s"%(self.sucursal.nombre,self.expres.icc)
		return sucuExp

	class Meta:
		ordering = ['-fxTransf','sucursal','expres']

class AlmacenAccesorio(models.Model):
	sucursal 	= models.ForeignKey(Sucursal)
	accesorio 	= models.ForeignKey(Accesorio)
	estado 		= models.BooleanField()
	fxTransf 	=models.DateTimeField(auto_now=True)
	def __unicode__(self):
		sucuAccesorio="%s %s"%(self.sucursal.nombre,self.accesorio.codigoBarras)
		return sucuAccesorio

	class Meta:
		ordering = ['-fxTransf','sucursal','accesorio']

class AlmacenFicha(models.Model):
	sucursal 	= models.ForeignKey(Sucursal)
	ficha 		= models.ForeignKey(Ficha)
	estado 		= models.BooleanField()
	fxTransf 	=models.DateTimeField(auto_now=True)
	def __unicode__(self):
		sucuFicha="%s %s"%(self.sucursal.nombre,self.ficha.folio)
		return sucuFicha

	class Meta:
		ordering = ['-fxTransf','sucursal','ficha']