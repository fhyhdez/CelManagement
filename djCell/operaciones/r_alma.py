# -*- coding: utf-8 -*-
from djCell.operaciones import comunes
from djCell.operaciones import repor
from django.db.models import Q
from djCell.apps.almacen.models import *
from django.conf import settings
STATIC_URL = settings.STATIC_URL

numElem=50

def AlmacenEquipos(q, estado, estatus):
	if q:
		qset=(Q(equipo__imei__icontains=q)|
		Q(equipo__icc__icontains=q)|
		Q(equipo__factura__folio__icontains=q)|
		Q(equipo__detallesEquipo__modelo__icontains=q)|
		Q(equipo__detallesEquipo__marca__marca__icontains=q)|
		Q(equipo__detallesEquipo__color__icontains=q)|
		Q(equipo__sucursal__nombre__icontains=q)|
		Q(equipo__noCell__icontains=q))
		datos=AlmacenEquipo.objects.filter(qset,estado=estado).exclude(equipo__estatus__estatus=estatus).order_by('equipo')
	else:
		datos=AlmacenEquipo.objects.filter(estado=estado).exclude(equipo__estatus__estatus=estatus).order_by('equipo')
	return datos
def ReporteAlmacenEquipos(pagina, datos, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Sucursal','Equipo','Estado', 'Fecha de Transferencia', 'Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.sucursal),
				repor.Rtd(dato.equipo),
				repor.Rtd_B(dato.estado),
				repor.Rtd(comunes.FechaSTR(dato.fxTransf)),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def AlmacenExpress(q, estado, estatus):
	if q:
		qset=(Q(expres__icc__icontains=q)|
		Q(expres__factura__folio__icontains=q)|
		Q(expres__noCell__icontains=q)|
		Q(expres__detallesExpres__descripcion__icontains=q)|
		Q(expres__sucursal__nombre__icontains=q)|
		Q(expres__detallesExpres__tipoIcc__tipoIcc__icontains=q))
		datos = AlmacenExpres.objects.filter(qset,estado=estado).exclude(expres__estatus__estatus=estatus).order_by('expres')	
	else:
		datos=AlmacenExpres.objects.filter(estado=estado).exclude(expres__estatus__estatus=estatus).order_by('expres')
	return datos
def ReporteAlmacenExpress(pagina, datos, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Sucursal','Express','Estado', 'Fecha de Transferencia', 'Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.sucursal),
				repor.Rtd(dato.expres),
				repor.Rtd_B(dato.estado),
				repor.Rtd(comunes.FechaSTR(dato.fxTransf)),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def AlmacenAccesorios(q, estado, estatus):
	if q:
		qset=(Q(accesorio__codigoBarras__icontains=q)|
		Q(accesorio__factura__folio__icontains=q)|
		Q(accesorio__detallesAccesorio__marca__marca__icontains=q)|
		Q(accesorio__detallesAccesorio__seccion__seccion__icontains=q)|
		Q(accesorio__sucursal__nombre__icontains=q)|
		Q(accesorio__detallesAccesorio__descripcion__icontains=q))
		datos = AlmacenAccesorio.objects.filter(qset,estado=estado).exclude(accesorio__estatusAccesorio__estatus=estatus).order_by('accesorio')
	else:
		datos=AlmacenAccesorio.objects.filter(estado=estado).exclude(accesorio__estatusAccesorio__estatus=estatus).order_by('accesorio')
	return datos
def ReporteAlmacenAccesorios(pagina, datos, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Sucursal','Accesorio','Estado', 'Fecha de Transferencia', 'Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.sucursal),
				repor.Rtd(dato.accesorio),
				repor.Rtd_B(dato.estado),
				repor.Rtd(comunes.FechaSTR(dato.fxTransf)),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def AlmacenFichas(q, estado, estatus):
	if q:
		qset=(Q(ficha__folio__icontains=q)|
		Q(ficha__factura__folio__icontains=q)|
		Q(ficha__sucursal__nombre__icontains=q)|
		Q(ficha__nominacion__nominacion__icontains=q))
		datos = AlmacenFicha.objects.filter(qset,estado=estado).exclude(ficha__estatusFicha__estatus=estatus).order_by('ficha')
			
	else:
		datos=AlmacenFicha.objects.filter(estado=estado).exclude(ficha__estatusFicha__estatus=estatus).order_by('ficha')
	return datos
def ReporteAlmacenFichas(pagina, datos, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Sucursal','Ficha','Estado', 'Fecha de Transferencia', 'Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.sucursal),
				repor.Rtd(dato.ficha),
				repor.Rtd_B(dato.estado),
				repor.Rtd(comunes.FechaSTR(dato.fxTransf)),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()