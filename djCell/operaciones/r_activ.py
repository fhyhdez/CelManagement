# -*- coding: utf-8 -*-
from djCell.operaciones import comunes
from djCell.operaciones import repor
from django.db.models import Q


from djCell.apps.sucursales.models import Sucursal
from djCell.apps.personal.models import Empleado
from djCell.apps.productos.models import Equipo, Expres
from djCell.apps.planes.models import Plan, Solicitud
from djCell.apps.activaciones.models import *
from django.conf import settings
STATIC_URL = settings.STATIC_URL

numElem=50


def ActivacionEquipos(q, status):
	if q:
		qset=(Q(fxActivacion__icontains=q) |
		 Q(equipo__imei__icontains=q) | 
		 Q(equipo__icc__icontains=q) | 
		 Q(equipo__detallesEquipo__marca__marca__icontains=q) | 
		 Q(equipo__detallesEquipo__modelo__icontains=q) | 
		 Q(tipoActivacion__tipo__icontains=q) |
		 Q(empleado__nombre__icontains=q) | 
		 Q(empleado__aPaterno__icontains=q) | 
		 Q(empleado__aMaterno__icontains=q) |  
		 Q(empleado__curp__icontains=q) | 
		 Q(sucursal__nombre__icontains=q))
		datos=ActivacionEquipo.objects.filter(qset,equipo__estatus__estatus=status).order_by('equipo')
	else:
		datos=ActivacionEquipo.objects.filter(equipo__estatus__estatus=status).order_by('equipo')
	return datos
def ReporteActivacionEquipos(pagina, datos, filtro, tituloR):
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Equipo','Tipo de Activacion','Fecha de activacion',
			'Usuario que activo' ,'Vendedor', 'Sucursal','Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.equipo),
				repor.Rtd(dato.tipoActivacion),
				repor.Rtd(comunes.FechaSTR(dato.fxActivacion)),
				repor.Rtd(dato.usuario.name),
				repor.Rtd(dato.empleado),
				repor.Rtd(dato.sucursal),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def ActivacionExpresss(q,status):
	if q:
		qset=(Q(fxActivacion__icontains=q) |
			 Q(express__icc__icontains=q) | 
			 Q(tipoActivacion__tipo__icontains=q) |
			 Q(empleado__nombre__icontains=q) | 
			 Q(empleado__aPaterno__icontains=q) | 
			 Q(empleado__aMaterno__icontains=q) |  
			 Q(empleado__curp__icontains=q) | 
			 Q(sucursal__nombre__icontains=q))
		datos=ActivacionExpress.objects.filter(qset,express__estatus__estatus=status).order_by('express')
	else:
		datos=ActivacionExpress.objects.filter(express__estatus__estatus=status).order_by('express')
	return datos
def ReporteActivacionExpresss(pagina, datos, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Express','Tipo de Activacion','Fecha de Activacion',
			'Usuario que activo' ,'Vendedor', 'Sucursal','Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.express),
				repor.Rtd(dato.tipoActivacion),
				repor.Rtd(comunes.FechaSTR(dato.fxActivacion)),
				repor.Rtd(dato.usuario),
				repor.Rtd(dato.empleado),
				repor.Rtd(dato.sucursal),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def ActivacionPlanes(q):
	if q:
		qset=(Q(fxActivacion__icontains=q) |
		 Q(plan__plan__icontains=q) |
		 Q(equipo__imei__icontains=q) | 
		 Q(equipo__icc__icontains=q) | 
		 Q(equipo__detallesEquipo__marca__marca__icontains=q) | 
		 Q(equipo__detallesEquipo__modelo__icontains=q) | 
		 Q(sucursal__nombre__icontains=q))
		datos=ActivacionPlan.objects.filter(qset).order_by('equipo')
	else:
		datos=ActivacionPlan.objects.all().order_by('equipo')
	return datos
def ReporteActivacionPlanes(pagina, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	datos = ActivacionPlanes(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Equipo','Plan','Solicitud','Sucursal', 'Fecha de Autorizacion',
			'Ejecutivo', 'form_act', 'difEquipo', 'difContado', 'finanMeses', 'numGratis', 'Lada',
			'actSno','noActcliente', 'hraCdom', 'hraRef', 'Fecha de Activacion'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.equipo),
				repor.Rtd(dato.plan),
				repor.Rtd(dato.solicitud),
				repor.Rtd(dato.sucursal),
				repor.Rtd(comunes.FechaSTR(dato.fxAutorizacion)),
				repor.Rtd(dato.ejecutivo),
				repor.Rtd(dato.form_act),
				repor.Rtd(dato.difEquipo),
				repor.Rtd(dato.difContado),
				repor.Rtd(dato.finanMeses),
				repor.Rtd(dato.numGratis),
				repor.Rtd(dato.lada),
				repor.Rtd(dato.actSno),
				repor.Rtd(dato.noActcliente),
				repor.Rtd(dato.hraCdom),
				repor.Rtd(dato.hraRef),
				repor.Rtd(comunes.FechaSTR(dato.fxActivacion)),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()