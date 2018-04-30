# -*- coding: utf-8 -*-
from djCell.operaciones import comunes
from djCell.operaciones import repor
from django.db.models import Q
from djCell.apps.personal.models import Empleado

from djCell.apps.amonestaciones.models import *
from django.conf import settings
STATIC_URL = settings.STATIC_URL

numElem=50

def Amonestaciones(q):
	if q:
		qset=(Q(fxAmonestacion__icontains=q) |
		 Q(empleado__nombre__icontains=q) | 
		 Q(empleado__aPaterno__icontains=q) | 
		 Q(empleado__aMaterno__icontains=q) | 
		 Q(empleado__curp__icontains=q) | 
		 Q(tipoAmonestacion__tipo__icontains=q))
		datos=Amonestacion.objects.filter(qset)
	else:
		datos=Amonestacion.objects.all()
	return datos
def ReporteAmonestaciones(pagina, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	datos = Amonestaciones(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Empleado','Tipo de Amonestacion','Comentarios','Fecha de Amonestacion',
		'Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.empleado),
				repor.Rtd(dato.tipoAmonestacion),
				repor.Rtd(dato.comentario),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.fxAmonestacion)),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()