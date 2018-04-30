# -*- coding: utf-8 -*-
from djCell.operaciones import comunes
from djCell.operaciones import repor
from django.db.models import Q


from djCell.apps.facturacion.models import *
from django.conf import settings
STATIC_URL = settings.STATIC_URL

numElem=50

def Facturaciones(q):
	if q:
		qset=(Q(clienteFacturacion__rfc__icontains=q)|
		Q(clienteFacturacion__razonSocial__icontains=q)|
		Q(clienteFacturacion__direccion__icontains=q)|
		Q(venta__folioVenta__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(venta__usuario__username__icontains=q)|
		Q(folioFiscal__icontains=q)|
		Q(estado__estado__icontains=q))
		datos=Facturacion.objects.filter(qset)
	else:
		datos=Facturacion.objects.all()
	return datos
def ReporteFacturaciones(pagina, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = Facturaciones(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Cliente Facturacion','Venta','Fecha de Factura', 'Folio Fiscal',
			'Total de venta', 'Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.clienteFacturacion),
				repor.Rtd(dato.venta),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.fxFactura)),
				repor.Rtd(dato.folioFiscal),
				repor.Rtd(dato.totalvta),
				repor.Rtd('<a href=\"/contabilidad/facturacion/facturas/reporte/?filtro=%s\">Ver detalle</a>'%(dato.id))

				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoResultados()
	else:
		return repor.NoDatos()

def FacturaEquipos(q, factura):
	if q:
		qset=(Q(equipo__imei__icontains=q)|
		Q(equipo__icc__icontains=q)|
		Q(equipo__factura__folio__icontains=q)|
		Q(equipo__detallesEquipo__modelo__icontains=q)|
		Q(equipo__detallesEquipo__marca__marca__icontains=q)|
		Q(equipo__detallesEquipo__color__icontains=q)|
		Q(equipo__sucursal__nombre__icontains=q)|
		Q(equipo__noCell__icontains=q)|
		Q(factura__clienteFacturacion__rfc__icontains=q)|
		Q(factura__clienteFacturacion__razonSocial__icontains=q)|
		Q(factura__clienteFacturacion__direccion__icontains=q)|
		Q(factura__venta__folioVenta__icontains=q)|
		Q(factura__venta__sucursal__nombre__icontains=q)|
		Q(factura__venta__usuario__username__icontains=q)|
		Q(factura__folioFiscal__icontains=q)|
		Q(factura__estado__estado__icontains=q))
		if factura:
			datos = FacturaEquipo.objects.filter(qset, factura=factura)
		else:
			datos = FacturaEquipo.objects.filter(qset)	
	else:
		if factura:
			datos = FacturaEquipo.objects.filter(factura=factura)
		else:
			datos=FacturaEquipo.objects.all()
	return datos
def ReporteFacturaEquipos(pagina, filtro, tituloR, factura):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = FacturaEquipos(filtro,factura)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Equipo','Factura', 'Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.equipo),
				repor.Rtd(dato.factura),
				repor.Rtd('<a href=\"/contabilidad/facturacion/facturas/reporte/?filtro=%s\">Ver detalle</a>'%(dato.factura.id))

				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoResultados()
	else:
		if factura:
			return ''
		else:
			return repor.NoDatos()


def FacturaExpress(q,factura):
	if q:
		qset=(Q(expres__icc__icontains=q)|
		Q(expres__factura__folio__icontains=q)|
		Q(expres__noCell__icontains=q)|
		Q(expres__detallesExpres__descripcion__icontains=q)|
		Q(expres__sucursal__nombre__icontains=q)|
		Q(expres__detallesExpres__tipoIcc__tipoIcc__icontains=q)|
		Q(factura__clienteFacturacion__rfc__icontains=q)|
		Q(factura__clienteFacturacion__razonSocial__icontains=q)|
		Q(factura__clienteFacturacion__direccion__icontains=q)|
		Q(factura__venta__folioVenta__icontains=q)|
		Q(factura__venta__sucursal__nombre__icontains=q)|
		Q(factura__venta__usuario__username__icontains=q)|
		Q(factura__folioFiscal__icontains=q)|
		Q(factura__estado__estado__icontains=q))
		if factura:
			datos = FacturaExpres.objects.filter(qset, factura=factura)
		else:
			datos = FacturaExpres.objects.filter(qset)	
	else:
		if factura:
			datos = FacturaExpres.objects.filter(factura=factura)
		else:
			datos=FacturaExpres.objects.all()
	return datos
