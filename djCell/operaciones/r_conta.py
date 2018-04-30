# -*- coding: utf-8 -*-
from djCell.operaciones import comunes
from djCell.operaciones import repor
from django.db.models import Q
from djCell.apps.contabilidad.models import *
from djCell.apps.personal.models import Empleado
from djCell.apps.proveedor.models import Proveedor
from djCell.apps.corteVta.models import CorteVenta
from django.contrib.auth.models import User

from django.conf import settings
STATIC_URL = settings.STATIC_URL
from django.middleware import csrf

numElem=50

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
def ReporteNominas(pagina, filtro, tituloR, request):
	nominas = Nominas(filtro)
	x=csrf.get_token(request)
	if nominas:
		nominas=repor.Paginador(nominas,numElem,pagina)
		contenido=repor.RTitulos(['Folio','Fecha de Creacion','Descripcion','Imprimir' ,'Seleccionar', 'Cerrar'])
		for nomina in nominas:
			rtr=[
				repor.Rtd(nomina.folio),
				repor.Rtd(comunes.FechaSTR(nomina.fxCreacion)),
				repor.Rtd(nomina.descripcion),
				repor.Rtd('<form  action=\".\" method=\"GET\" enctype=\"multipart/form-data\"><a href=\"\" class=\"tooltipbasic\" data-tooltip=\"Descargar Nomina seleccionada\"><input type=\"checkbox\" name=\"excel\" value=\"Exportar\">Descargar Reporte</a> || <input title=\"De clic para imprimir la consulta\" class=\"submit success\" type=\"submit\" value=\"Descargar\"><input type=\"hidden\" name=\"key\" value=\"%s\"/></form>'%(nomina.id)),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(nomina.id))
				]
			if nomina.cerrar:
				rtr.append( repor.Rtd_B(nomina.cerrar) )
			else:
				rtr.append(repor.Rtd('<form  name=formConfir%s action=\".\" method=\"POST\" enctype=\"multipart/form-data\"><input name=\"CerrarNomina\"title=\"De clic para cerrar la Nomina\" class=\"submit success\" type=\"submit\" onclick=\"Confirmacion(formConfir%s)\" value=\"Cerrar\"><input type=\"hidden\" name=\"nominaId\" value=\"%s\"/><input type=\"hidden\" name=\"csrfmiddlewaretoken\" value=\"%s\"/></form>'%(nomina.id,nomina.id,nomina.id, x)))
				
			contenido='%s%s'%(contenido ,repor.Rtr(rtr))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,nominas))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()


def CuentaEmpleados(q):
	if q:
		qset=(Q(empleado__nombre__icontains=q)|
		Q(empleado__aPaterno__icontains=q)|
		Q(empleado__aMaterno__icontains=q)|
		Q(empleado__telefono__icontains=q)|
		Q(empleado__puesto__puesto__icontains=q)|
		Q(empleado__area__area__icontains=q)|
		Q(empleado__curp__icontains=q)|
		Q(tipoCuenta__tipo__icontains=q)|
		Q(fxCreacion__icontains=q)|
		Q(observacion__icontains=q))
		datos=CuentaEmpleado.objects.filter(qset)
	else:
		datos=CuentaEmpleado.objects.all()
	return datos
def CuentasEmpleado(empleado):
	if empleado:
		datos = CuentaEmpleado.objects.filter(empleado=empleado)
	else:
		datos=None
	return datos
def ReporteCuentaEmpleados(pagina, empleado ,filtro, tituloR, seleccionar):
	#si no se manejan filtros especiales se puede quitar datos y usar
	if empleado:
		datos = CuentasEmpleado(empleado)
	else:
		datos = CuentaEmpleados(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		cont=['Folio','Empleado','Tipo de Cuenta', 'Monto original', 'Fecha de Registro',
			'Observaciones', 'Adeudo Actual']
		if seleccionar:
			cont.append('Seleccionar')
		contenido=repor.RTitulos(cont)
		for dato in datos:
			d_cont=[

				repor.Rtd(dato.folio),
				repor.Rtd(dato.empleado),
				repor.Rtd(dato.tipoCuenta),
				repor.Rtd(dato.monto),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.fxCreacion)),
				repor.Rtd(dato.observacion),
				repor.Rtd(dato.adeudo)
				#Link de seleccion o contruccion compleja
				
				]
			if seleccionar:
				d_cont.append(repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id)))
			contenido='%s%s'%(contenido ,repor.Rtr(d_cont))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoResultados()
	else:
		return repor.NoDatos()

