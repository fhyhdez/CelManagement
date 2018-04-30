# -*- coding: utf-8 -*-
'''from djCell.operaciones import comunes
from djCell.operaciones import repor
from django.db.models import Q


from djCell.apps.auditoria.models import *
from django.conf import settings
STATIC_URL = settings.STATIC_URL

numElem=50


Plantilla de Reporte html
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