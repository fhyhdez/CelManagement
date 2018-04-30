# -*- coding: utf-8 -*-

#este modulo pretende ser una base para la visualizacion de vistas de informacion, se procurara usar un diseño lo mas
#generico para poder ser empleado por los distintos tipos de datos, tambien incluira herramientas adicionales como
#la paginacion y plantilla general para la busqueda.

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
STATIC_URL = settings.STATIC_URL


#plantilla general para busquedas, retorna un html con un textbox y un boton para realizar busquedas mediante variable
#variable por get de nombre 'filtro', se usa en la plantilla como {{buscador|safe}}
def Busqueda(titulo,filtro):
	html='<div id=\"grid\">\n<table id=\"grid\">\n<tr>\n<td id=\"gridhead\">%s</td>\n<td id=\"gridhead\">Buscar</td>\n</tr>\n<tr>\n<form action=\'.\'  method=\'GET\'>\n<td><input type=\'texto\' name=\'filtro\' value=\'%s\'></td>\n<td><input class=\"submit success\" type=\"submit\" value=\'Buscar\'></td>\n</form>\n</tr>\n</table>\n</div>\n'%(titulo, filtro)
	return '%s<br>'%(html)

def EncabezadoR(titulo):
	return '<br>\n<h2>%s</h2>\n<div id=\"grid\"><table id=\"grid\">'%(titulo)

def NoResultados():
	return 'No se encontraron Resultados para el Filtro'

def NoDatos():
	return 'No hay datos disponibles'

def PiesRS():
	#***********Fooder*******
	pie='</table></div>'
	# *********** fin **********
	return pie

#paginador y plantilla para la base del Reporte en html, usa variable get pagina
def Paginador(objetos, maximo, pagina):
	paginado = Paginator(objetos, maximo)
	try:
		paginado = paginado.page(pagina)
	except PageNotAnInteger:
		paginado = paginado.page(1)
	except EmptyPage:
		paginado = paginado.page(paginado.num_pages)
	return paginado

def Paginas(filtro,consulta):
	#***********Fooder*******
	pie='</table></div>\n<div class=\"pagination\">\n<span class=\"step-links\">\n'
	numero = consulta.number
	if consulta.has_previous():
		pie='%s<a href=\"?pagina=%s&amp;filtro=%s\">Anterior</a>\n'%(pie, consulta.previous_page_number(), filtro)

	pie='%s<span class="current">\n'%(pie)
	pie='%sPagina %s de %s.\n'%(pie, consulta.number, str(consulta.paginator.num_pages))
	pie='%s</span>\n'%(pie)

	if consulta.has_next():
		pie='%s<a href=\"?pagina=%s&amp;filtro=%s\">Siguiente</a>\n'%(pie, consulta.next_page_number(), filtro)

	pie='%s</span></div>\n'%(pie)
	# *********** fin **********
	return pie

def RTitulos(titulos):
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)
	return contenido

def Rtd(dato):
	if dato:
		return u'<td>%s</td>\n'%(dato)
	else:
		return '<td></td>\n'

def Rtd_B(estado):
	contenido='<td>'
	if estado:
		contenido='%s<img src=\"%simg/icons/tick.png\" />'%(contenido, STATIC_URL)
	else:
		contenido='%s<img src=\"%simg/icons/exclamation.png\" />'%(contenido, STATIC_URL)
	contenido='%s</td>\n'%(contenido)
	return contenido

def Rtr(tds):
	contenido='<tr>\n'
	for td in tds:
		contenido=('%s%s'%(contenido,td))
	return '%s</tr>\n'%(contenido)