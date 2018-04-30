# -*- coding: utf-8 -*-

from djCell.apps.activaciones.models import *
from djCell.apps.sucursales.models import VendedorSucursal
from djCell.apps.personal.models import Empleado
from djCell.apps.contabilidad.models import *
from decimal import Decimal
from djCell.apps.comisiones.models import Comision
from djCell.apps.ventas.models import *
from djCell.apps.servicios.models import *
from djCell.apps.catalogos.models import *
from djCell.interface.contabilidad.forms import EmpleadoForm, VendedorSucursalForm
from djCell.interface.contabilidad.forms import ColoniaCiudad



#Modulos de operaciones
from djCell.operaciones import op_pagina, r_conta, repor
from djCell.operaciones.comunes import agregarCiudades

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

def empleado_nuevo(request, nivel):
	titulo='Nuevo Empleado'
	descr='Formulario para el ingreso de un nuevo empleado'
	mensaje=''
	empleado=None
	sucursal=None
	instance = None
	colForm = ColoniaCiudad()
	ide=request.GET.get('ide','')
	if ide:
		try:
			empleado=Empleado.objects.get(id=ide)
			titulo='Edicion de Datos del Empleado'
			descr=''
			try:
				se=VendedorSucursal.objects.get(empleado=empleado)
				sucursal=se.sucursal
			except :
				pass
		except :
			mensaje='Empleado No Encontrado'
	if empleado:
		emplForm=EmpleadoForm(instance=empleado)
		colForm = ColoniaCiudad({'colonia':empleado.colonia.colonia, 'ciudad':empleado.ciudad.ciudad })
	else:
		emplForm=EmpleadoForm()
		colForm = ColoniaCiudad()
	if sucursal:
		sucForm=VendedorSucursalForm(initial={'sucursal':sucursal})
	else:
		sucForm=VendedorSucursalForm()
	if 'actualizar' in request.POST:
		ide=request.POST.get('ide','')
		if ide:
			empleado=Empleado.objects.get(id=ide)
			emplForm=EmpleadoForm(request.POST, instance=empleado)
			colForm = ColoniaCiudad(request.POST)
		else:
			emplForm=EmpleadoForm(request.POST)
			colForm = ColoniaCiudad(request.POST)
		z1 = agregarCiudades(request.POST.get('colonia',''),request.POST.get('ciudad',''),request.POST.get('estado',''),None)
		
		if emplForm.is_valid():
			#try:
			empleado=emplForm.save(commit=False) #patita535
			empleado.colonia = Colonia.objects.get(id=z1[0])
			empleado.ciudad = Ciudad.objects.get(id=z1[1])
			empleado.save()
			emplForm=EmpleadoForm()
			colForm = ColoniaCiudad()
			mensaje='Empleado %s Guardado y Actualizado Exitosamente'%(empleado)
			sucForm=VendedorSucursalForm(request.POST)
			if sucForm.is_valid():
				venSuc=None
				sucursal=sucForm.cleaned_data['sucursal']
				try:
					venSuc=VendedorSucursal.objects.get(empleado=empleado)
				except :
					venSuc=VendedorSucursal()
					venSuc.empleado=empleado
				venSuc.sucursal=sucursal
				venSuc.save()
				sucForm=VendedorSucursalForm()
			'''except :
													transaction.rollback()
													mensaje='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
												else:
													transaction.commit()'''
	return {'nivel':nivel, 'ide':ide, 'titulo':titulo, 'descr':descr, 'mensaje':mensaje, 'emplForm':emplForm, 'colForm':colForm ,'sucForm':sucForm}

def empleado_reporte(request, nivel):
	q=request.GET.get('filtro','')
	pagina=request.GET.get('pagina','')
	empleados=None
	empleado=None
	amones=None
	comisiones=None
	cuentas=[]
	cuenta=None
	historial=None
	nomina=None
	nEmpleados=0
	mensaje='No Hay Resultados'
	if q:
		try:
			empleado=Empleado.objects.get(id=q)
			amones=Amonestacion.objects.filter(empleado=empleado).order_by('-id')[:20]
			comisiones=Comision.objects.filter(empleado=empleado).order_by('-id')[:20]
			cuenta=CuentaEmpleado.objects.filter(empleado=empleado).order_by('fxCreacion')
			if cuenta:
				for cue in cuenta:
					historial=HistorialEmpleado.objects.filter(cuentaEmpleado=cue)
					cuentas.append([cue,historial])
			q=''
			nomina=Nomina.objects.filter(empleado=empleado).order_by('-id')[:20]
		except :
			empleados=Empleados(q)
	else:
		empleados=Empleados(None)
	if empleados:
		nEmpleados=len(empleados)
		empleados = op_pagina.Paginador(empleados, 50, pagina)
		mensaje=''
		empleados=ReporteEmpleados(empleados, q, '/contabilidad/nomina/empleados/nuevo/','Reporte de Empleados')
	buscador=Busqueda(q)
	if empleado:
		ctx={'nivel':nivel,'buscador':buscador, 'mensaje':mensaje, 'empleado':empleado, 'amones':amones, 'comisiones':comisiones, 'cuentas':cuentas, 'nomina':nomina}
	else:
		ctx={'nivel':nivel,'buscador':buscador, 'mensaje':mensaje, 'empleados':empleados, 'q':q, 'nEmpleados':nEmpleados}
	return ctx

