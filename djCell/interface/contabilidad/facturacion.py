# -*- coding: utf-8 -*-

from djCell.apps.facturacion.models import *

from decimal import Decimal
import re

from django.db import transaction

from djCell.interface.contabilidad.forms import FacturacionAGranel
from django.http import HttpResponseRedirect
from djCell.apps.catalogos.models import *

#Modulos de operaciones
from djCell.operaciones import op_pagina, r_conta, repor, r_factu, r_ventas


def Facturas_reporte(nivel, request):
	q=request.GET.get('filtro','')
	pagina=request.GET.get('pagina','')
	reporte=None

	factura=None
	try:
		factura=Facturacion.objects.get(id=q)
	except :
		reporte=r_factu.ReporteFacturaciones(pagina, q, 'Reporte de facturas Realizadas')

	if factura:
		reporte=r_factu.ReporteFacturaEquipos(pagina, None, 'Equipos Facturados', factura)
		reporte='%s <br> %s'%(reporte,r_factu.ReporteFacturaExpress(pagina, None, 'Expres Facturados', factura))
		reporte='%s <br> %s'%(reporte,r_factu.ReporteFacturaFichass(pagina, None, 'Fichas Facturadas', factura))
		reporte='%s <br> %s'%(reporte,r_factu.ReporteFacturaAccesorios(pagina, None, 'Accesorios Facturados', factura))

	ctx={'nivel':nivel, 'buscador':repor.Busqueda('Filtro para Facturas Realizadas',q) ,
	 'reporte':reporte, 'titulo': 'Reporte de Facturas', 'factura': factura}

	return ctx



def Facturas_agregar(nivel, request):
	form=FacturacionAGranel()
	equipos=r_ventas.VentaEquipos(None, False)
	expres=r_ventas.VentaExpress(None, False)
	accesorios=r_ventas.VentaAccesorios(None, False)
	fichas=r_ventas.VentaFichass(None, False)
	info = ""
	clienterfc=None
	factura=None
	liga=None
	if 'guardar' in request.POST:
		form = FacturacionAGranel(request.POST or None)
		if form.is_valid():
			rfc 	= (form.cleaned_data['rfc']).upper()
			folio 	= form.cleaned_data['folio']
			try:
				clienterfc = ClienteFacturacion.objects.get(rfc=(rfc).upper())
			except :
				txt=str(rfc).upper()
				re1='[A-Z]{3,4}-[0-9]{2}[0-1][0-9][0-3][0-9]-[A-Z0-9]?[A-Z0-9]?[0-9A-Z]?'
				rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
				m = rg.search(txt)
				if m:
					try:
						with transaction.atomic():
							a = ClienteFacturacion()
							a.rfc 			= (rfc).upper()
							a.razonSocial 	= ("Por actualizar").title()
							a.direccion 	= ("Por actualizar").title()
							a.colonia 		= Colonia.objects.get(id=1)
							a.ciudad 		= Ciudad.objects.get(id=1)
							a.cp 			= CP.objects.get(id=1)
							a.estado 		= Estado.objects.get(estado__icontains='PUEBLA')
							a.save()
							clienterfc = a
					except :
						form = FacturacionAGranel(request.POST or None)
						info = "El Cliente nuevo se tendra que registrar en contabilidad. Consulte a un administrador."
				else:
					form = FacturacionAGranel(request.POST or None)
					info = "El RFC no es correcto, Cliente nuevo."
		else:
			form = FacturacionAGranel(request.POST or None)
			info = "Verifique sus datos"
		if clienterfc:
			try:
				with transaction.atomic():
					f =  Facturacion()
					f.clienteFacturacion = clienterfc
					f.folioFiscal = folio
					f.totalvta = 0
					f.save()
					factura=f
					
					#info = "Productos a Factura " + f.folioFiscal+" Venta "+str(vta)
			except :
				info = "Hubo errores en la transaccion, favor de verificar con contabilidad"
		if factura:
			total=0
			for equi in equipos:
				chek=request.POST.get('eq_%s'%(equi.equipo.id),'')
				if chek:
					fac=FacturaEquipo()
					fac.factura=factura
					fac.equipo=equi.equipo
					fac.save()

					equipo=equi.equipo

					equipo.productoFacturado=True
					equipo.save()
					
					total+=equi.precVenta

			for exp in expres:
				chek=request.POST.get('ex_%s'%(exp.expres.id),'')
				if chek:
					fac=FacturaExpres()
					fac.factura=factura
					fac.expres=exp.expres
					fac.save()

					expres=exp.expres

					expres.productoFacturado=True
					expres.save()
					
					total+=exp.precVenta

			for acc in accesorios:
				chek=request.POST.get('ac_%s'%(acc.accesorio.id),'')
				if chek:
					fac=FacturaAccesorio()
					fac.factura=factura
					fac.accesorio=acc.accesorio
					fac.save()

					accesorio=acc.accesorio

					accesorio.productoFacturado=True
					accesorio.save()
					
					total+=acc.precVenta

			for fic in fichas:
				chek=request.POST.get('fi_%s'%(fic.ficha.id),'')
				if chek:
					fac=FacturaFichas()
					fac.factura=factura
					fac.ficha=fic.ficha
					fac.save()
					ficha=fic.ficha

					ficha.productoFacturado=True
					ficha.save()
					
					total+=fic.precVenta

			factura.totalvta=total
			factura.save()
			form = FacturacionAGranel()
			equipos=r_ventas.VentaEquipos(None, False)
			expres=r_ventas.VentaExpress(None, False)
			accesorios=r_ventas.VentaAccesorios(None, False)
			fichas=r_ventas.VentaFichass(None, False)
			info = "%s <br>La Factura %s fue guardada con exito. Siga la siguiente liga para ver los detalles: "%(info, factura)
			liga="/contabilidad/facturacion/facturas/reporte/?filtro=%s"%(factura.id)
			#return HttpResponseRedirect('/contabilidad/facturacion/facturas/reporte/?filtro=%s'%(factura.id))


	ctx={'nivel':nivel , 'titulo': 'Agregar Facturas a Granel', 'form':form, 'equipos':equipos, 'expres':expres,
	'accesorios':accesorios, 'fichas':fichas, 'info':info, 'liga':liga}

	return ctx


