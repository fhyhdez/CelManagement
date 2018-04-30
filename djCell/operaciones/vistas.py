# -*- coding: utf-8 -*-
from django.db.models import Q
from djCell.apps.contabilidad.models import * 
from djCell.apps.ventas.models import * 
from djCell.apps.credito.models import * 
from djCell.operaciones.comunes import *
from djCell.operaciones.r_conta import *
import contabilidadm

#este modulo pretende ser una base para la visualizacion de vistas de informacion, se procurara usar un diseño lo mas
#generico para poder ser empleado por los distintos tipos de datos, tambien incluira herramientas adicionales como
#la paginacion y plantilla general para la busqueda.

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import comunes

from django.conf import settings
STATIC_URL = settings.STATIC_URL

#plantilla general para busquedas, retorna un html con un textbox y un boton para realizar busquedas mediante variable
#variable por get de nombre 'filtro', se usa en la plantilla como {{buscador|safe}}
def Busqueda(titulo):
	filtro = ""
	html='<div id=\"grid\">\n<table id=\"grid\">\n<tr>\n<td id=\"gridhead\">%s</td>\n<td id=\"gridhead\">Buscar</td>\n</tr>\n<tr>\n<form action=\'.\'  method=\'GET\'>\n<td><input type=\'texto\' name=\'filtro\' value=\'%s\'></td>\n<td><input class=\"submit success\" type=\"submit\" value=\'Buscar\'></td>\n</form>\n</tr>\n</table>\n</div>\n'%(titulo, filtro)
	return '%s<br>'%(html)


def NoResultados():
	return 'No se encontraron Resultados para el Filtro'


def EncabezadoR(titulo):
	return '<br>\n<h2>%s</h2>\n<div id=\"grid\"><table id=\"grid\">'%(titulo)

def EncabezadoR2(titulo):
	return '<br>\n<h2>%s</h2>\n<div id=\"grid\"><div onclick=\"seleccionar(this)\"> <table id=\"grid\">'%(titulo)

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

def ReporteEmpleados(empleados, filtro, editar, tituloR):
	titulos=['CURP','Nombre','Direccion','Telefono','Fecha de Ingreso','Puesto','Area','Activo','Detalles', 'Editar']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for empleado in empleados:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, empleado.curp)
		contenido='%s<td>%s %s %s</td>\n'%(contenido, empleado.nombre, empleado.aPaterno, empleado.aMaterno)
		contenido='%s<td>%s, %s, %s, %s</td>\n'%(contenido, empleado.direccion, empleado.colonia, empleado.ciudad, empleado.estado)
		contenido='%s<td>%s</td>\n'%(contenido, empleado.telefono)
		contenido='%s<td>%s</td>\n'%(contenido, FechaSTR(empleado.fxIngreso))
		contenido='%s<td>%s</td>\n'%(contenido, empleado.puesto)
		contenido='%s<td>%s</td>\n'%(contenido, empleado.area)
		#activo
		contenido='%s<td>'%(contenido)
		if empleado.estadoEmpleado:
			contenido='%s<img src=\"%simg/icons/tick.png\" />'%(contenido, STATIC_URL)
		else:
			contenido='%s<img src=\"%simg/icons/exclamation.png\" />'%(contenido, STATIC_URL)
		contenido='%s</td>\n'%(contenido)
		
		#detalle
		contenido='%s<td><a href=\"?filtro=%s\">Seleccionar</a></td>\n'%(contenido, empleado.id)
		#editar
		if editar:
			contenido='%s<td><a href=\"%s?ide=%s\">Editar</a></td>\n'%(contenido,editar, empleado.id)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(filtro,empleados))

	return html