def empleadoAbonarCuenta(request, nivel):
	q=request.GET.get('filtro','')
	pagina=request.GET.get('pagina','')
	cuentas=None
	cuenta=None
	historial=None
	nCuentas=0
	mensaje = ''

	if request.method == "POST":
		q=request.POST.get('cuenta','')
		abono=Decimal(request.POST.get('abono',''))
		descripcion=request.POST.get('desc','')
		try:
		#if True:
			cuenta=CuentaEmpleado.objects.get(id=q)
			if cuenta.adeudo:
				excedente = 0
				if cuenta.adeudo < abono:
					excedente = Decimal(abono) - Decimal(cuenta.adeudo)
					abono= cuenta.adeudo
				ab=HistorialEmpleado()
				ab.cuentaEmpleado=cuenta
				ab.descuento = abono
				ab.observacion = descripcion
				cuenta.adeudo=Decimal(cuenta.adeudo)-Decimal(abono)
				ab.save()
				cuenta.save()
				historial = r_conta.ReporteHistorialEmpleados(pagina, cuenta, q)
				mensaje =' Se realizo un abono de '+str(abono)
				if not cuenta.adeudo:
					mensaje = mensaje + '. La cuenta ya ha sido liquidada'
					if excedente:
						mensaje = mensaje + ', hubo un excedente de '+str(excedente)
			else:
				mensaje ='La cuenta ya ha sido liquidada'
		except :
			mensaje ='Error interno, no se encontro la cuenta, no se realizo ningun abono'
	else:
		try:
			cuenta=CuentaEmpleado.objects.get(id=q)
			historial = r_conta.ReporteHistorialEmpleados(pagina, cuenta, q)
		except :
			cuentas=r_conta.ReporteCuentaEmpleados(pagina, None, q,'Cuentas de Empleados, Seleccione una para abono manual', True)

	ctx={'nivel':nivel, 'historial':historial, 'buscador':repor.Busqueda('Abono de Cuentas de Empleado',q),'mensaje':mensaje ,'cuentas':cuentas, 'cuenta':cuenta, 'nCuentas':nCuentas}
		
	return ctx

def updComision(empleado,user, mes):
	#today = datetime.now()
	#dateFormat = today.strftime("%Y-%m") #mes actual
	dateFormat=mes
	kit = 0
	tip = 0
	plan = 0 
	serv = 0
	try:
		eq = VentaEquipo.objects.filter(venta__aceptada=True,venta__fecha__icontains=dateFormat)
		for x in eq:
			try:
				brr = ActivacionEquipo.objects.get(equipo__imei=x.equipo.imei,empleado__id=empleado.id)
				tipo = brr.tipoActivacion.tipo
				if tipo == 'Tip':
					tip = tip + x.equipo.detallesEquipo.gama.comision
				elif tipo == 'Kit':
					kit = kit + x.equipo.detallesEquipo.gama.comision

			except ActivacionEquipo.DoesNotExist:
				pass
	except VentaEquipo.DoesNotExist:
		pass

	try:
		mmm = ActivacionPlan.objects.filter(ejecutivo=empleado,fxActivacion__icontains=dateFormat)
		for x in mmm:
			plan = plan + x.plan.comision
	except ActivacionPlan.DoesNotExist:
		pass

	try:
		zzz = comisionesReparacion.objects.filter(usuario=user,reparacion__fxRevision__icontains=dateFormat,reparacion__pagado=True)
		for x in zzz:
			serv = serv + x.reparacion.estado.comisionReparacion

	except comisionesReparacion.DoesNotExist:
		pass

	total=kit+tip+plan+serv
	if not (total == 0):
		try:
			grrr = Comision.objects.get(empleado=empleado,mes__icontains=dateFormat,pagado=False)
			grrr.comEquipoKit = kit
			grrr.comEquipoTip = tip
			grrr.comPlanes	= plan
			grrr.comServicios = serv
			grrr.save()

		except :
			a = Comision()
			a.empleado  = empleado
			a.comEquipoKit = kit
			a.comEquipoTip = tip
			a.comPlanes	= plan
			a.comServicios = serv
			a.mes = dateFormat+'-01'#el 01  es solo para que sea valido, el dia nunca se ve
			a.pagado = False
			a.save()
			

def CerrarNomina(idNom):
	mensaje=''
	try:
		nomina=Nomina.objects.get(id=idNom)
		empleados = NominaEmpleado.objects.filter(nomina = nomina, pagado =False ).count()
		if empleados == 0:
			nomina.cerrar=True
			nomina.save()
			mensaje='Nomina %s Se ha Cerrado, Se inhabilita el pago y la edicion relacionada a la misma'%(nomina)
		else:
			mensaje='Ud. no puede cerrar la nomina con empleados que no han recibido pago.'
	except :
		mensaje='No se encontro la Nomina que intento Cerrar'
	
	return mensaje