def HistorialEmpleados(cuenta):
	if cuenta:
		datos = HistorialEmpleado.objects.filter(cuentaEmpleado=cuenta).order_by('-id')
	else:
		datos = None
	return datos
def ReporteHistorialEmpleados(pagina, cuenta, filtro):
	#si no se manejan filtros especiales se puede quitar datos y usar
	if cuenta:
		datos = HistorialEmpleados(cuenta)
		tituloR = 'Historial de la Cuenta %s'%(cuenta)
		if datos:
			datos=repor.Paginador(datos,numElem,pagina)
			contenido=repor.RTitulos(['Descuento','Fecha de pago', 'Observaciones'])
			for dato in datos:
				contenido='%s%s'%(contenido ,repor.Rtr([

					repor.Rtd(dato.descuento),
					#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
					repor.Rtd(comunes.FechaSTR(dato.fxPago)),
					repor.Rtd(dato.observacion)

					]))
			return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
		elif filtro:
			return repor.NoResultados()
		else:
			return repor.NoDatos()
	else:
		return 'No se encontro la Cuenta'

def NominaEmpleados(q):
	if q:
		qset=(Q(empleado__nombre__icontains=q)|
		Q(empleado__aPaterno__icontains=q)|
		Q(empleado__aMaterno__icontains=q)|
		Q(folio__icontains=q))
		nominas=Nomina.objects.filter(qset).order_by('fxPago')
	else:
		nominas=Nomina.objects.all().order_by('fxPago')
	return nominas

