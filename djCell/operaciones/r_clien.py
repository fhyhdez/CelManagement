# -*- coding: utf-8 -*-
from djCell.operaciones import comunes
from djCell.operaciones import repor
from django.db.models import Q
from djCell.apps.catalogos.models import Ciudad,CP,Colonia, Estado
from djCell.apps.sucursales.models import Sucursal


from djCell.apps.clientes.models import *
from django.conf import settings
STATIC_URL = settings.STATIC_URL

numElem=50

def ClienteServicios(q, tipo, suc):
	if q:
		qset = (Q(nombre__icontains=q) | Q(direccion__icontains=q) | Q(folio__icontains=q)  | 
		Q(colonia__colonia__icontains=q) | Q(ciudad__ciudad__icontains=q))
		datos=ClienteServicio.objects.filter(qset,tipoCliente=tipo,sucursal__id=suc).distinct()
	else:
		datos=ClienteServicio.objects.filter(tipoCliente=tipo,sucursal__id=suc).distinct()
	return datos
def ReporteClienteServicios(pagina, datos, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Nombre','Direccion','Sucursal', 'Fecha de Ingreso', 'Tipo de Cliente',
			'Folio'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.nombre),
				repor.Rtd('%s, Colonia %s, Ciudad de %s'%(dato.direccion, dato.colonia, dato.ciudad)),
				repor.Rtd(dato.sucursal),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.fxIngreso)),
				repor.Rtd(dato.tipoCliente),
				repor.Rtd(dato.folio),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def ClienteFacturaciones(q):
	if q:
		qset=(Q(rfc__icontains=q)|
		Q(razonSocial__icontains=q)|
		Q(direccion__icontains=q))
		datos=ClienteFacturacion.objects.filter(qset)
	else:
		datos=ClienteFacturacion.objects.all()
	return datos
def ReporteClienteFacturaciones(pagina, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = ClienteFacturaciones(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['RFC','Razon Social','Direccion', 'Editar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.rfc),
				repor.Rtd(dato.razonSocial),
				repor.Rtd('%s, Colonia %s, Ciudad de %s, C.P. %s, %s'%(dato.direccion, dato.colonia, dato.ciudad, dato.cp, dato.estado)),
				repor.Rtd('<a href=\"/contabilidad/facturacion/facturas/cliente/nuevo/?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def Mayoristas(q):
	if q:
		qset=(Q(cliente__rfc__icontains=q) |
		Q(cliente__razonSocial__icontains=q) | 
		Q(cliente__direccion__icontains=q))
		datos=Mayorista.objects.filter(qset)
	else:
		datos=Mayorista.objects.all()
	return datos
def ReporteMayoristas(pagina, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = Mayoristas(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Cliente','Descuento en Fichas','Descuento en Recargas', 'Telefono'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.cliente),
				repor.Rtd(dato.descuentoFichas),
				repor.Rtd(dato.descuentoRecargas),
				repor.Rtd(dato.telefono),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()
