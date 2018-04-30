# -*- coding: utf-8 -*-
from djCell.operaciones import comunes
from djCell.operaciones import repor
from django.db.models import Q
from django.contrib.auth.models import User
from djCell.apps.sucursales.models import Sucursal
from djCell.apps.personal.models import Empleado
from djCell.apps.productos.models import Equipo, Expres, Accesorio, Ficha

from djCell.apps.auditoria.models import *
from django.conf import settings
STATIC_URL = settings.STATIC_URL

numElem=50

def ArqueoCajas(q):
	if q:
		qset=(Q(sucursal__nombre__icontains=q)|
		Q(vendedor__user__username__icontains=q)|
		Q(auditor__nombre__icontains=q))
		datos=ArqueoCaja.objects.filter(qset)
	else:
		datos=ArqueoCaja.objects.all()
	return datos
def ReporteArqueoCajas(pagina, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar
	datos = ArqueoCajas(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Fecha de Arqueo','Sucursal','Vendedor', 'Auditor', 'Total de Caja',
			'Total de Arqueo', 'Diferencia de Arqueo', 'Observaciones'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(comunes.FechaSTR(dato.fxArqueo)),
				repor.Rtd(dato.sucursal),
				repor.Rtd(dato.vendedor),
				repor.Rtd(dato.auditor),
				repor.Rtd(dato.totalCaja),
				repor.Rtd(dato.totalArqueo),
				repor.Rtd(dato.difArqueo),
				repor.Rtd(dato.observaciones)
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def Inventarios(q, cerrado):
	if q:
		qset=(Q(sucursal__nombre__icontains=q)|
		Q(folio__icontains=q)|
		Q(fxInicio__icontains=q)|
		Q(fxFinal__icontains=q))
		if cerrado:
			datos = Inventario.objects.filter(qset)
		else:
			datos = Inventario.objects.filter(qset, cerrado=cerrado)
	else:
		if cerrado:
			datos=Inventario.objects.all()
		else:
			datos = Inventario.objects.filter(cerrado=cerrado)
	return datos
def ReporteInventarios(pagina, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = Inventarios(filtro, True)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Folio','Fecha de Inicio','Fecha  de Finalizacion', 'Sucursal', 
			'Diferencia de Equipos', 'Diferencia de Express', 'Diferencia de Fichas', 'Diferencia de Accesorios',
			'Diferencia de Otros', 'Diferencia de Street', 'Sancion', 'Descripcion de la Sancion', 'Elevado',
			'Determina', 'Observaciones', 'Terminada', 'Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.folio),
				repor.Rtd(comunes.FechaSTR(dato.fxInicio)),
				repor.Rtd(comunes.FechaSTR(dato.fxFinal)),
				repor.Rtd(dato.sucursal),
				repor.Rtd(dato.difEquipo),
				repor.Rtd(dato.difExpres),
				repor.Rtd(dato.difFicha),
				repor.Rtd(dato.difAccesorio),
				repor.Rtd(dato.difOtros),
				repor.Rtd(dato.difStreet),
				repor.Rtd(dato.sancion),
				repor.Rtd(dato.descSancion),
				repor.Rtd(dato.elevado),
				repor.Rtd(dato.determina),
				repor.Rtd(dato.observaciones),
				repor.Rtd_B(dato.terminada),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoResultados()
	else:
		return repor.NoDatos()
def ReporteInventariosMinimo(pagina, filtro, tituloR, cerrado):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = Inventarios(filtro, cerrado)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Folio','Fecha de Inicio','Fecha  de Finalizacion', 'Sucursal',
			'Determina', 'Observaciones', 'Terminada', 'Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.folio),
				repor.Rtd(comunes.FechaSTR(dato.fxInicio)),
				repor.Rtd(comunes.FechaSTR(dato.fxFinal)),
				repor.Rtd(dato.sucursal),
				repor.Rtd(dato.determina),
				repor.Rtd(dato.observaciones),
				repor.Rtd_B(dato.terminada),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoResultados()
	else:
		return repor.NoDatos()

def InvEquipos(q,inventario,revisado):
	if q:
		qset=(Q(equipo__imei__icontains=q)|
		Q(equipo__icc__icontains=q)|
		Q(equipo__detallesEquipo__marca__marca__icontains=q)|
		Q(equipo__detallesEquipo__modelo__icontains=q))
		datos=InvEquipo.objects.filter(qset, inventario=inventario, revisado=revisado)
	else:
		datos=InvEquipo.objects.filter(inventario=inventario, revisado=revisado)
	return datos
def ReporteInvEquipos(pagina, datos, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Inventario','Equipo','Existencia', 'Accesorios', 'Observaciones', 'Revisado',
			'Fecha de revision'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.inventario),
				repor.Rtd(dato.equipo),
				repor.Rtd_B(dato.existe),
				repor.Rtd_B(dato.accesorios),
				repor.Rtd(dato.observacion),
				repor.Rtd_B(dato.revisado),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.fxRevision)),
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def InvExpress(q,inventario,revisado):
	if q:
		qset=(Q(expres__icc__icontains=q)|
		Q(expres__noCell__icontains=q))
		datos=InvExpres.objects.filter(qset, inventario=inventario, revisado=revisado)
	else:
		datos=InvExpres.objects.filter(inventario=inventario, revisado=revisado)
	return datos
def ReporteInvExpress(pagina, datos, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Inventario','Expres','Existencia', 'Observaciones', 'Revisado',
			'Fecha de revision'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.inventario),
				repor.Rtd(dato.expres),
				repor.Rtd_B(dato.existe),
				repor.Rtd(dato.observacion),
				repor.Rtd_B(dato.revisado),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.fxRevision))

				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def InvAccesorios(q,inventario,revisado):
	if q:
		qset=(Q(accesorio__codigoBarras__icontains=q)|
		Q(accesorio__detallesAccesorio__marca__marca__icontains=q)|
		Q(accesorio__detallesAccesorio__descripcion__icontains=q))
		datos=InvAccesorio.objects.filter(qset, inventario=inventario, revisado=False)
	else:
		datos=InvAccesorio.objects.filter(inventario=inventario, revisado=revisado)
	return datos
def ReporteInvAccesorios(pagina, datos, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Inventario','Accesorio','Existencia', 'Observaciones', 'Revisado',
			'Fecha de revision'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.inventario),
				repor.Rtd(dato.accesorio),
				repor.Rtd_B(dato.existe),
				repor.Rtd(dato.observacion),
				repor.Rtd_B(dato.revisado),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.fxRevision))

				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()




def ReporteInventarioAuditores(inven, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	if inven:
		try:
			datos=InventarioAuditores.objects.filter(inventario=inven)
		except :
			datos=None
	if datos:
		contenido=repor.RTitulos(['Auditor asignado','Auditando'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.auditor),
				repor.Rtd_B(dato.turno)

				]))
		return '%s\n%s'%(repor.EncabezadoR(tituloR),contenido)
	else:
		return None