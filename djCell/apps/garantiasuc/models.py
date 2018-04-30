from django.db import models
from djCell.apps.sucursales.models import Sucursal
from djCell.apps.productos.models import Equipo
from djCell.apps.papeletas.models import Papeleta

class EstadoGarantia(models.Model):
	estado = models.CharField(max_length=80, unique=True)
	def __unicode__(self):
		return self.estado

	class Meta:
		ordering = ['estado']

class Garantia(models.Model):
	papeleta 	= models.ForeignKey(Papeleta)
	equipo 		= models.ForeignKey(Equipo)
	falla 		= models.TextField()
	sucursal 	= models.ForeignKey(Sucursal) # a que suc llego
	fxSucursal 	= models.DateTimeField(auto_now=True)
	llegoAlmacen = models.BooleanField(default=False)
	fxAlmacen 	= models.DateTimeField(null=True,blank=True)
	fxCAC 		= models.DateTimeField(null=True,blank=True)
	observacion = models.TextField(null=True, blank=True) # como entrega el equipo
	estado 		= models.ForeignKey(EstadoGarantia)
	fxRevision	= models.DateTimeField(null=True,blank=True)
	def __unicode__(self):
		garantia="%s %s %s %s %s"%(self.sucursal.nombre,self.equipo.detallesEquipo.marca.marca, self.equipo.detallesEquipo.modelo, self.equipo.imei, self.falla)
		return garantia

	class Meta:
		ordering = ['-fxSucursal','-fxRevision','-fxAlmacen','papeleta__folioPapeleta']
