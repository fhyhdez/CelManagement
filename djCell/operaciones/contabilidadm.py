# -*- coding: utf-8 -*-
from django.db.models import Q
from djCell.apps.personal.models import *
from djCell.apps.contabilidad.models import *
from djCell.apps.productos.models import *
from djCell.apps.recargas.models import *
from djCell.apps.ventas.models import *
from djCell.apps.credito.models import *
from djCell.apps.almacen.models import * 
from djCell.apps.comisiones.models import Comision
from djCell.apps.proveedor.models import *
from djCell.apps.clientes.models import ClienteFacturacion
from djCell.apps.corteVta.models import CorteVenta, DiferenciasCorte

def Empleados(q):
	if q:
		qset=(Q(nombre__icontains=q)|
		Q(aPaterno__icontains=q)|
		Q(aMaterno__icontains=q)|
		Q(direccion__icontains=q)|
		Q(telefono__icontains=q)|
		Q(fxIngreso__icontains=q)|
		Q(fxNacimiento__icontains=q)|
		Q(puesto__puesto__icontains=q)|
		Q(area__area__icontains=q)|
		Q(colonia__colonia__icontains=q)|
		Q(ciudad__ciudad__icontains=q)|
		Q(estado__estado__icontains=q)|
		Q(curp__icontains=q))
		empleados=Empleado.objects.filter(qset).order_by('curp','estadoEmpleado')
	else:
		empleados=Empleado.objects.all().order_by('curp','estadoEmpleado')
	return empleados


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

def Cuentas(q):
	if q:
		qset=(Q(cuenta__icontains=q)|
		Q(nocuenta__icontains=q)|
		Q(observacion__icontains=q))
		cuentas=Cuenta.objects.filter(qset)
	else:
		cuentas=Cuenta.objects.all()
	return cuentas