def ReporteCortes(pagina, filtro, cortes, tituloR):
	cortes=Paginador(cortes,50,pagina)
	titulos=['Folio','Fecha de Corte','Sucursal','Total de Ventas', 'Total de Gastos', 'Total', 'Observacion','Encargado del cierre','Verificar']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for corte in cortes:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, corte.folioCorteVta)
		contenido='%s<td>%s</td>\n'%(contenido, FechaSTR(corte.fxCorte))
		contenido='%s<td>%s</td>\n'%(contenido, corte.sucursal)
		contenido='%s<td>%s</td>\n'%(contenido, corte.totalVta)
		contenido='%s<td>%s</td>\n'%(contenido, corte.totalGastos)
		contenido='%s<td>%s</td>\n'%(contenido, corte.total)
		if corte.observacion:
			contenido='%s<td>%s</td>\n'%(contenido, corte.observacion)
		else:
			contenido='%s<td>%s</td>\n'%(contenido, "." )
		contenido='%s<td>%s</td>\n'%(contenido, corte.cierraCorte)
		if corte.revisado:
			contenido='%s<td><img src=\"%simg/icons/tick.png\" /></td>\n'%(contenido, STATIC_URL)
		else:
			contenido='%s<td><a href=\"?filtro=%s\">Seleccionar</a></td>\n'%(contenido, corte.id)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(filtro, cortes))

	return html

def ReporteDirefenciaCortes(pagina, filtro, cortes, tituloR):
	cortes=Paginador(cortes,50,pagina)
	titulos=['Corte de Venta','Diferencia','Fecha de Corte','Personal que Reviso', 'Observacion']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for corte in cortes:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, corte.corteVenta)
		contenido='%s<td>%s</td>\n'%(contenido, corte.diferencia)
		contenido='%s<td>%s</td>\n'%(contenido, FechaSTR(corte.fxDiferencia))
		contenido='%s<td>%s</td>\n'%(contenido, corte.revisaCorte)
		contenido='%s<td>%s</td>\n'%(contenido, corte.observacion)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(filtro, cortes))

	return html


def ReporteNominaEmpleado(nominas, tituloR, admin):
	titulos=['Folio','Empleado','Salario','Dias Trabajados','Bono de Puntualidad','Bono de Productividad','Vales de despensa','SubTotal','Descuento', 'Total','Fecha Pago','Observaciones', 'Firma', 'Pagado', 'Pagar']
	if admin:
		titulos.append('Editar')
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)
	for nomina in nominas:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, nomina.nomina.folio)
		contenido='%s<td>%s</td>\n'%(contenido, nomina.empleado)
		contenido='%s<td>%s</td>\n'%(contenido, nomina.salarioDia)

		contenido='%s<td>'%(contenido)
		if nomina.diasTrab:
			contenido='%s %s'%(contenido, nomina.diasTrab)
		elif not nomina.nomina.cerrar:
			contenido='%s<a href=\"/contabilidad/nomina/nueva_nomina/?nominaId=%s&amp;filtro=%s\">Asignar Dias</a>'%(contenido, nomina.id, nomina.nomina.id)
		contenido='%s</td>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, nomina.bonoPuntualidad)
		contenido='%s<td>%s</td>\n'%(contenido, nomina.bonoProductividad)
		contenido='%s<td>%s</td>\n'%(contenido, nomina.bonoVales)
		contenido='%s<td>%s</td>\n'%(contenido, (nomina.total+nomina.descuento))
		contenido='%s<td>%s</td>\n'%(contenido, nomina.descuento) # .ForeignKey(HistorialEmpleado) descuento de historial
		contenido='%s<td>%s</td>\n'%(contenido, nomina.total)
		contenido='%s<td>%s</td>\n'%(contenido, FechaSTR(nomina.fxPago))
		contenido='%s<td>%s</td>\n'%(contenido, nomina.observacion)
		contenido='%s<td>%s</td>\n'%(contenido, "")

		contenido='%s<td>'%(contenido)
		if nomina.pagado:
			contenido='%s<img src=\"%simg/icons/tick.png\" />'%(contenido, STATIC_URL)
			contenido='%s</td>\n'%(contenido)
			contenido='%s<td></td>\n'%(contenido)
		elif not nomina.nomina.cerrar:
			contenido='%s<img src=\"%simg/icons/exclamation.png\" />'%(contenido, STATIC_URL)
			contenido='%s</td>\n'%(contenido)
			contenido='%s<td><a href=\"/contabilidad/nomina/nominas/?nominaId=%s&amp;filtro=%s\">Pagar</a></td>\n'%(contenido, nomina.id, nomina.nomina.id)
		else:
			contenido='%s<img src=\"%simg/icons/exclamation.png\" />'%(contenido, STATIC_URL)
			contenido='%s</td>\n'%(contenido)
			contenido='%s<td></td>\n'%(contenido)

		if admin and (not nomina.pagado) and (not nomina.nomina.cerrar):
			contenido='%s<td><a href=\"/contabilidad/nomina/nueva_nomina/?nominaId=%s&amp;filtro=%s\">Editar</a></td>\n'%(contenido, nomina.id, nomina.nomina.id)
		else:
			contenido='%s<td></td>\n'%(contenido)
		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesRS())

	return html


