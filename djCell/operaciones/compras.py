# -*- coding: utf-8 -*-
from djCell.apps.proveedor.models import Proveedor
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from djCell.apps.sucursales.models import Sucursal, VendedorSucursal
from djCell.apps.movimientos.models import Movimiento
from djCell.apps.clientes.models import ClienteFacturacion
from djCell.apps.personal.models import Usuario
from djCell.apps.almacen.models import AlmacenEquipo, AlmacenExpres, AlmacenAccesorio, AlmacenFicha
from djCell.apps.recargas.models import  SaldoSucursal
from djCell.apps.productos.models import TiempoGarantia,Estatus,Marca,Gama,DetallesEquipo,Equipo,TipoIcc,DetallesExpres,Expres, Secciones,MarcaAccesorio,DetallesAccesorio,EstatusAccesorio,Accesorio, NominacionFicha,EstatusFicha,Ficha,  TiempoAire
from djCell.apps.proveedor.models import Factura
from datetime import datetime, timedelta, date
from decimal import Decimal
import time
from django.db.models import Q


def Paginador(objetos, maximo, pagina):
	paginado = Paginator(objetos, maximo)
	try:
		paginado = paginado.page(pagina)
	except PageNotAnInteger:
		paginado = paginado.page(1)
	except EmptyPage:
		paginado = paginado.page(paginado.num_pages)
	return paginado

def Busqueda(filtro):
	html='<div id=\"grid\">\n<table id=\"grid\">\n<tr>\n<td id=\"gridhead\">Filtro</td>\n<td id=\"gridhead\">Buscar</td>\n</tr>\n<tr>\n<form action=\'.\'  method=\'GET\'>\n<td><input type=\'texto\' name=\'filtro\' value=\'%s\'></td>\n<td><input class=\"submit success\" type=\"submit\" value=\'buscar\'></td>\n</form>\n</tr>\n</table>\n</div>\n'%(filtro)
	return html

def NoResultados():
	return 'No se encontraron Resultados para el Filtro'

def EncabezadoR(titulo):
	return '<br><br>\n<h2>%s</h2>\n<div id=\"grid\"><table id=\"grid\">'%(titulo)

def PiesR(filtro,consulta):
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


def PiesRS():
	#***********Fooder*******
	pie='</table></div>'
	# *********** fin **********
	return pie


def Proveedores(q):
	if q:
		qset=(Q(rfc__icontains=q)|
		Q(nombre__icontains=q)|
		Q(direccion__icontains=q)|
		Q(tel__icontains=q))
		proveedores=Proveedor.objects.filter(qset)
	else:
		proveedores=Proveedor.objects.all()
	return proveedores

def ReporteProveedores(pagina, filtro, tituloR):
	proveedores=Paginador(Proveedores(filtro),50,pagina)
	titulos=['RFC','Nombre','Direccion','Telefono', 'Editar']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for proveedor in proveedores:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, proveedor.rfc)
		contenido='%s<td>%s</td>\n'%(contenido, proveedor.nombre)
		contenido='%s<td>%s</td>\n'%(contenido, proveedor.direccion)
		contenido='%s<td>%s</td>\n'%(contenido, proveedor.tel)
		contenido='%s<td><a href=\"/compras/compras/proveedor/nuevo?filtro=%s\">Editar</a></td>\n'%(contenido, proveedor.id)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(filtro,proveedores))

	return html

def folioxSucursal(sucursal):
	#numero de transferencias de la sucursal, mas la generada
	noMov = Movimiento.objects.filter(sucursalDestino=sucursal).count()+1
	cad = str(noMov)+""
	folio = ""
	nuevo = False
	while  nuevo == False:
		#formato
		folio = "T"+str(sucursal.id)+"-"
		add =""
		to = 4 -len(cad)
		for x in xrange(0,to):
			add = add +"0"
		folio = folio + add + str(noMov)
		try:
			pfff = Movimiento.objects.get(folio=folio)
			nuevo = False
			cad = str(Decimal(cad)+1)+'-R'
		except :
			nuevo = True

	return folio

