# -*- coding: utf-8 -*-
from djCell.operaciones import comunes
from djCell.operaciones import repor
from django.db.models import Q
from djCell.apps.contabilidad.models import *
from djCell.apps.personal.models import Empleado
from djCell.apps.proveedor.models import Proveedor
from djCell.apps.corteVta.models import CorteVenta
from django.contrib.auth.models import User


''' Plantilla de Reporte html
pagina -- entero que representa el numero de pagina en el paginador
filtro -- fitro de la consulta
tituloR -- Titulo del encabezado del Reporte

#**************** Queri para el filtro ***
def Nominas(filtro):
	if filtro:
		qset=(
			Q(folio__icontains=filtro)|
			Q(descripcion__icontains=filtro)
			)
		return Nomina.objects.filter(qset).order_by('-id')
	else:
		return Nomina.objects.all().order_by('-id')
# *************** Plantilla HTML *********
def ReporteNominas(pagina, filtro, tituloR):
	objetos = Objetos(filtro)		#*
	if objetos:
		objetos=repor.Paginador(objetos,4,pagina)
		contenido=repor.RTitulos(['Titulo1','Titulo2','....Etc'])#*
		for objeto in objetos:		#*
			contenido='%s%s'%(contenido ,repor.Rtr([
				repor.Rtd(   *objeto.texto*   ),		# aplica para textos
				repor.Rtd(   *comunes.FechaSTR(objeto.fecha)*   ),	#aplica para Fechas, pone bien el formato
				repor.Rtd_B( *objeto.boolean*    ),	#aplica para booleanos, pone una imagen negativa o positiva
				repor.Rtd(   *'<a href=\"?filtro=%s\">Seleccionar</a>'%(objeto.id)*   ) #Ejemplo de contruccion avanzada
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,objetos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()


'''
def Nominas(filtro):
	if filtro:
		qset=(
			Q(folio__icontains=filtro)|
			Q(descripcion__icontains=filtro)
			)
		return Nomina.objects.filter(qset).order_by('-id')
	else:
		return Nomina.objects.all().order_by('-id')
# **************************************************
def ReporteNominas(pagina, filtro, tituloR):
	nominas = Nominas(filtro)
	if nominas:
		nominas=repor.Paginador(nominas,4,pagina)
		contenido=repor.RTitulos(['Folio','Fecha de Creacion','Descripcion','Imprimir' ,'Seleccionar'])
		for nomina in nominas:
			contenido='%s%s'%(contenido ,repor.Rtr([
				repor.Rtd(nomina.folio),
				repor.Rtd(comunes.FechaSTR(nomina.fxCreacion)),
				repor.Rtd(nomina.descripcion),
				repor.Rtd('<form  action=\".\" method=\"GET\" enctype=\"multipart/form-data\"><a href=\"\" class=\"tooltipbasic\" data-tooltip=\"Descargar Nomina seleccionada\"><input type=\"checkbox\" name=\"excel\" value=\"Exportar\">Descargar Reporte</a> || <input title=\"De clic para imprimir la consulta\" class=\"submit success\" type=\"submit\" value=\"Descargar\"><input type=\"hidden\" name=\"key\" value=\"%s\"/></form>'%(nomina.id)),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(nomina.id)),
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,nominas))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()