def ReporteComisiones(pagina, filtro, tituloR, faltantes):
	comisiones=Paginador(contabilidadm.Comisiones(filtro, faltantes),50,pagina)
	html=''
	if comisiones:
		titulos=['Empleado','Comision por EquipoKit','Comision por EquipoTip','Comision por Planes','Comision por Servicios','Mes Calculado','Pago Efectuado','Fecha Pago','Seleccionar']
		contenido='<tr>\n'
		for titulo in titulos:
			contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
		contenido='%s</tr>\n'%(contenido)

		for comision in comisiones:
			contenido='%s<tr>\n'%(contenido)

			contenido='%s<td>%s</td>\n'%(contenido, comision.empleado)
			contenido='%s<td>%s</td>\n'%(contenido, comision.comEquipoKit)
			contenido='%s<td>%s</td>\n'%(contenido, comision.comEquipoTip)
			contenido='%s<td>%s</td>\n'%(contenido, comision.comPlanes)
			contenido='%s<td>%s</td>\n'%(contenido, comision.comServicios)
			contenido='%s<td>%s</td>\n'%(contenido, comunes.FechaMes(comision.mes))

			contenido='%s<td>'%(contenido)
			if comision.pagado:
				contenido='%s<img src=\"%simg/icons/tick.png\" />'%(contenido, STATIC_URL)
			else:
				contenido='%s<img src=\"%simg/icons/exclamation.png\" />'%(contenido, STATIC_URL)
			contenido='%s</td>\n'%(contenido)

			if comision.fxPago:
				contenido='%s<td>%s</td>\n'%(contenido, FechaSTR(comision.fxPago))
			else:
				contenido='%s<td>%s</td>\n'%(contenido, FechaSTR(comision.fxPago))

			contenido='%s<td><a href=\"?filtro=%s\">Seleccionar</a></td>\n'%(contenido, comision.id)

			contenido='%s</tr>\n'%(contenido)



		html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(filtro,comisiones))

	return html



def ReporteNominas(pagina, filtro, nominas, tituloR):
	nominas=Paginador(nominas,50,pagina)
	titulos=['Folio','Fecha de Creacion','Descripcion','Imprimir' ,'Seleccionar']#'Imprimir' , huellita
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for nomina in nominas:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, nomina.folio)
		contenido='%s<td>%s</td>\n'%(contenido, FechaSTR(nomina.fxCreacion))
		contenido='%s<td>%s</td>\n'%(contenido, nomina.descripcion)
		contenido='%s<td><form  action=\".\" method=\"GET\" enctype=\"multipart/form-data\"><a href=\"\" class=\"tooltipbasic\" data-tooltip=\"Descargar Nomina seleccionada\"><input type=\"checkbox\" name=\"excel\" value=\"Exportar\">Descargar Reporte</a> || <input title=\"De clic para imprimir la consulta\" class=\"submit success\" type=\"submit\" value=\"Descargar\"><input type=\"hidden\" name=\"key\" value=\"%s\"/></form></td>\n'%(contenido,nomina.id)
		contenido='%s<td><a href=\"?filtro=%s\">Seleccionar</a></td>\n'%(contenido, nomina.id)


		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesRS())

	return html


