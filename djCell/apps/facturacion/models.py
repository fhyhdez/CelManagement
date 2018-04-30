from django.db import models

from djCell.apps.proveedor.models import Proveedor, FormaPago
from djCell.apps.ventas.models import Venta
from djCell.apps.clientes.models import ClienteFacturacion
from djCell.apps.productos.models import Equipo,Expres,Accesorio,Ficha
from djCell.apps.recargas.models import Recarga
from datetime import datetime, timedelta

class EstadoFacturacion(models.Model):
	estado = models.CharField(max_length=80)
	def __unicode__(self):
		return self.estado

	class Meta:
		ordering = ['estado']

class Facturacion(models.Model):
	clienteFacturacion = models.ForeignKey(ClienteFacturacion)
	venta = models.ForeignKey(Venta, null=True, blank=True)
	fxFactura 	= models.DateTimeField(auto_now=True)
	folioFiscal = models.CharField(max_length=50, null=True, blank=True)
	totalvta 	= models.DecimalField(max_digits=10,decimal_places=2, null=True,blank=True, default=0)
	estado 		= models.ForeignKey(EstadoFacturacion,null=True, blank=True)

	def __unicode__(self):
		factura="%s || %s || $%s  "%(self.clienteFacturacion.rfc, self.folioFiscal, self.totalvta )
		return factura

	class Meta:
		ordering = ['-fxFactura','folioFiscal','clienteFacturacion']


class FacturaEquipo(models.Model):
	factura = models.ForeignKey(Facturacion)
	equipo 		= models.ForeignKey(Equipo)
	def __unicode__(self):
		ventaEquipo="%s - %s"%(self.factura,self.equipo)
		return ventaEquipo

class FacturaExpres(models.Model):
	factura = models.ForeignKey(Facturacion)
	expres 		= models.ForeignKey(Expres)
	def __unicode__(self):
		ventaExpres="%s - %s"%(self.factura,self.expres)
		return ventaExpres


class FacturaAccesorio(models.Model):
	factura = models.ForeignKey(Facturacion)
	accesorio 	= models.ForeignKey(Accesorio)
	def __unicode__(self):
		ventaAccesorio="%s - %s"%(self.factura,self.accesorio)
		return ventaAccesorio


class FacturaFichas(models.Model):
	factura = models.ForeignKey(Facturacion)
	ficha 		= models.ForeignKey(Ficha)
	def __unicode__(self):
		ventaFicha="%s - %s"%(self.factura,self.ficha)
		return ventaFicha

class FacturaRecarga(models.Model):
	factura = models.ForeignKey(Facturacion)
	recarga 	= models.ForeignKey(Recarga)
	def __unicode__(self):
		ventaRecarga="%s - %s"%(self.factura,self.recarga)
		return ventaRecarga

