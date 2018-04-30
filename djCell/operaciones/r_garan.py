# -*- coding: utf-8 -*-
from djCell.operaciones import comunes
from djCell.operaciones import repor
from django.db.models import Q

from djCell.apps.sucursales.models import Sucursal
from djCell.apps.productos.models import Equipo
from djCell.apps.papeletas.models import Papeleta

from djCell.apps.garantiaSuc.models import *
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

def Garantias(q):
	if q:
		qset=(Q(sucursal__nombre__icontains=q) |Q(papeleta__folioPapeleta__icontains=q) | 
			Q(papeleta__nombre__icontains=q) | Q(equipo__imei__icontains=q) | 
		 	Q(equipo__icc__icontains=q))
		garantia = Garantia.objects.filter(qset).order_by('estado') #.order_by('sucursal').order_by('fxSucursal')
	else:
		garantia = Garantia.objects.all().order_by('estado')
	return garantia
def ReporteGarantias(pagina, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = Garantias(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Papeleta','Equipo','Falla', 'Sucursal', 'Fecha de ingreso',
			'¿LLego a almacen?', 'Fecha de LLegada a almacen', 'Fecha de CAC', 'Observacion', 
			'Estado', 'Fecha de Revision'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.papeleta),
				repor.Rtd(dato.equipo),
				repor.Rtd(dato.falla),
				repor.Rtd(dato.sucursal),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.fxSucursal)),
				repor.Rtd_B(dato.llegoAlmacen),
				repor.Rtd(comunes.FechaSTR(dato.fxAlmacen)),
				repor.Rtd(comunes.FechaSTR(dato.fxCAC)),
				repor.Rtd(dato.observacion),
				repor.Rtd(dato.estado),
				repor.Rtd(comunes.FechaSTR(dato.fxRevision))

				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()