def nvoMayorista(razonSocial):
	generarFolio = None
	today = datetime.now()
	dateFormat = today.strftime("%Y%m%d")
	tam = len(dateFormat)
	fecha= ""
	for x in xrange(2,tam):
		fecha = fecha + dateFormat[x]

	cadena = razonSocial.upper().strip().replace(" ","")
	lencad = len(cadena)
	prov = ""
	for x in xrange(0,lencad):
		if x % 2 != 0:
			prov = prov + cadena[x]
	nom=""
	for x in xrange(0,3):
		nom  = nom + prov[x]
	nuevo = False
	while nuevo == False:
		pfff = str(time.time())
		omo = ""
		for x in xrange(7,10):
			omo = omo + pfff[x]
		generarFolio = nom +'-'+ fecha +'-'+ omo
		try:
			v = ClienteFacturacion.objects.get(rfc=generarFolio)
			nuevo = False
		except ClienteFacturacion.DoesNotExist:
			nuevo = True
	#'''
	return generarFolio

def suc_Permisos(nivel,user,sucursal): #troll 
	ok = False
	try:
		_usuario 			= Usuario.objects.get(user=user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		#accede al corte el vendedor de la sucursal q tiene asignada
		#acceso por nivel, django 0, admin 1, contado2r, analista3
		if mysucursal.id == sucursal.id or nivel == 0  or nivel == 1 or nivel == 2 or nivel == 3:
			ok = True
		else:
			ok = False	
	except :
		pass

	return ok


def almacenItems(tipo,item,sd,so):
	if tipo==0:
		try:
			aux=AlmacenEquipo.objects.get(estado=True,equipo=item,sucursal=so)
			aux.estado=False
			aux.save()
		except :
			pass 
		if sd:
			try:
				alEq=AlmacenEquipo()
				alEq.sucursal=sd
				alEq.equipo=item
				alEq.estado=True
				alEq.save()
				item.sucursal=sd
				item.save()
			except :
				pass 

	elif tipo==1:
		try:
			aux=AlmacenExpres.objects.get(estado=True,expres=item,sucursal=so)
			aux.estado=False
			aux.save()
		except :
			pass 
		if sd:
			try:
				alEq=AlmacenExpres()
				alEq.sucursal=sd
				alEq.expres=item
				alEq.estado=True
				alEq.save()
				item.sucursal=sd
				item.save()
			except :
				pass 

	elif tipo==2:
		try:
			aux=AlmacenAccesorio.objects.get(estado=True,accesorio=item,sucursal=so)
			aux.estado=False
			aux.save()
		except :
			pass 
		if sd:
			try:
				alEq=AlmacenAccesorio()
				alEq.sucursal=sd
				alEq.accesorio=item
				alEq.estado=True
				alEq.save()
				item.sucursal=sd
				item.save()
			except :
				pass 

	elif tipo==3:
		try:
			aux=AlmacenFicha.objects.get(estado=True,ficha=item,sucursal=so)
			aux.estado=False
			aux.save()
		except :
			pass 
		if sd:
			try:
				alEq=AlmacenFicha()
				alEq.sucursal=sd
				alEq.ficha=item
				alEq.estado=True
				alEq.save()
				item.sucursal=sd
				item.save()
			except :
				pass 

	elif tipo==4:
		saldo=item
		saldoAnte=0
		try:
			aux=SaldoSucursal.objects.get(sucursal=so)
			aux.saldo="%.2f" % round(aux.saldo-item,2)
			aux.save()
		except :
			pass
		if sd:
			try:
				try:
					sucursal=SaldoSucursal.objects.get(sucursal=sd)
					saldoAnte=sucursal.saldo
					sucursal.saldo="%.2f" % round(sucursal.saldo+item,2)
					sucursal.save()
				except :
					sucursal=SaldoSucursal()
					sucursal.sucursal=sd
					sucursal.saldo=item
					sucursal.save()
				historial=HistorialSaldo()
				historial.sucursal=sd
				historial.saldoInicial = saldoAnte
				historial.abono 	= saldo
				historial.save()
			except :
				pass

def ListaItems(tipo,sucursal,qset,pagina):
	items=None
	if sucursal:
		if qset:
			if tipo==0:
				items=Equipo.objects.filter(qset,sucursal=sucursal)
			if tipo==1:
				items=Expres.objects.filter(qset,sucursal=sucursal)
			if tipo==2:
				items=Accesorio.objects.filter(qset,sucursal=sucursal)
			if tipo==3:
				items=Ficha.objects.filter(qset,sucursal=sucursal)
		else:
			if tipo==0:
				items=Equipo.objects.filter(sucursal=sucursal)
			if tipo==1:
				items=Expres.objects.filter(sucursal=sucursal)
			if tipo==2:
				items=Accesorio.objects.filter(sucursal=sucursal)
			if tipo==3:
				items=Ficha.objects.filter(sucursal=sucursal)
	else:
		if qset:
			if tipo==0:
				items=Equipo.objects.filter(qset)
			if tipo==1:
				items=Expres.objects.filter(qset)
			if tipo==2:
				items=Accesorio.objects.filter(qset)
			if tipo==3:
				items=Ficha.objects.filter(qset)
		else:
			if tipo==0:
				items=Equipo.objects.all()
			if tipo==1:
				items=Expres.objects.all()
			if tipo==2:
				items=Accesorio.objects.all()
			if tipo==3:
				items=Ficha.objects.all()
	if pagina:
		paginator = Paginator(items, 50)
		try:
			items = paginator.page(pagina)
		except PageNotAnInteger:
			items = paginator.page(1)
		except EmptyPage:
			items = paginator.page(paginator.num_pages)
	return items

def ListaFacturas(b_folio):
	qset=(Q(folio__icontains=b_folio)|
		Q(documento__icontains=b_folio)|
		Q(proveedor__rfc__icontains=b_folio)|
		Q(proveedor__nombre__icontains=b_folio)|
		Q(proveedor__tel__icontains=b_folio)|
		Q(fxFactura__icontains=b_folio)|
		Q(fxIngreso__icontains=b_folio)|
		Q(observacion__icontains=b_folio)|
		Q(usuario__username__icontains=b_folio))
	b_facturas=Factura.objects.filter(qset).distinct()
	if b_facturas:
		pass
	else:
		b_facturas=None
	return b_facturas

def SerieFichas(b_fichas):
	inicio=0
	final=0
	nomina=0
	total=len(b_fichas)
	_100=len(b_fichas.filter(nominacion__nominacion=100))
	_200=len(b_fichas.filter(nominacion__nominacion=200))
	_300=len(b_fichas.filter(nominacion__nominacion=300))
	_500=len(b_fichas.filter(nominacion__nominacion=500))
	fichas=[]
	for ficha in b_fichas.order_by('folio'):
		if final+1 != int(ficha.folio):
			if inicio != 0:
				fichas.append([final-inicio+1,inicio,final,'%s'%(nomina)])
				inicio=int(ficha.folio)
			else:
				inicio=int(ficha.folio)
							
		final=int(ficha.folio)
		nomina=ficha.nominacion.nominacion
	if inicio != 0:
		fichas.append([final-inicio+1,inicio,final,'%s'%(nomina)])

	if fichas:
		fichas.append(['','','',''])
		fichas.append(['Total de Fichas:  %s'%(total),'','',''])
		fichas.append(['Total de 100: %s'%(_100),'Total de 200: %s'%(_200),'Total de 300: %s'%(_300),'Total de 500: %s'%(_500)])
	return fichas

def SerieListasFichas(b_fichas):
	inicio=0
	final=0
	nomina=0
	total=len(b_fichas)
	_100=len(b_fichas.filter(ficha__nominacion__nominacion=100))
	_200=len(b_fichas.filter(ficha__nominacion__nominacion=200))
	_300=len(b_fichas.filter(ficha__nominacion__nominacion=300))
	_500=len(b_fichas.filter(ficha__nominacion__nominacion=500))
	fichas=[]
	for ficha in b_fichas.order_by('ficha__folio'):
		if final+1 != int(ficha.ficha.folio):
			if inicio != 0:
				fichas.append([final-inicio+1,inicio,final,'%s'%(nomina)])
				inicio=int(ficha.ficha.folio)
			else:
				inicio=int(ficha.ficha.folio)
							
		final=int(ficha.ficha.folio)
		nomina=ficha.ficha.nominacion.nominacion
	if inicio != 0:
		fichas.append([final-inicio+1,inicio,final,'%s'%(nomina)])
	if fichas:
		fichas.append(['','','',''])
		fichas.append(['Total de Fichas:  %s'%(total),'','',''])
		fichas.append(['Total de 100: %s'%(_100),'Total de 200: %s'%(_200),'Total de 300: %s'%(_300),'Total de 500: %s'%(_500)])
	return fichas

def nvo_folio_detalles(tipo):
	generarFolio = None
	nuevo = False
	while nuevo == False:
		pfff = str(time.time())
		omo = ""
		for x in xrange(7,10):
			omo = omo + pfff[x]
		generarFolio = str(tipo) +'-' + omo
		try:
			v = DetallesEquipo.objects.get(folio=generarFolio)
			nuevo = False
		except DetallesEquipo.DoesNotExist:
			nuevo = True
	return generarFolio

def confirmarItems(tipo,item,sd,so):
	if tipo==0:
		try:
			aux=AlmacenEquipo.objects.get(estado=True,equipo=item,sucursal=so)
			aux.estado=False
			aux.save()
			item.estatus = Estatus.objects.get(estatus='Robado')
			item.save()
		except :
			pass
		if sd:
			alEq=AlmacenEquipo()
			alEq.sucursal=sd
			alEq.equipo=item
			alEq.estado=True
			alEq.save()
			item.sucursal=sd
			item.estatus = Estatus.objects.get(estatus='Existente')
			item.save()

	elif tipo==1:
		try:
			aux=AlmacenExpres.objects.get(estado=True,expres=item,sucursal=so)
			aux.estado=False
			aux.save()
			item.estatus = Estatus.objects.get(estatus='Robado')
			item.save()
		except :
			pass
		if sd:
			alEq=AlmacenExpres()
			alEq.sucursal=sd
			alEq.expres=item
			alEq.estado=True
			alEq.save()
			item.sucursal=sd
			item.estatus = Estatus.objects.get(estatus='Existente')
			item.save()

	elif tipo==2:
		try:
			aux=AlmacenAccesorio.objects.get(estado=True,accesorio=item,sucursal=so)
			aux.estado=False
			aux.save()

			item.estatusAccesorio = EstatusAccesorio.objects.get(estatus='Robado')
			item.save()
		except :
			pass
		if sd:
			alEq=AlmacenAccesorio()
			alEq.sucursal=sd
			alEq.accesorio=item
			alEq.estado=True
			alEq.save()
			item.sucursal=sd
			item.estatusAccesorio = EstatusAccesorio.objects.get(estatus='Existente')
			item.save()

	elif tipo==3:
		try:
			aux=AlmacenFicha.objects.get(estado=True,ficha=item,sucursal=so)
			aux.estado=False
			aux.save()
			item.estatusFicha = EstatusFicha.objects.get(estatus='Robado')
			item.save()
		except :
			pass
		if sd:
			alEq=AlmacenFicha()
			alEq.sucursal=sd
			alEq.ficha=item
			alEq.estado=True
			alEq.save()
			item.sucursal=sd
			item.estatusFicha = EstatusFicha.objects.get(estatus='Existente')
			item.save()



