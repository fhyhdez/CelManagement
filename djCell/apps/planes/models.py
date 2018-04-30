from django.db import models
from django.contrib.auth.models import User
from djCell.apps.sucursales.models import Sucursal
from djCell.apps.personal.models import Empleado
from djCell.apps.proveedor.models import FormaPago
from djCell.apps.productos.models import Equipo, Expres, TiempoGarantia, DetallesEquipo
from djCell.apps.catalogos.models import Ciudad, CP, Colonia, Estado
from datetime import datetime, timedelta

class EstadoSolicitud(models.Model):
	estado = models.CharField(max_length=80, unique=True)
	def __unicode__(self):
		return self.estado

	class Meta:
		ordering = ['estado']

class TipoRelacion(models.Model):
	tipo = models.CharField(max_length=80, unique=True)
	def __unicode__(self):
		return self.tipo

	class Meta:
		ordering = ['tipo']

class Banco(models.Model):
	banco = models.CharField(max_length=80, unique=True)
	def __unicode__(self):
		return self.banco

	class Meta:
		ordering = ['banco']

class DetallePlan(models.Model):
	llamaPaga	= models.BooleanField()
  	recibePaga	= models.BooleanField()
  	tarjCred 	= models.BooleanField()
  	plazoMin	= models.IntegerField()
  	plazoLibre	= models.CharField(max_length=80,null=True, blank=True)
  	minInc		= models.IntegerField()
  	minAd	 	= models.IntegerField()
  	pagoVent	= models.BooleanField()
  	pico	 	= models.DecimalField(max_digits=10,decimal_places=2)
  	noPico	 	= models.DecimalField(max_digits=10,decimal_places=2)
  	minRoaming	= models.DecimalField(max_digits=10,decimal_places=2)
  	minNal	 	= models.DecimalField(max_digits=10,decimal_places=2)
  	cargoFijo	= models.DecimalField(max_digits=10,decimal_places=2)
  	otros	 	= models.BooleanField()
  	limConsumo	= models.DecimalField(max_digits=10,decimal_places=2)
  	program	 	= models.DecimalField(max_digits=10,decimal_places=2)
  	enGarantia	= models.DecimalField(max_digits=10,decimal_places=2)
  	def __unicode__(self):
		detallePlan="%s %s %s"%( self.plazoMin, self.plazoLibre, self.minNal)
		return detallePlan

	class Meta:
		ordering = ['plazoMin','plazoLibre']

class Plan(models.Model):
	plan 			= models.CharField(max_length=80, unique=True)
	costo 			= models.DecimalField(max_digits=10,decimal_places=2)
	tiempoGarantia 	= models.ForeignKey(TiempoGarantia)
	detallePlan 	= models.ForeignKey(DetallePlan)
	equiposGratis 	= models.TextField() # anotar todos los equipos que vienen gratis con eese plan
	activo  		= models.BooleanField(default=True)
	comision	= models.DecimalField(max_digits=10,decimal_places=2)
	def __unicode__(self):
		plan="%s %s"%( self.plan, self.costo)
		return plan

	class Meta:
		ordering = ['plan','costo','activo']

