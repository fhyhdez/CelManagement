# -*- coding: utf-8 -*-
from djCell.operaciones import comunes
from djCell.operaciones import repor
from django.db.models import Q

from django.contrib.auth.models import User
from djCell.apps.personal.models import Empleado
from djCell.apps.sucursales.models import Sucursal
from djCell.apps.productos.models import DetallesEquipo
from djCell.apps.clientes.models import ClienteServicio
from djCell.apps.ventas.models import Venta

from djCell.apps.amonestaciones.models import *
from django.conf import settings
STATIC_URL = settings.STATIC_URL

numElem=50


def Apartados(q):
	if q:
		qset=(Q(clienteApartado__nombre__icontains=q)|
		Q(clienteApartado__folio__icontains=q)|
		Q(equipo__folio__icontains=q)|
		Q(equipo__gama__gama__icontains=q)|
		Q(equipo__marca__marca__icontains=q)|
		Q(equipo__modelo__icontains=q)|
		Q(observacion__icontains=q)|
		Q(estado__estado__icontains=q))
		datos=Apartado.objects.filter(qset)
	else:
		datos=Apartado.objects.all()
	return datos
def ReporteApartados(pagina, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar
	datos = Apartados(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Cliente','Equipo','Observaciones','Precio del equipo', 'Fecha de apartado',
			'Pagado', 'Estado de Apartado', 'Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.clienteApartado),
				repor.Rtd(dato.equipo),
				repor.Rtd(dato.observacion),
				repor.Rtd(dato.precioEquipo),
				repor.Rtd(comunes.FechaSTR(dato.fxApartado)),
				repor.Rtd_B(dato.pagado) #es para los booleanos, cambia el texto por una imagen
				repor.Rtd(dato.estado),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def HistorialApartados(apar):
	if apar:
		datos=HistorialApartado.objects.filter(apartado=apar)
	else:
		None
	return datos
def ReporteHistorialApartados(pagina, apartado, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	if apartado:
		datos=HistorialApartados(apartado)
		if datos:
			datos=repor.Paginador(datos,numElem,pagina)
			contenido=repor.RTitulos(['Apartado','Abono','Tipo', 'Fecha de Abono'])
			for dato in datos:
				contenido='%s%s'%(contenido ,repor.Rtr([

					repor.Rtd(dato.apartado),
					repor.Rtd(dato.abono),
					repor.Rtd(dato.tipo),
					#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
					repor.Rtd(comunes.FechaSTR(dato.fxAbono)),
					
					]))
			return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
		elif filtro:
			return repor.NoDatos()
		else:
			return repor.NoResultados()
	else:
		return 'No se encontro Apartado'