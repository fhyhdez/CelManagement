from django.db import models
from django.contrib.auth.models import User
from djCell.apps.personal.models import Empleado
from djCell.apps.sucursales.models import Sucursal
from djCell.apps.productos.models import Equipo
from djCell.apps.clientes.models import ClienteServicio
from djCell.apps.ventas.models import Venta
from datetime import datetime, timedelta

class TipoGastoSucursal(models.Model):
	tipo = models.CharField(max_length=80, unique=True)
	def __unicode__(self):
		return self.tipo

	class Meta:
		ordering = ['tipo']
		
class CorteVenta(models.Model):
	folioCorteVta 	= models.CharField(max_length=80) #folio generado cte-suc-fecha-id
	fxCorte 		= models.DateTimeField(auto_now=True)
	sucursal 		= models.ForeignKey(Sucursal)
	totalVta 		= models.DecimalField(max_digits=10,decimal_places=2)
	totalGastos 	= models.DecimalField(max_digits=10,decimal_places=2)
	total 			= models.DecimalField(max_digits=10,decimal_places=2)
	observacion 	= models.TextField(null=True, blank=True)
	cierraCorte 	= models.ForeignKey(User)
	revisado 		= models.BooleanField(blank=True, default=False)
	cerrado 		= models.BooleanField(default=False)
	def __unicode__(self):
		corteVenta ="~ %s || %s || %s $ %s"%(self.folioCorteVta, self.fxCorte.strftime("%d-%m-%Y"), self.sucursal.nombre, self.total)
		return corteVenta

	class Meta:
		ordering = ['-fxCorte','folioCorteVta','sucursal']

class GastosSucursal(models.Model):
	tipoGasto 	= models.ForeignKey(TipoGastoSucursal)
	gasto 		= models.DecimalField(max_digits=10,decimal_places=2)
	fxGasto 	= models.DateTimeField(auto_now=True)
	sucursal 	= models.ForeignKey(Sucursal)
	usuario 	= models.ForeignKey(User)
	observacion = models.TextField(null=True, blank=True)
	corteVenta  = models.ForeignKey(CorteVenta)
	def __unicode__(self):
		gastoSucursal ="%s %s %s %s %s"%(self.tipoGasto.tipo, self.gasto, self.empleado.curp, self.empleado.nombre, self.observacion)
		return gastoSucursal

	class Meta:
		ordering = ['-fxGasto','tipoGasto__tipo','sucursal__nombre','corteVenta__folioCorteVta' ,'usuario']

class VentasCorte(models.Model):
	corteVenta = models.ForeignKey(CorteVenta)
	venta = models.ForeignKey(Venta)
	def __unicode__(self):
		wua ="corte: %s vta: %s total venta: %s"%(self.corteVenta.folioCorteVta, self.venta.folioVenta, self.venta.total)
		return wua

	class Meta:
		ordering = ['corteVenta__folioCorteVta','venta']
		

class DiferenciasCorte(models.Model):
	corteVenta 	= models.ForeignKey(CorteVenta)
	diferencia 	= models.DecimalField(max_digits=10,decimal_places=2)
	fxDiferencia = models.DateTimeField(auto_now=True)
	revisaCorte = models.ForeignKey(User)
	observacion = models.TextField(null=True, blank=True)
	def __unicode__(self):
		difCorte ="%s %s %s"%(self.corteVenta.folioCorteVta, self.diferencia, self.fxDiferencia.strftime("%d-%m-%Y %X"))
		return difCorte

	class Meta:
		ordering = ['-fxDiferencia','corteVenta__folioCorteVta','revisaCorte']

class RecargasVendidoCorte(models.Model): #historial de saldo vendido en el corte
	sucursal = models.ForeignKey(Sucursal)
	fecha 	= models.DateTimeField(auto_now=True)
	corte = models.ForeignKey(CorteVenta)
	totalVentas = models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
	saldoFinal 	= models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
	observaciones = models.TextField(null=True, blank=True)
	def __unicode__(self):
		diaCorte ="%s - %s,Vendido: $%s, Final: $%s"%(self.sucursal,self.fecha,self.totalVentas,self.saldoFinal)
		return diaCorte

	class Meta:
		ordering = ['-corte__folioCorteVta']