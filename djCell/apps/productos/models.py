from django.db import models
from django.contrib.auth.models import User
from djCell.apps.proveedor.models import Factura
from djCell.apps.sucursales.models import Sucursal
from datetime import datetime, timedelta

class TiempoGarantia(models.Model):
	dias = models.IntegerField()
	def __unicode__(self):
		garantia="%s Meses de Garantia"%(self.dias)
		return garantia

class Estatus(models.Model):
	estatus = models.CharField(max_length=50, unique=True)
	def __unicode__(self):
		return self.estatus

#*********************************Equipo************************************************
class Marca(models.Model):
	marca = models.CharField(max_length=50, unique=True)
	def __unicode__(self):
		return self.marca

	class Meta:
		ordering = ['marca']

class Gama(models.Model):
	gama = models.CharField(max_length=50)
	comision = models.DecimalField(max_digits=10,decimal_places=2)
	def __unicode__(self):
		return self.gama

	class Meta:
		ordering = ['gama', 'comision']

class DetallesEquipo(models.Model):
	folio = models.CharField(max_length=10, unique=True)
	gama 	= models.ForeignKey(Gama)
	marca 	= models.ForeignKey(Marca)
	modelo 	= models.CharField(max_length=50)
	color 	= models.CharField(max_length=30)
	tiempoGarantia = models.ForeignKey(TiempoGarantia)
	precioMenudeo = models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)
	precioMayoreo = models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)
	def __unicode__(self):
		equipo="%s--%s - %s"%(self.marca.marca,self.modelo, self.color)
		return equipo

	class Meta:
		ordering = ['marca__marca','modelo','color']

class HistorialPreciosEquipos(models.Model):
	detallesEquipo 	= models.ForeignKey(DetallesEquipo) 
	fecha 			= models.DateTimeField(auto_now=True)
	usuario 		= models.ForeignKey(User)
	precioMayoreo	= models.DecimalField(max_digits=10,decimal_places=2)
	precioMenudeo	= models.DecimalField(max_digits=10,decimal_places=2)
	def __unicode__(self):
		equipo ="%s %s %s - %s - my:%s, mn:%s"%(self.detallesEquipo.marca.marca, self.detallesEquipo.modelo, self.detallesEquipo.color, self.fecha.strftime("%d-%m-%Y"), self.precioMayoreo, self.precioMenudeo)
		return equipo

	class Meta:
		ordering = ['detallesEquipo','precioMayoreo','precioMenudeo']

class Equipo(models.Model):
	factura 	= models.ForeignKey(Factura)
	imei 		= models.DecimalField(max_digits=15,decimal_places=0, unique=True, null=True, blank=True) #changed 29ene1737
	icc 		= models.DecimalField(max_digits=19,decimal_places=0, null=True, blank=True) #changed 29ene1737
	detallesEquipo = models.ForeignKey(DetallesEquipo)
	noCell 		= models.CharField(max_length=15, default='Sin Asignar', null=True, blank=True)
	accesorioEqu = models.TextField(default='Cargador', null=True, blank=True)
	estatus 	= models.ForeignKey(Estatus, blank=True, null=True)
	importeFactura = models.DecimalField(max_digits=10,decimal_places=2)
	sucursal 	= models.ForeignKey(Sucursal, blank=True, null=True)
	observ 	= models.TextField(null=True, blank=True)#fatyma was here ...por si tiene faltante algun accesorio a quiva
	productoFacturado = models.BooleanField(default=False)
	def __unicode__(self):
		eek ="%s %s %s || %s %s || %s"%(self.detallesEquipo.marca.marca, self.detallesEquipo.modelo,self.detallesEquipo.color, self.imei, self.icc , self.sucursal.nombre)
		return eek
	class Meta:
		ordering=['sucursal', 'detallesEquipo','imei']
#***************************************************************************************



#************************************Express********************************************
class TipoIcc(models.Model):
	tipoIcc = models.CharField(max_length=50,unique=True)
	def __unicode__(self):
		return self.tipoIcc

	class Meta:
		ordering = ['tipoIcc']

class DetallesExpres(models.Model):
	descripcion 	= models.CharField(max_length=150)
	tipoIcc 		= models.ForeignKey(TipoIcc)
	tiempoGarantia 	= models.ForeignKey(TiempoGarantia) #porque esta este aqui? no se supone es otro para combo?
	precioMenudeo  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	precioMayoreo  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	def __unicode__(self):
		expres="%s - $ %s | $ %s"%(self.descripcion,self.precioMenudeo, self.precioMayoreo)
		return expres

	class Meta:
		ordering = ['descripcion','precioMenudeo','precioMayoreo']

class Expres(models.Model):
	factura  	= models.ForeignKey(Factura, blank=True, null=True)
	icc 		= models.DecimalField(max_digits=19,decimal_places=0,unique=True) #changed 29ene1737
	noCell 		= models.CharField(max_length=15, default='Sin Asignar')
	detallesExpres = models.ForeignKey(DetallesExpres, blank=True, null=True)
	estatus 	= models.ForeignKey(Estatus, blank=True, null=True)
	importeFactura = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	sucursal 	= models.ForeignKey(Sucursal, blank=True, null=True)
	observ 	= models.TextField(null=True, blank=True)
	productoFacturado = models.BooleanField(default=False)
	def __unicode__(self):
		return 'icc: %s'%(self.icc)

	class Meta:
		ordering = ['icc']
'''
class ObservacionExpres(models.Model):
	fecha 	= models.DateTimeField(auto_now=True)
	expres 	= models.ForeignKey(Expres)
	observ 	= models.TextField(null=True, blank=True)
	usuario = models.ForeignKey(User)
	def __unicode__(self):
		observacion="%s %s"%(self.fecha,self.expres)
		return observacion
#'''

