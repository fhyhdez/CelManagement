# -*- coding: utf-8 -*-
from djCell.operaciones import comunes
from djCell.operaciones import repor
from django.db.models import Q

from djCell.apps.catalogos.models import Ciudad,CP,Colonia, Estado
from djCell.apps.ventas.models import Venta
from djCell.apps.clientes.models import ClienteFacturacion
from django.contrib.auth.models import User

from djCell.apps.credito.models import *
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

def Subdistribuidores(q):
	if q:
		qset=(Q(cliente__rfc__icontains=q) |
		Q(cliente__razonSocial__icontains=q) | 
		Q(cliente__direccion__icontains=q))
		datos=Subdistribuidor.objects.filter(qset)
	else:
		datos=Subdistribuidor.objects.all()
	return datos
def ReporteSubdistribuidores(pagina, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = Subdistribuidores(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Cliente','Limite de Credito','Fecha de ingreso', 'Estado', 'Telefono', 
			'Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.cliente),
				repor.Rtd(dato.limCredito),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.fxIngreso)),
				repor.Rtd(dato.edo),
				repor.Rtd(dato.telefono),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()


def Creditos(q, subdist):
	if subdist:
		datos=Credito.objects.filter(subdist=subdist)
	elif q:
		qset=(Q(subdist__cliente__rfc__icontains=q)|
		Q(subdist__cliente__razonSocial__icontains=q)|
		Q(subdist__cliente__direccion__icontains=q)|
		Q(subdist__telefono__icontains=q)|
		Q(folioc__icontains=q)|
		Q(venta__folioVenta__icontains=q)|
		Q(observacion__icontains=q))
		datos=Credito.objects.filter(qset)
	else:
		datos=Credito.objects.all()
	return datos
def ReporteCreditos(pagina, subdist, filtro):
	#si no se manejan filtros especiales se puede quitar datos y usar
	if subdist:
		tituloR='Credito del Subdistribuidor %s'%(subdist)
		datos = Creditos(filtro, subdist)
		if datos:
			datos=repor.Paginador(datos,numElem,pagina)
			contenido=repor.RTitulos(['Folio','Venta','Total de la Venta', 'Plazo', 'Fecha del Credito',
			'Estado de Credito', 'Observaciones', 'Seleccionar' ])
			for dato in datos:
				contenido='%s%s'%(contenido ,repor.Rtr([

					repor.Rtd(dato.folioc),
					repor.Rtd(dato.venta),
					repor.Rtd(dato.totalvta),
					repor.Rtd(dato.plazo),
					#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
					repor.Rtd(comunes.FechaSTR(dato.fxCredito)),
					repor.Rtd(dato.edo),
					repor.Rtd(dato.observacion),
					repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
					
					]))
			return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
		elif filtro:
			return repor.NoDatos()
		else:
			return repor.NoResultados()
	else:
		return 'Error de Servidor, no se encontro Subdistribuidor'

def HistorialSubdistribuidores(credito):
	if credito:
		datos=HistorialSubdistribuidor.objects.filter(credito=credito)
	else:
		None
	return datos
def ReporteHistorialSubdistribuidores(pagina, credito, filtro):
	#si no se manejan filtros especiales se puede quitar datos y usar
	if credito:
		datos = HistorialSubdistribuidores(credito)
		tituloR = 'Historial de Credito %s, del Subdistribuidor'%(credito, credito.subdist)
		if datos:
			datos=repor.Paginador(datos,numElem,pagina)
			contenido=repor.RTitulos(['Abono','Fecha de Abono'])
			for dato in datos:
				contenido='%s%s'%(contenido ,repor.Rtr([

					repor.Rtd(dato.abono),
					#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
					repor.Rtd(comunes.FechaSTR(dato.fxAbono))
					]))
			return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
		elif filtro:
			return repor.NoDatos()
		else:
			return repor.NoResultados()
	return 'No se encontro el la Linea de Credito especificada'