from django.db import models

#***************************************************************************************
#***********************Catalogos de Direccion******************************************
class Estado(models.Model):
	estado = models.CharField(max_length=100)
	def __unicode__(self):
		return self.estado

	class Meta:
		ordering = ['estado']

class Ciudad(models.Model):
	estado = models.ForeignKey(Estado)
	ciudad = models.CharField(max_length=100)
	def __unicode__(self):
		return self.ciudad

	class Meta:
		ordering = ['estado','ciudad']

class Colonia(models.Model):
	ciudad  = models.ForeignKey(Ciudad)
	colonia = models.CharField(max_length=100)
	def __unicode__(self):
		return self.colonia

	class Meta:
		ordering = ['ciudad__ciudad','colonia']

class CP(models.Model):
	colonia = models.ForeignKey(Colonia)
	cp = models.CharField(max_length=5)
	def __unicode__(self):
		return self.cp

	class Meta:
		ordering = ['colonia__colonia','cp']

class Zona(models.Model):
	zona =models.CharField(max_length=100)
	def __unicode__(self):
		return self.zona

	class Meta:
		ordering = ['zona']
#***************************************************************************************