class HistorialPreciosExpres(models.Model):
	detalles  = models.ForeignKey(DetallesExpres) 
	fecha    = models.DateTimeField(auto_now=True)
	usuario   = models.ForeignKey(User)
	precioMayoreo = models.DecimalField(max_digits=10,decimal_places=2)
	precioMenudeo = models.DecimalField(max_digits=10,decimal_places=2)
 	def __unicode__(self):
  		equipo ="%s - %s - my:%s, mn:%s"%(self.detalles.descripcion, self.fecha.strftime("%d-%m-%Y"), self.precioMayoreo, self.precioMenudeo)
  		return equipo

  	class Meta:
		ordering = ['-fecha' ,'detalles__descripcion','precioMayoreo','precioMenudeo']
#***************************************************************************************



#*****************************Accsorios*************************************************
class Secciones(models.Model):
	seccion     = models.CharField(max_length=80, unique=True)
	def __unicode__(self):
		return self.seccion

	class Meta:
		ordering = ['seccion']

class MarcaAccesorio(models.Model):
	marca = models.CharField(max_length=50, unique=True)
	def __unicode__(self):
		return self.marca

	class Meta:
		ordering = ['marca']

class DetallesAccesorio(models.Model):
	folio = models.CharField(max_length=10, unique=True)
	marca 	= models.ForeignKey(MarcaAccesorio)
	descripcion = models.CharField(max_length=150)
	seccion = models.ForeignKey(Secciones)
	precioMenudeo = models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)
	precioMayoreo = models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)
	def __unicode__(self):
		accesorio="%s--%s %s"%(self.descripcion,self.marca, self.seccion)
		return accesorio

	class Meta:
		ordering = ['folio','marca__marca']

class HistorialPreciosAccesorios(models.Model):
	detallesAccesorio 	= models.ForeignKey(DetallesAccesorio) 
	fecha 			= models.DateTimeField(auto_now=True)
	usuario 		= models.ForeignKey(User)
	precioMayoreo 	= models.DecimalField(max_digits=10,decimal_places=2)
	precioMenudeo	= models.DecimalField(max_digits=10,decimal_places=2)
	def __unicode__(self):
		accesorio ="%s %s - %s - my:%s, mn:%s"%(self.detallesAccesorio.marca.marca, self.detallesAccesorio.seccion, self.fecha.strftime("%d-%m-%Y"), self.precioMayoreo, self.precioMenudeo)
		return accesorio

	class Meta:
		ordering = ['detallesAccesorio__marca__marca','-fecha']

class EstatusAccesorio(models.Model):
	estatus = models.CharField(max_length=150)
	def __unicode__(self):
		return self.estatus

	class Meta:
		ordering = ['estatus']

class Accesorio(models.Model):
	factura 	= models.ForeignKey(Factura, blank=True, null=True)
	codigoBarras = models.CharField(max_length=25, unique=True)
	detallesAccesorio = models.ForeignKey(DetallesAccesorio, blank=True, null=True)
	estatusAccesorio = models.ForeignKey(EstatusAccesorio, blank=True, null=True)
	precioFact 	= models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	sucursal 	= models.ForeignKey(Sucursal, blank=True, null=True)
	productoFacturado = models.BooleanField(default=False)
	def __unicode__(self):
		eek ="%s || %s || %s || %s"%(self.codigoBarras,self.detallesAccesorio.seccion.seccion,self.detallesAccesorio.marca.marca,self.detallesAccesorio.descripcion)
		return eek

	class Meta:
		ordering = ['codigoBarras','detallesAccesorio']


#**************************************************************************************


#********************************Fichas************************************************
class NominacionFicha(models.Model):
	nominacion 	=	models.DecimalField(max_digits=10,decimal_places=2, unique=True)
	def __unicode__(self):
		nomin="$ %s"%(self.nominacion)
		return nomin

	class Meta:
		ordering = ['nominacion']

class EstatusFicha(models.Model):
	estatus = models.CharField(max_length=100)
	def __unicode__(self):
		return self.estatus

	class Meta:
		ordering = ['estatus']

class Ficha(models.Model):
	factura = models.ForeignKey(Factura, blank=True, null=True)
	folio 	= models.DecimalField(max_digits=14,decimal_places=0)
	nominacion 	= models.ForeignKey(NominacionFicha, blank=True, null=True)
	precioFac 	= models.DecimalField(max_digits=10,decimal_places=2, blank=True, null=True)
	estatusFicha = models.ForeignKey(EstatusFicha, blank=True, null=True)
	sucursal 	= models.ForeignKey(Sucursal, blank=True, null=True)
	productoFacturado = models.BooleanField(default=False)
	def __unicode__(self):
		eek ="$ %s || %s"%(self.nominacion.nominacion,self.folio)
		return eek

	class Meta:
		ordering = ['nominacion','folio']

class ObservacionFichas(models.Model):
	fecha = models.DateTimeField(auto_now=True)
	ficha = models.ForeignKey(Ficha)
	observ = models.TextField(null=True, blank=True)
	usuario = models.ForeignKey(User)
	def __unicode__(self):
		observacion="%s %s"%(self.fecha.strftime("%d-%m-%Y"),self.ficha)
		return observacion

	class Meta:
		ordering = ['-fecha','ficha']

class TiempoAire(models.Model):
	factura = models.ForeignKey(Factura)
	saldo 	= models.DecimalField(max_digits=10,decimal_places=2)
	precioFac = models.DecimalField(max_digits=10,decimal_places=2)
	def __unicode__(self):
		eek ="Factura: %s ||Precio Fact. $ %s || Saldo: %s"%(self.factura,self.precioFac,self.saldo)
		return eek

	class Meta:
		ordering = ['factura']