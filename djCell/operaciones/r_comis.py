# -*- coding: utf-8 -*-
from djCell.operaciones import comunes
from djCell.operaciones import repor
from django.db.models import Q
from django.contrib.auth.models import User
from djCell.apps.personal.models import Empleado


from djCell.apps.clientes.models import *
from django.conf import settings
STATIC_URL = settings.STATIC_URL

numElem=50


def Comisiones(q, fal):
	if fal:
		comisiones=Comision.objects.filter(pagado=False).order_by('mes')
	else:
		if q:
			qset=(Q(empleado__nombre__icontains=q)|
			Q(empleado__aPaterno__icontains=q)|
			Q(empleado__aMaterno__icontains=q)|
			Q(mes__icontains=q)|
			Q(fxPago__icontains=q))
			comisiones=Comision.objects.filter(qset).order_by('mes')
		else:
			comisiones=Comision.objects.all().order_by('mes')
	return comisiones
def ReporteComisiones(pagina, datos, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Empleado','Comisiones por Equipo Kit','Comisiones por Equipo Tip',
			'Comisiones de Planes', 'Comisiones por Servicios', 'Mes', 'Pagado', 'Fecha de Pago'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.empleado),
				repor.Rtd(dato.comEquipoKit),
				repor.Rtd(dato.comEquipoTip),
				repor.Rtd(dato.comPlanes),
				repor.Rtd(dato.comServicios),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.mes)),
				repor.Rtd_B(dato.pagado),
				repor.Rtd(comunes.FechaSTR(dato.fxPago))

				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()