def ReporteCuentas(pagina, filtro, tituloR):
	cuentas=Paginador(Cuentas(filtro),50,pagina)
	titulos=['Cuenta','No. Cuenta','Observaciones','Fecha de Registro', 'Saldo', 'Depositar']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for cuenta in cuentas:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, cuenta.cuenta)
		contenido='%s<td>%s</td>\n'%(contenido, cuenta.nocuenta)
		contenido='%s<td>%s</td>\n'%(contenido, cuenta.observacion)
		contenido='%s<td>%s</td>\n'%(contenido, FechaSTR(cuenta.fxIngreso))
		contenido='%s<td>%s</td>\n'%(contenido, cuenta.saldo)
		contenido='%s<td><a href=\"/contabilidad/polizas/ingresos/depositos/?filtro=%s\">Depositar</a></td>\n'%(contenido, cuenta.id)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(filtro,cuentas))

	return html


def ReporteCaja(filtro,pagina, tituloR, limite):
	try:
		caja=Caja.objects.get(nombre='Caja Principal')
	except:
		#try:
		caja=Caja()
		caja.nombre='Caja Principal'
		caja.saldo=0
		caja.save()
		
	if limite:
		historial=HistorialCaja.objects.filter(caja=caja, abono = True).order_by('-id')[:5]
	else:
		historial=HistorialCaja.objects.filter(caja=caja, abono = True).order_by('-id')
	
	historial=Paginador(historial,50,pagina)
	titulos=['Monto','Fecha de Registro', 'Descripcion', 'Abono/Descuento']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for abono in historial:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, abono.monto)
		contenido='%s<td>%s</td>\n'%(contenido, FechaSTR(abono.fxIngreso))
		contenido='%s<td>%s</td>\n'%(contenido, abono.descripcion)

		contenido='%s<td>'%(contenido)
		if abono.abono:
			contenido='%s<img src=\"%simg/icons/tick.png\" />'%(contenido, STATIC_URL)
		else:
			contenido='%s<img src=\"%simg/icons/exclamation.png\" />'%(contenido, STATIC_URL)
		contenido='%s</td>\n'%(contenido)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(filtro,historial))

	return html


def ReporteGastos(filtro,pagina, tituloR, limite):
	try:
		caja=Caja.objects.get(nombre='Caja Principal')
	except:
		#try:
		caja=Caja()
		caja.nombre='Caja Principal'
		caja.saldo=0
		caja.save()
		
	if limite:
		historial=Gastos.objects.all().order_by('-id')[:5]
	else:
		historial=Gastos.objects.all().order_by('-id')
	if filtro:
		qset=(Q(folioNota__icontains=filtro)|
			Q(descripcion__icontains=filtro)|
			Q(fxGasto__icontains=filtro)|
			Q(monto__icontains=filtro)|
			Q(observacion__icontains=filtro))
		historial=Gastos.objects.filter(qset).order_by('-id')

	historial=Paginador(historial,50,pagina)
	titulos=['Folio de la Nota','Fecha de Gasto', 'Monto', 'Observaciones']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for abono in historial:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, abono.folioNota)
		contenido='%s<td>%s</td>\n'%(contenido, FechaSTR(abono.fxGasto))
		contenido='%s<td>%s</td>\n'%(contenido, abono.monto)
		contenido='%s<td>%s</td>\n'%(contenido, abono.observacion)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(filtro,historial))

	return html

def ReporteCuentaHistorial(pagina, filtro, deposito, tituloR, limitar):
	if limitar:
		historial=Paginador(contabilidadm.CuentaHistoriales(filtro, deposito).order_by('-id')[:5],50,pagina)
	else:
		historial=Paginador(contabilidadm.CuentaHistoriales(filtro, deposito).order_by('-id'),50,pagina)
	titulos=['No. Referencia','Fecha','Cuenta','Proveedor', 'Concepto', 'Cantidad']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for mov in historial:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, mov.noReferencia)
		contenido='%s<td>%s</td>\n'%(contenido, FechaSTR(mov.fecha))
		contenido='%s<td>%s</td>\n'%(contenido, mov.cuenta)
		contenido='%s<td>%s</td>\n'%(contenido, mov.proveedor)
		contenido='%s<td>%s</td>\n'%(contenido, mov.concepto)
		contenido='%s<td>%s</td>\n'%(contenido, mov.cantidad)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(filtro,historial))

	return html

