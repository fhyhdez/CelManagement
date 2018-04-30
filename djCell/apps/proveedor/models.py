from django.db import models
from django.contrib.auth.models import User

class Proveedor(models.Model):
	rfc=models.CharField(max_length=15, unique=True, verbose_name="RFC")	
	nombre = models.CharField(max_length=300)
	direccion = models.TextField()
	tel = models.CharField(max_length=15, verbose_name="Telefono")
	def __unicode__(self):
		clave='%s -- %s'%(self.rfc, self.nombre)
		return clave

	class Meta:
		ordering = ['rfc','nombre']


#************************************Factura Entrada************************************
class FormaPago(models.Model):
	forma=models.CharField(max_length=50,unique=True)
	def __unicode__(self):
		return self.forma

	class Meta:
		ordering = ['forma']


'''# inhabilitada por falta de practica y confusion 29jul13
class TipoFactura(models.Model):# segun el producto, amigo kit -equipos, express, recargas, accesorios, otros
	tipo = models.CharField(max_length=80)
	def __unicode__(self):
		return self.tipo
	class Meta:
		ordering = ['tipo']
#'''
class Factura(models.Model):
	conFactura 	= models.BooleanField(default=True) # factura = true, sino es con nota (sin factura)
	documento 	= models.CharField(max_length=25, blank=True, null=True)
	folio 		= models.CharField(max_length=20, unique=True) # folio de nota o de factura
	proveedor 	= models.ForeignKey(Proveedor)
	fxFactura 	= models.DateField()
	formaPago 	= models.ForeignKey(FormaPago)
	subTotal 	= models.DecimalField(max_digits=10,decimal_places=2)
	descuento 	= models.DecimalField(max_digits=10,decimal_places=2)
	iva 		= models.DecimalField(max_digits=10,decimal_places=2) #no son necesarios, eeen fin.
	montoTotal 	= models.DecimalField(max_digits=10,decimal_places=2)
	fxIngreso 	= models.DateField(auto_now=True)
	#tipoFactura = models.ForeignKey(TipoFactura, null=True, blank=True, default='')
	observacion = models.TextField(null=True,blank=True)
	usuario 	= models.ForeignKey(User)
	def __unicode__(self):
		clave='Folio: %s'%(self.folio)
		return clave

	class Meta:
		ordering = ['-fxIngreso']
#***************************************************************************************