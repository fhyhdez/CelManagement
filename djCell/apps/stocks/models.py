from django.db import models
from djCell.apps.sucursales.models import Sucursal
from djCell.apps.productos.models import DetallesEquipo,DetallesAccesorio, NominacionFicha

class StockEquipo(models.Model):
	sucursal 	= models.ForeignKey(Sucursal)
	detalle 	= models.ForeignKey(DetallesEquipo)
	stockMin 	= models.IntegerField( null=True, blank=True)
	stockMax 	= models.IntegerField( null=True, blank=True)
	def __unicode__(self):
		stockEquipo="%s %s %s %s %s %s"%(self.sucursal.nombre, self.detalle.marca.marca, self.detalle.modelo, self.detalle.color, self.stockMin, self.stockMax)
		return stockEquipo

	class Meta:
		ordering = ['sucursal__nombre','detalle']

class StockExpres(models.Model):
	sucursal 	= models.ForeignKey(Sucursal)
	stockMin 	= models.IntegerField(null=True, blank=True)
	stockMax 	= models.IntegerField(null=True, blank=True)
	def __unicode__(self):
		stockExpres="%s %s %s"%(self.sucursal.nombre, self.stockMin, self.stockMax)
		return stockExpres

	class Meta:
		ordering = ['sucursal__nombre']

class StockAccesorio(models.Model):
	sucursal 	= models.ForeignKey(Sucursal)
	detalle		= models.ForeignKey(DetallesAccesorio)
	stockMin 	= models.IntegerField(null=True, blank=True)
	stockMax 	= models.IntegerField(null=True, blank=True)
	def __unicode__(self):
		stockAccesorio="%s %s %s %s"%(self.sucursal.nombre, self.detalle.seccion.seccion, self.stockMin, self.stockMax)
		return stockAccesorio

	class Meta:
		ordering = ['sucursal__nombre','detalle']

class StockFicha(models.Model):
	sucursal 	= models.ForeignKey(Sucursal)
	nominacion 	= models.ForeignKey(NominacionFicha)
	stockMin 	= models.IntegerField(null=True, blank=True)
	stockMax 	= models.IntegerField(null=True, blank=True)
	def __unicode__(self):
		stockFichas="%s %s %s %s"%(self.sucursal.nombre, self.nominacion.nominacion, self.stockMin, self.stockMax)
		return stockFichas

	class Meta:
		ordering = ['sucursal__nombre','nominacion']
