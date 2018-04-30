# -*- coding: utf-8 -*-
from djCell.operaciones import comunes
from djCell.operaciones import repor
from django.db.models import Q

from djCell.apps.ventas.models import *
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
		return repor.NoResultados()
	else:
		return repor.NoDatos()


'''

def VentaEquipos(q, factu):
	if q:
		qset=(Q(equipo__imei__icontains=q)|
		Q(equipo__icc__icontains=q)|
		Q(equipo__factura__folio__icontains=q)|
		Q(equipo__detallesEquipo__modelo__icontains=q)|
		Q(equipo__detallesEquipo__marca__marca__icontains=q)|
		Q(equipo__detallesEquipo__color__icontains=q)|
		Q(equipo__sucursal__nombre__icontains=q)|
		Q(equipo__noCell__icontains=q)|
		Q(venta__folioVenta__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(venta__usuario__username__icontains=q))
		datos=VentaEquipo.objects.filter(qset, equipo__productoFacturado=factu)
	else:
		datos=VentaEquipo.objects.filter(equipo__productoFacturado=factu)
	return datos
def ReporteVentaEquipos(pagina, filtro, tituloR, factu):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = VentaEquipos(filtro, factu)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Equipo','Venta'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.equipo),
				repor.Rtd(dato.venta)
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				#repor.Rtd(comunes.FechaSTR(dato.FECHA)),
				#repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoResultados()
	else:
		return repor.NoDatos()


def VentaExpress(q, factu):
	if q:
		qset=(Q(expres__icc__icontains=q)|
		Q(expres__factura__folio__icontains=q)|
		Q(expres__noCell__icontains=q)|
		Q(expres__detallesExpres__descripcion__icontains=q)|
		Q(expres__sucursal__nombre__icontains=q)|
		Q(expres__detallesExpres__tipoIcc__tipoIcc__icontains=q)|
		Q(venta__folioVenta__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(venta__usuario__username__icontains=q))
		datos = VentaExpres.objects.filter(qset,expres__productoFacturado=factu)
	else:
		datos=VentaExpres.objects.filter(expres__productoFacturado=factu)
	return datos
def ReporteVentaExpress(pagina, filtro, tituloR, factu):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = VentaExpress(filtro, factu)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Expres','Venta'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.expres),
				repor.Rtd(dato.venta)
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				#repor.Rtd(comunes.FechaSTR(dato.FECHA)),
				#repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoResultados()
	else:
		return repor.NoDatos()



def VentaAccesorios(q, factu):
	if q:
		qset=(Q(accesorio__codigoBarras__icontains=q)|
		Q(accesorio__factura__folio__icontains=q)|
		Q(accesorio__detallesAccesorio__marca__marca__icontains=q)|
		Q(accesorio__detallesAccesorio__seccion__seccion__icontains=q)|
		Q(accesorio__sucursal__nombre__icontains=q)|
		Q(accesorio__detallesAccesorio__descripcion__icontains=q)|
		Q(venta__folioVenta__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(venta__usuario__username__icontains=q))
		datos = VentaAccesorio.objects.filter(qset, accesorio__productoFacturado=factu)
	else:
		datos=VentaAccesorio.objects.filter(accesorio__productoFacturado=factu)
	return datos
def ReporteVentaAccesorios(pagina, filtro, tituloR, factu):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = VentaAccesorios(filtro, factu)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Accesorio','Ficha'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.accesorio),
				repor.Rtd(dato.venta),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				#repor.Rtd(comunes.FechaSTR(dato.FECHA)),
				#repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoResultados()
	else:
		return repor.NoDatos()


def VentaFichass(q, factu):
	if q:
		qset=(Q(ficha__folio__icontains=q)|
		Q(ficha__factura__folio__icontains=q)|
		Q(ficha__sucursal__nombre__icontains=q)|
		Q(ficha__nominacion__nominacion__icontains=q)|
		Q(venta__folioVenta__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(venta__usuario__username__icontains=q))
		datos = VentaFichas.objects.filter(qset, ficha__productoFacturado=factu)
			
	else:
		datos=VentaFichas.objects.filter(ficha__productoFacturado=factu)
	return datos
def ReporteVentaFichass(pagina, filtro, tituloR, factu):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = VentaFichass(filtro, factu)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Ficha','Venta'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.ficha),
				repor.Rtd(dato.venta)
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				#repor.Rtd(comunes.FechaSTR(dato.FECHA)),
				#repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoResultados()
	else:
		return repor.NoDatos()

