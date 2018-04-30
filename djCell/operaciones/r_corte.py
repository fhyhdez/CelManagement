# -*- coding: utf-8 -*-
from djCell.operaciones import comunes
from djCell.operaciones import repor
from django.db.models import Q
from django.contrib.auth.models import User
from djCell.apps.personal.models import Empleado
from djCell.apps.sucursales.models import Sucursal
from djCell.apps.productos.models import Equipo
from djCell.apps.clientes.models import ClienteServicio
from djCell.apps.ventas.models import Venta

from djCell.apps.corteVta.models import *
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
def CorteVentas(q):
	if q:
		qset=(Q(folioCorteVta__icontains=q)|
		Q(sucursal__nombre__icontains=q)|
		Q(observacion__icontains=q))
		datos=CorteVenta.objects.filter(qset)
	else:
		datos=CorteVenta.objects.all()
	return datos
def ReporteCorteVentas(pagina, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = CorteVentas(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Folio','Fecha de Corte','Sucursal', 'Total de Venta', 'Total de Gastos',
			'Total', 'Observaciones', 'Usuario que cerro el corte', 'Revisado', 'Cerrado', 'Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.folioCorteVta),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.fxCorte)),
				repor.Rtd(dato.sucursal),
				repor.Rtd(dato.totalVta),
				repor.Rtd(dato.totalGastos),
				repor.Rtd(dato.total),
				repor.Rtd(dato.observacion),
				repor.Rtd(dato.cierraCorte),
				repor.Rtd_B(dato.revisado),
				repor.Rtd_B(dato.cerrado),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def GastosSucursales(sucursal):
	if sucursal:
		datos=GastosSucursal.objects.filter(sucursal=sucursal)
	else:
		datos=None
	return datos
def ReporteGastosSucursales(pagina, sucursal, filtro):
	#si no se manejan filtros especiales se puede quitar datos y usar
	if sucursal:
		tituloR ='Gastos de la Sucursal %s'%(sucursal)
		datos = GastosSucursales(sucursal)
		if datos:
			datos=repor.Paginador(datos,numElem,pagina)
			contenido=repor.RTitulos(['Tipo de Gasto','Gasto','Fecha del Gasto', 'Usuario que Registro',
				'Observaciones', 'Corte de Venta' ])
			for dato in datos:
				contenido='%s%s'%(contenido ,repor.Rtr([

					repor.Rtd(dato.tipoGasto),
					repor.Rtd(dato.gasto),
					#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
					repor.Rtd(comunes.FechaSTR(dato.fxGasto)),
					repor.Rtd(dato.usuario),
					repor.Rtd(dato.observacion),
					repor.Rtd(dato.corteVenta)
					#repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
					
					]))
			return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
		elif filtro:
			return repor.NoDatos()
		else:
			return repor.NoResultados()
	else:
		return 'Error de datos, Sucursal no encontrada'

'''
class VentasCorte(models.Model):
	corteVenta = models.ForeignKey(CorteVenta)
	venta = models.ForeignKey(Venta)
	def __unicode__(self):
		wua ="corte: %s vta: %s total venta: %s"%(self.corteVenta.folioCorteVta, self.venta.folioVenta, self.venta.total)
		return wua
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

def DiferenciasCortes(q):
	if q:
		qset=(Q(corteVenta__folioCorteVta__icontains=q)|
		Q(corteVenta__sucursal__nombre__icontains=q)|
		Q(corteVenta__observacion__icontains=q)|
		Q(revisaCorte__username__icontains=q)|
		Q(observacion__icontains=q))
		datos=DiferenciasCorte.objects.filter(qset)
	else:
		datos=DiferenciasCorte.objects.all()
	return datos
def ReporteDiferenciasCortes(pagina, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = DiferenciasCortes(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Corte de Venta','Diferencia','Fecha de Diferencia',
			'Usuario que reviso el corte', 'Observaciones'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.corteVenta),
				repor.Rtd(dato.diferencia),
				repor.Rtd(comunes.FechaSTR(dato.fxDiferencia)),
				repor.Rtd(dato.revisaCorte),
				repor.Rtd(dato.observacion)
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def RecargasVendidoCortes(q):
	if q:
		qset=(Q(sucursal__nombre__icontains=q)|
		Q(corte__sucursal__nombre__icontains=q)|
		Q(corte__observacion__icontains=q)|
		Q(observaciones__icontains=q))
		datos=DiferenciasCorte.objects.filter(qset)
	else:
		datos=DiferenciasCorte.objects.all()
	return datos
def ReporteRecargasVendidoCortes(pagina, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = RecargasVendidoCortes(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Sucursal','Fecha','Corte', 'Total de Ventas', 'Saldo Final', 'Observaciones'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.sucursal),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.fecha)),
				repor.Rtd(dato.corte),
				repor.Rtd(dato.totalVentas),
				repor.Rtd(dato.saldoFinal),
				repor.Rtd(dato.observaciones)

				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