def ReporteProveedores(pagina, filtro, tituloR):
	proveedores=Paginador(contabilidadm.Proveedores(filtro),50,pagina)
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
		contenido='%s<td><a href=\"/contabilidad/polizas/lineas_credito/proveedores/nuevo?filtro=%s\">Editar</a></td>\n'%(contenido, proveedor.id)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(filtro,proveedores))

	return html


def ReporteLineaCreditos(pagina, filtro, tituloR):
	lineas=Paginador(LineaCreditos(filtro),50,pagina)
	titulos=['Proveedor','Notas del Credito','Total','Fecha de Creacion', 'Deuda', 'Abonar', 'Historial']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for linea in lineas:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, linea.proveedor)
		contenido='%s<td>%s</td>\n'%(contenido, linea.notaCredito)
		contenido='%s<td>%s</td>\n'%(contenido, linea.total)
		contenido='%s<td>%s</td>\n'%(contenido, FechaSTR(linea.fxCredito))
		contenido='%s<td>%s</td>\n'%(contenido, linea.deuda)
		if linea.pagado:
			contenido='%s<td>Liquidado</td>\n'%(contenido)
		else:
			contenido='%s<td><a href=\"/contabilidad/polizas/lineas_credito/abonos/?filtro=%s\">Abonar</a></td>\n'%(contenido, linea.id)
		contenido='%s<td><a href=\"/contabilidad/polizas/lineas_credito/historial/?filtro=%s\">Historial</a></td>\n'%(contenido, linea.id)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(filtro,lineas))

	return html


def ReporteHistLCreditos(pagina, linea, tituloR):
	historial=Paginador(HistLCredito.objects.filter(lineaCredito=linea),100,pagina)
	titulos=['Linea de Credito','Abono','Fecha de Abono','Observaciones']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for historia in historial:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, historia.lineaCredito)
		contenido='%s<td>%s</td>\n'%(contenido, historia.abono)
		contenido='%s<td>%s</td>\n'%(contenido, FechaSTR(historia.fxAbono))
		contenido='%s<td>%s</td>\n'%(contenido, historia.observacion)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR('',historial))

	return html


def ReporteClienteFactuacion(pagina, filtro, tituloR):
	listas=Paginador(ClienteFacturaciones(filtro),50,pagina)
	titulos=['RFC','Razon Social','Direccion','Editar']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for lista in listas:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, lista.rfc)
		contenido='%s<td>%s</td>\n'%(contenido, lista.razonSocial)
		contenido='%s<td>%s, %s, %s, cp: %s, Estado de %s</td>\n'%(contenido, lista.direccion, lista.colonia, lista.ciudad, lista.cp, lista.estado)
		contenido='%s<td><a href=\"/contabilidad/facturacion/clientes/nuevo?filtro=%s\">Editar</a></td>\n'%(contenido, lista.id)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(filtro,listas))

	return html

def ReporteFacturadas(pagina, q, tituloR):
	listas = None
	if q:
		qset=(Q(venta__folioVenta__icontains=q)|
		Q(venta__fecha__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(venta__usuario__username__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(factura__folioFiscal__icontains=q)|
		Q(factura__certifSat__icontains=q)|
		Q(factura__certifEmisor__icontains=q)|
		Q(factura__serieFolio__icontains=q)|
		Q(factura__observacion__icontains=q)|
		Q(factura__clienteFacturacion__rfc__icontains=q))
		#listas=VentaFactura.objects.filter(qset)
	else:
		#listas=VentaFactura.objects.all()
		pass

	listas=Paginador(listas,50,pagina)
	titulos=['Factura','Venta']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for lista in listas:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, lista.factura)
		contenido='%s<td>%s</td>\n'%(contenido, lista.venta)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(q,listas))

	return html