def CuentaHistoriales(q, deposito):
	if q:
		qset=(Q(noReferencia__icontains=q)|
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

def ClienteFacturaciones(q):
	if q:
		qset=(Q(rfc__icontains=q)|
		Q(razonSocial__icontains=q)|
		Q(direccion__icontains=q))
		lineas=ClienteFacturacion.objects.filter(qset)
	else:
		lineas=ClienteFacturacion.objects.all()
	return lineas


def listarInventario(equipos,expres,accesorios,fichas):
	l1 = []
	l2 = []
	l3 = []
	l4 = []
	for x in equipos:
		#equipo, imei, icc, nocell ,accesorios, observaciones
		item = x.equipo.detallesEquipo.marca.marca.title()+' '+x.equipo.detallesEquipo.modelo.title()+' '+x.equipo.detallesEquipo.color.title()
		l1.append([item,str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.equipo.accesorioEqu.title(),x.observacion ])
	for x in expres:
		#icc, nocell
		l2.append([str(x.expres.icc),x.expres.noCell, x.observacion])
	for x in accesorios:
		item = x.accesorio.detallesAccesorio.seccion.seccion+' '+x.accesorio.detallesAccesorio.marca.marca+' '+x.accesorio.detallesAccesorio.descripcion+' '
		l3.append([str(x.accesorio.codigoBarras),item,x.observacion])
	for x in fichas:
		l4.append([str(x.ficha.nominacion.nominacion),str(x.ficha.folio),x.observacion])
	
	inventario = []
	inventario.append(l1)
	inventario.append(l2)
	inventario.append(l3)
	inventario.append(l4)
	return inventario

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


def sumaVentasActivas(sucursal,fecha):
	suma = 0
	try:
		vtas = Venta.objects.filter(sucursal__id=sucursal,aceptada=True,fecha__icontains=fecha)
		for x in vtas:
			if x.credito:
				pass
			else:
				suma = suma + x.total
	except :
		suma = 0
	return suma

def sumaCortesActivos(sucursal,fecha):
	suma = 0
	try:
		vtas = CorteVenta.objects.filter(sucursal__id=sucursal,fxCorte__icontains=fecha,cerrado=False)
		for x in vtas:
			suma = suma + x.total
	except :
		suma = 0
	return suma



def fillCancelaciones():
	vc = Venta.objects.filter(aceptada=False)
	can = None
	for x in vc:
		try:
			can = Cancelaciones.objects.get(venta=x)
		except :
			can = Cancelaciones()
			can.venta = x
			can.save()

def back_almacenItems(tipo,item,so):
	if tipo==0:
		try:
			aux=AlmacenEquipo.objects.get(estado=False,equipo=item,sucursal=so)
			aux.estado=True
			aux.save()
			estatus=None
			try:
				estatus=Estatus.objects.get(estatus="Existente")
			except :
				estatus=Estatus()
				estatus.estatus="Existente"
				estatus.save()

			item.estatus=estatus
			item.sucursal=sd
			item.save()
		except :
			pass
			
	elif tipo==1:
		try:
			aux=AlmacenExpres.objects.get(estado=False,expres=item,sucursal=so)
			aux.estado=True
			aux.save()
			estatus=None
			try:
				estatus=Estatus.objects.get(estatus="Existente")
			except :
				estatus=Estatus()
				estatus.estatus="Existente"
				estatus.save()
				
			item.estatus=estatus
			item.sucursal=sd
			item.save()
		except :
			pass

	elif tipo==2:
		try:
			aux=AlmacenAccesorio.objects.get(estado=False,accesorio=item,sucursal=so)
			aux.estado=True
			aux.save()
			estatus=None
			try:
				estatus=EstatusAccesorio.objects.get(estatus="Existente")
			except :
				estatus=EstatusAccesorio()
				estatus.estatus="Existente"
				estatus.save()
				
			item.estatus=estatus
			item.sucursal=sd
			item.save()
		except :
			pass

	elif tipo==3:
		try:
			aux=AlmacenFicha.objects.get(estado=False,ficha=item,sucursal=so)
			aux.estado=True
			aux.save()
			estatus=None
			try:
				estatus=EstatusFicha.objects.get(estatus="Existente")
			except :
				estatus=EstatusFicha()
				estatus.estatus="Existente"
				estatus.save()
				
			item.estatus=estatus
			item.sucursal=sd
			item.save()
		except :
			pass

	elif tipo==4:
		try:
			aux=SaldoSucursal.objects.get(sucursal=so)
			aux.saldo="%.2f" % round(aux.saldo+item,2)
			aux.save()
		except :
			pass
		
def liberarProductos(venta):
	v = Venta.objects.get(id=venta)
	suc = Sucursal.objects.get(id= v.sucursal.id)
	#equipos
	try:
		ev = VentaEquipo.objects.filter(venta=v)
		for x in ev:
			try:
				back_almacenItems(1,x.equipo,suc)
			except :
				pass
	except :
		pass #no hay equipos en esa venta

	#express
	try:
		ev = VentaExpres.objects.filter(venta=v)
		for x in ev:
			try:
				back_almacenItems(2,x.expres,suc)
			except :
				pass
	except :
		pass #no hay equipos en esa venta

	#accesorios
	try:
		ev = VentaAccesorio.objects.filter(venta=v)
		for x in ev:
			try:
				back_almacenItems(3,x.accesorio,suc)
			except :
				pass
	except :
		pass #no hay equipos en esa venta

	#fichas
	try:
		ev = VentaFichas.objects.filter(venta=v)
		for x in ev:
			try:
				back_almacenItems(1,x.ficha,suc)
			except :
				pass
	except :
		pass #no hay equipos en esa venta

	#saldo
	try:
		ev = VentaRecarga.objects.filter(venta=v)
		for x in ev:
			try:
				back_almacenItems(4,x.recarga.montos.monto,suc)
			except :
				pass
	except :
		pass #no hay equipos en esa venta


