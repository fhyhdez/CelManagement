# -*- coding: utf-8 -*-
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
		datos=ClienteFacturacion.objects.filter(qset)
	else:
		datos=ClienteFacturacion.objects.all()
	return datos

def VentaFacturadas(q):
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
		datos=VentaFactura.objects.filter(qset)
	else:
		datos=VentaFactura.objects.filter()
	return datos

def Ventas(q):
	if q:
		qset=(Q(folioVenta__icontains=q)|
		Q(fecha__icontains=q)|
		Q(sucursal__nombre__icontains=q)|
		Q(usuario__username__icontains=q)|
		Q(sucursal__nombre__icontains=q)|
		Q(sucursal__nombre__icontains=q))
		datos=Venta.objects.filter(qset,facturada=False, aceptada=True)
	else:
		datos=Venta.objects.filter(facturada=False, aceptada=True)
	return datos

def VentaEquipos(q):
	if q:
		qset=(
		Q(venta__folioVenta__icontains=q)|
		Q(venta__fecha__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(venta__usuario__username__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(equipo__imei__icontains=q)|
		Q(equipo__icc__icontains=q)|
		Q(equipo__detallesEquipo__marca__marca__icontains=q)|
		Q(equipo__detallesEquipo__modelo__icontains=q)
		)
		datos=VentaEquipo.objects.filter(qset)
	else:
		datos=VentaEquipo.objects.all()
	return datos

def VentaExpress(q):
	if q:
		qset=(
		Q(venta__folioVenta__icontains=q)|
		Q(venta__fecha__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(venta__usuario__username__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(expres__icc__icontains=q)|
		Q(expres__noCell__icontains=q)
		)
		datos=VentaExpres.objects.filter(qset)
	else:
		datos=VentaExpres.objects.all()
	return datos

def VentaAccesorios(q):
	if q:
		qset=(Q(venta__folioVenta__icontains=q)|
		Q(venta__fecha__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(venta__usuario__username__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(accesorio__codigoBarras__icontains=q)|
		Q(accesorio__detallesAccesorio__marca__marca__icontains=q)|
		Q(accesorio__detallesAccesorio__descripcion__icontains=q))
		datos=VentaAccesorio.objects.filter(qset)
	else:
		datos=VentaAccesorio.objects.all()
	return datos

def VentaFichass(q):
	if q:
		qset=(Q(venta__folioVenta__icontains=q)|
		Q(venta__fecha__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(venta__usuario__username__icontains=q)|
		Q(venta__sucursal__nombre__icontains=q)|
		Q(ficha__folio__icontains=q)|
		Q(ficha__nominacion__nominacion__icontains=q))
		datos=VentaFichas.objects.filter(qset)
	else:
		datos=VentaFichas.objects.all()
	return datos

def Subdistribuidores(q):
	if q:
		qset=(Q(cliente__rfc__icontains=q)|
		Q(cliente__razonSocial__icontains=q)|
		Q(cliente__direccion__icontains=q)|
		Q(telefono__icontains=q))
		datos=Subdistribuidor.objects.filter(qset)
	else:
		datos=Subdistribuidor.objects.all()
	return datos

def Creditos(q):
	if q:
		qset=(Q(subdist__cliente__rfc__icontains=q)|
		Q(subdist__cliente__razonSocial__icontains=q)|
		Q(subdist__cliente__direccion__icontains=q)|
		Q(subdist__telefono__icontains=q)|
		Q(folioc__icontains=q)|
		Q(venta__folioVenta__icontains=q)|
		Q(observacion__icontains=q))
		datos=Credito.objects.filter(qset)
	else:
		datos=Credito.objects.all()
	return datos

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

def Usuarios(q):
	if q:
		qset=(Q(empleado__nombre__icontains=q)|
		Q(empleado__aPaterno__icontains=q)|
		Q(empleado__aMaterno__icontains=q)|
		Q(empleado__direccion__icontains=q)|
		Q(empleado__telefono__icontains=q)|
		Q(empleado__puesto__puesto__icontains=q)|
		Q(empleado__area__area__icontains=q)|
		Q(user__username__icontains=q)|
		Q(permiso__descripcion__icontains=q))
		datos=Usuario.objects.filter(qset)
	else:
		datos=Usuario.objects.all()
	return datos

def Sucursales(q):
	if q:
		qset=(Q(nombre__icontains=q) |
			 Q(encargado__nombre__icontains=q) | 
			 Q(encargado__aPaterno__icontains=q) | 
			 Q(encargado__aMaterno__icontains=q) | 
			 Q(encargado__curp__icontains=q) | 
			 Q(zona__zona__icontains=q) | 
			 Q(direccion__icontains=q))
		datos=Sucursal.objects.filter(qset).order_by('nombre')
	else:
		datos=Sucursal.objects.all().order_by('nombre')
	return datos

def VendedorSucursales(q, mysucursal):
	if q:
		qset=(Q(sucursal__nombre__icontains=q) |
			 Q(empleado__nombre__icontains=q) | 
			 Q(empleado__aPaterno__icontains=q) | 
			 Q(empleado__aMaterno__icontains=q) | 
			 Q(empleado__curp__icontains=q) | 
			 Q(sucursal__zona__zona__icontains=q))
		datos=VendedorSucursal.objects.filter(qset,empleado__estadoEmpleado=True).exclude(sucursal=mysucursal).order_by('sucursal').order_by('empleado')
	else:
		datos=VendedorSucursal.objects.filter(empleado__estadoEmpleado=True).exclude(sucursal=mysucursal).order_by('sucursal').order_by('empleado')
	return datos

def CorteVentas(q):
	if q:
		qset=(Q(folioCorteVta__icontains=q)|
		Q(sucursal__nombre__icontains=q)|
		Q(observacion__icontains=q))
		datos=CorteVenta.objects.filter(qset)
	else:
		datos=CorteVenta.objects.all()
	return datos

def DiferenciasCortes(q):
	if q:
		qset=(Q(corteVenta__folioCorteVta__icontains=q)|
		Q(corteVenta__sucursal__nombre__icontains=q)|
		Q(corteVenta__observacion__icontains=q)|
		Q(revisaCorte__username__icontains=q)|
		Q(observacion__icontains=q))
		datos=DiferenciasCorte.objects.filter(qset)
	else:
		datos=DiferenciasCorte.objects.all()
	return datos


def InvEquipos(q,inventario,revisado):
	if q:
		qset=(Q(equipo__imei__icontains=q)|
		Q(equipo__icc__icontains=q)|
		Q(equipo__detallesEquipo__marca__marca__icontains=q)|
		Q(equipo__detallesEquipo__modelo__icontains=q))
		datos=InvEquipo.objects.filter(qset, inventario=inventario, revisado=revisado)
	else:
		datos=InvEquipo.objects.filter(inventario=inventario, revisado=revisado)
	return datos

def InvAccesorios(q,inventario,revisado):
	if q:
		qset=(Q(accesorio__codigoBarras__icontains=q)|
		Q(accesorio__detallesAccesorio__marca__marca__icontains=q)|
		Q(accesorio__detallesAccesorio__descripcion__icontains=q))
		datos=InvAccesorio.objects.filter(qset, inventario=inventario, revisado=False)
	else:
		datos=InvAccesorio.objects.filter(inventario=inventario, revisado=revisado)
	return datos

def InvExpress(q,inventario,revisado):
	if q:
		qset=(Q(expres__icc__icontains=q)|
		Q(expres__noCell__icontains=q))
		datos=InvExpres.objects.filter(qset, inventario=inventario, revisado=revisado)
	else:
		datos=InvExpres.objects.filter(inventario=inventario, revisado=revisado)
	return datos

def InvFichas(q,inventario,revisado):
	if q:
		qset=(Q(ficha__folio__icontains=q)|
		Q(ficha__nominacion__nominacion__icontains=q))
		datos=InvFicha.objects.filter(qset, inventario=inventario, revisado=revisado)
	else:
		datos=InvFicha.objects.filter(inventario=inventario, revisado=revisado)
	return datos

def Inventarios(q):
	if q:
		qset=(Q(sucursal__nombre__icontains=q)|
		Q(folio__icontains=q)|
		Q(fxInicio__icontains=q)|
		Q(fxFinal__icontains=q))
		datos = Inventario.objects.filter(qset)
	else:
		datos=Inventario.objects.all()
	return datos

def Facturas(q):
	if q:
		qset=(Q(folio__icontains=q)|
		Q(documento__icontains=q)|
		Q(proveedor__rfc__icontains=q)|
		Q(proveedor__nombre__icontains=q)|
		Q(proveedor__tel__icontains=q)|
		Q(fxFactura__icontains=q)|
		Q(fxIngreso__icontains=q)|
		Q(observacion__icontains=q)|
		Q(usuario__username__icontains=q))
		datos=Factura.objects.filter(qset).distinct()
	else:
		datos=Factura.objects.all()
	return datos

def Cancelacioness(q,activo):
	if q:
		qset=(Q(venta__folioVenta__icontains=q) |
			 Q(venta__sucursal__nombre__icontains=q) | 
			 Q(venta__usuario__username__icontains=q))
		datos = Cancelaciones.objects.filter(qset,activo=activo).order_by('fxCancelacion').reverse()
	else:
		datos=Cancelaciones.objects.filter(activo=activo).order_by('fxCancelacion').reverse()
	return datos

def EquipoReparaciones(q):
	if q:
		qset=(Q(cliente__nombre__icontains=q) |
		 Q(sucursal__nombre__icontains=q) |
		 Q(cliente__sucursal__nombre__icontains=q)|
		 Q(cliente__folio__icontains=q))
		datos = EquipoReparacion.objects.filter(qset)
	else:
		datos=EquipoReparacion.objects.all()
	return datos

def DetallesEquipos(q):
	if q:
		qset=(Q(gama__gama__icontains=q)|
		Q(marca__marca__icontains=q)|
		Q(modelo__icontains=q)|
		Q(color__icontains=q)|
		Q(folio__icontains=q))
		datos=DetallesEquipo.objects.filter(qset).distinct()
	else:
		datos=DetallesEquipo.objects.all()
	return datos

def DetallesAccesorios(q):
	if q:
		qset=(Q(marca__marca__icontains=q)|
		Q(descripcion__icontains=q)|
		Q(seccion__seccion__icontains=q)|
		Q(precioMenudeo__icontains=q))
		datos=DetallesAccesorio.objects.filter(qset).distinct()
	else:
		datos=DetallesAccesorio.objects.all()
	return datos

def DetallesExpress(q):
	if q:
		qset=(Q(descripcion__icontains=q)|
		Q(tipoIcc__tipoIcc__icontains=q))
		datos=DetallesExpres.objects.filter(qset).distinct()
	else:
		datos=DetallesExpres.objects.all()
	return datos

def Planes(q, activo):
	if q:
		qset=(Q(plan__icontains=q)|
		Q(costo__icontains=q)|
		Q(equiposGratis__icontains=q))
		datos=Plan.objects.filter(qset,activo=activo).distinct()
	else:
		datos=Plan.objects.all()
	return datos

def AlmacenEquipos(q, estado, estatus):
	if q:
		qset=(Q(equipo__imei__icontains=q)|
		Q(equipo__icc__icontains=q)|
		Q(equipo__factura__folio__icontains=q)|
		Q(equipo__detallesEquipo__modelo__icontains=q)|
		Q(equipo__detallesEquipo__marca__marca__icontains=q)|
		Q(equipo__detallesEquipo__color__icontains=q)|
		Q(equipo__sucursal__nombre__icontains=q)|
		Q(equipo__noCell__icontains=q))
		datos=AlmacenEquipo.objects.filter(qset,estado=estado).exclude(equipo__estatus__estatus=estatus).order_by('equipo')
	else:
		datos=AlmacenEquipo.objects.filter(estado=estado).exclude(equipo__estatus__estatus=estatus).order_by('equipo')
	return datos

def AlmacenExpress(q, estado, estatus):
	if q:
		qset=(Q(expres__icc__icontains=q)|
		Q(expres__factura__folio__icontains=q)|
		Q(expres__noCell__icontains=q)|
		Q(expres__detallesExpres__descripcion__icontains=q)|
		Q(expres__sucursal__nombre__icontains=q)|
		Q(expres__detallesExpres__tipoIcc__tipoIcc__icontains=q))
		datos = AlmacenExpres.objects.filter(qset,estado=estado).exclude(expres__estatus__estatus=estatus).order_by('expres')	
	else:
		datos=AlmacenExpres.objects.filter(estado=estado).exclude(expres__estatus__estatus=estatus).order_by('expres')
	return datos

def AlmacenAccesorios(q, estado, estatus):
	if q:
		qset=(Q(accesorio__codigoBarras__icontains=q)|
		Q(accesorio__factura__folio__icontains=q)|
		Q(accesorio__detallesAccesorio__marca__marca__icontains=q)|
		Q(accesorio__detallesAccesorio__seccion__seccion__icontains=q)|
		Q(accesorio__sucursal__nombre__icontains=q)|
		Q(accesorio__detallesAccesorio__descripcion__icontains=q))
		datos = AlmacenAccesorio.objects.filter(qset,estado=estado).exclude(accesorio__estatusAccesorio__estatus=estatus).order_by('accesorio')
	else:
		datos=AlmacenAccesorio.objects.filter(estado=estado).exclude(accesorio__estatusAccesorio__estatus=estatus).order_by('accesorio')
	return datos

def AlmacenFichas(q, estado, estatus):
	if q:
		qset=(Q(ficha__folio__icontains=q)|
		Q(ficha__factura__folio__icontains=q)|
		Q(ficha__sucursal__nombre__icontains=q)|
		Q(ficha__nominacion__nominacion__icontains=q))
		datos = AlmacenFicha.objects.filter(qset,estado=estado).exclude(ficha__estatusFicha__estatus=estatus).order_by('ficha')
			
	else:
		datos=AlmacenFicha.objects.filter(estado=estado).exclude(ficha__estatusFicha__estatus=estatus).order_by('ficha')
	return datos

def SaldoSucursales(q):
	if q:
		datos = SaldoSucursal.objects.filter(sucursal__nombre__icontains=q).order_by('sucursal')
	else:
		datos = SaldoSucursal.objects.all()
	return datos



def Amonestaciones(q):
	if q:
		qset=(Q(fxAmonestacion__icontains=q) |
		 Q(empleado__nombre__icontains=q) | 
		 Q(empleado__aPaterno__icontains=q) | 
		 Q(empleado__aMaterno__icontains=q) | 
		 Q(empleado__curp__icontains=q) | 
		 Q(tipoAmonestacion__tipo__icontains=q))
		datos=Amonestacion.objects.filter(qset)
	else:
		datos=Amonestacion.objects.all()
	return datos

def Empleados(q, estado):
	qset2 = (Q(puesto__puesto__icontains='encargado') | Q(puesto__puesto__icontains='vendedor'))
	if q:
		qset=(Q(curp__icontains=q) |
			 Q(nombre__icontains=q) | 
			 Q(aPaterno__icontains=q) | 
			 Q(aMaterno__icontains=q))
		datos=Empleado.objects.filter(qset2,qset,estadoEmpleado=estado).order_by('curp')
	else:
		datos=Empleado.objects.filter(qset2,estadoEmpleado=estado).order_by('curp')
	return datos

def Solicitudes(q):
	if q:
		qset=(Q(folio__icontains=q)|
		Q(sucursal__nombre__icontains=q) |
		Q(fxSolicitud__icontains=q) |
		Q(vendedor__curp__icontains=q) |
		Q(nombre__icontains=q) |
		Q(aPat__icontains=q) |
		Q(aMat__icontains=q) |
		Q(plan__plan__icontains=q) |
		Q(plan__costo__icontains=q) |
		Q(estado__estado__icontains=q) |
		Q(fxModificacion__icontains=q))

		datos=Solicitud.objects.filter(qset).order_by('folio').order_by('fxSolicitud').order_by('nombre').order_by('sucursal')
	else:
		datos=Solicitud.objects.all().order_by('folio').order_by('fxSolicitud').order_by('nombre').order_by('sucursal')
	return datos


def FlexeoEquipos(q):
	if q:
		qset = (Q(portabilidad__cliente__nombre__icontains=q) | 
		Q(portabilidad__cliente__folio__icontains=q) | 
		Q(portabilidad__cliente__direccion__icontains=q) | 
		Q(portabilidad__cliente__sucursal__nombre__icontains=q))
		datos=FlexeoEquipo.objects.filter(qset)
	else:
		datos=FlexeoEquipo.objects.all()
	return datos

def Metas(q, estado):
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

def Cancelacioness(q, activo):
	if q:
		qset=(Q(venta__folioVenta__icontains=q) |
			 Q(venta__sucursal__nombre__icontains=q) | 
			 Q(venta__usuario__username__icontains=q))
		datos=Cancelaciones.objects.filter(qset,activo=activo).order_by('fxCancelacion').reverse()
	else:
		datos=Cancelaciones.objects.filter(activo=activo).order_by('fxCancelacion').reverse()
	return datos

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

def SolicitudNuevoProductos(q):
	if q:
		qset=(Q(folio__icontains=q) |
		 Q(nuevoProducto__icontains=q) | 
		 Q(estado__estado__icontains=q) | 
		 Q(sucursal__nombre__icontains=q))
		datos = SolicitudNuevoProducto.objects.filter(qset).order_by('estado')
	else:
		datos=SolicitudNuevoProducto.objects.all()
	return datos

def StockEquipos(q, r_sucu):
	if q:
		qset=(Q(detalle__gama__gama__icontains=q)|
		Q(detalle__modelo__icontains=q)|
		Q(detalle__marca__marca__icontains=q))
		datos=StockEquipo.objects.filter(qset,sucursal=r_sucu)
	else:
		datos=StockEquipo.objects.filter(sucursal=r_sucu)
	return datos

def StockAccesorios(q, r_sucu):
	if q:
		qset=(Q(detalle__descripcion__icontains=q)|
		Q(detalle__seccion__seccion__icontains=q)|
		Q(detalle__marca__marca__icontains=q))
		datos=StockAccesorio.objects.filter(qset,sucursal=r_sucu)
	else:
		datos=StockAccesorio.objects.filter(sucursal=r_sucu)
	return datos

def Subdistribuidores(q):
	if q:
		qset=(Q(cliente__rfc__icontains=q) |
		Q(cliente__razonSocial__icontains=q) | 
		Q(cliente__direccion__icontains=q))
		datos=Subdistribuidor.objects.filter(qset)
	else:
		datos=Subdistribuidor.objects.all()
	return datos

def Mayoristas(q):
	if q:
		qset=(Q(cliente__rfc__icontains=q) |
		Q(cliente__razonSocial__icontains=q) | 
		Q(cliente__direccion__icontains=q))
		datos=Mayorista.objects.filter(qset)
	else:
		datos=Mayorista.objects.all()
	return datos

def Movimientos(q, nombre, confir):
	if q:
		qset=(Q(folio__icontains=q)|
		Q(fx_movimiento__icontains=q)|
		Q(sucursalDestino__nombre__icontains=q))
		datos=Movimiento.objects.filter(qset,tipoMovimiento__nombre=nombre,confirmacion=confir).distinct()
	else:
		datos=Movimiento.objects.filter(tipoMovimiento__nombre=nombre,confirmacion=confir).distinct()
	return datos

def Garantias(q):
	if q:
		qset=(Q(sucursal__nombre__icontains=q) |Q(papeleta__folioPapeleta__icontains=q) | 
			Q(papeleta__nombre__icontains=q) | Q(equipo__imei__icontains=q) | 
		 	Q(equipo__icc__icontains=q))
		garantia = Garantia.objects.filter(qset).order_by('estado') #.order_by('sucursal').order_by('fxSucursal')
	else:
		garantia = Garantia.objects.all().order_by('estado')
	return garantia

def ServiciosPlans(q):
	if q:
		qset=(Q(solicitante__folio__icontains=q)| Q(sucursal__nombre__icontains=q) |Q(fxSolicitud__icontains=q) |
		Q(solicitante__nombre__icontains=q) |Q(solicitante__aPat__icontains=q) |Q(solicitante__aMat__icontains=q) |
		Q(solicitante__plan__plan__icontains=q)|Q(servicioRequiere__icontains=q)|
		Q(fxAtencion__icontains=q) |Q(fxSolicitud__icontains=q))
		datos=ServiciosPlan.objects.filter(qset).order_by('fxSolicitud').order_by('sucursal').order_by('solicitante').order_by('fxAtencion')
	else:
		datos=ServiciosPlan.objects.all().order_by('fxSolicitud').order_by('sucursal').order_by('solicitante').order_by('fxAtencion')
	return datos

def Portabilidades(q):
	if q:
		qset = (Q(cliente__nombre__icontains=q) |
		Q(sucursal__nombre__icontains=q) |
		Q(noaPortar__icontains=q) |
		Q(estado__estado__icontains=q) |
		Q(cliente__folio__icontains=q))
		datos=Portabilidad.objects.filter(qset).distinct().order_by('fxIngreso')
	else:
		datos=Portabilidad.objects.all().distinct().order_by('fxIngreso')
	return datos

def ClienteServicios(q, tipo, suc):
	if q:
		qset = (Q(nombre__icontains=q) | Q(direccion__icontains=q) | Q(folio__icontains=q)  | 
		Q(colonia__colonia__icontains=q) | Q(ciudad__ciudad__icontains=q))
		datos=ClienteServicio.objects.filter(qset,tipoCliente=tipo,sucursal__id=suc).distinct()
	else:
		datos=ClienteServicio.objects.filter(tipoCliente=tipo,sucursal__id=suc).distinct()
	return datos

def Papeletas(q, suc, tipo):
	if q:
		qset=(Q(folioPapeleta__icontains=q) |
		 Q(nombre__icontains=q) | Q(calle__icontains=q) | 
		 Q(colonia__colonia__icontains=q) | Q(codP__cp__icontains=q) | 
		 Q(ciudad__ciudad__icontains=q) | Q(estado__estado__icontains=q) | 
		 Q(telAsig__icontains=q) | Q(esnImei__icontains=q))
		datos=Papeleta.objects.filter(qset,sucursal__id=suc).exclude(tipoProducto__tipo__icontains=tipo).order_by('folioPapeleta').order_by('nombre').order_by('fxActivacion')
	else:
		datos=Papeleta.objects.filter(sucursal__id=suc).exclude(tipoProducto__tipo__icontains=tipo).order_by('folioPapeleta').order_by('nombre').order_by('fxActivacion')
	return datos

def ActivacionEquipos(q, status):
	if q:
		qset=(Q(fxActivacion__icontains=q) |
		 Q(equipo__imei__icontains=q) | 
		 Q(equipo__icc__icontains=q) | 
		 Q(equipo__detallesEquipo__marca__marca__icontains=q) | 
		 Q(equipo__detallesEquipo__modelo__icontains=q) | 
		 Q(tipoActivacion__tipo__icontains=q) |
		 Q(empleado__nombre__icontains=q) | 
		 Q(empleado__aPaterno__icontains=q) | 
		 Q(empleado__aMaterno__icontains=q) |  
		 Q(empleado__curp__icontains=q) | 
		 Q(sucursal__nombre__icontains=q))
		datos=ActivacionEquipo.objects.filter(qset,equipo__estatus__estatus=status).order_by('equipo')
	else:
		datos=ActivacionEquipo.objects.filter(equipo__estatus__estatus=status).order_by('equipo')
	return datos

def ActivacionExpresss(q,status):
	if q:
		qset=(Q(fxActivacion__icontains=q) |
			 Q(express__icc__icontains=q) | 
			 Q(tipoActivacion__tipo__icontains=q) |
			 Q(empleado__nombre__icontains=q) | 
			 Q(empleado__aPaterno__icontains=q) | 
			 Q(empleado__aMaterno__icontains=q) |  
			 Q(empleado__curp__icontains=q) | 
			 Q(sucursal__nombre__icontains=q))
		datos=ActivacionExpress.objects.filter(qset,express__estatus__estatus=status).order_by('express')
	else:
		datos=ActivacionExpress.objects.filter(express__estatus__estatus=status).order_by('express')
	return datos

def ActivacionPlanes(q):
	if q:
		qset=(Q(fxActivacion__icontains=q) |
		 Q(plan__plan__icontains=q) |
		 Q(equipo__imei__icontains=q) | 
		 Q(equipo__icc__icontains=q) | 
		 Q(equipo__detallesEquipo__marca__marca__icontains=q) | 
		 Q(equipo__detallesEquipo__modelo__icontains=q) | 
		 Q(sucursal__nombre__icontains=q))
		datos=ActivacionPlan.objects.filter(qset).order_by('equipo')
	else:
		datos=ActivacionPlan.objects.all().order_by('equipo')
	return datos