def ReporteNoFacturadas(pagina, q, tituloR):
	listas = None
	if q:
		qset=(Q(folioVenta__icontains=q)|
		Q(fecha__icontains=q)|
		Q(sucursal__nombre__icontains=q)|
		Q(usuario__username__icontains=q)|
		Q(sucursal__nombre__icontains=q)|
		Q(sucursal__nombre__icontains=q))
		listas=Venta.objects.filter(qset,facturada=False, aceptada=True)
	else:
		listas=Venta.objects.filter(facturada=False, aceptada=True)

	listas=Paginador(listas,50,pagina)
	titulos=['Folio de la Venta','Fecha', 'Sucursal', 'Total']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for lista in listas:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, lista.folioVenta)
		contenido='%s<td>%s</td>\n'%(contenido, FechaSTR(lista.fecha))
		contenido='%s<td>%s</td>\n'%(contenido, lista.sucursal)
		contenido='%s<td>%s</td>\n'%(contenido, lista.total)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(q,listas))

	return html

def ReporteEquiposSinFactura(pagina, q, tituloR):
	listas = None
	if q:
		qset=(Q(venta__folioVenta__icontains=q)|
		Q(venta__fecha__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(venta__usuario__username__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(equipo__imei__icontains=q)|
		Q(equipo__icc__icontains=q)|
		Q(equipo__detallesEquipo__marca__marca__icontains=q)|
		Q(equipo__detallesEquipo__modelo__icontains=q))
		listas=VentaEquipo.objects.filter(qset, equipo__factura__conFactura=False)
	else:
		listas=VentaEquipo.objects.filter(equipo__factura__conFactura=False)

	listas=Paginador(listas,50,pagina)
	titulos=['Venta','Equipo', 'Precio de Venta']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for lista in listas:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, lista.venta)
		contenido='%s<td>%s</td>\n'%(contenido, lista.equipo)
		contenido='%s<td>%s</td>\n'%(contenido, lista.precVenta)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(q,listas))

	return html

def ReporteExpresSinFactura(pagina, q, tituloR):
	if q:
		qset=(Q(venta__folioVenta__icontains=q)|
		Q(venta__fecha__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(venta__usuario__username__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(expres__icc__icontains=q)|
		Q(expres__noCell__icontains=q))
		listas=VentaExpres.objects.filter(qset, expres__factura__conFactura=False)
	else:
		listas=VentaExpres.objects.filter(expres__factura__conFactura=False)

	listas=Paginador(listas,50,pagina)
	titulos=['Venta','Expres', 'Precio de Venta']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for lista in listas:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, lista.venta)
		contenido='%s<td>%s</td>\n'%(contenido, lista.expres)
		contenido='%s<td>%s</td>\n'%(contenido, lista.precVenta)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(q,listas))

	return html

def ReporteAccesorioSinFactura(pagina, q, tituloR):
	if q:
		qset=(Q(venta__folioVenta__icontains=q)|
		Q(venta__fecha__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(venta__usuario__username__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(accesorio__codigoBarras__icontains=q)|
		Q(accesorio__detallesAccesorio__marca__marca__icontains=q)|
		Q(accesorio__detallesAccesorio__descripcion__icontains=q))
		listas=VentaAccesorio.objects.filter(qset, accesorio__factura__conFactura=False)
	else:
		listas=VentaAccesorio.objects.filter(accesorio__factura__conFactura=False)

	listas=Paginador(listas,50,pagina)
	titulos=['Venta','Accesorio', 'Precio de Venta']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for lista in listas:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, lista.venta)
		contenido='%s<td>%s</td>\n'%(contenido, lista.Accesorio)
		contenido='%s<td>%s</td>\n'%(contenido, lista.precVenta)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(q,listas))

	return html