def Equipos_facturados(nivel, request):
	q=request.GET.get('filtro','')
	pagina=request.GET.get('pagina','')
	reporte=r_factu.ReporteFacturaEquipos(pagina, q, 'Equipos Facturados', None)

	ctx={'nivel':nivel, 'buscador':repor.Busqueda('Equipos Facturados',q) , 
	'reporte':reporte, 'titulo':'Reporte de Equipos Facturados'}
	return ctx

def Equipos_pendientes(nivel, request):
	q=request.GET.get('filtro','')
	pagina=request.GET.get('pagina','')
	reporte=r_ventas.ReporteVentaEquipos(pagina, q, 'Equipos Pendientes a Facturar', False)
	ctx={'nivel':nivel, 'buscador':repor.Busqueda('Equipos pendientes',q) , 
	'reporte':reporte, 'titulo':'Reporte de Equipos pendientes a Facturar'}
	return ctx

def Express_facturados(nivel, request):
	q=request.GET.get('filtro','')
	pagina=request.GET.get('pagina','')
	reporte=r_factu.ReporteFacturaExpress(pagina, q, 'Expres Facturados', None)
	ctx={'nivel':nivel, 'buscador':repor.Busqueda('Expres Facturados',q) , 
	'reporte':reporte, 'titulo':'Reporte de Expres Facturados'}
	return ctx

def Express_pendientes(nivel, request):
	q=request.GET.get('filtro','')
	pagina=request.GET.get('pagina','')
	reporte=r_ventas.ReporteVentaExpress(pagina, q, 'Express pendientes de Facturar', False)
	ctx={'nivel':nivel, 'buscador':repor.Busqueda('Expres pendientes',q) , 
	'reporte':reporte, 'titulo':'Reporte de Expres pendientes a Facturar'}
	return ctx

def Fichas_facturadas(nivel, request):
	q=request.GET.get('filtro','')
	pagina=request.GET.get('pagina','')
	reporte=r_factu.ReporteFacturaFichass(pagina, q, 'Fichas Facturadas', None)
	ctx={'nivel':nivel, 'buscador':repor.Busqueda('Fichas Facturados',q) , 
	'reporte':reporte, 'titulo':'Reporte de Fichas Facturadas'}
	return ctx

def Fichas_pendientes(nivel, request):
	q=request.GET.get('filtro','')
	pagina=request.GET.get('pagina','')
	reporte=r_ventas.ReporteVentaFichass(pagina, q, 'Fichas Pendientes a Facturar', False)
	ctx={'nivel':nivel, 'buscador':repor.Busqueda('Fichas pendientes',q) , 
	'reporte':reporte, 'titulo':'Reporte de Fichas Pendientes a Facturar'}
	return ctx

def Accesorios_facturados(nivel, request):
	q=request.GET.get('filtro','')
	pagina=request.GET.get('pagina','')
	reporte=r_factu.ReporteFacturaAccesorios(pagina, q, 'Accesorios Facturados', None)
	ctx={'nivel':nivel, 'buscador':repor.Busqueda('Accesorios Facturados',q) ,
	'reporte':reporte, 'titulo':'Reporte de Accesorios Facturados'}
	return ctx

def Accesorios_pendientes(nivel, request):
	q=request.GET.get('filtro','')
	pagina=request.GET.get('pagina','')
	reporte=r_ventas.ReporteVentaAccesorios(pagina, q, 'Accesorios Pendientes de Facturar', False)
	ctx={'nivel':nivel, 'buscador':repor.Busqueda('Accesorios pendientes',q) , 
	'reporte':reporte, 'titulo':'Reporte de Accesorios pendientes a Facturar'}
	return ctx