from django.db import models
from django.contrib.auth.models import User
from djCell.apps.sucursales.models import Sucursal
from datetime import datetime, timedelta

class Monto(models.Model):
	monto = models.IntegerField()#combo de montos 20,30, 50,100,....etc
	def __unicode__(self):
		precio="$ %s"%(self.monto)
		return precio

	class Meta:
		ordering = ['monto']

class Recarga(models.Model):
	folio 	= models.CharField(max_length=40, unique=True) #folio que retorna telcel por la recarga enviada, exampl: FE394848595
	montos 	= models.ForeignKey(Monto) # monto de la recarga enviada example: 30
	sucursal = models.ForeignKey(Sucursal)
	observaciones = models.TextField(null=True, blank=True)
	productoFacturado = models.BooleanField(default=False)
	def __unicode__(self):
		return self.folio	

	class Meta:
		ordering = ['folio','sucursal__nombre']

class HistorialSaldo(models.Model):
	sucursal = models.ForeignKey(Sucursal)
	fecha 	= models.DateTimeField(auto_now=True)
	saldoInicial = models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
	abono 	= models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
	totalVentas = models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
	saldoFinal 	= models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
	observaciones = models.TextField(null=True, blank=True)
	def __unicode__(self):
		diaSuc="%s %s"%(self.sucursal,self.fecha.strftime("%d-%m-%Y"))
		return diaSuc

	class Meta:
		ordering = ['-fecha','sucursal__nombre']

class SaldoSucursal(models.Model):
	sucursal = models.ForeignKey(Sucursal)
	saldo 	= models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
	def __unicode__(self):
		salado="%s $%s"%(self.sucursal,self.saldo)
		return salado

	class Meta:
		ordering = ['sucursal__nombre','saldo']

class SaldoStock(models.Model):
	sucursal = models.ForeignKey(Sucursal)
	minimo 	 = models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
	maximo 	 = models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
	def __unicode__(self):
		pizzahot="%s minimo:%s, maximo:%s"%(self.sucursal,self.minimo,self.maximo)
		return pizzahot

	class Meta:
		ordering = ['sucursal__nombre']