def ReporteFichasSinFactura(pagina, q, tituloR):
	if q:
		qset=(Q(venta__folioVenta__icontains=q)|
		Q(venta__fecha__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(venta__usuario__username__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(ficha__folio__icontains=q)|
		Q(ficha__nominacion__nominacion__icontains=q))
		listas=VentaFichas.objects.filter(qset, ficha__factura__conFactura=False)
	else:
		listas=VentaFichas.objects.filter(ficha__factura__conFactura=False)

	listas=Paginador(listas,50,pagina)
	titulos=['Venta','Ficha', 'Precio de Venta']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for lista in listas:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, lista.venta)
		contenido='%s<td>%s</td>\n'%(contenido, lista.ficha)
		contenido='%s<td>%s</td>\n'%(contenido, lista.precVenta)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(q,listas))

	return html

def ReporteSubDistribuidores(pagina, q, tituloR):
	if q:

		qset=(Q(cliente__rfc__icontains=q)|
		Q(cliente__razonSocial__icontains=q)|
		Q(cliente__direccion__icontains=q)|
		Q(telefono__icontains=q))
		listas=Subdistribuidor.objects.filter(qset)
	else:
		listas=Subdistribuidor.objects.all()

	listas=Paginador(listas,50,pagina)
	titulos=['Cliente','Limite de Credito', 'Fecha de Ingreso', 'Estado', 'Telefono']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for lista in listas:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, lista.cliente)
		contenido='%s<td>%s</td>\n'%(contenido, lista.limCredito)
		contenido='%s<td>%s</td>\n'%(contenido, FechaSTR(lista.fxIngreso))
		contenido='%s<td>%s</td>\n'%(contenido, lista.edo)
		contenido='%s<td>%s</td>\n'%(contenido, lista.telefono)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(q,listas))

	return html

def ReporteCreditoSubDistribuidores(pagina, q, tituloR):
	if q:

		qset=(Q(subdist__cliente__rfc__icontains=q)|
		Q(subdist__cliente__razonSocial__icontains=q)|
		Q(subdist__cliente__direccion__icontains=q)|
		Q(subdist__telefono__icontains=q)|
		Q(folioc__icontains=q)|
		Q(venta__folioVenta__icontains=q)|
		Q(observacion__icontains=q))
		listas=Credito.objects.filter(qset)
	else:
		listas=Credito.objects.all()

	listas=Paginador(listas,50,pagina)
	titulos=['Folio del Credito','Subdistribuidor', 'Venta', 'Totalvta', 'Plazo', 'Fecha de Credito', 'Estado', 'Observacion', 'Historial']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for lista in listas:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, lista.folioc)
		contenido='%s<td>%s</td>\n'%(contenido, lista.subdist)
		contenido='%s<td>%s</td>\n'%(contenido, lista.venta)
		contenido='%s<td>%s</td>\n'%(contenido, lista.totalvta)
		contenido='%s<td>%s</td>\n'%(contenido, lista.plazo)
		contenido='%s<td>%s</td>\n'%(contenido, FechaSTR(lista.fxCredito))
		contenido='%s<td>%s</td>\n'%(contenido, lista.edo)
		contenido='%s<td>%s</td>\n'%(contenido, lista.observacion)
		contenido='%s<td><a href=\"/contabilidad/cobranzas/sub_distribuidores/historial?filtro=%s\">Historial</a></td>\n'%(contenido, lista.id)

		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(q,listas))

	return html

def ReporteCreditoSubDistribuidoresHistorial(pagina, credito, tituloR):
	listas=HistorialSubdistribuidor.objects.filter(credito=credito)

	listas=Paginador(listas,50,pagina)
	titulos=['Credito','Abono', 'Fecha de Abono']
	contenido='<tr>\n'
	for titulo in titulos:
		contenido='%s <td id=\"gridhead\">%s</td>'%(contenido, titulo)
	contenido='%s</tr>\n'%(contenido)

	for lista in listas:
		contenido='%s<tr>\n'%(contenido)

		contenido='%s<td>%s</td>\n'%(contenido, lista.credito)
		contenido='%s<td>%s</td>\n'%(contenido, lista.abono)
		contenido='%s<td>%s</td>\n'%(contenido, FechaSTR(lista.fxAbono))
		contenido='%s</tr>\n'%(contenido)

	html='%s\n%s\n%s'%(EncabezadoR(tituloR), contenido, PiesR(credito,listas))

	return html







