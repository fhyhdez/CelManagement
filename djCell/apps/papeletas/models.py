from django.db import models
from djCell.apps.catalogos.models import Ciudad, CP, Colonia, Estado
from djCell.apps.sucursales.models import Sucursal
from djCell.apps.personal.models import Empleado

class TipoProducto(models.Model):
	tipo = models.CharField(max_length=80, unique=True)
	def __unicode__(self):
		return self.tipo

	class Meta:
		ordering = ['tipo']


class Papeleta(models.Model):
	folioPapeleta = models.CharField(max_length=80, unique=True) # folio de la papeleta
	sucursal = models.ForeignKey(Sucursal) # sucursal donde se capturo la papeleta
	empleado = models.ForeignKey(Empleado) # empleado que hizo la venta
	nombre 	= models.CharField(max_length=300)
	calle 	= models.TextField()
	colonia = models.ForeignKey(Colonia)
	codP 	= models.ForeignKey(CP)
	ciudad 	= models.ForeignKey(Ciudad)
	estado 	= models.ForeignKey (Estado)
	telPart = models.CharField(max_length=20,null=True, blank=True)
	telAsig = models.CharField(max_length=10)
	esnImei = models.CharField(max_length=30)
	dat 	= models.CharField(max_length=10, default="ACCELL")
	tipoProducto=models.ForeignKey(TipoProducto)
	fxActivacion = models.DateTimeField(auto_now=True)#fecha de captura
	tgarantia = models.IntegerField()
	def __unicode__(self):
		papeleta="%s %s %s %s %s %s %s %s %s %s"%(self.telAsig, self.nombre, self.calle, self.codP.cp, self.ciudad.ciudad, self.estado.estado, self.fxActivacion, self.esnImei, self.dat, self.tipoProducto.tipo)
		return papeleta

	class Meta:
		ordering = ['-fxActivacion','folioPapeleta','sucursal__nombre']