def ReporteFacturaExpress(pagina, filtro, tituloR, factura):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = FacturaExpress(filtro, factura)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Expres','Factura', 'Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.expres),
				repor.Rtd(dato.factura),
				repor.Rtd('<a href=\"/contabilidad/facturacion/facturas/reporte/?filtro=%s\">Ver detalle</a>'%(dato.factura.id))

				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoResultados()
	else:
		if factura:
			return ''
		else:
			return repor.NoDatos()





def FacturaAccesorios(q, factura):
	if q:
		qset=(Q(accesorio__codigoBarras__icontains=q)|
		Q(accesorio__factura__folio__icontains=q)|
		Q(accesorio__detallesAccesorio__marca__marca__icontains=q)|
		Q(accesorio__detallesAccesorio__seccion__seccion__icontains=q)|
		Q(accesorio__sucursal__nombre__icontains=q)|
		Q(accesorio__detallesAccesorio__descripcion__icontains=q)|
		Q(factura__clienteFacturacion__rfc__icontains=q)|
		Q(factura__clienteFacturacion__razonSocial__icontains=q)|
		Q(factura__clienteFacturacion__direccion__icontains=q)|
		Q(factura__venta__folioVenta__icontains=q)|
		Q(factura__venta__sucursal__nombre__icontains=q)|
		Q(factura__venta__usuario__username__icontains=q)|
		Q(factura__folioFiscal__icontains=q)|
		Q(factura__estado__estado__icontains=q))
		if factura:
			datos = FacturaAccesorio.objects.filter(qset, factura=factura)
		else:
			datos = FacturaAccesorio.objects.filter(qset)	
	else:
		if factura:
			datos = FacturaAccesorio.objects.filter(factura=factura)
		else:
			datos=FacturaAccesorio.objects.all()
	return datos
def ReporteFacturaAccesorios(pagina, filtro, tituloR, factura):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = FacturaAccesorios(filtro, factura)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Accesorios','Factura', 'Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.accesorio),
				repor.Rtd(dato.factura),
				repor.Rtd('<a href=\"/contabilidad/facturacion/facturas/reporte/?filtro=%s\">Ver detalle</a>'%(dato.factura.id))

				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoResultados()
	else:
		if factura:
			return ''
		else:
			return repor.NoDatos()



def FacturaFichass(q, factura):
	if q:
		qset=(Q(ficha__folio__icontains=q)|
		Q(ficha__factura__folio__icontains=q)|
		Q(ficha__sucursal__nombre__icontains=q)|
		Q(ficha__nominacion__nominacion__icontains=q)|
		Q(factura__clienteFacturacion__rfc__icontains=q)|
		Q(factura__clienteFacturacion__razonSocial__icontains=q)|
		Q(factura__clienteFacturacion__direccion__icontains=q)|
		Q(factura__venta__folioVenta__icontains=q)|
		Q(factura__venta__sucursal__nombre__icontains=q)|
		Q(factura__venta__usuario__username__icontains=q)|
		Q(factura__folioFiscal__icontains=q)|
		Q(factura__estado__estado__icontains=q))
		if factura:
			datos = FacturaFichas.objects.filter(qset, factura=factura)
		else:
			datos = FacturaFichas.objects.filter(qset)	
	else:
		if factura:
			datos = FacturaFichas.objects.filter(factura=factura)
		else:
			datos=FacturaFichas.objects.all()
	return datos
def ReporteFacturaFichass(pagina, filtro, tituloR, factura):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = FacturaFichass(filtro, factura)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Ficha','Factura', 'Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.ficha),
				repor.Rtd(dato.factura),
				repor.Rtd('<a href=\"/contabilidad/facturacion/facturas/reporte/?filtro=%s\">Ver detalle</a>'%(dato.factura.id))

				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoResultados()
	else:
		if factura:
			return ''
		else:
			return repor.NoDatos()