def ReporteNominaEmpleados(pagina, filtro, tituloR, admin):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = NominaEmpleados(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		titulos=['Folio','Empleado','Salario','Dias Trabajados','Bono de Puntualidad',
			'Bono de Productividad','Vales de despensa','SubTotal','Descuento', 'Total','Fecha Pago',
			'Observaciones', 'Pagado', 'Pagar']
		if admin:
			titulos.append('Editar')
		contenido=repor.RTitulos(titulos)
		for dato in datos:
			contenedor=[
				repor.Rtd(dato.dato.nomina.folio),
				repor.Rtd(dato.dato.empleado),
				repor.Rtd(dato.dato.salarioDia)
				]
			if dato.diasTrab:
				contenedor.append(repor.Rtd(dato.diasTrab))
			else:
				contenedor.append(repor.Rtd('<a href=\"/contabilidad/nomina/nueva_nomina/?nominaId=%s&amp;filtro=%s\">Asignar Dias</a>'%( dato.id, dato.nomina.id)))
			contenedor.append(repor.Rtd(dato.bonoPuntualidad))
			contenedor.append(repor.Rtd(dato.bonoProductividad))
			contenedor.append(repor.Rtd(dato.bonoVales))
			contenedor.append(repor.Rtd((dato.total+dato.descuento)))
			contenedor.append(repor.Rtd(dato.descuento))
			contenedor.append(repor.Rtd(dato.total))
			contenedor.append(repor.Rtd(comunes.FechaSTR(dato.fxPago)))
			contenedor.append(repor.Rtd(dato.observacion))
			contenedor.append(repor.Rtd_B(dato.pagado))
			contenedor.append(repor.Rtd(
				'<a href=\"/contabilidad/nomina/nominas/?nominaId=%s&amp;filtro=%s\">Pagar</a>\n'%(dato.id, dato.nomina.id)
				))
			if admin:
				contenedor.append(repor.Rtd(
					'<td><a href=\"/contabilidad/nomina/nueva_nomina/?nominaId=%s&amp;filtro=%s\">Editar</a>\n'%(dato.id, dato.nomina.id)
					))

			contenido='%s%s'%(contenido ,repor.Rtr(contenedor))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()


def Metass(q, estado):
	qset2 = (Q(empleado__puesto__puesto__icontains='encargado') | Q(empleado__puesto__puesto__icontains='vendedor'))
	if q:
		qset=(Q(empleado__curp__icontains=q) |
			 Q(empleado__nombre__icontains=q) | 
			 Q(empleado__aPaterno__icontains=q) | 
			 Q(empleado__aMaterno__icontains=q))
		datos=Meta.objects.filter(qset,qset2,empleado__estadoEmpleado=estado).order_by('empleado')
	else:
		datos=Meta.objects.filter(qset2,empleado__estadoEmpleado=estado).order_by('empleado')
	return datos
def ReporteMetass(pagina, datos, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Empleado','Meta de Equipos','Meta de Planes', 'Meta de Servicios'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.empleado),
				repor.Rtd(dato.metaEquipo),
				repor.Rtd(dato.metaPlanes),
				repor.Rtd(dato.metaServicios),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def Cajas(q):
	if q:
		datos = Caja.objects.filter(nombre__icontains=q)
	else:
		datos=Caja.objects.all()
	return datos

def ReporteCajas(pagina,  filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = Cajas(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Nombre','Saldo','Seleccionar'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.nombre),
				repor.Rtd(dato.saldo),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def HistorialCajas(caja):
	if q:
		datos = HistorialCaja.objects.filter(caja=caja).order_by('-id')
	else:
		None
	return datos

def ReporteHistorialCajas(pagina, caja, filtro ):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	if caja:
		datos = HistorialCajas(caja)
		tituloR = 'Historial de la Caja %s'%(caja)
		if datos:
			datos=repor.Paginador(datos,numElem,pagina)
			contenido=repor.RTitulos(['Fecha de Movimiento','Monto','Descripcion', 'Movimiento'])
			for dato in datos:
				contenido='%s%s'%(contenido ,repor.Rtr([

					repor.Rtd(comunes.FechaSTR(dato.FECHA)),
					repor.Rtd(dato.monto),
					repor.Rtd(dato.descripcion),
					repor.Rtd_B(dato.abono),
					
					]))
			return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
		elif filtro:
			return repor.NoDatos()
		else:
			return repor.NoResultados()
	else:
		return 'No se encontro la Caja'

def Gastoss(q):
	if q:
		qset=(Q(folioNota__icontains=q) |
			 Q(descripcion__icontains=q) | 
			 Q(observacion__icontains=q))
		datos=Gastos.objects.filter(qset).order_by('-id')
	else:
		datos=Gastos.objects.all().order_by('-id')
	return datos
def ReporteGastoss(pagina, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = Gastoss(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Folio de la Nota','Descripcion','Fecha de Gasto', 'Fecha de Registro',
			'Monto', 'Observacion'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.folioNota),
				repor.Rtd(dato.descripcion),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.fxGasto)),
				repor.Rtd(comunes.FechaSTR(dato.fxRegistro)),
				repor.Rtd(dato.monto),
				repor.Rtd(dato.observacion)

				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def Cuentas(q):
	if q:
		qset=(Q(cuenta__icontains=q)|
		Q(nocuenta__icontains=q)|
		Q(observacion__icontains=q))
		cuentas=Cuenta.objects.filter(qset)
	else:
		cuentas=Cuenta.objects.all()
	return cuentas
	
def ReporteCuentas(pagina, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = Cuentas(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Cuenta','No. de Cuenta','Saldo', 'Observaciones', 'Fecha de Ingreso'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.cuenta),
				repor.Rtd(dato.nocuenta),
				repor.Rtd(dato.saldo),
				repor.Rtd(dato.observacion),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.fxIngreso))
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def CuentaHistoriales(q, deposito, cuenta):
	if cuenta:
		if deposito:
			cuentas=CuentaHistorial.objects.filter(cuenta=cuenta, deposito=True)
		else:
			cuentas=CuentaHistorial.objects.filter(cuenta=cuenta, deposito=False)
	elif q:
		qset=(Q(noReferencia__icontains=q)|
		Q(cheque__icontains=q)|
		Q(poliza__icontains=q)|
		Q(noReferencia__icontains=q)|
		Q(fecha__icontains=q)|
		Q(cuenta__cuenta__icontains=q)|
		Q(cuenta__nocuenta__icontains=q)|
		Q(cuenta__observacion__icontains=q)|
		Q(proveedor__rfc__icontains=q)|
		Q(proveedor__nombre__icontains=q)|
		Q(proveedor__tel__icontains=q)|
		Q(concepto__icontains=q))
		if deposito:
			cuentas=CuentaHistorial.objects.filter(qset, deposito=True)
		else:
			cuentas=CuentaHistorial.objects.filter(qset, deposito=False)
	else:
		if deposito:
			cuentas=CuentaHistorial.objects.filter(deposito=True)
		else:
			cuentas=CuentaHistorial.objects.filter(deposito=False)
	return cuentas
def ReporteCuentaHistoriales(pagina, cuenta, deposito, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar datos = Objetos(filtro)
	datos=CuentaHistoriales(filtro, deposito,cuenta)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Cheque', 'Poliza', 'No. de Referencia','Fecha','Cuenta',
			'Proveedor', 'Concepto', 'Cantidad', 'Estado'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.cheque),
				repor.Rtd(dato.poliza),
				repor.Rtd(dato.noReferencia),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.fecha)),
				repor.Rtd(dato.cuenta),
				repor.Rtd(dato.proveedor),
				repor.Rtd(dato.concepto),
				repor.Rtd(dato.cantidad),
				repor.Rtd(dato.estado)

				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoResultados()
	else:
		return repor.NoDatos()

def LineaCreditos(q):
	if q:
		qset=(Q(proveedor__rfc__icontains=q)|
		Q(proveedor__nombre__icontains=q)|
		Q(proveedor__tel__icontains=q)|
		Q(notaCredito__icontains=q))
		lineas=LineaCredito.objects.filter(qset)
	else:
		lineas=LineaCredito.objects.filter(pagado=False)
	return lineas
def ReporteLineaCreditos(pagina, filtro, tituloR):
	#si no se manejan filtros especiales se puede quitar datos y usar 
	datos = LineaCreditos(filtro)
	if datos:
		datos=repor.Paginador(datos,numElem,pagina)
		contenido=repor.RTitulos(['Proveedor','Anotaciones del Credito','Total', 'Fecha de Credito', 'Deuda',
			'Pagado', 'Selecciona'])
		for dato in datos:
			contenido='%s%s'%(contenido ,repor.Rtr([

				repor.Rtd(dato.proveedor),
				repor.Rtd(dato.notaCredito),
				repor.Rtd(dato.total),
				#repor.Rtd_B(boolean) es para los booleanos, cambia el texto por una imagen
				repor.Rtd(comunes.FechaSTR(dato.fxCredito)),
				repor.Rtd(dato.deuda),
				repor.Rtd_B(dato.pagado),
				repor.Rtd('<a href=\"?filtro=%s\">Seleccionar</a>'%(dato.id))#Link de seleccion o contruccion compleja
				
				]))
		return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
	elif filtro:
		return repor.NoDatos()
	else:
		return repor.NoResultados()

def HistLCreditos(credito):
	if credito:
		cuentas=Cuenta.objects.filter(lineaCredito=credito)
	else:
		cuentas=None
	return cuentas
def ReporteHistLCreditos(pagina, credito, filtro):
	#si no se manejan filtros especiales se puede quitar datos y usar
	if credito:
		datos = HistLCreditos(credito)
		tituloR ='Historial de Credito de la Cuenta %s'%(credito)
		if datos:
			datos=repor.Paginador(datos,numElem,pagina)
			contenido=repor.RTitulos(['Fecha de Abono','Cantidad Abonada','Observaciones'])
			for dato in datos:
				contenido='%s%s'%(contenido ,repor.Rtr([

					repor.Rtd(comunes.FechaSTR(dato.fxAbono)),
					repor.Rtd(dato.abono),
					repor.Rtd(dato.observacion)

					]))
			return '%s\n%s\n%s'%(repor.EncabezadoR(tituloR),contenido , repor.Paginas(filtro,datos))
		elif filtro:
			return repor.NoDatos()
		else:
			return repor.NoResultados()
	else:
		return 'No se encontro la Linea de Credito'