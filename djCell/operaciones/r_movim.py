# -*- coding: utf-8 -*-
from djCell.operaciones import comunes
from djCell.operaciones import repor
from django.db.models import Q

from django.contrib.auth.models import User
from djCell.apps.sucursales.models import Sucursal
from djCell.apps.productos.models import Equipo, Expres, Accesorio, Ficha

from djCell.apps.movimientos.models import *
from django.conf import settings
STATIC_URL = settings.STATIC_URL

numElem=50


'''Plantilla de Reporte html
pagina -- entero que representa el numero de pagina en el paginador
filtro -- fitro de la consulta
tituloR -- Titulo del encabezado del Reporte

#**************** Queri para el filtro ***
def Objetos(filtro):
	return datos
# **************************************************
def ReporteObjetos(pagina, datos, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['TITULO1','TITULO2','TITULO·'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.TEXTO),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.FECHA)),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()


'''
def Movimientos(q, nombre, confir):
	if q:
		qset=(Q(folio__icontains=q)|
		Q(fx_movimiento__icontains=q)|
		Q(sucursalDestino__nombre__icontains=q))
		datos=Movimiento.objects.filter(qset,tipoMovimiento__nombre=nombre,confirmacion=confir).distinct()
	else:
		datos=Movimiento.objects.filter(tipoMovimiento__nombre=nombre,confirmacion=confir).distinct()
	return datos
def ReporteMovimientos(pagina, datos, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Folio','Tipo de Movimiento','Fecha de Movimiento', 'Sucursal de origen',
			'Sucursal Destino', 'Usuario que emitio', 'Usuario que resivio', 'Confirmacion'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.folio),
				repor.Rtd(dato.tipoMovimiento),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.fx_movimiento)),
				repor.Rtd(dato.sucursalOrigen),
				repor.Rtd(dato.sucursalDestino),
				repor.Rtd(dato.usuarioOrigen),
				repor.Rtd(dato.usuarioDestino),
				repor.Rtd_B(dato.confirmacion),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def ListaEquipos(q, movimiento):
	if q:
		qset=(Q(movimiento__folio__icontains=q)|
		Q(movimiento__fx_movimiento__icontains=q)|
		Q(movimiento__sucursalDestino__nombre__icontains=q)|
		Q(equipo__imei__icontains=q)|
		Q(equipo__icc__icontains=q)|
		Q(equipo__detallesEquipo__gama__gama__icontains=q)|
		Q(equipo__detallesEquipo__marca__marca__icontains=q)|
		Q(equipo__detallesEquipo__modelo__icontains=q)|
		Q(equipo__folio=q))
		datos=ListaEquipo.objects.filter(qset,movimiento=movimiento).distinct()
	else:
		datos=ListaEquipo.objects.filter(movimiento=movimiento).distinct()
	return datos
class ListaEquipo(models.Model):
	movimiento 	= models.ForeignKey(Movimiento, limit_choices_to=Q(confirmacion=False))
	equipo 		= models.ForeignKey(Equipo,limit_choices_to=~Q(estatus__estatus ='Vendido'))
	confirmacion = models.BooleanField(default=False)
	def __unicode__(self):
		equipoMov="%s %s"%(self.equipo, self.movimiento)
		return equipoMov
def ReporteListaEquipos(pagina, datos, movimiento, filtro):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	if movimiento:
		datos = Objetos(filtro, movimiento)
		tituloR = 'Equipos en el Movimiento %s'%(movimiento)
		if datos:
			datos=repor.Paginador(datos,numElem,pagina)
			contenido=repor.RTitulos(['Equipo','Confirmacion'])
			for dato in datos:
				contenido='%s%s'%(contenido ,repor.Rtr([

					repor.Rtd(dato.equipo),
					repor.Rtd_B(dato.confirmacion)
					]))
			return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
		elif filtro:
			return repor.NoDatos()
		else:
			return repor.NoResultados()
	else:
		return 'No se Enontro el Movimiento'



class ListaExpres(models.Model):
	movimiento 	= models.ForeignKey(Movimiento, limit_choices_to=Q(confirmacion=False))
	expres 		= models.ForeignKey(Expres)
	confirmacion = models.BooleanField(default=False)
	def __unicode__(self):
		expresMov="%s %s"%(self.expres, self.movimiento)
		return expresMov

class ListaAccesorio(models.Model):
	movimiento 	= models.ForeignKey(Movimiento, limit_choices_to=Q(confirmacion=False))
	accesorio 	= models.ForeignKey(Accesorio)
	confirmacion = models.BooleanField(default=False)
	def __unicode__(self):
		accesorioMov="%s %s"%(self.accesorio, self.movimiento)
		return accesorioMov

class ListaFichas(models.Model):
	movimiento  = models.ForeignKey(Movimiento, limit_choices_to=Q(confirmacion=False))
	ficha 		= models.ForeignKey(Ficha)
	confirmacion = models.BooleanField(default=False)
	def __unicode__(self):
		fichaMov="%s %s"%(self.ficha, self.movimiento)
		return fichaMov

class TransferenciaSaldo(models.Model):
	movimiento = models.ForeignKey(Movimiento, limit_choices_to=Q(confirmacion=False))#humm
	monto = models.DecimalField(max_digits=10,decimal_places=2) #monto
	observaciones = models.TextField(null=True, blank=True)#observaciones
	def __unicode__(self):
		return str(self.monto)