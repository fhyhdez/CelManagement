# -*- coding: utf-8 -*-
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def Paginador(objetos, maximo, pagina):
	paginado = Paginator(objetos, maximo)
	try:
		paginado = paginado.page(pagina)
	except PageNotAnInteger:
		paginado = paginado.page(1)
	except EmptyPage:
		paginado = paginado.page(paginado.num_pages)
	return paginado