class Solicitud(models.Model):
	#control datos
	fxSolicitud = models.DateTimeField()
	canalVta 	= models.CharField(max_length=50)
	folioSisAct = models.CharField(max_length=50)
	lineaSolicitadas = models.CharField(max_length=20)
	vendedor 	= models.ForeignKey(Empleado)
	subdist 	= models.CharField(max_length=80)
	diTelcel 	= models.BooleanField() # si o no
	lineaReferencia = models.CharField(max_length=30)
	# mesa de control
	fxConsultaBuro 		= models.DateField(null=True,blank=True)
	folioConsultaBuro 	= models.CharField(max_length=30, null=True, blank=True)
	observacionSolicitud = models.TextField(null=True, blank=True)
	#Datos personales
	nombre 		= models.CharField(max_length=300)
  	aPat 		= models.CharField(max_length=180) 
  	aMat 		= models.CharField(max_length=180)
  	fxNac 		= models.DateField()
  	nacionalidad = models.CharField(max_length=180)
  	email 		= models.CharField(max_length=180,null=True, blank=True)
  	tipoIdentif = models.CharField(max_length=180)
  	folIdent 	= models.CharField(max_length=180,null=True, blank=True)
  	formPago 	= models.ForeignKey(FormaPago)
  	banco 		= models.ForeignKey(Banco, related_name='banco_personal',null=True, blank=True)
  	numTc 		= models.CharField(max_length=180,null=True, blank=True)
  	# domicilio
  	calleP 		= models.TextField()
  	noextP 		= models.CharField(max_length=50)
  	nointP 		= models.CharField(max_length=50,null=True, blank=True)
  	coloniaP 	= models.ForeignKey(Colonia, related_name='colonia_personal')
  	cpP 		= models.ForeignKey(CP, related_name='cp_personal')
  	calle1P 	= models.TextField(null=True, blank=True) 
  	calle2P 	= models.TextField(null=True, blank=True)
  	ciudadP 	= models.ForeignKey(Ciudad, related_name='ciudad_personal')
  	countryP 	= models.ForeignKey(Estado, related_name='country_personal')
  	telP 		= models.CharField(max_length=20, null=True, blank=True)
  	refDomP 	= models.CharField(max_length=300)
	# ocupacion
	puesto 		= models.CharField(max_length=180)
  	antiguedad 	= models.IntegerField()
  	ingresomens = models.DecimalField(max_digits=10,decimal_places=2)
  	empNegocio 	= models.CharField(max_length=180, null=True, blank=True)
  	giro 		= models.CharField(max_length=180, null=True, blank=True)
  	# domicilio del empleo
  	ecalle 		= models.TextField()
  	enoext 		= models.CharField(max_length=50)
  	enoint 		= models.CharField(max_length=50,null=True, blank=True)
  	ecolonia 	= models.ForeignKey(Colonia, related_name='colonia_empleo')
  	ecp 		= models.ForeignKey(CP, related_name='cp_empleo')
  	ecalle1 	= models.TextField(null=True, blank=True) 
  	ecalle2 	= models.TextField(null=True, blank=True)
  	eciudad 	= models.ForeignKey(Ciudad, related_name='ciudad_empleo')
  	ecountry 	= models.ForeignKey(Estado, related_name='country_empleo')
  	etel 		= models.CharField(max_length=20,null=True, blank=True)
  	eextension 	= models.CharField(max_length=10,null=True, blank=True)
	#Evaluacion economica
	numautos	= models.IntegerField(null=True, blank=True)
  	modelo		= models.CharField(max_length=80,null=True, blank=True)
  	casaPropia	= models.BooleanField() #si o no
  	casaValor	= models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
  	renta		= models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
	#banco y referencia
	banco1 		= models.ForeignKey(Banco, related_name='banco_ref1',null=True, blank=True)
	ctaBanco1 	= models.CharField(max_length=50, null=True, blank=True)
	telBanco1 	= models.CharField(max_length=20, null=True, blank=True)
	banco2 		= models.ForeignKey(Banco, related_name='banco_ref2', null=True, blank=True)
	ctaBanco2 	= models.CharField(max_length=50, null=True, blank=True)
	telBanco2 	= models.CharField(max_length=20, null=True, blank=True)
	banco1Comercial = models.ForeignKey(Banco, related_name='banco_comref1', null=True, blank=True)
	ctaBanco1Comercial = models.CharField(max_length=50, null=True, blank=True)
	telBanco1Comercial = models.CharField(max_length=20, null=True, blank=True)
	banco2Comercial = models.ForeignKey(Banco, related_name='banco_comref2', null=True, blank=True)
	ctaBanco2Comercial = models.CharField(max_length=50, null=True, blank=True)
	telBanco2Comercial = models.CharField(max_length=20, null=True, blank=True)
	#referenciaPersonal
	nombreApellidos1 = models.CharField(max_length=250)
	direccRef1	= models.TextField()
	telOfiRef1	= models.CharField(max_length=10)
	tipoRef1 	= models.ForeignKey(TipoRelacion, related_name='tipo_ref1')
	nombreApellidos2 = models.CharField(max_length=250, null=True, blank=True)
	direccRef2	= models.TextField(max_length=300, null=True, blank=True)
	telOfiRef2	= models.CharField(max_length=10, null=True, blank=True)
	tipoRef2 	= models.ForeignKey(TipoRelacion, related_name='tipo_ref2', null=True, blank=True)
	nombreApellidos3 = models.CharField(max_length=250, null=True, blank=True)
	direccRef3	= models.TextField(max_length=300, null=True, blank=True)
	telOfiRef3	= models.CharField(max_length=10, null=True, blank=True)
	tipoRef3 	= models.ForeignKey(TipoRelacion, related_name='tipo_ref3', null=True, blank=True)
	#datos facturacion
	nomRazon 	= models.CharField(max_length=80, null=True, blank=True)
	sexo 		= models.CharField(max_length=10, null=True, blank=True)
	rfc 		= models.CharField(max_length=20, null=True, blank=True)
	nomRep 		= models.CharField(max_length=250, null=True, blank=True)
	profesion 	= models.CharField(max_length=180, null=True, blank=True)
	ocupacion 	= models.CharField(max_length=180, null=True, blank=True)
	cargo 		= models.CharField(max_length=180, null=True, blank=True)
	direcc 		= models.TextField(null=True, blank=True)
	telPart 	= models.CharField(max_length=20, null=True, blank=True)
	telOfi 		= models.CharField(max_length=20, null=True, blank=True)
	refPersonal = models.CharField(max_length=250, null=True, blank=True)
	telRefpers 	= models.CharField(max_length=20, null=True, blank=True)
	tipoIdent 	= models.CharField(max_length=20, null=True, blank=True)
	noIdent 	= models.CharField(max_length=50, null=True, blank=True)
	#equipo solicitado
	equipoSolicitado = models.TextField(null=True,blank=True)
	#sucursal donde se solicita
	sucursal 	= models.ForeignKey(Sucursal)
	#plan solicitado
	plan 		= models.ForeignKey(Plan)
	fxModificacion = models.DateTimeField(null=True, blank=True)#fecha de revision ultima
	estado 		= models.ForeignKey(EstadoSolicitud)
	observacion = models.TextField(null=True,blank=True)
	folio = models.CharField(max_length=80)
	activado = models.BooleanField(default=False)
	def __unicode__(self):
		solicitud="%s %s %s %s %s %s"%( self.fxSolicitud.strftime("%d-%m-%Y"), self.nombre,self.aPat, self.aMat, self.equipoSolicitado, self.estado.estado)
		return solicitud

	class Meta:
		ordering = ['-fxSolicitud','nombre','aPat','aMat','plan__plan', 'sucursal__nombre']

class ServiciosPlan(models.Model):
	fxSolicitud = models.DateTimeField(auto_now=True) #fx de solicitado en la sucursal
	sucursal 	= models.ForeignKey(Sucursal) # sucursal a la que lo solicita
	solicitante = models.ForeignKey(Solicitud) # solicitante q debe estar en la hora de solicitudes
	servicioRequiere = models.TextField() # explicacion del servicio que requiere, actualizacion etc, seria un tipo, pero wuaaa mas tablas
	fxAtencion 	= models.DateField(null=True, blank=True) # fx de atencion en el area de planes
	atendido 	= models.BooleanField(default=False) # atendido = true, no atendido/en espera = false
	def __unicode__(self):
		servicio="%s - %s / %s"%(self.fxSolicitud.strftime("%d-%m-%Y"), self.sucursal.nombre, self.solicitante.nombre, self.solicitante.aPat, self.solicitante.aMat)
		return servicio

	class Meta:
		ordering = ['-fxSolicitud','sucursal__nombre']
		