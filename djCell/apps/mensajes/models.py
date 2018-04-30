from django.db import models
from djCell.apps.sucursales.models import Sucursal
from django.contrib.auth.models import User

class EstadoMensaje(models.Model):
	estado = models.CharField(max_length=80, unique=True)
	def __unicode__(self):
		return self.estado

	class Meta:
		ordering = ['estado']

class SolicitudNuevoProducto(models.Model):
	folio 			= models.CharField(max_length=80) #folio generado SUC-fecha-id
	nuevoProducto 	= models.TextField(null=True, blank=True)
	fxNuevoProducto = models.DateTimeField(auto_now=True)
	sucursal 	= models.ForeignKey(Sucursal)
	usuario 	= models.ForeignKey(User)
	estado 		= models.ForeignKey(EstadoMensaje)
	def __unicode__(self):
		nuevo="%s %s %s "%(self.folio, self.nuevoProducto, self.sucursal.nombre)
		return nuevo

	class Meta:
		ordering = ['-fxNuevoProducto','folio','nuevoProducto']
		