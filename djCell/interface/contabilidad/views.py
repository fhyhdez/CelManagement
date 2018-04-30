# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import datetime, timedelta
import time
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import xlwt
import re
from django.db import transaction
#apps models
from djCell.apps.activaciones.models import TipoActivacion, ActivacionEquipo, ActivacionExpress, ActivacionPlan
from djCell.apps.personal.models import Usuario
from djCell.apps.recargas.models import Monto,Recarga,SaldoSucursal, HistorialSaldo, SaldoStock
from djCell.apps.sucursales.models import EstadoSucursal, TipoSucursal, Sucursal, VendedorSucursal
from djCell.apps.personal.models import Empleado
from djCell.apps.amonestaciones.models import Amonestacion
from djCell.apps.comisiones.models import Comision
from djCell.apps.contabilidad.models import TipoCuenta, Nomina, NominaEmpleado, CuentaEmpleado, HistorialEmpleado, Cuenta, Caja, HistorialCaja, CuentaHistorial, LineaCredito, HistLCredito, Gastos
from djCell.apps.productos.models import TiempoGarantia,Estatus,Marca,Gama,DetallesEquipo,Equipo,TipoIcc,DetallesExpres,Expres, Secciones,MarcaAccesorio,DetallesAccesorio,EstatusAccesorio,Accesorio, NominacionFicha,EstatusFicha,Ficha,  TiempoAire
from djCell.apps.proveedor.models import Proveedor, FormaPago,  Factura
from djCell.apps.clientes.models import ClienteFacturacion
from djCell.apps.ventas.models import EstadoVenta, Venta,VentaEquipo,VentaExpres,VentaAccesorio,VentaFichas,VentaRecarga,VentaPlan,Renta, Cancelaciones, VentaMayoreo,TipoPago, Anticipo
from djCell.apps.facturacion.models import *
from djCell.apps.credito.models import Subdistribuidor, Credito, HistorialSubdistribuidor
from djCell.apps.garantiasuc.models import EstadoGarantia, Garantia
from djCell.apps.planes.models import EstadoSolicitud, Solicitud, TipoRelacion, Banco, Plan, DetallePlan, ServiciosPlan
from djCell.apps.servicios.models import TipoReparacion, EstadoReparacion,Reparacion, EquipoReparacion, HistorialClienteReparacion, comisionesReparacion
from djCell.apps.auditoria.models import Inventario, InvEquipo, InvExpres,InvAccesorio,InvFicha
from djCell.apps.almacen.models import AlmacenEquipo, AlmacenExpres, AlmacenAccesorio, AlmacenFicha
from djCell.apps.auditoria.models import ArqueoCaja, Inventario, InvEquipo, InvExpres,InvAccesorio,InvFicha
from djCell.apps.catalogos.models import Estado, Ciudad, Colonia, CP, Zona
from djCell.apps.papeletas.models import TipoProducto, Papeleta
from djCell.apps.movimientos.models import TipoMovimiento, Movimiento, ListaEquipo, ListaExpres, ListaAccesorio, ListaFichas, TransferenciaSaldo
from djCell.apps.corteVta.models import CorteVenta, DiferenciasCorte


#interface Formularios
from djCell.interface.contabilidad.forms import * 
from djCell.interface.admingral.forms import *


from django.conf import settings
STATIC_URL = settings.STATIC_URL

numElem=50

#Modulos en archivos

import nomina,facturacion, auditoria
from djCell.operaciones import r_conta, comunes, r_factu, repor, r_clien, r_audit
from djCell.operaciones.comunes import agregarCiudades, Permiso
from djCell.operaciones.vistas import *
from djCell.operaciones.contabilidadm import Comisiones,ListaFacturas, Empleados
from djCell.operaciones.exceles import *
from djCell.operaciones.ventasgral import *


@login_required(login_url='/')
def index_view(request):
	nivel=Permiso(request.user,[0,1,2,3,4])
	if nivel != -1:
		ctx={'nivel':nivel}
		return render_to_response('contabilidad/index.html', ctx , context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#Codigo en Depuracion 12/02/2014, migrado al archivo nomina.py, abarcado toda la seccion /contabilidad/nomina/
@login_required(login_url='/')
def contabilidad_nomina_empleados_nuevo_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		ctx=nomina.empleado_nuevo(request, nivel)
		return render_to_response('contabilidad/empleadoAdd.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_nomina_empleados_reporte_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
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
			empleados = Paginador(empleados, 50, pagina)
			mensaje=''
			empleados=ReporteEmpleados(empleados, q, '/contabilidad/nomina/empleados/nuevo/','Reporte de Empleados')

		buscador=Busqueda(q)

		if empleado:
			ctx={'nivel':nivel,'buscador':buscador, 'mensaje':mensaje, 'empleado':empleado, 'amones':amones, 'comisiones':comisiones, 'cuentas':cuentas, 'nomina':nomina}
		else:
			ctx={'nivel':nivel,'buscador':buscador, 'mensaje':mensaje, 'empleados':empleados, 'q':q, 'nEmpleados':nEmpleados}
		return render_to_response('contabilidad/empleadosReporte.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_nomina_empleados_estado_cta_agregar_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		q=request.GET.get('q','')
		pagina=request.GET.get('pagina','')
		empleados=None
		empleado=None
		cuentas=None
		nEmpleados=0
		cuentaForm=CuentaEmpleadoForm()
		mensaje='No Hay Resultados'
		guardado=None
		if q:
			try:
				empleado=Empleado.objects.get(id=q)
			except :
				empleados=Empleados(q)
		if empleados:
			nEmpleados=len(empleados)
			empleados = Paginador(empleados, 50, pagina)

		if 'actualizar' in request.POST:
			cuentaForm=CuentaEmpleadoForm(request.POST)
			if cuentaForm.is_valid():
				#try:
				today = datetime.now() #fecha actual
				d = today.strftime("%d%m%Y") # fecha con formato
				numero=CuentaEmpleado.objects.count()
				folio 		= '%s%s'%(numero+1,d)
				empleado 	= cuentaForm.cleaned_data['empleado']
				tipoCuenta 	= cuentaForm.cleaned_data['tipoCuenta']
				monto 		= cuentaForm.cleaned_data['monto']
				observacion = cuentaForm.cleaned_data['observacion']
				
				cuenta=CuentaEmpleado()
				cuenta.folio 		= folio
				cuenta.empleado 	= empleado
				cuenta.tipoCuenta 	= tipoCuenta
				cuenta.monto 		= monto
				cuenta.observacion = observacion
				cuenta.adeudo  = monto

				cuenta.save()
				guardado='Cuenta %s nueva Guardada correctamente.'%(cuenta)
				cuentaForm=CuentaEmpleadoForm()

		if empleado:
			cuentaForm=CuentaEmpleadoForm(initial={'empleado':empleado})
			cuentas=CuentaEmpleado.objects.filter(empleado=empleado)	
			mensaje=''
			ctx={'nivel':nivel, 'cuentaForm':cuentaForm, 'guardado':guardado, 'mensaje':mensaje, 'empleado':empleado, 'cuentas':cuentas}
		else:
			ctx={'nivel':nivel, 'cuentaForm':cuentaForm, 'mensaje':mensaje, 'empleados':empleados, 'q':q, 'nEmpleados':nEmpleados}
		return render_to_response('contabilidad/empleadosAddCuenta.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_nomina_empleados_estado_cta_abonar_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		ctx=nomina.empleadoAbonarCuenta(request, nivel)
		return render_to_response('contabilidad/empleadosAbonar.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_nomina_empleados_estado_cta_historial_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		q=request.GET.get('q','')
		pagina=request.GET.get('pagina','')
		cuentas=None
		cuenta=None
		historial=None
		nCuentas=0
		if q:
			try:
				cuenta=CuentaEmpleado.objects.get(id=q)
				historial=HistorialEmpleado.objects.filter(cuentaEmpleado=cuenta)
			except :
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
				cuentas=CuentaEmpleado.objects.filter(qset)
		else:
			cuentas=CuentaEmpleado.objects.all()
		if cuentas:
			nCuentas=len(cuentas)
			cuentas=Paginador(cuentas.order_by('-fxCreacion'),50,pagina)

		ctx={'nivel':nivel, 'cuentas':cuentas, 'cuenta':cuenta, 'historial':historial, 'nCuentas':nCuentas, 'q':q}
		return render_to_response('contabilidad/empleadosHistorialCuenta.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_nomina_usuarios_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		q=request.GET.get('q','')
		pagina=request.GET.get('pagina','')
		usuario=None
		usuarios=None
		nUsuarios=0
		mensaje='Sin Resultados'
		if q:
			try:
				usuario=Usuario.objects.get(id=q)
				mensaje=''
				q=''
			except :
				qset=(Q(empleado__nombre__icontains=q)|
				Q(empleado__aPaterno__icontains=q)|
				Q(empleado__aMaterno__icontains=q)|
				Q(empleado__direccion__icontains=q)|
				Q(empleado__telefono__icontains=q)|
				Q(empleado__puesto__puesto__icontains=q)|
				Q(empleado__area__area__icontains=q)|
				Q(user__username__icontains=q)|
				Q(permiso__descripcion__icontains=q))
				usuarios=Usuario.objects.filter(qset)
		else:
			usuarios=Usuario.objects.all()

		if usuarios:
			nUsuarios=len(usuarios)
			usuarios=Paginador(usuarios,50,pagina)
		ctx={'nivel':nivel, 'mensaje':mensaje, 'q':q, 'usuario':usuario, 'usuarios':usuarios, 'nUsuarios':nUsuarios}
		return render_to_response('contabilidad/usuariosReporte.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_nomina_nueva_nomina_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		admin=False
		if nivel== 0 or nivel == 1:
			admin=True
		eNom=request.GET.get('nominaId','')
		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')
		mensaje=''
		fNominas=None
		fNomina=None
		nominas=None
		_nomina=None
		listaEmNom=None
		eNomina=None
		buscador=None
		cuentasEmpl=None


		if 'gNomina' in request.POST:
			fNominas=NominaForm(request.POST)
			if fNominas.is_valid():
				today = datetime.now() #fecha actual
				dateFormat = today.strftime("%Y-%m-%d") # fecha con formato
				#try:
				_nomina=fNominas.save()
				_nomina.folio = 'Nom-%s'%(Folio(Nomina.objects.count(),None))
				_nomina.save()
				q=_nomina.id
				mensaje='Nomina %s guardada correctamente'%(_nomina)

		if 'gNominaAutomatica' in request.POST:
			fNominas=NominaForm(request.POST)
			if fNominas.is_valid():
				today = datetime.now() #fecha actual
				dateFormat = today.strftime("%Y-%m-%d") # fecha con formato
				#if Nomina.objects.filter(fxCreacion = dateFormat).exists():
				#	mensaje='No se puede realizar doble registro de Nomina el mismo dia'
				#else:
				if True:
					_nomina=fNominas.save()
					_nomina.folio = 'Nom-%s'%(Folio(Nomina.objects.count(),None))
					_nomina.save()
					empleados=Empleado.objects.filter(estadoEmpleado=True)
					for empleado in empleados:
						if not NominaEmpleado.objects.filter(empleado=empleado, nomina=_nomina).exists():
							noE=NominaEmpleado()
							noE.nomina=_nomina
							noE.empleado=empleado
							noE.salarioDia=empleado.salarioxDia
							noE.save()
					mensaje='Nomina %s guardada correctamente y generada para todos los empleados Activos'%(_nomina)
					q=_nomina.id
					

		if 'CerrarNomina' in request.POST:
			idNom = request.POST.get('nominaId','')
			mensaje = nomina.CerrarNomina(idNom)

		if 'guardaEmpleado' in request.POST:
			enom = request.POST.get('idEN','')
			q = request.POST.get('idN','')
			fNomina=NominaEmpleadoForm()
			try:
				_nomina=Nomina.objects.get(id=q)
			except:
				pass
			if _nomina:
				if not _nomina.cerrar:
					edicion=False
					try:
						eNomina = NominaEmpleado.objects.get(id=enom)
					except:
						pass
					
					if eNomina:
						if admin or eNomina.diasTrab == 0:
							fNomina = NominaEmpleadoForm(request.POST, instance=eNomina)
							if eNomina.pagado:
								mensaje='La nomina ya fue cobrada, no se puede realizar la edicion'
								fNomina=NominaEmpleadoForm()
								_nomina=None
						else:
							eNomina=None
							
					else:
						fNomina=NominaEmpleadoForm(request.POST)
					if fNomina.is_valid():
						empleado = fNomina.cleaned_data['empleado']
						if NominaEmpleado.objects.filter(nomina = _nomina, empleado = empleado).exists() and eNomina==None:
							mensaje='No se puede realizar doble registro en la misma nomina %s al mismo empleado %s'%(_nomina, empleado)
							empleado=None
						else:
							descuento = fNomina.cleaned_data['descuento']
							if not descuento:
								descuento=0
							dias = fNomina.cleaned_data['diasTrab']
							if not dias:
								dias=0
							salarioDia = empleado.salarioxDia
							bonoPuntualidad = fNomina.cleaned_data['bonoPuntualidad']
							if not bonoPuntualidad:
								bonoPuntualidad=0
							bonoVales = fNomina.cleaned_data['bonoVales']
							if not bonoVales:
								bonoVales = 0
							bonoProductividad = fNomina.cleaned_data['bonoProductividad']
							if not bonoProductividad:
								bonoProductividad = 0


							total=(dias*salarioDia)+bonoPuntualidad+bonoVales+bonoProductividad
							if descuento<total:
								#try:
								if not eNomina:
									eNomina=NominaEmpleado()
								eNomina.nomina=_nomina
								eNomina.empleado=empleado
								eNomina.descuento = descuento
								eNomina.diasTrab = dias
								eNomina.bonoPuntualidad = bonoPuntualidad
								eNomina.bonoVales = bonoVales
								eNomina.bonoProductividad = bonoProductividad
								eNomina.salarioDia=salarioDia
								eNomina.total="%.2f" % round(total-descuento,2)
								eNomina.save()
								mensaje = 'Registro %s Guardado Correctamente'%(eNomina)
								fNomina = NominaEmpleadoForm()
								empleado = None
								eNomina = None
							else:
								mensaje='El Descuento de %s supera el total Ganado de %s, No se realizo registro, verificar datos'%(descuento,total)
				else:
					mensaje = 'No se puede modificar de una Nomina ya Cerrada'
			else:
				mensaje='Error en la Nomina seleccionada'
				q=''

		try:
			_nomina=Nomina.objects.get(id=q)
			try:
				eNomina = NominaEmpleado.objects.get(id=eNom)
				fNomina = NominaEmpleadoForm(instance=eNomina)
				cuentasEmpl = r_conta.ReporteCuentaEmpleados(pagina, eNomina.empleado ,q, 'Cuentas del Empleado %s'%(eNomina.empleado), False)
			except:
				fNomina=NominaEmpleadoForm()
			listaEmNom=NominaEmpleado.objects.filter(nomina=_nomina).order_by('empleado')
			fNominas=None
		except:
			fNominas=NominaForm()
			buscador=Busqueda(q)
			if q:
				qset=(Q(folio__icontains=q)|
					Q(descripcion__icontains=q))
				nominas=Nomina.objects.filter(qset).order_by('-id')
			else:
				nominas=Nomina.objects.all().order_by('-id')[:20]

		if nominas:
			nominas = r_conta.ReporteNominas(pagina, q, 'Nominas Disponibles', request)

		if listaEmNom:
			listaEmNom=ReporteNominaEmpleado(listaEmNom, 'Empleados incluidos en la Nomina %s'%(_nomina), admin)



		ctx={'nivel':nivel, 'cuentasEmpl':cuentasEmpl, 'buscador':buscador, 'mensaje':mensaje, 'fNominas':fNominas, 'fNomina':fNomina, 'nominas':nominas, 'nomina':_nomina, 'listaEmNom':listaEmNom, 'eNomina':eNomina}
		return render_to_response('contabilidad/nuevaNomina.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_nomina_generar_nomina_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:

		ctx={'nivel':nivel}
		return render_to_response('contabilidad/nuevaNomina.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_nomina_nominas_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		admin=False
		if nivel== 0 or nivel == 1:
			admin=True
		#?nominaId=3&filtro=1
		info=''
		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')
		noE=request.GET.get('nominaId','')
		nominas=None
		nomi=None
		nominaE=None
		nominaEmls=None
		cuentas=None
		mensaje='No Hay Resultados'

		if request.method == "GET":
			exportar = request.GET.get('excel','')
			key =  request.GET.get('key','')
			if exportar == 'Exportar':
				#identificar nomina
				nominas = NominaEmpleado.objects.filter(nomina__id=key)
				folio =  Nomina.objects.get(id=key).folio
				header = ['Empleado','Salario por dia' ,'Dias Trabajados','Bono de Puntualidad','Bono Vales','Bono de Productividad','SubTotal','Descuento','Total','Fecha Pago','Observaciones','Pagado']
				takoyaky = []
				for x in nominas:
					pagado = "No"
					if x.pagado:
						pagado = "Si"
					fx = ""
					if x.fxPago:
						fx = x.fxPago
					SubTotal = x.diasTrab * x.salarioDia + x.bonoProductividad + x.bonoVales + x.bonoPuntualidad
					total = SubTotal - x.descuento
					takoyaky.append([ u"%s %s %s"%(x.empleado.nombre.title(),x.empleado.aPaterno.title(),x.empleado.aMaterno.title()),
						str(x.salarioDia),str(x.diasTrab),str(x.bonoPuntualidad),str(x.bonoVales),str(x.bonoProductividad),str(SubTotal),
						str(x.descuento),str(x.total),str(fx),x.observacion,pagado])

				
				
				try:
					return exportarNomina(folio,header,takoyaky)
				except :
					info = "No se genero su Archivo."
		if 'CerrarNomina' in request.POST:
			idNom = request.POST.get('nominaId','')
			mensaje = nomina.CerrarNomina(idNom)

		if 'pagar' in request.POST:
			idN=request.POST.get('idN','')
			try:
				nominaE=NominaEmpleado.objects.get(id=idN, pagado=False)
				if not nominaE.nomina.cerrar:
					nominaE.pagado=True
					nominaE.fxPago=datetime.now()
					nominaE.save()
					mensaje='Pago Registrado para la Nomina %s ,'%(nominaE)
					q=nominaE.nomina.id
					if nominaE.descuento:
						totalD=nominaE.descuento
						cuenAbonos=[]
						cuentas=CuentaEmpleado.objects.filter(empleado=nominaE.empleado).exclude(adeudo=0).order_by('adeudo')
						for cuenta in cuentas:
							abonar=request.POST.get('%s'%(cuenta.folio),'')
							if abonar:
								cuenAbonos.append(cuenta)
						if cuenAbonos:
							numero = len(cuenAbonos)
							descuento=totalD/numero
							residuo=0
							for cuent in cuenAbonos:
								hist=HistorialEmpleado()
								hist.cuentaEmpleado 	= cuent
								hist.observacion 	= 'Descuento de la Nomina %s'%(nominaE.nomina.folio)
								if cuent.adeudo <= (descuento+residuo):
									hist.descuento 		= cuent.adeudo
									residuo=descuento+residuo-cuent.adeudo
									cuent.adeudo=0
								else:
									hist.descuento 	= "%.2f" % round(descuento+residuo,2)
									residuo=0
									cuent.adeudo="%.2f" % round(cuent.adeudo-descuento-residuo,2)
								hist.save()
								cuent.save()
								mensaje='%s Se realizo el abono %s a la cuenta %s, '%(mensaje, hist,cuent)
							if residuo:
								nominaE.total="%.2f" % round(nominaE.total+residuo,2)
								nominaE.descuento = "%.2f" % round(nominaE.descuento-residuo,2)
								nominaE.save()
					nominaE=None
				else:
					mensaje='La Nomina que intenta Pagar ya esta Cerrada'
			except :
				mensaje='No se encontro La nomina que intenta pagar'
			

		try:
			nomi=Nomina.objects.get(id=q)
			q=''
			try:
				nominaE=NominaEmpleado.objects.get(id=noE)
				cuentas=CuentaEmpleado.objects.filter(empleado=nominaE.empleado).exclude(adeudo=0).order_by('adeudo')
			except :
				nominaEmls=NominaEmpleado.objects.filter(nomina=nomi).order_by('empleado')
				nominaEmls=ReporteNominaEmpleado(nominaEmls, 'Empleados en la Nomina %s'%(nomi), admin)
		except :
			nominas=r_conta.ReporteNominas(pagina, q,'321 Nominas Disponibles', request)
		


		buscador=Busqueda(q)

		ctx={'nivel':nivel, 'nominaE':nominaE, 'nominaEmls':nominaEmls, 'nominas':nominas, 'nomina':nomi, 'cuentas':cuentas, 'mensaje':mensaje, 'buscador':buscador, 'info':info}
		return render_to_response('contabilidad/reporteNomina.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_nomina_comisiones_actualizar_gama_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		ctx={'nivel':nivel}
		return render_to_response('contabilidad/index.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_nomina_comisiones_gama_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		alta=None
		media=None
		baja=None
		servicio=None
		mensaje=''
		try:
			alta=Gama.objects.get(gama='Alta')
		except:
			alta=Gama()
			alta.gama='Alta'
			alta.comision=0
			alta.save()
		try:
			media=Gama.objects.get(gama='Media')
		except:
			media=Gama()
			media.gama='Media'
			media.comision=0
			media.save()
		try:
			baja=Gama.objects.get(gama='Baja')
		except:
			baja=Gama()
			baja.gama='Baja'
			baja.comision=0
			baja.save()
		try:
			servicio=EstadoReparacion.objects.get(gama='Entregado a Cliente')
		except:
			servicio=EstadoReparacion()
			servicio.estado='Entregado a Cliente'
			servicio.comisionReparacion=0
			servicio.save()

		if 'actualizar' in request.POST:
			_alta=request.POST.get('alta','')
			#try:
			alta.comision=_alta
			alta.save()
			mensaje='%sGama Alta Actualizado Correctamente con: $%s, \n'%(mensaje,_alta)
			
			_media=request.POST.get('media','')
			#try:
			media.comision=_media
			media.save()
			mensaje='%sGama Media Actualizado Correctamente con: $%s, \n'%(mensaje,_media)

			_baja=request.POST.get('baja','')
			#try:
			baja.comision=_baja
			baja.save()
			mensaje='%sGama Baja Actualizado Correctamente con: $%s, \n'%(mensaje,_baja)
			
			_servicio=request.POST.get('servicio','')
			#try:
			servicio.comisionReparacion=_servicio
			servicio.save()
			mensaje='%sComision de Servicio Actualizado Correctamente con: $%s, \n'%(mensaje,_servicio)
			
		
		ctx={'nivel':nivel, 'mensaje':mensaje, 'alta':alta, 'media':media, 'baja':baja, 'servicio':servicio}
		return render_to_response('contabilidad/actualizarGamas.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')



@login_required(login_url='/')
def contabilidad_nomina_comisiones_actualizar_servicios_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		mensaje=''
		ctx={'nivel':nivel, 'mesaje':mensaje}
		return render_to_response('contabilidad/index.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_nomina_comisiones_reporte_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:

		faltantes=False
		mensaje=''
		total=0

		if 'faltantes' in request.POST:
			faltantes=True

		if 'generar' in request.POST:
			today = datetime.now()
			mes = int(today.strftime("%m"))#mes actual
			year = int(today.strftime("%Y")) #mes actual
			if mes == 1:
				mes=12
				year=year-1
			else:
				mes=mes-1
			if mes<10:
				mes='0%s'%(mes)

			mes='%s-%s'%(year,mes)
			#'''
			#today = datetime.now()
			#mes = today.strftime("%Y-%m") #mes actual

			qset=(Q(permiso__nivel=1)|
				Q(permiso__nivel=11)|
				Q(permiso__nivel=12))

			usuarios=Usuario.objects.filter(qset, empleado__estadoEmpleado=True)

			for usuario in usuarios:
				nomina.updComision(usuario.empleado,usuario.user, mes)
			
			mensaje='Comisiones Generadas para el mes %s'%(mes)

		if 'pagar' in request.POST:
			idC=request.POST.get('id','')
			#try:
			comi=Comision.objects.get(id=idC)
			comi.pagado=True
			today = datetime.now()
			comi.fxPago = datetime.now()
			comi.save()
			mensaje = 'Se ha Actualizado correctamente.'
			

		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')
		comisiones=''
		comision=None
		try:
			comision=Comision.objects.get(id=q)
			total=comision.comEquipoKit+comision.comEquipoTip+comision.comPlanes+comision.comServicios
			q=''
		except:
			comisiones=ReporteComisiones(pagina,q,'Reporte de Comisiones', faltantes)
		if not comisiones:
			mensaje='No hay resultados'
		
		buscador=Busqueda(q)

		ctx={'nivel':nivel, 'comisiones':comisiones, 'comision':comision, 'mensaje':mensaje, 'buscador':buscador, 'total':total}
		return render_to_response('contabilidad/comisiones.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_polizas_cuentas_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')
		fCuenta=CuentaForm()
		mensaje=''

		if 'guardar' in request.POST:
			fCuenta=CuentaForm(request.POST)
			if fCuenta.is_valid():
				cuenta=fCuenta.save()
				fCuenta=CuentaForm()
				mensaje='Cuenta %s, guardada correctamente'%(cuenta)
				cuenta=None

		cuentas=ReporteCuentas(pagina,q,'Cuentas Existentes')
		buscador=Busqueda(q)
		
		ctx={'nivel':nivel, 'fCuenta':fCuenta, 'mensaje':mensaje, 'cuentas':cuentas, 'buscador':buscador}
		return render_to_response('contabilidad/cuentasAdd.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')
		cta ="%s %s"%(self.cuenta, self.nocuenta)
		return cta


@login_required(login_url='/')
def contabilidad_caja_gastos_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		fGastos=GastosForm(initial={'fxGasto':datetime.now()})
		try:
			caja=Caja.objects.get(nombre='Caja Principal')
		except:
			caja=Caja()
			caja.nombre='Caja Principal'
			caja.saldo=0
			caja.save()
		mensaje=''
		saldo=caja.saldo

		if 'guardar' in request.POST:
			fGastos=GastosForm(request.POST)
			if fGastos.is_valid():
				monto=fGastos.cleaned_data['monto']
				if monto>saldo:
					mensaje='Saldo en caja insuficiente para el gasto, Transaccion no realizada.'
				else:
					#try:
					gasto=fGastos.save()
					caja.saldo="%.2f" % round(saldo-monto,2)
					caja.save()
					hi=HistorialCaja()
					hi.caja=caja
					hi.monto=gasto.monto
					hi.descripcion='Egreso por el Gasto %s'%(gasto)
					hi.abono=False
					hi.save()
					mensaje='Gasto %s registrado correctamente'%(gasto)
					fGastos=GastosForm()

		historial=ReporteGastos(None,None,'Ultimos 5 Gastos registrados',True)
		saldo=caja.saldo
		
		ctx={'nivel':nivel, 'fGastos':fGastos, 'saldo':saldo, 'mensaje':mensaje, 'historial':historial}
		return render_to_response('contabilidad/gastosAdd.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_caja_reporte_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')
		try:
			caja=Caja.objects.get(nombre='Caja Principal')
		except:
			caja=Caja()
			caja.nombre='Caja Principal'
			caja.saldo=0
			caja.save()
		saldo=caja.saldo
		buscador=Busqueda(q)
		historial=ReporteGastos(q,pagina,'Reporte de Gastos',False)
		
		ctx={'nivel':nivel, 'buscador':buscador, 'saldo':saldo, 'historial':historial}
		return render_to_response('contabilidad/gastosReporte.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_caja_ingresos_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		fIngreso=HistorialCajaForm()
		try:
			caja=Caja.objects.get(nombre='Caja Principal')
		except:
			caja=Caja()
			caja.nombre='Caja Principal'
			caja.saldo=0
			caja.save()
		mensaje=''
		saldo=caja.saldo
		historial = None

		if 'guardar' in request.POST:
			fIngreso=HistorialCajaForm(request.POST or None)
			if fIngreso.is_valid():
				#try:
				monto=fIngreso.cleaned_data['monto']
				des=fIngreso.cleaned_data['descripcion']

				ing=HistorialCaja()
				ing.caja=caja
				ing.monto=monto
				ing.descripcion=des
				ing.abono=True
				ing.save()
				
				caja.saldo="%.2f" % round(saldo+monto,2)
				caja.save()
				mensaje='Ingreso Guardado correctamente'
				fIngreso=HistorialCajaForm()
				
				historial = ReporteCaja(None,None,'Ultimos 5 Ingresos a la Caja registrados',True)

		saldo=caja.saldo
		
		ctx={'nivel':nivel, 'fIngreso':fIngreso, 'saldo':saldo, 'mensaje':mensaje , 'historial':historial
		}
		return render_to_response('contabilidad/cajaIngreso.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_polizas_ingresos_depositos_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		mensaje=''
		fDeposito=CuentaHistorialForm()
		q=request.GET.get('filtro','')
		if q:
			try:
				cuenta=Cuenta.objects.get(id=q)
				fDeposito=CuentaHistorialForm(initial={'cuenta':cuenta})
				mensaje = 'Deposito a la Cuenta: %s'%(cuenta)
			except :
				mensaje='Cuenta no encontrada'

		if 'depositar' in request.POST:
			fDeposito=CuentaHistorialForm(request.POST)
			if fDeposito.is_valid():
				#try:
				deposito=fDeposito.save()
				cuenta=deposito.cuenta
				cuenta.saldo="%.2f" % round(cuenta.saldo+deposito.cantidad,2)
				cuenta.save()

				deposito.deposito=True
				deposito.save()
				mensaje='Deposito %s realizado Correctamente'%(deposito)
				fDeposito=CuentaHistorialForm()

		depositos=ReporteCuentaHistorial(None, None, True, 'Ultimos 5 depositos realizados', True)
		
		ctx={'nivel':nivel, 'mensaje':mensaje, 'fDeposito':fDeposito, 'depositos':depositos}
		return render_to_response('contabilidad/depositoAdd.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_polizas_egresos_poliza_cheques_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		mensaje=''
		fPoliza=CuentaHistorialForm()
		q=request.GET.get('filtro','')
		if q:
			try:
				cuenta=Cuenta.objects.get(id=q)
				fPoliza=CuentaHistorialForm(initial={'cuenta':cuenta})
				mensaje = 'Registrar la Poliza a la Cuenta: %s'%(cuenta)
			except :
				mensaje='Cuenta no encontrada'

		if 'guardar' in request.POST:
			fPoliza=CuentaHistorialForm(request.POST)
			if fPoliza.is_valid():
				cuenta=fPoliza.cleaned_data['cuenta']
				cantidad=fPoliza.cleaned_data['cantidad']
				if cantidad > cuenta.saldo:
					mensaje='Saldo insuficiente en la cuenta %s, no se puede registrar la poliza con %s'%(cuenta, cantidad)
				else:
					#try:
					deposito = fPoliza.save()
					cuenta.saldo="%.2f" % round(cuenta.saldo-cantidad,2)
					cuenta.save()

					deposito.deposito = False
					deposito.save()
					mensaje = 'Poliza %s registrada Correctamente'%(deposito)
					fPoliza = CuentaHistorialForm()
					

		polizas=ReporteCuentaHistorial(None, None, False, 'Ultimas 5 Polizas registradas', True)
		
		ctx={'nivel':nivel, 'mensaje':mensaje, 'fPoliza':fPoliza, 'polizas':polizas}
		return render_to_response('contabilidad/polizasAdd.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_polizas_reporte_poliza_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		mensaje=''
		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')

		buscador=Busqueda(q)
		polizas=r_conta.ReporteCuentaHistoriales(pagina, None, False, q, 'Reporte de Polizas')
		
		ctx={'nivel':nivel, 'buscador':buscador, 'polizas':polizas}
		return render_to_response('contabilidad/polizasReporte.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_polizas_lineas_credito_proveedores_nuevo_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		q=request.GET.get('filtro','')
		fProveedor=ProveedorForm()
		mensaje=''
		provee=None
		if q:
			try:
				provee=Proveedor.objects.get(id=q)
				fProveedor=ProveedorForm(instance=provee)
			except :
				mensaje = 'Proveedor No Encontrado'

		if 'guardar' in request.POST:
			idP=request.POST.get('idP','')
			try:
				provee=Proveedor.objects.get(id=idP)
				fProveedor=ProveedorForm(request.POST, instance=provee)
			except :
				fProveedor=ProveedorForm(request.POST)
			if fProveedor.is_valid():
				txt=str(fProveedor.cleaned_data['rfc']).upper()
				re1='[A-Z]{3,4}-[0-9]{2}[0-1][0-9][0-3][0-9]-[A-Z0-9]?[A-Z0-9]?[0-9A-Z]?'
				rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
				m = rg.search(txt)
				if m:
					provee = fProveedor.save()
					fProveedor = ProveedorForm()
					mensaje = 'Proveedor %s, Agregado Correctamente'%(provee)
					provee=None
				else:
					mensaje = 'El RFC no tiene un formato correcto. '
		
		ctx={'nivel':nivel, 'fProveedor':fProveedor, 'mensaje':mensaje, 'provee':provee}
		return render_to_response('contabilidad/proveedorAdd.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_polizas_lineas_credito_proveedores_catalogo_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		mensaje=''
		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')

		buscador=Busqueda(q)
		proveedores=ReporteProveedores (pagina, q, 'Reporte de Proveedores')
		
		ctx={'nivel':nivel, 'buscador':buscador, 'proveedores':proveedores}
		return render_to_response('contabilidad/proveedoresReporte.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_polizas_lineas_credito_nueva_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		mensaje=''
		fLinea=LineaCreditoForm()

		if 'guardar' in request.POST:
			fLinea=LineaCreditoForm(request.POST)
			if fLinea.is_valid():
				#try:
				linea=fLinea.save()
				linea.deuda=linea.total
				linea.save()
				mensaje='Linea %s, Guardada Correctamente'%(linea)
				fLinea=LineaCreditoForm()
		
		ctx={'nivel':nivel, 'fLinea':fLinea, 'mensaje':mensaje}
		return render_to_response('contabilidad/lineaCreditoAdd.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_polizas_lineas_credito_abonos_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		fAbono=HistLCreditoForm()
		mensaje=''
		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')

		try:
			linea=LineaCredito.objects.get(id = q)
			fAbono=HistLCreditoForm(initial={'lineaCredito':linea})
		except :
			pass

		buscador=Busqueda(q)

		if 'guardar' in request.POST:
			fAbono=HistLCreditoForm(request.POST)
			if fAbono.is_valid():
				linea=fAbono.cleaned_data['lineaCredito']
				if not linea.pagado:
					#try:
					abono=fAbono.save()
					residuo=0
					linea=abono.lineaCredito
					if linea.deuda <= abono.abono:
						linea.deuda=0
						residuo= abono.abono - linea.deuda
					else:
						linea.deuda="%.2f" % round( linea.deuda - abono.abono ,2)
					if linea.deuda == 0:
						linea.pagado=True
						mensaje='Linea %s liquidada, '%(linea)
					linea.save()
					mensaje='%sAbono %s Realizado correctamente a la Cuenta de Credito %s'%(mensaje, abono, linea)
					if residuo:
						#abono.abono="%.2f" % round( abono.abono - residuo ,2)
						abono.abono="%.2f" % round( abono.abono ,2)
						abono.save()
						mensaje='%s, Con un Residuo de %s'%(mensaje, residuo)
					fAbono=HistLCreditoForm()
					
				else:
					mensaje='Linea %s saldada, no es nesesario abonar mas'%(linea)

		lineas=ReporteLineaCreditos(pagina, q, 'Lineas de Credito existentes')
		
		ctx={ 'nivel':nivel, 'fAbono':fAbono, 'mensaje':mensaje, 'lineas':lineas, 'buscador':buscador }
		return render_to_response('contabilidad/lineaCreditoAbono.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_polizas_lineas_credito_historial_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')
		lineas=None
		linea=None
		historial=None

		try:
			linea=LineaCredito.objects.get(id = q)
			historial=ReporteHistLCreditos(None, linea, 'Historial de Credito')
			q=''
		except :
			lineas=ReporteLineaCreditos(pagina, q, 'Lineas de Credito existentes')

		buscador=Busqueda(q)

		
		ctx={ 'nivel':nivel, 'linea':linea, 'historial':historial, 'lineas':lineas, 'buscador':buscador }
		return render_to_response('contabilidad/lineaCreditoHistorial.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

@login_required(login_url='/')
def contabilidad_facturacion_clientes_nuevo_view(request):
	nivel=Permiso(request.user,[0,1,2])
	#ClienteFacturacionForm
	if nivel != -1:
		q=request.GET.get('filtro','')
		fCliente=ClienteFacturacionForm()
		mensaje=''
		cliente=None
		if q:
			try:
				cliente=ClienteFacturacion.objects.get(id=q)
				fCliente=ClienteFacturacionForm({
				'rfc': cliente.rfc,
				'razonSocial': cliente.razonSocial,
				'direccion': cliente.direccion,
				'colonia': cliente.colonia.colonia,
				'ciudad': cliente.ciudad.ciudad,
				'cp': cliente.cp,
				'estado': cliente.estado.id})
			except :
				mensaje = 'Cliente No Encontrado'

		if 'guardar' in request.POST:
			idP=request.POST.get('idC','')
			upd = None
			try:
				cliente=ClienteFacturacion.objects.get(id=idP)
				upd = True
				fCliente=ClienteFacturacionForm(request.POST)
			except :
				fCliente=ClienteFacturacionForm(request.POST)
			if fCliente.is_valid():
				rfc 		= fCliente.cleaned_data['rfc']
				razonSocial = fCliente.cleaned_data['razonSocial']
				direccion 	= fCliente.cleaned_data['direccion']
				colonia 	= fCliente.cleaned_data['colonia']
				ciudad  	= fCliente.cleaned_data['ciudad']
				cp 			= fCliente.cleaned_data['cp']
				estado  	= fCliente.cleaned_data['estado']
				a=None
				z1 = agregarCiudades(colonia,ciudad,estado,cp)
				#try:
				re1='[A-Z]{3,4}-[0-9]{2}[0-1][0-9][0-3][0-9]-[A-Z0-9]?[A-Z0-9]?[0-9A-Z]?'
				txt=str(rfc).upper()
				rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
				m = rg.search(txt)
				if m:
					pass
				else:
					mensaje = "El formato de rfc, no es correcto."
					fCliente = ClienteFacturacionForm(request.POST)
					ctx={'nivel':nivel, 'fCliente':fCliente, 'mensaje':mensaje, 'cliente':cliente}
					return render_to_response('contabilidad/clienteAdd.html', ctx ,context_instance=RequestContext(request))
				if upd:
					a = ClienteFacturacion.objects.get(id=idP)
					a.rfc 		= (rfc).upper()
					a.razonSocial = (razonSocial).title()
					a.direccion 	= (direccion).title()
					a.colonia = Colonia.objects.get(id=z1[0])
					a.ciudad = Ciudad.objects.get(id=z1[1])
					a.cp 	= CP.objects.get(id=z1[2])
					a.estado = Estado.objects.get(id=estado)
					a.save()
					mensaje = 'Cliente %s, modificado Correctamente'%(a)
				else:
					a = ClienteFacturacion()
					a.rfc 		= (rfc).upper()
					a.razonSocial = (razonSocial).title()
					a.direccion 	= (direccion).title()
					a.colonia = Colonia.objects.get(id=z1[0])
					a.ciudad = Ciudad.objects.get(id=z1[1])
					a.cp 	= CP.objects.get(id=z1[2])
					a.estado = Estado.objects.get(id=estado)
					a.save()
					mensaje = 'Cliente %s, Agregado Correctamente'%(a)
				'''except :
																					transaction.rollback()
																					mensaje='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
																				else:
																					transaction.commit()'''				
				fCliente = ClienteFacturacionForm()
				cliente=None
		
		ctx={'nivel':nivel, 'fCliente':fCliente, 'mensaje':mensaje, 'cliente':cliente}
		return render_to_response('contabilidad/clienteAdd.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')
@login_required(login_url='/')
def contabilidad_facturacion_clientes_catalogo_view(request):
	nivel=Permiso(request.user,[0,1,2])
	#ReporteClienteFactuacion(pagina, filtro, tituloR)
	if nivel != -1:
		mensaje=''
		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')

		clientes=r_clien.ReporteClienteFacturaciones (pagina, q, 'Reporte de Clientes')
		
		ctx={'nivel':nivel, 'buscador':repor.Busqueda('Filtro para Facturas Realizadas',q), 'clientes':clientes}
		return render_to_response('contabilidad/clienteReporte.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#vistas agregadas para facturacion con el nuevo modelo 19/03/2014
@login_required(login_url='/')
def contabilidad_facturacion_facturas_reporte_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		ctx=facturacion.Facturas_reporte(nivel, request)
		return render_to_response('contabilidad/reporteFacturas.html', ctx , context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

@login_required(login_url='/')
def contabilidad_facturacion_facturas_agregar_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	#ClienteFacturacionForm
	if nivel != -1:
		ctx=facturacion.Facturas_agregar(nivel, request)
		return render_to_response('contabilidad/facturaAgregar.html', ctx , context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

@login_required(login_url='/')
def contabilidad_facturacion_equipo_facturada_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		ctx=facturacion.Equipos_facturados(nivel, request)
		return render_to_response('contabilidad/reporte_basico.html', ctx , context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

@login_required(login_url='/')
def contabilidad_facturacion_equipo_pendiente_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	#ClienteFacturacionForm
	if nivel != -1:
		ctx=facturacion.Equipos_pendientes(nivel, request)
		return render_to_response('contabilidad/reporte_basico.html', ctx , context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

@login_required(login_url='/')
def contabilidad_facturacion_express_facturada_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	#ClienteFacturacionForm
	if nivel != -1:
		ctx=facturacion.Express_facturados(nivel, request)
		return render_to_response('contabilidad/reporte_basico.html', ctx , context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

@login_required(login_url='/')
def contabilidad_facturacion_express_pendiente_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	#ClienteFacturacionForm
	if nivel != -1:
		ctx=facturacion.Express_pendientes(nivel, request)
		return render_to_response('contabilidad/reporte_basico.html', ctx , context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

@login_required(login_url='/')
def contabilidad_facturacion_ficha_facturada_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	#ClienteFacturacionForm
	if nivel != -1:
		ctx=facturacion.Fichas_facturadas(nivel, request)
		return render_to_response('contabilidad/reporte_basico.html', ctx , context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

@login_required(login_url='/')
def contabilidad_facturacion_ficha_pendiente_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	#ClienteFacturacionForm
	if nivel != -1:
		ctx=facturacion.Fichas_pendientes(nivel, request)
		return render_to_response('contabilidad/reporte_basico.html', ctx , context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

@login_required(login_url='/')
def contabilidad_facturacion_accesorio_facturada_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	#ClienteFacturacionForm
	if nivel != -1:
		ctx=facturacion.Accesorios_facturados(nivel, request)
		return render_to_response('contabilidad/reporte_basico.html', ctx , context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

@login_required(login_url='/')
def contabilidad_facturacion_accesorio_pendiente_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	#ClienteFacturacionForm
	if nivel != -1:
		ctx=facturacion.Accesorios_pendientes(nivel, request)
		return render_to_response('contabilidad/reporte_basico.html', ctx , context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')
#*******************************************************************


@login_required(login_url='/')
def contabilidad_cobranzas_sub_distribuidores_catalogo_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		mensaje=''
		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')

		buscador=Busqueda(q)
		subDis=ReporteSubDistribuidores (pagina, q, 'Catalogo de Sub Distribuidores')
		
		ctx={'nivel':nivel, 'buscador':buscador, 'subDis':subDis}
		return render_to_response('contabilidad/catalogoSubDis.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_cobranzas_sub_distribuidores_historial_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		mensaje=''
		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')
		creditos=None
		historial=None
		
		try:
			numero = Decimal(q)
			credito=Credito.objects.get(id = numero)
			historial=ReporteCreditoSubDistribuidoresHistorial(pagina, credito, 'Historial del Credito %s'%(credito))
			q=''
		except :
		#else:
			creditos=ReporteCreditoSubDistribuidores(pagina, q, 'Creditos Existentes')

		buscador=Busqueda(q)
		
		ctx={'nivel':nivel, 'buscador':buscador, 'creditos':creditos, 'historial':historial}
		return render_to_response('contabilidad/historialSubDis.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo probado
@login_required(login_url='/')
def contabilidad_sucursales_nueva_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		form = addSucursal()
		info = ""
		if request.method == "POST":
			form = addSucursal(request.POST or None)
			if form.is_valid():
				nombre 		= form.cleaned_data['nombre']
				direccion 	= form.cleaned_data['direccion']
				colonia 	= form.cleaned_data['colonia'] #buscar
				ciudad  	= form.cleaned_data['ciudad'] #buscar
				estado 		= form.cleaned_data['estado'] #id de estado
				cp 			= form.cleaned_data['cp'] #buscar
				zona		= form.cleaned_data['zona'] #id 
				zona2		= form.cleaned_data['zona2'] #id 
				encargado 	= form.cleaned_data['encargado'] #id empleado
				noCelOfi 	= form.cleaned_data['noCelOfi']
				tipo 		= form.cleaned_data['tipo'] #id 

				z1 =agregarCiudades(colonia,ciudad,estado,cp)
				myempleado = Empleado.objects.get(id=encargado)
				lazona = None
				if zona2:
					try:
						lazona = Zona.objects.get(zona__icontains=zona2)
					except Zona.DoesNotExist:
						z = Zona()
						z.zona = zona2.title()
						z.save()
						lazona = z
				else:
					lazona = Zona.objects.get(id=zona)
				try:
					noRepite = Sucursal.objects.get(nombre=nombre.title())#sucursal repetida
					info = "Lo sentimos, el nombre de la sucursal o evento, ya existe. Intente con otro nombre."
					form= addEvento(request.POST)
					ctx = {'form':form, 'info':info, 'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/nuevoEvento.html', ctx,context_instance=RequestContext(request))
				except :
					pass

				sucAnterior = None
				try:
					nousuario = Usuario.objects.get(empleado=myempleado,permiso=12)
					ocupado = Sucursal.objects.get(encargado=myempleado) # el empleado ya tiene una sucursal asignada como encargado
					sucAnterior = VendedorSucursal.objects.get(empleado=myempleado)
					if ocupado:
						info = "El empleado que quiere asignar como encargado, ya pertenece a una sucursal como tal. Intente con otro."
						form= addSucursal(request.POST)
						ctx = {'form':form, 'info':info, 'nivel':nivel}
						return render_to_response('contabilidad/nuevaSucursal.html', ctx,context_instance=RequestContext(request))
				except Usuario.DoesNotExist:
					info = "El empleado que quiere asignar como encargado, No tiene un usuario disponible para acceder al portal. Intente con otro o pida a un administrador agregar dicho empleado."
					form= addSucursal(request.POST)
					ctx = {'form':form, 'info':info, 'nivel':nivel}
					return render_to_response('contabilidad/nuevaSucursal.html', ctx,context_instance=RequestContext(request))					
				except Sucursal.DoesNotExist:
					pass
				except VendedorSucursal.DoesNotExist:
					pass

				if sucAnterior:
					sucAnterior.delete() #lo borramos de la sucursal anterior, para asignarlo a la nueva.

				#try:
				a = Sucursal()
				a.tipoSucursal = TipoSucursal.objects.get(id=tipo)
				a.nombre 	= nombre.title()
				a.encargado = myempleado
				if noCelOfi:
					a.noCelOfi 	= noCelOfi
				a.direccion = direccion.title()
				a.colonia = Colonia.objects.get(id=z1[0])
				a.cp 	  = CP.objects.get(id=z1[2])
				a.ciudad  = Ciudad.objects.get(id=z1[1])
				a.zona	= lazona
				a.estado  = EstadoSucursal.objects.get(estado='Activa')
				a.save()

				b = VendedorSucursal()
				b.empleado = myempleado
				b.sucursal = a
				b.save()#'''
				info ="Se agrego correctamente el Evento/Sucursal: "+str(a.id) +" - "+a.nombre+" Encargado: "+myempleado.nombre
				
				form = addSucursal()
				ctx = {'form':form, 'info':info, 'nivel':nivel}
				return render_to_response('contabilidad/nuevaSucursal.html', ctx,context_instance=RequestContext(request))	
			else:
				info = "No se registraron los datos, verifique sus datos."
				form= addSucursal(request.POST)
		
		ctx = {'form':form, 'info':info, 'nivel':nivel}
		return render_to_response('contabilidad/nuevaSucursal.html', ctx,context_instance=RequestContext(request))
		
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo probado
@login_required(login_url='/')
def contabilidad_sucursales_sucursales_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		query  = request.GET.get('q','')
		pag1=request.GET.get('pag','')
		info = ""
		eventos = Sucursal.objects.all().order_by('nombre')

		if query:
			qset=(Q(nombre__icontains=query) |
			 Q(encargado__nombre__icontains=query) | 
			 Q(encargado__aPaterno__icontains=query) | 
			 Q(encargado__aMaterno__icontains=query) | 
			 Q(encargado__curp__icontains=query) | 
			 Q(zona__zona__icontains=query) | 
			 Q(direccion__icontains=query))
			eventos = Sucursal.objects.filter(qset).order_by('nombre')
		
		
		paginator1 = Paginator(eventos, 50)

		pSucursales=None
		
		try:
			pSucursales = paginator1.page(pag1)
		except PageNotAnInteger:
			pSucursales= paginator1.page(1)
		except EmptyPage:
			pSucursales = paginator1.page(paginator1.num_pages)

		if request.method == "GET":
			if request.GET.get('upd'):
				s = request.GET.get('upd','')
				if s:
					x = Sucursal.objects.get(id= s)
					form = addSucursal({'nombre':x.nombre,'direccion':x.direccion,'colonia':x.colonia.colonia,
						'ciudad':x.ciudad.ciudad,'estado':x.estado.id,'cp':x.cp.cp,'zona':x.zona.id,
						'encargado':x.encargado.id,'noCelOfi':x.noCelOfi,'tipo':x.tipoSucursal.id})
					
					ctx={'key':x.id ,'form':form,'query':query,'nivel':nivel}
					return render_to_response('contabilidad/reporteSucursalesActualizar.html', ctx ,context_instance=RequestContext(request))
		
		if request.method == "POST":
			form = addSucursal(request.POST or None)
			key=request.POST.get('miki','')
			if form.is_valid():
				nombre 		= form.cleaned_data['nombre']
				direccion 	= form.cleaned_data['direccion']
				colonia 	= form.cleaned_data['colonia'] #buscar
				ciudad  	= form.cleaned_data['ciudad'] #buscar
				estado 		= form.cleaned_data['estado'] #id de estado
				cp 			= form.cleaned_data['cp'] #buscar
				zona		= form.cleaned_data['zona'] #id 
				zona2		= form.cleaned_data['zona2'] #id 
				encargado 	= form.cleaned_data['encargado'] #id empleado
				noCelOfi 	= form.cleaned_data['noCelOfi']
				tipo 		= form.cleaned_data['tipo'] #id 

				z1 =agregarCiudades(colonia,ciudad,estado,cp)
				myempleado = Empleado.objects.get(id=encargado)
				lazona = None
				if zona2:
					try:
						lazona = Zona.objects.get(zona__icontains=zona2)
					except Zona.DoesNotExist:
						z = Zona()
						z.zona = zona2.title()
						z.save()
						lazona = z
				else:
					lazona = Zona.objects.get(id=zona)
				
				sucAnterior = None
				try:
					nousuario = Usuario.objects.get(empleado=myempleado,permiso=12)
					ocupado = Sucursal.objects.get(encargado=myempleado,id=key) # el empleado ya tiene una sucursal asignada como encargado
					sucAnterior = VendedorSucursal.objects.get(empleado=myempleado)
					if ocupado:
						pass
					else:
						info = "El empleado que quiere asignar como encargado, ya pertenece a una sucursal como tal. Intente con otro."
						form= addSucursal(request.POST)
						ctx={'key':key,'form':form,'query':query,'nivel':nivel,'info':info }
						return render_to_response('contabilidad/reporteSucursalesActualizar.html', ctx ,context_instance=RequestContext(request))
				except Usuario.DoesNotExist:
					info = "El empleado que quiere asignar como encargado, No tiene un usuario disponible para acceder al portal. Intente con otro o pida a un administrador agregar dicho empleado."
					form= addSucursal(request.POST)
					ctx={'key':key,'form':form,'query':query,'nivel':nivel,'info':info }
					return render_to_response('contabilidad/reporteSucursalesActualizar.html', ctx ,context_instance=RequestContext(request))
				except Sucursal.DoesNotExist:
					pass
				except VendedorSucursal.DoesNotExist:
					pass

				if sucAnterior:
					sucAnterior.delete() #lo borramos de la sucursal anterior, para asignarlo a la nueva.
				#try:
				a = Sucursal(id=key)
				a.tipoSucursal = TipoSucursal.objects.get(id=tipo)
				a.nombre 	= nombre.title()
				a.encargado = myempleado
				if noCelOfi:
					a.noCelOfi 	= noCelOfi
				a.direccion = direccion.title()
				a.colonia = Colonia.objects.get(id=z1[0])
				a.cp 	  = CP.objects.get(id=z1[2])
				a.ciudad  = Ciudad.objects.get(id=z1[1])
				a.zona	= lazona
				a.estado  = EstadoSucursal.objects.get(estado='Activa')
				a.save()

				b = VendedorSucursal()
				b.empleado = myempleado
				b.sucursal = a
				b.save()
				info ="Se agrego correctamente el Evento: "+a.nombre+" Encargad@: "+myempleado.nombre
				ctx={'buscar':True,'Sucursal':pSucursales,'query':query,'nivel':nivel,'info':info}
				return render_to_response('contabilidad/reporteSucursalesActualizar.html', ctx ,context_instance=RequestContext(request))
				
			else:
				info = "No se registraron los datos, verifique sus datos."
				form= addSucursal(request.POST)
				ctx={'key':key,'form':form,'query':query,'nivel':nivel,'info':info }
				return render_to_response('contabilidad/reporteSucursalesActualizar.html', ctx ,context_instance=RequestContext(request))


		ctx={'buscar':True,'Sucursal':pSucursales,'query':query,'nivel':nivel,'info':info}
		return render_to_response('contabilidad/reporteSucursalesActualizar.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo probado copy duplicity
@login_required(login_url='/')
def contabilidad_sucursales_vendedores_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		query  = request.GET.get('q','')
		pag1=request.GET.get('pag','')

		vd = VendedorSucursal.objects.all().exclude(sucursal=mysucursal).order_by('sucursal').order_by('empleado')

		if query:
			qset=(Q(sucursal__nombre__icontains=query) |
			 Q(empleado__nombre__icontains=query) | 
			 Q(empleado__aPaterno__icontains=query) | 
			 Q(empleado__aMaterno__icontains=query) | 
			 Q(empleado__curp__icontains=query) | 
			 Q(sucursal__zona__zona__icontains=query))
			vd = VendedorSucursal.objects.filter(qset,empleado__estadoEmpleado=True).exclude(sucursal=mysucursal).order_by('sucursal').order_by('empleado')
		
		
		paginator1 = Paginator(vd, 50)

		pAm=None
		
		try:
			pAm = paginator1.page(pag1)
		except PageNotAnInteger:
			pAm= paginator1.page(1)
		except EmptyPage:
			pAm = paginator1.page(paginator1.num_pages)


		ctx={'empleado':pAm,'query':query,'nivel':nivel}
		return render_to_response('contabilidad/reporteVendedores.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo probado
@login_required(login_url='/')
def contabilidad_sucursales_papeletas_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		
		form = reporteFecha({'fxInicio':datetime.now().date()})
		info =""
		query = ""
		pagina = request.GET.get('pagina','')
		gaara=None
		gaara = Papeleta.objects.all().order_by('fxActivacion').reverse()

		if request.method == "POST":
			form = reporteFecha(request.POST)
			if form.is_valid():
				fxInicio 	= form.cleaned_data['fxInicio']
				fxFinal 	= form.cleaned_data['fxFinal']
				if fxFinal and fxInicio:
					gaara = Papeleta.objects.filter(fxActivacion__range=[fxInicio,fxFinal]).order_by('fxActivacion')
					query = "Entre fechas : "+str(fxInicio)+" y "+str(fxFinal)
				else:
					gaara = Papeleta.objects.filter(fxActivacion__icontains=fxInicio).order_by('fxActivacion')
					query = "De fecha : "+str(fxInicio)

				exportar = request.POST.get('excel','')
				if exportar == 'Exportar':
					result = []
					header = ['TELEFONO ASIGNADO','NOMBRE CLIENTE','CALLE','COLONIA','COD.POSTAL','CIUDAD','ESTADO','TEL.PARTICULAR','FECHA ACTIVACION','ESN/IMEI','DAT','PRODUCTO']
					for x in gaara:
						dateFormat = x.fxActivacion.strftime("%m/%d/%Y") # fecha con formato
						result.append([	x.telAsig,x.nombre.upper(),x.calle.upper(),x.colonia.colonia.upper(),
							str(x.codP.cp),	x.ciudad.ciudad.upper(),x.estado.estado.upper(),str(x.telPart),
							str(dateFormat),str(x.esnImei),x.dat.upper(),x.tipoProducto.tipo.upper()])
					try:
						return exportPapeletas(query,result,header)
					except :
						info = "No se genero su Archivo."
			else:
				info = "Seleccione un rango de fechas"
				form= reporteFecha(request.POST)
		
		paginator = Paginator(gaara, 50)
		p_Item=None
		try:
			p_Item = paginator.page(pagina)
		except PageNotAnInteger:
			p_Item = paginator.page(1)
		except EmptyPage:
			p_Item = paginator.page(paginator.num_pages)
		
		ctx = {'papeletas':p_Item,'form':form ,'query':query ,'info':info, 'nivel':nivel}
		return render_to_response('contabilidad/reportePapeletas.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#prev
@login_required(login_url='/')
def contabilidad_sucursales_arqueos_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		query=request.GET.get('q','')
		
		r_items=None
		vendedor = []
		info=''

		if query:
			qset=(Q(fxArqueo__icontains=query)|
				Q(sucursal__nombre__icontains=query)|
				Q(vendedor__username__icontains=query) |
				Q(auditor__nombre__icontains=query)|
				Q(auditor__aPaterno__icontains=query)|
				Q(auditor__aMaterno__icontains=query)|
				Q(auditor__curp__icontains=query))
			r_items=ArqueoCaja.objects.filter(qset)
		else:			
			r_items=ArqueoCaja.objects.all().order_by('-fxArqueo')
		for x in r_items:
			vendedor.append([ x, Usuario.objects.get(user=x.vendedor) ])

		ctx={'nivel':nivel, 'query':query, 'r_items':r_items,'vendedor':vendedor,'info':info}
		return render_to_response('contabilidad/reporteArqueo.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_sucursales_cortes_verificar_revisar_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		mensaje=''
		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')
		corte=None
		cortes=None
		veri=None

		if 'verificacion' in request.POST:
			idC=request.POST.get('idC','')
			try:
				corte=CorteVenta.objects.get(id=idC, revisado=False)
			except :
				pass
			if corte:
				veri=VerificacionForm(request.POST)
				if veri.is_valid():
					if True:#try:
						totalCorte = veri.cleaned_data['totalCorte']
						obser = veri.cleaned_data['observacion']
						if totalCorte >= corte.total:
							#si coincide
							corte.revisado=True
							if totalCorte>corte.total:
								exedente = totalCorte - corte.total
								if corte.observacion:
									corte.observacion='%s, El corte presento un exedente de $ %s'%(corte.observacion, exedente)
								else:
									corte.observacion='El corte presento un exedente de $ %s'%(exedente)
								if obser:
									corte.observacion='%s, %s'%(corte.observacion, obser)
							else:
								if corte.observacion:
									corte.observacion='%s, El corte verificado correctamente, sin diferencia'%(corte.observacion)
								else:
									corte.observacion='El corte verificado correctamente, sin diferencia'

						else:
							#no coincide
							faltante = corte.total - totalCorte
							dif = DiferenciasCorte()
							dif.corteVenta = corte
							dif.diferencia = "%.2f" % round(faltante,2)
							dif.revisaCorte = request.user
							dif.observacion = obser
							dif.save()

							#cuaenta deudora
							cuD=CuentaEmpleado()
							cuD.folio=Folio(CuentaEmpleado.objects.count(),None)
							cuD.empleado = corte.sucursal.encargado
							cuD.tipoCuenta = TipoCuenta.objects.get(tipo='Diferencia de Corte')
							cuD.monto = "%.2f" % round(faltante,2)
							cuD.observacion = 'Diferencia de Corte %s'%(corte)
							cuD.adeudo = "%.2f" % round(faltante,2)
							cuD.save()
							if corte.observacion:
								corte.observacion='%s, El corte presento un faltante de $ %s, se agrego a la cuenta %s'%(corte.observacion, faltante, cuD)
							else:
								corte.observacion='El corte presento un faltante de $ %s, se agrego a la cuenta %s'%(faltante, cuD)
						corte.revisado=True
						corte.save()
						mensaje='Corte verificado %s, observacion: %s'%(corte, corte.observacion)
						corte=None
			else:
				mensaje='Error en la seleccion del Corte de Venta'


		try:
			corte=CorteVenta.objects.get(id=q,revisado=False)
			veri=VerificacionForm()
			q=''
		except:
			if q:
				qset=(Q(folioCorteVta__icontains=q)|
					Q(sucursal__nombre__icontains=q)|
					Q(observacion__icontains=q))
				cortes=CorteVenta.objects.filter(qset)
			else:
				cortes=CorteVenta.objects.filter(revisado=False)
			veri=None
		if cortes:
			cortes = ReporteCortes(pagina, q, cortes, 'Cortes de Venta')

		buscador=Busqueda(q)

		
		ctx={'nivel':nivel, 'mensaje':mensaje, 'corte':corte, 'cortes':cortes, 'veri':veri, 'buscador':buscador}
		return render_to_response('contabilidad/verificarCorte.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_sucursales_cortes_verificar_diferencias_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		mensaje=''
		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')
		diferencias=None
		if q:
			qset=(Q(corteVenta__folioCorteVta__icontains=q)|
				Q(corteVenta__sucursal__nombre__icontains=q)|
				Q(corteVenta__observacion__icontains=q)|
				Q(revisaCorte__username__icontains=q)|
				Q(observacion__icontains=q))
			diferencias=DiferenciasCorte.objects.filter(qset)
		else:
			diferencias=DiferenciasCorte.objects.all()

		if diferencias:
			diferencias=ReporteDirefenciaCortes(pagina, q, diferencias, 'Reporte de Diferencias de Corte')
		else:
			mensaje='Sin Resultados'

		buscador=Busqueda(q)

		ctx={'nivel':nivel, 'mensaje':mensaje, 'diferencias':diferencias, 'buscador':buscador}
		return render_to_response('contabilidad/reporteDiferencias.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_sucursales_cortes_reporte_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		mensaje=''
		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')
		cortes=None


		if q:
			qset=(Q(folioCorteVta__icontains=q)|
				Q(sucursal__nombre__icontains=q)|
				Q(observacion__icontains=q))
			cortes=CorteVenta.objects.filter(qset)
		else:
			cortes=CorteVenta.objects.filter()

		if cortes:
			cortes = ReporteCortes(pagina, q, cortes, 'Reporte de Cortes de Venta')
		else:
			mensaje='sinresultados'

		buscador=Busqueda(q)
		
		ctx={'nivel':nivel, 'mensaje':mensaje, 'cortes':cortes, 'buscador':buscador}
		return render_to_response('contabilidad/reporteCortesVenta.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo probado
@login_required(login_url='/')
def contabilidad_sucursales_recargas_reporte_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		form = reporteFecha({'fxInicio':datetime.now().date()})
		form2 = conSucursal()
		info =""
		query = ""
		pagina = request.GET.get('pagina','')
		gaara=None
		gaara = TransferenciaSaldo.objects.filter(movimiento__tipoMovimiento__nombre="Transferencia").order_by('movimiento').reverse()

		if request.method == "POST":
			form = reporteFecha(request.POST)
			form2 = conSucursal(request.POST)
			if form.is_valid() and form2.is_valid():
				fxInicio 	= form.cleaned_data['fxInicio']
				fxFinal 	= form.cleaned_data['fxFinal']
				sucursal = form2.cleaned_data['sucursal'] #id sucursal 
				if fxFinal and fxInicio:
					gaara = TransferenciaSaldo.objects.filter(movimiento__tipoMovimiento__nombre="Transferencia",movimiento__fx_movimiento__range=[fxInicio,fxFinal], movimiento__sucursalDestino__id=sucursal)
					query = "Entre fechas : "+str(fxInicio)+" y "+str(fxFinal)
				else:
					gaara = TransferenciaSaldo.objects.filter(movimiento__tipoMovimiento__nombre="Transferencia",movimiento__fx_movimiento__icontains=fxInicio, movimiento__sucursalDestino__id=sucursal)
					query = "De fecha : "+str(fxInicio)

			else:
				info = "Seleccione un rango de fechas"
				form= reporteFecha(request.POST)
				form2 = conSucursal(request.POST)
		
		paginator = Paginator(gaara, 50)
		p_Item=None
		try:
			p_Item = paginator.page(pagina)
		except PageNotAnInteger:
			p_Item = paginator.page(1)
		except EmptyPage:
			p_Item = paginator.page(paginator.num_pages)
		
		ctx = {'depositos':p_Item,'form':form,'form2':form2,'query':query ,'info':info, 'nivel':nivel}
		return render_to_response('contabilidad/reporteRecargas.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_sucursales_auditorias_nueva_view(request):
	nivel=Permiso(request.user,[0,1,2,3,4])
	if nivel != -1:
		mensaje=''
		fInventario=InventarioForm()


		if 'guardar' in request.POST:
			fInventario=InventarioForm(request.POST)
			mensaje = auditoria.nuevaGuardar(fInventario, request.user)
			if not mensaje:
				inv=Inventario.objects.all().order_by('-id')[0]
				if inv:
					return HttpResponseRedirect('/contabilidad/sucursales/auditorias/activas/?filtro=%s'%(inv.id))

		ctx={'nivel':nivel, 'fInventario':fInventario, 'mensaje':mensaje, 'Titulo':'Registro de una auditoria'}
		return render_to_response('contabilidad/auditoriaAdd.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

@login_required(login_url='/')
def contabilidad_sucursales_auditorias_activas_view(request):
	nivel=Permiso(request.user,[0,1,2,3,4])
	if nivel != -1:
		mensaje=''
		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')
		asignados=None
		desplEq = None
		desplEx = None
		desplAc = None
		desplFi = None
		empleados= None
		try:
			inventario=Inventario.objects.get(id=q)
			inventarios=None
		except :
			inventario=None
			inventarios=r_audit.ReporteInventariosMinimo(pagina, q, 'Auditorias Activas', False)


		formAsig=InventarioAuditoresForm()
		
		if 'asignar' in request.POST:
			idInv=request.POST.get('inventario','')
			formAsig=InventarioAuditoresForm(request.POST)
			try:
				inventario=Inventario.objects.get(id=idInv)
				mensaje=auditoria.asignarAuditor(formAsig)
				if not mensaje:
					mensaje= 'Asignacion realizada con exito'
					formAsig=InventarioAuditoresForm()
			except :
				inventario=None
				mensaje='Error en el servidor, la asignacio no se realizo'

		if 'cancelar' in request.POST:
			idInv=request.POST.get('idInv','')
			confir=request.POST.get('confir','')
			try:
				inventario=Inventario.objects.get(id=idInv)
				if confir:
					mensaje=auditoria.cancelarAuditoria(inventario, request.user)
					if not mensaje:
						mensaje= 'Cancelacion realizada con exito'
			except :
				inventario=None
				mensaje='Error en el servidor, la cancelacion no se realizo'
			

		if 'terminar' in request.POST:
			idInv=request.POST.get('idInv','')
			confir=request.POST.get('confir','')
			try:
			#if True:
				inventario=Inventario.objects.get(id=idInv)
				if confir:
					mensaje=auditoria.terminarAuditoria(inventario, request.user)
					if not mensaje:
						mensaje= 'Auditoria terminada con exito'
						diferencia=Decimal(inventario.difEquipo)+Decimal(inventario.difExpres)+Decimal(inventario.difFicha)+Decimal(inventario.difAccesorio)+Decimal(inventario.difOtros)+Decimal(inventario.difStreet)
						if not diferencia:
							inventario.cerrado=True
							obser=inventario.observaciones
							if obser:
								obser ="%s. "%(obser)
							obser='%sTambien fue Cerrada, no hubo diferencias al finalizar'%(obser)
							inventario.observaciones=obser
							inventario.save()
							mensaje= 'Auditoria terminada y Cerrada, no hubo diferencias al finalizar'
			except :
				inventario=None
				mensaje='Error en el servidor, la terminacion no se realizo'

		if 'cerrar' in request.POST:
			idInv=request.POST.get('idInv','')
			confir=request.POST.get('confir','')
			try:
				inventario=Inventario.objects.get(id=idInv)
				if confir:
					mensaje=auditoria.cerrarAuditoria(inventario, request)
			except :
				inventario=None
				mensaje='Error en el servidor, el cierre no se realizo'

		if inventario:
			asignados=r_audit.ReporteInventarioAuditores(inventario, 'Auditores asignados a %s'%(inventario))
			if inventario. terminada:
				desplEq=InvEquipo.objects.filter(inventario=inventario)
				desplEx=InvExpres.objects.filter(inventario=inventario)
				desplAc=InvAccesorio.objects.filter(inventario=inventario)
				desplFi=InvFicha.objects.filter(inventario=inventario)
				empleados=VendedorSucursal.objects.filter(sucursal=inventario.sucursal, empleado__estadoEmpleado=True)
		
		ctx={'nivel':nivel, 'mensaje':mensaje, 'buscador':repor.Busqueda('Auditorias Activas',q), 'titulo':'Auditorias Activas', 
		'inventario':inventario, 'inventarios':inventarios, 'asignados':asignados, 'formAsig':formAsig,
		'desplEq':desplEq,  'desplEx':desplEx, 'desplAc':desplAc, 'desplFi':desplFi, 'empleados':empleados}
		return render_to_response('contabilidad/auditoriaActivas.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def contabilidad_sucursales_auditorias_determinar_equipo_view(request):
	nivel=Permiso(request.user,[0,1,2,3,4])
	
	if nivel != -1:
		mensaje=''
		listas=None
		titulo='Determinar Equipos'
		q=''
		empleado=comunes.empleado(request.user)
		if  'seleccion' in request.POST:
				audi_id=request.POST.get('audi_id','')
				mensaje=auditoria.seleccionAuditor(audi_id, empleado)

		try:
			inventario=InventarioAuditores.objects.get(auditor=empleado,
			 inventario__terminada=False, turno=True)
			inventario=inventario.inventario
			inventariosA=None
		except:
			inventario=None
			inventariosA=InventarioAuditores.objects.filter(auditor=empleado,
			 inventario__terminada=False)

		if inventariosA:
			titulo='Tiene varias Auditorias asignadas, Seleccione una para comenzar'
		elif inventario:
			q=request.GET.get('filtro','')

			if  'revisar' in request.POST:
				q=request.POST.get('filtro','')
				if inventario:
					#try:
					qset=(Q(equipo__imei__icontains=q)|
					Q(equipo__icc__icontains=q)|
					Q(equipo__detallesEquipo__marca__marca__icontains=q)|
					Q(equipo__detallesEquipo__modelo__icontains=q))
					listas=InvEquipo.objects.filter(qset, inventario=inventario, revisado=False)
					for item in listas:
						exis=request.POST.get('CBox%s'%(item.id),'')
						comen=request.POST.get('TArea%s'%(item.id),'')
						if exis:
							item.existe = True
							item.observacion = comen
							item.revisado = True
							item.fxRevision = datetime.now()
							item.save()

			if q:
				qset=(Q(equipo__imei__icontains=q)|
				Q(equipo__icc__icontains=q)|
				Q(equipo__detallesEquipo__marca__marca__icontains=q)|
				Q(equipo__detallesEquipo__modelo__icontains=q))
				listas=InvEquipo.objects.filter(qset, inventario=inventario, revisado=False)
				if not listas:
					mensaje='Sin Resultados para esta busqueda: %s, limpie el filtro'%(q)
			else:
				listas=InvEquipo.objects.filter(inventario=inventario, revisado=False)
				if not listas:
					mensaje='No hay mas productos en esta seccion por verificar'

		else:
			titulo='No tiene Auditorias asignada en este momento'

		buscador=Busqueda(q)
		ctx={'nivel':nivel, 'mensaje':mensaje, 'q':q, 'buscador':buscador, 'listas':listas,
		'titulo':titulo, 'inventarios':inventariosA}
		return render_to_response('contabilidad/determinarEquipo.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')



@login_required(login_url='/')
def contabilidad_sucursales_auditorias_determinar_accesorio_view(request):
	nivel=Permiso(request.user,[0,1,2,3,4])
	if nivel != -1:
		mensaje=''
		listas=None
		titulo='Determinar Accesorios'
		q=''
		empleado=comunes.empleado(request.user)
		if  'seleccion' in request.POST:
				audi_id=request.POST.get('audi_id','')
				mensaje=auditoria.seleccionAuditor(audi_id, empleado)

		try:
			inventario=InventarioAuditores.objects.get(auditor=empleado,
			 inventario__terminada=False, turno=True)
			inventario=inventario.inventario
			inventariosA=None
		except:
			inventario=None
			inventariosA=InventarioAuditores.objects.filter(auditor=empleado,
			 inventario__terminada=False)

		if inventariosA:
			titulo='Tiene varias Auditorias asignadas, Seleccione una para comenzar'
		elif inventario:
			q=request.GET.get('filtro','')

			if  'revisar' in request.POST:
				q=request.POST.get('filtro','')
				if inventario:
					#try:
					qset=(Q(accesorio__codigoBarras__icontains=q)|
					Q(accesorio__detallesAccesorio__marca__marca__icontains=q)|
					Q(accesorio__detallesAccesorio__descripcion__icontains=q))
					listas=InvAccesorio.objects.filter(qset, inventario=inventario, revisado=False)
					for item in listas:
						exis=request.POST.get('CBox%s'%(item.id),'')
						comen=request.POST.get('TArea%s'%(item.id),'')
						if exis:
							item.existe = True
							item.observacion = comen
							item.revisado = True
							item.fxRevision = datetime.now()
							item.save()

			if q:
				qset=(Q(accesorio__codigoBarras__icontains=q)|
				Q(accesorio__detallesAccesorio__marca__marca__icontains=q)|
				Q(accesorio__detallesAccesorio__descripcion__icontains=q))
				listas=InvAccesorio.objects.filter(qset, inventario=inventario, revisado=False)
				if not listas:
					mensaje='Sin Resultados para esta busqueda: %s, limpie el filtro'%(q)
			else:
				listas=InvAccesorio.objects.filter(inventario=inventario, revisado=False)
				if not listas:
					mensaje='No hay mas productos en esta seccion por verificar'

		else:
			titulo='No tiene Auditorias asignada en este momento'

		buscador=Busqueda(q)
		ctx={'nivel':nivel, 'mensaje':mensaje, 'q':q, 'buscador':buscador, 'listas':listas,
		'titulo':titulo, 'inventarios':inventariosA}
		return render_to_response('contabilidad/determinarAccesorios.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')



@login_required(login_url='/')
def contabilidad_sucursales_auditorias_determinar_expres_view(request):
	nivel=Permiso(request.user,[0,1,2,3,4])
	if nivel != -1:
		mensaje=''
		listas=None
		titulo='Determinar Expres'
		q=''
		empleado=comunes.empleado(request.user)
		if  'seleccion' in request.POST:
				audi_id=request.POST.get('audi_id','')
				mensaje=auditoria.seleccionAuditor(audi_id, empleado)

		try:
			inventario=InventarioAuditores.objects.get(auditor=empleado,
			 inventario__terminada=False, turno=True)
			inventario=inventario.inventario
			inventariosA=None
		except:
			inventario=None
			inventariosA=InventarioAuditores.objects.filter(auditor=empleado,
			 inventario__terminada=False)

		if inventariosA:
			titulo='Tiene varias Auditorias asignadas, Seleccione una para comenzar'
		elif inventario:
			q=request.GET.get('filtro','')

			if  'revisar' in request.POST:
				q=request.POST.get('filtro','')
				if inventario:
					#try:
					qset=(Q(expres__icc__icontains=q)|
					Q(expres__noCell__icontains=q))
					listas=InvExpres.objects.filter(qset, inventario=inventario, revisado=False)
					for item in listas:
						exis=request.POST.get('CBox%s'%(item.id),'')
						comen=request.POST.get('TArea%s'%(item.id),'')
						if exis:
							item.existe = True
							item.observacion = comen
							item.revisado = True
							item.fxRevision = datetime.now()
							item.save()
					

			if q:
				qset=(Q(expres__icc__icontains=q)|
				Q(expres__noCell__icontains=q))
				listas=InvExpres.objects.filter(qset, inventario=inventario, revisado=False)
				if not listas:
					mensaje='Sin Resultados para esta busqueda: %s, limpie el filtro'%(q)
			else:
				listas=InvExpres.objects.filter(inventario=inventario, revisado=False)
				if not listas:
					mensaje='No hay mas productos en esta seccion por verificar'

		else:
			titulo='No tiene Auditorias asignada en este momento'

		buscador=Busqueda(q)
		ctx={'nivel':nivel, 'mensaje':mensaje, 'q':q, 'buscador':buscador, 'listas':listas,
		'titulo':titulo, 'inventarios':inventariosA}
		return render_to_response('contabilidad/determinarExpres.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')



@login_required(login_url='/')
def contabilidad_sucursales_auditorias_determinar_ficha_view(request):
	nivel=Permiso(request.user,[0,1,2,3,4])
	if nivel != -1:
		mensaje=''
		listas=None
		titulo='Determinar Fichas'
		q=''
		empleado=comunes.empleado(request.user)
		if  'seleccion' in request.POST:
				audi_id=request.POST.get('audi_id','')
				mensaje=auditoria.seleccionAuditor(audi_id, empleado)

		try:
			inventario=InventarioAuditores.objects.get(auditor=empleado,
			 inventario__terminada=False, turno=True)
			inventario=inventario.inventario
			inventariosA=None
		except:
			inventario=None
			inventariosA=InventarioAuditores.objects.filter(auditor=empleado,
			 inventario__terminada=False)

		if inventariosA:
			titulo='Tiene varias Auditorias asignadas, Seleccione una para comenzar'
		elif inventario:
			q=request.GET.get('filtro','')

			if  'revisar' in request.POST:
				q=request.POST.get('filtro','')
				if inventario:
					#try:
					qset=(Q(ficha__folio__icontains=q)|
					Q(ficha__nominacion__nominacion__icontains=q))
					listas=InvFicha.objects.filter(qset, inventario=inventario, revisado=False)
					for item in listas:
						exis=request.POST.get('CBox%s'%(item.id),'')
						comen=request.POST.get('TArea%s'%(item.id),'')
						if exis:
							item.existe = True
							item.observacion = comen
							item.revisado = True
							item.fxRevision = datetime.now()
							item.save()
					

			if q:
				qset=(Q(ficha__folio__icontains=q)|
				Q(ficha__nominacion__nominacion__icontains=q))
				listas=InvFicha.objects.filter(qset, inventario=inventario, revisado=False)
				if not listas:
					mensaje='Sin Resultados para esta busqueda: %s, limpie el filtro'%(q)
			else:
				listas=InvFicha.objects.filter(inventario=inventario, revisado=False)
				if not listas:
					mensaje='No hay mas productos en esta seccion por verificar'

		else:
			titulo='No tiene Auditorias asignada en este momento'

		buscador=Busqueda(q)
		ctx={'nivel':nivel, 'mensaje':mensaje, 'q':q, 'buscador':buscador, 'listas':listas,
		'titulo':titulo, 'inventarios':inventariosA}
		return render_to_response('contabilidad/determinarFichas.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

@login_required(login_url='/')
def contabilidad_sucursales_auditorias_determinar_estado_view(request):
	nivel=Permiso(request.user,[0,1,2,3,4])
	if nivel != -1:
		mensaje=''
		listas=None
		titulo=''
		asignados=None
		desplEq = None
		desplEx = None
		desplAc = None
		desplFi = None
		empleado=comunes.empleado(request.user)
		if  'seleccion' in request.POST:
				audi_id=request.POST.get('audi_id','')
				mensaje=auditoria.seleccionAuditor(audi_id, empleado)

		try:
			inventario=InventarioAuditores.objects.get(auditor=empleado,
			 inventario__terminada=False, turno=True)
			inventario=inventario.inventario
			inventariosA=None
		except:
			inventario=None
			inventariosA=InventarioAuditores.objects.filter(auditor=empleado,
			 inventario__terminada=False)

		if inventariosA:
			titulo='Tiene varias Auditorias asignadas, Seleccione una para comenzar'
		elif inventario:
			titulo='Estado actual de la Auditoria %s'%(inventario)
			desplEq=InvEquipo.objects.filter(inventario=inventario)
			desplEx=InvExpres.objects.filter(inventario=inventario)
			desplAc=InvAccesorio.objects.filter(inventario=inventario)
			desplFi=InvFicha.objects.filter(inventario=inventario)
		else:
			titulo='No tiene Auditorias asignada en este momento'

		ctx={'nivel':nivel, 'mensaje':mensaje, 'inventarios':inventariosA, 
		'titulo':titulo, 'desplEq':desplEq, 'desplEx':desplEx, 'desplAc':desplAc, 
		'desplFi':desplFi}
		return render_to_response('contabilidad/determinarEstado.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#reporte listo
@login_required(login_url='/')
def contabilidad_sucursales_auditorias_reportes_view(request):
	nivel=Permiso(request.user,[0,1,2,3,4])
	if nivel != -1:
		mensaje=''
		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')
		inventarios = None
		inventario = None
		desplEq = None
		desplEx = None
		desplAc = None
		desplFi = None
		try:
			inventario=Inventario.objects.get(id=q)
			desplEq=InvEquipo.objects.filter(inventario=inventario)
			desplEx=InvExpres.objects.filter(inventario=inventario)
			desplAc=InvAccesorio.objects.filter(inventario=inventario)
			desplFi=InvFicha.objects.filter(inventario=inventario)
			q=''
		except :
			if q:
				qset=(Q(sucursal__nombre__icontains=q)|
				Q(folio__icontains=q)|
				Q(fxInicio__icontains=q)|
				Q(fxFinal__icontains=q))
				inventarios = Inventario.objects.filter(qset, cerrado=True)
			else:
				inventarios = Inventario.objects.filter(cerrado=True)

		buscador=Busqueda(q)

		if request.method == "POST":
			exportar = request.POST.get('excel','')
			expMov =  request.POST.get('expMov','')
			if exportar == 'Exportar':
				inv = Inventario.objects.get(folio= expMov)
				equipos = InvEquipo.objects.filter(inventario=inv)
				expres = InvExpres.objects.filter(inventario=inv)
				accesorios = InvAccesorio.objects.filter(inventario=inv)
				fichas = InvFicha.objects.filter(inventario=inv)

				mili = listarInventario(equipos,expres,accesorios,fichas)
				try:
					return exportInventario(mili[0],mili[1], mili[2], mili[3] ,inv.sucursal.nombre.title())
				except :
					info = "No se genero su Archivo."

		
		ctx={'nivel':nivel, 'buscador':buscador, 'mensaje':mensaje, 'inventarios':inventarios, 'inventario':inventario, 'desplEq':desplEq, 'desplEx':desplEx, 'desplAc':desplAc, 'desplFi':desplFi}
		return render_to_response('contabilidad/auditoriaReporte.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

	
#listo probado
@login_required(login_url='/')
def contabilidad_reportes_compras_facturas_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		b_folio=request.GET.get('q','')
		b_factura=None
		b_facturas=None
		b_equipos=None
		b_express=None
		b_accesorios=None
		b_fichas=None
		b_recargas=None
		fichas=[]
		if b_folio:
			#obtencion de la factura
			try:
				b_factura=Factura.objects.get(folio=b_folio)
				b_equipos=Equipo.objects.filter(factura=b_factura)
				b_express=Expres.objects.filter(factura=b_factura)
				b_accesorios=Accesorio.objects.filter(factura=b_factura)
				b_fichas=Ficha.objects.filter(factura=b_factura).order_by('folio')
				b_recargas=TiempoAire.objects.filter(factura=b_factura)
				fichas=SerieFichas(b_fichas)
			except :
				b_facturas=ListaFacturas(b_folio)
		else:
			b_facturas=Factura.objects.all().distinct()

		ctx = {'nivel':nivel,'b_folio':b_folio ,'b_factura':b_factura, 'b_facturas':b_facturas, 'b_equipos':b_equipos, 'b_express':b_express, 'b_accesorios':b_accesorios, 'fichas':fichas, 'b_recargas':b_recargas}
		return render_to_response('contabilidad/almacenReporte.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo probado
@login_required(login_url='/')
def contabilidad_reportes_compras_costos_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		query  = request.GET.get('item','')
		pag1 = request.GET.get('pagEq','')
		pag2 = request.GET.get('pagEx','')
		pag3 = request.GET.get('pagC','')
		pag4 = request.GET.get('pagF','')
		pag5 = request.GET.get('pagT','')
		
		almEquipo = AlmacenEquipo.objects.filter(estado=True).exclude(equipo__estatus__estatus='Vendido').order_by('equipo')
		almExpress = AlmacenExpres.objects.filter(estado=True).exclude(expres__estatus__estatus='Vendido').order_by('expres')
		almAccs = AlmacenAccesorio.objects.filter(estado=True).exclude(accesorio__estatusAccesorio__estatus='Vendido').order_by('accesorio')
		almFic = AlmacenFicha.objects.filter(estado=True).exclude(ficha__estatusFicha__estatus='Vendido').order_by('ficha')
		almSaldo = SaldoSucursal.objects.all()
		nineros = []
		if query:
			qsetE=(Q(equipo__detallesEquipo__marca__marca__icontains=query) |
				Q(equipo__detallesEquipo__modelo__icontains=query) |
				Q(equipo__imei__icontains=query) |
				Q(equipo__icc__icontains=query)|
				Q(sucursal__nombre__icontains=query))
			qsetX=(Q(expres__icc__icontains=query)|Q(sucursal__nombre__icontains=query))
			qsetA=(Q(accesorio__codigoBarras__icontains=query)| 
				Q(accesorio__detallesAccesorio__marca__marca__icontains=query)|
				Q(accesorio__detallesAccesorio__seccion__seccion__icontains=query)| 
				Q(accesorio__detallesAccesorio__descripcion__icontains=query)|
				Q(sucursal__nombre__icontains=query))
			qsetF=(Q(ficha__folio__icontains=query)|
				Q(ficha__nominacion__nominacion__icontains=query)|
				Q(sucursal__nombre__icontains=query))

			almEquipo = AlmacenEquipo.objects.filter(qsetE,estado=True).exclude(equipo__estatus__estatus='Vendido').order_by('equipo')
			almExpress = AlmacenExpres.objects.filter(qsetX,estado=True).exclude(expres__estatus__estatus='Vendido').order_by('expres')
			almAccs = AlmacenAccesorio.objects.filter(qsetA,estado=True).exclude(accesorio__estatusAccesorio__estatus='Vendido').order_by('accesorio')
			almFic = AlmacenFicha.objects.filter(qsetF,estado=True).exclude(ficha__estatusFicha__estatus='Vendido').order_by('ficha')
			almSaldo = SaldoSucursal.objects.filter(sucursal__nombre__icontains=query).order_by('sucursal')
			suc = Sucursal.objects.filter(nombre__icontains=query)
			sEq = 0
			sEx = 0
			sAc = 0
			sFi = 0
			nEq = 0
			nEx = 0
			nAc = 0
			nFi = 0
			for x in suc:
				for j in almEquipo:
					if x.id == j.sucursal.id:
						nEq = nEq + 1
						sEq = sEq + j.equipo.importeFactura
				for j in almExpress:
					if x.id == j.sucursal.id:
						nEx = nEx + 1
						sEx = sEx + j.expres.importeFactura
				for j in almAccs:
					if x.id == j.sucursal.id:
						nAc = nAc + 1
						sAc = sAc + j.accesorio.precioFact
				for j in almFic:
					if x.id == j.sucursal.id:
						nFi = nFi + 1
						sFi = sFi + j.ficha.precioFac
				total = sEq + sEx + sAc + sFi
				nineros.append([x.nombre.title(),nEq,sEq,nEx,sEx,nAc,sAc,nFi,sFi,total])
				#-------------------0-------------1---2---3---4---5---6---7---8---9--				

		
		paginator1 = Paginator(almEquipo, 50)
		paginator2 = Paginator(almExpress, 50)
		paginator3 = Paginator(almAccs, 50)
		paginator4 = Paginator(almFic, 50)
		paginator5 = Paginator(almSaldo, 50)
		pEq = None
		pEx = None
		pAc = None
		pFi = None
		pSa = None
		try:
			pEq = paginator1.page(pag1)
		except PageNotAnInteger:
			pEq= paginator1.page(1)
		except EmptyPage:
			pEq = paginator1.page(paginator1.num_pages)
				
		try:
			pEx = paginator2.page(pag2)
		except PageNotAnInteger:
			pEx= paginator2.page(1)
		except EmptyPage:
			pEx = paginator2.page(paginator2.num_pages)

		try:
			pAc = paginator3.page(pag3)
		except PageNotAnInteger:
			pAc= paginator3.page(1)
		except EmptyPage:
			pAc = paginator3.page(paginator3.num_pages)

		try:
			pFi = paginator4.page(pag4)
		except PageNotAnInteger:
			pFi= paginator4.page(1)
		except EmptyPage:
			pFi = paginator4.page(paginator4.num_pages)

		try:
			pSa = paginator5.page(pag5)
		except PageNotAnInteger:
			pSa= paginator5.page(1)
		except EmptyPage:
			pSa = paginator5.page(paginator5.num_pages)

		
		ctx={'nineros':nineros,'almEquipos':pEq,'almExpress':pEx,'almAccs':pAc,'almFic':pFi,'almSaldo':pSa,'query':query,'nivel':nivel}
		return render_to_response('contabilidad/existenciasTodo.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo probado
@login_required(login_url='/')
def contabilidad_reportes_compras_garantias_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		pagina = request.GET.get('pagG','')
		query  = request.GET.get('q','')
		garantia=None
		
		if query:
			qset=(Q(sucursal__nombre__icontains=query) |Q(papeleta__folioPapeleta__icontains=query) | 
				Q(papeleta__nombre__icontains=query) | Q(equipo__imei__icontains=query) | 
			 	Q(equipo__icc__icontains=query))
			garantia = Garantia.objects.filter(qset).order_by('estado') #.order_by('sucursal').order_by('fxSucursal')
		else:
			garantia = Garantia.objects.all().order_by('estado') #.order_by('sucursal').order_by('fxSucursal')

		paginator = Paginator(garantia, 50)
		pgar=None
		try:
			pgar = paginator.page(pagina)
		except PageNotAnInteger:
			pgar = paginator.page(1)
		except EmptyPage:
			pgar = paginator.page(paginator.num_pages)

		ctx={'nivel':nivel, 'garantias':pgar, 'query':query}
		return render_to_response('contabilidad/mySolicitudGarantias.html',ctx,context_instance=RequestContext(request))
		
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo probado
@login_required(login_url='/')
def contabilidad_reportes_estadisticas_consultar_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		query  = request.GET.get('q','')
		pag1=request.GET.get('pag','')
		
		eventos = Sucursal.objects.all()

		if query:
			qset=(Q(nombre__icontains=query) |
			 Q(encargado__nombre__icontains=query) | 
			 Q(encargado__aPaterno__icontains=query) | 
			 Q(encargado__aMaterno__icontains=query) | 
			 Q(encargado__curp__icontains=query) | 
			 Q(zona__zona__icontains=query) | 
			 Q(direccion__icontains=query))
			eventos = Sucursal.objects.filter(qset)
			
		paginator1 = Paginator(eventos, 50)
		pSucursales=None
		
		try:
			pSucursales = paginator1.page(pag1)
		except PageNotAnInteger:
			pSucursales= paginator1.page(1)
		except EmptyPage:
			pSucursales = paginator1.page(paginator1.num_pages)

		if request.method == "GET":
			if request.GET.get('acumulado'):
				s = request.GET.get('acumulado','')
				if s:
					#sucursal
					anyoAct = datetime.today().year
					anyoAnt = datetime.today().year - 1
					mostrar = True
					las = Sucursal.objects.get(id=s)
					nomSucursal = las.nombre
					mes = ['01','02','03','04','05','06','07','08','09','10','11','12']
					col = ['Kit','Tip','Paq. G.','Otros','Express']
					vtas =[] #['','','','','','','','','','','','']
					no = len(col)
					no2 = len(mes)
					#activacion de equipos kit del mes del año actual
					j=0
					vtasAnt=[]
					vtasAct=[]

					for x in xrange(0,no):
						if j <4:
							vtas = []
							for n in xrange(0,no2):
								try:
									this ='%s-%s'%(anyoAnt,mes[n])	
									eq = VentaEquipo.objects.filter(venta__fecha__icontains=this,venta__aceptada=True,venta__sucursal=las)
									suma = 0
									for x in eq:
										try:
											g1 = ActivacionEquipo.objects.get(tipoActivacion__tipo=col[j],equipo=x.equipo)
											suma = suma + 1
										except :
											pass
									vtas.append(suma)
								except :
									vtas.append(0)
							totRow = 0
							zen = len(vtas)
							for x in xrange(0,zen):
								totRow = totRow + vtas[x]
							vtasAnt.append([col[j],vtas[0],vtas[1],vtas[2],vtas[3],vtas[4],vtas[5],vtas[6],vtas[7],vtas[8],vtas[9],vtas[10],vtas[11],totRow])
							j = j + 1

						if j == 4:
							vtas = []
							for n in xrange(0,no2):
								try:
									this ='%s-%s'%(anyoAnt,mes[n])		
									ex = VentaExpres.objects.filter(venta__fecha__icontains=this,venta__aceptada=True,venta__sucursal=las)
									suma2=0
									for x in ex:
										try:
											g1=ActivacionExpress.objects.filter(express=x.expres)
											suma2 = suma2 + 1
										except :
											pass
									vtas.append(suma2)
								except :
									vtas.append(0)
							totRow = 0
							zen = len(vtas)
							for x in xrange(0,zen):
								totRow = totRow + vtas[x]
							vtasAnt.append([col[j],vtas[0],vtas[1],vtas[2],vtas[3],vtas[4],vtas[5],vtas[6],vtas[7],vtas[8],vtas[9],vtas[10],vtas[11],totRow ])
							j = j + 1

					j = 0
					for x in xrange(0,no):
						if j <4:
							vtas = []
							for n in xrange(0,no2):
								try:
									this ='%s-%s'%(anyoAct,mes[n])
									eq = VentaEquipo.objects.filter(venta__fecha__icontains=this,venta__aceptada=True,venta__sucursal=las)
									suma = 0
									for x in eq:
										try:
											g1 = ActivacionEquipo.objects.get(tipoActivacion__tipo=col[j],equipo=x.equipo)
											suma = suma + 1
										except :
											pass
									vtas.append(suma)
								except :
									vtas.append(0)
							totRow = 0
							zen = len(vtas)
							for x in xrange(0,zen):
								totRow = totRow + vtas[x]
							vtasAct.append([col[j],vtas[0],vtas[1],vtas[2],vtas[3],vtas[4],vtas[5],vtas[6],vtas[7],vtas[8],vtas[9],vtas[10],vtas[11],totRow ])
							j = j + 1

						if j == 4:
							vtas = []
							for n in xrange(0,no2):
								try:
									this ='%s-%s'%(anyoAct,mes[n])	
									ex = VentaExpres.objects.filter(venta__fecha__icontains=this,venta__aceptada=True,venta__sucursal=las)
									suma2=0
									for x in ex:
										try:
											g1=ActivacionExpress.objects.filter(express=x.expres)
											suma2 = suma2 + 1
										except :
											pass
									vtas.append(suma2)
								except :
									vtas.append(0)
							totRow = 0
							zen = len(vtas)
							for x in xrange(0,zen):
								totRow = totRow + vtas[x]
							vtasAct.append([col[j],vtas[0],vtas[1],vtas[2],vtas[3],vtas[4],vtas[5],vtas[6],vtas[7],vtas[8],vtas[9],vtas[10],vtas[11],totRow ])
							j = j + 1


					ctx={'anyoAct':anyoAct,'anyoAnt':anyoAnt,'nomSucursal':nomSucursal,'mostrar':mostrar,'vtasAct':vtasAct,'vtasAnt':vtasAnt,'Sucursal':pSucursales,'query':query,'nivel':nivel}
					return render_to_response('contabilidad/reporteSucursalesActivas.html', ctx,context_instance=RequestContext(request))
							
		ctx={'Sucursal':pSucursales,'query':query,'nivel':nivel}
		return render_to_response('contabilidad/reporteSucursalesActivas.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo probado
@login_required(login_url='/')
def contabilidad_reportes_existencias_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		query  = request.GET.get('item','')
		pag1 = request.GET.get('pagEq','')
		pag2 = request.GET.get('pagEx','')
		pag3 = request.GET.get('pagC','')
		pag4 = request.GET.get('pagF','')
		pag5 = request.GET.get('pagT','')
		
		almEquipo = AlmacenEquipo.objects.filter(estado=True).exclude(equipo__estatus__estatus='Vendido').order_by('equipo')
		almExpress = AlmacenExpres.objects.filter(estado=True).exclude(expres__estatus__estatus='Vendido').order_by('expres')
		almAccs = AlmacenAccesorio.objects.filter(estado=True).exclude(accesorio__estatusAccesorio__estatus='Vendido').order_by('accesorio')
		almFic = AlmacenFicha.objects.filter(estado=True).exclude(ficha__estatusFicha__estatus='Vendido').order_by('ficha')
		almSaldo = SaldoSucursal.objects.all()
		nineros = []
		if query:
			qsetE=(Q(equipo__detallesEquipo__marca__marca__icontains=query) |
				Q(equipo__detallesEquipo__modelo__icontains=query) |
				Q(equipo__imei__icontains=query) |
				Q(equipo__icc__icontains=query)|
				Q(sucursal__nombre__icontains=query))
			qsetX=(Q(expres__icc__icontains=query)|Q(sucursal__nombre__icontains=query))
			qsetA=(Q(accesorio__codigoBarras__icontains=query)| 
				Q(accesorio__detallesAccesorio__marca__marca__icontains=query)|
				Q(accesorio__detallesAccesorio__seccion__seccion__icontains=query)| 
				Q(accesorio__detallesAccesorio__descripcion__icontains=query)|
				Q(sucursal__nombre__icontains=query))
			qsetF=(Q(ficha__folio__icontains=query)|
				Q(ficha__nominacion__nominacion__icontains=query)|
				Q(sucursal__nombre__icontains=query))

			almEquipo = AlmacenEquipo.objects.filter(qsetE,estado=True).exclude(equipo__estatus__estatus='Vendido').order_by('equipo')
			almExpress = AlmacenExpres.objects.filter(qsetX,estado=True).exclude(expres__estatus__estatus='Vendido').order_by('expres')
			almAccs = AlmacenAccesorio.objects.filter(qsetA,estado=True).exclude(accesorio__estatusAccesorio__estatus='Vendido').order_by('accesorio')
			almFic = AlmacenFicha.objects.filter(qsetF,estado=True).exclude(ficha__estatusFicha__estatus='Vendido').order_by('ficha')
			almSaldo = SaldoSucursal.objects.filter(sucursal__nombre__icontains=query).order_by('sucursal')
			suc = Sucursal.objects.filter(nombre__icontains=query)
			for x in suc:
				nEq = 0
				nEx = 0
				nAc = 0
				nFi = 0
				for j in almEquipo:
					if x.id == j.sucursal.id:
						nEq = nEq + 1
				for j in almExpress:
					if x.id == j.sucursal.id:
						nEx = nEx + 1
				for j in almAccs:
					if x.id == j.sucursal.id:
						nAc = nAc + 1
				for j in almFic:
					if x.id == j.sucursal.id:
						nFi = nFi + 1
				nineros.append([x.nombre.title(),nEq,None,nEx,None,nAc,None,nFi,None,None])
		
		paginator1 = Paginator(almEquipo, 50)
		paginator2 = Paginator(almExpress, 50)
		paginator3 = Paginator(almAccs, 50)
		paginator4 = Paginator(almFic, 50)
		paginator5 = Paginator(almSaldo, 50)
		pEq = None
		pEx = None
		pAc = None
		pFi = None
		pSa = None
		try:
			pEq = paginator1.page(pag1)
		except PageNotAnInteger:
			pEq= paginator1.page(1)
		except EmptyPage:
			pEq = paginator1.page(paginator1.num_pages)
				
		try:
			pEx = paginator2.page(pag2)
		except PageNotAnInteger:
			pEx= paginator2.page(1)
		except EmptyPage:
			pEx = paginator2.page(paginator2.num_pages)

		try:
			pAc = paginator3.page(pag3)
		except PageNotAnInteger:
			pAc= paginator3.page(1)
		except EmptyPage:
			pAc = paginator3.page(paginator3.num_pages)

		try:
			pFi = paginator4.page(pag4)
		except PageNotAnInteger:
			pFi= paginator4.page(1)
		except EmptyPage:
			pFi = paginator4.page(paginator4.num_pages)

		try:
			pSa = paginator5.page(pag5)
		except PageNotAnInteger:
			pSa= paginator5.page(1)
		except EmptyPage:
			pSa = paginator5.page(paginator5.num_pages)

		
		ctx={'nineros':nineros,'almEquipos':pEq,'almExpress':pEx,'almAccs':pAc,'almFic':pFi,'almSaldo':pSa,'query':query,'nivel':nivel}
		return render_to_response('contabilidad/existenciasTodo.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo probado
@login_required(login_url='/')
def contabilidad_reportes_planes_pendientes_view(request):
	nivel=Permiso(request.user,[0,1,2])
	if nivel != -1:
		info =""
		pagina = request.GET.get('pagina','')
		query  = request.GET.get('q','')
		gaara=None
		if query:
			qset=(Q(folio__icontains=query)| Q(sucursal__nombre__icontains=query) |Q(fxSolicitud__icontains=query) |Q(vendedor__curp__icontains=query) |
				Q(nombre__icontains=query) |Q(aPat__icontains=query) |Q(aMat__icontains=query) |Q(plan__plan__icontains=query) |
				Q(plan__costo__icontains=query) |Q(estado__estado__icontains=query) |Q(fxModificacion__icontains=query))

			gaara = Solicitud.objects.filter(qset).order_by('folio').order_by('fxSolicitud').order_by('nombre').order_by('sucursal')
		else:
			gaara = Solicitud.objects.all().order_by('folio').order_by('fxSolicitud').order_by('nombre').order_by('sucursal')

		paginator = Paginator(gaara, 20)
		
		solicitudes=None
		try:
			solicitudes = paginator.page(pagina)
		except PageNotAnInteger:
			solicitudes = paginator.page(1)
		except EmptyPage:
			solicitudes = paginator.page(paginator.num_pages)
		
		if request.method == "GET":
			if request.GET.get('pop'):
				s = request.GET.get('pop','')
				
				if s:
					grrr = Solicitud.objects.get(id=s)
					info = "Datos actualmente."
				else:
					info="Oops! lo sentimos, alguien ha cambiado la Solicitud manualmente...regrese a la pagina principal."
				ctx = {'grrr':grrr,'info':info, 'nivel':nivel}
				return render_to_response('contabilidad/solicitudCompleta.html',ctx,context_instance=RequestContext(request))
					

		ctx = {'solicitudes':solicitudes,'query':query,'info':info, 'nivel':nivel}
		return render_to_response('contabilidad/seguimientoPlanes.html',ctx,context_instance=RequestContext(request))
		
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo probado
@login_required(login_url='/')
def contabilidad_sucursales_reporte_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		query  = request.GET.get('q','')
		pag1=request.GET.get('pag','')
		
		qset2=(Q(tipoSucursal__tipo__icontains='Evento') | Q(tipoSucursal__tipo__icontains='Sucursal'))# | Q(tipoSucursal__tipo__icontains='Sucursal')
		eventos = Sucursal.objects.filter(qset2).exclude(id=mysucursal.id).order_by('nombre')

		if query:
			qset=(Q(nombre__icontains=query) |
			 Q(encargado__nombre__icontains=query) | 
			 Q(encargado__aPaterno__icontains=query) | 
			 Q(encargado__aMaterno__icontains=query) | 
			 Q(encargado__curp__icontains=query) | 
			 Q(zona__zona__icontains=query) | 
			 Q(direccion__icontains=query))
			eventos = Sucursal.objects.filter(qset,qset2).exclude(id=mysucursal.id).order_by('nombre')
		
		
		paginator1 = Paginator(eventos, 50)

		pSucursales=None
		
		try:
			pSucursales = paginator1.page(pag1)
		except PageNotAnInteger:
			pSucursales= paginator1.page(1)
		except EmptyPage:
			pSucursales = paginator1.page(paginator1.num_pages)

		if request.method == "GET":
			if request.GET.get('inac'):
				s = request.GET.get('inac','')
				if s:
					#try:
					upd = Sucursal.objects.get(id= s)
					upd.estado = EstadoSucursal.objects.get(estado='Inactiva')
					upd.save()

			if request.GET.get('act'):
				s = request.GET.get('act','')
				if s:
					#try:
					upd = Sucursal.objects.get(id= s)
					upd.estado = EstadoSucursal.objects.get(estado='Activa')
					upd.save()
					

		ctx={'Sucursal':pSucursales,'query':query,'nivel':nivel}
		return render_to_response('contabilidad/reporteActivarSucursales.html', ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo probado
@login_required(login_url='/')
def contabilidad_sucursales_vendedores_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		query  = request.GET.get('q','')
		pag1=request.GET.get('pag','')

		vd = VendedorSucursal.objects.all().exclude(sucursal=mysucursal).order_by('sucursal').order_by('empleado')

		if query:
			qset=(Q(sucursal__nombre__icontains=query) |
			 Q(empleado__nombre__icontains=query) | 
			 Q(empleado__aPaterno__icontains=query) | 
			 Q(empleado__aMaterno__icontains=query) | 
			 Q(empleado__curp__icontains=query) | 
			 Q(sucursal__zona__zona__icontains=query))
			vd = VendedorSucursal.objects.filter(qset,empleado__estadoEmpleado=True).exclude(sucursal=mysucursal).order_by('sucursal').order_by('empleado')
		
		
		paginator1 = Paginator(vd, 50)

		pAm=None
		
		try:
			pAm = paginator1.page(pag1)
		except PageNotAnInteger:
			pAm= paginator1.page(1)
		except EmptyPage:
			pAm = paginator1.page(paginator1.num_pages)


		ctx={'empleado':pAm,'query':query,'nivel':nivel}
		return render_to_response('contabilidad/reporteVendedores.html', ctx,context_instance=RequestContext(request))
		
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo probado
@login_required(login_url='/')
def contabilidad_sucursales_caja_sucursal_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		query  = request.GET.get('q','')
		pag1=request.GET.get('pagina','')
		hoy = datetime.now().date()
		info = ""
		msgs = []
		glo= []
		glo.append(str(hoy))
		tva = 0
		tca = 0
		las = Sucursal.objects.filter(estado__estado__icontains='Activa').order_by('nombre').order_by('zona')
		for x in las:
			msgs.append([x.nombre.title(),x.zona.zona.title(),sumaVentasActivas(x.id,hoy),sumaCortesActivos(x.id,hoy)])
			tva = tva + sumaVentasActivas(x.id,hoy)
			tca = tca + sumaCortesActivos(x.id,hoy)
		glo.append(tva)
		glo.append(tca)

		if query:
			msgs = []
			las = Sucursal.objects.filter(nombre__icontains=query,estado__estado__icontains='Activa').order_by('nombre').order_by('zona')
			for x in las:
				msgs.append([x.nombre.title(),x.zona.zona.title(),sumaVentasActivas(x.id,hoy),sumaCortesActivos(x.id,hoy)])			
		
		paginator1 = Paginator(msgs, 50)
		pMensages=None
		
		try:
			pMensages = paginator1.page(pag1)
		except PageNotAnInteger:
			pMensages= paginator1.page(1)
		except EmptyPage:
			pMensages = paginator1.page(paginator1.num_pages)

		ctx = {'global':glo,"sucursales":pMensages,"query": query,'info':info,'nivel':nivel}
		return render_to_response('contabilidad/cajaSucursales.html',ctx,context_instance=RequestContext(request))
		
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo probado
@login_required(login_url='/')
def contabilidad_autorizaciones_cancelaciones_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		info = ""
		fillCancelaciones()
		query  = request.GET.get('q','')
		pag1=request.GET.get('pagina','')
		
		if request.method == "GET":
			if request.GET.get('pop'):
				s = request.GET.get('pop','')
				if s:
					lasuc = Cancelaciones.objects.get(id=s).venta.id
					vtaCanceladas = Venta.objects.filter(id=lasuc,aceptada=False)
					eqVendido = None
					expVendido = None
					ficVendido = None
					accVendido = None
					recVendido = None
					planVendido = None
					rentaVendido = None
					menosAnticipo =  None
					try:
						eqVendido = VentaEquipo.objects.all()
						expVendido = VentaExpres.objects.all()
						ficVendido = VentaFichas.objects.all()
						accVendido = VentaAccesorio.objects.all()
						recVendido = VentaRecarga.objects.all()
						planVendido = VentaPlan.objects.all()
						rentaVendido = Renta.objects.all()
						menosAnticipo = Anticipo.objects.all()
					except VentaEquipo.DoesNotExist:
						eqVendido = None
					except VentaExpres.DoesNotExist:
						expVendido = None
					except VentaFichas.DoesNotExist:
						ficVendido = None
					except VentaAccesorio.DoesNotExist:
						accVendido = None
					except VentaRecarga.DoesNotExist:
						recVendido = None
					except Anticipo.DoesNotExist:
						menosAnticipo = None
					except VentaPlan.DoesNotExist:
						planVendido = None
					except Renta.DoesNotExist:
						rentaVendido = None
					ctx = {'rentaVendido':rentaVendido,'planVendido':planVendido,'anticipo':menosAnticipo,
					'accVendido':accVendido,'vtaCanceladas':vtaCanceladas,'recVendido':recVendido,'ficVendido':ficVendido,
					'expVendido':expVendido,'eqVendido':eqVendido,'nivel':nivel}
					return render_to_response('contabilidad/productosCancelados.html',ctx,context_instance=RequestContext(request))
				else:
					info = "Oops!, alguien ha modificado la informacion, regrese a la pagina principal para verificar."
					ctx = {'rentaVendido':rentaVendido,'planVendido':planVendido,'anticipo':menosAnticipo,
					'accVendido':accVendido,'vtaCanceladas':vtaCanceladas,'recVendido':recVendido,'ficVendido':ficVendido,
					'expVendido':expVendido,'eqVendido':eqVendido,'nivel':nivel}
					return render_to_response('contabilidad/productosCancelados.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('del'):
				s = request.GET.get('del','')
				if s:
					#try:
					upd = Cancelaciones.objects.get(id=s)
					upd.activo = False
					upd.save()

					#quitar la venta
					mivi = Venta.objects.get(id=upd.venta.id)
					mivi.activa = False
					mivi.save()
					

		if request.method == "POST":
			key=request.POST.get('upd','')
			if key:
				#venta
				#try:
				v = Cancelaciones.objects.get(id=key).venta
				#liberamos productos
				resultados = liberarProductos(v.id)
				#autorizamos venta
				canc = v
				canc.estado = EstadoVenta.objects.get(estado='Autorizada')
				canc.save()
				info = " Se liberaron los productos de la venta "+str(v.folioVenta)+ " "+resultados
				
			else:
				info = "No se puede seleccionar un valor no Existente"

		msgs = Cancelaciones.objects.filter(activo=True).order_by('fxCancelacion').reverse()
		if query:
			qset=(Q(venta__folioVenta__icontains=query) |
			 Q(venta__sucursal__nombre__icontains=query) | 
			 Q(venta__usuario__username__icontains=query))
			msgs = Cancelaciones.objects.filter(qset,activo=True).order_by('fxCancelacion').reverse()
		
		paginator1 = Paginator(msgs, 50)
		pMensages=None
		
		try:
			pMensages = paginator1.page(pag1)
		except PageNotAnInteger:
			pMensages= paginator1.page(1)
		except EmptyPage:
			pMensages = paginator1.page(paginator1.num_pages)

		ctx={'cancelaciones':pMensages,'query':query,'info':info,'nivel':nivel}
		return render_to_response('contabilidad/autorizacionCancelaciones.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo probado
@login_required(login_url='/')
def contabilidad_autorizaciones_papelera_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		info = ""
		fillCancelaciones()
		query  = request.GET.get('q','')
		pag1=request.GET.get('pagina','')
					
		msgs = Cancelaciones.objects.filter(activo=False).order_by('fxCancelacion').reverse()
		if query:
			qset=(Q(venta__folioVenta__icontains=query) |
			 Q(venta__sucursal__nombre__icontains=query) | 
			 Q(venta__usuario__username__icontains=query))
			msgs = Cancelaciones.objects.filter(qset,activo=True).order_by('fxCancelacion').reverse()
		
		paginator1 = Paginator(msgs, 50)
		pMensages=None
		
		try:
			pMensages = paginator1.page(pag1)
		except PageNotAnInteger:
			pMensages= paginator1.page(1)
		except EmptyPage:
			pMensages = paginator1.page(paginator1.num_pages)

		ctx={'cancelaciones':pMensages,'query':query,'info':info,'nivel':nivel}
		return render_to_response('contabilidad/bandejaCancelaciones.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo probado
@login_required(login_url='/')
def contabilidad_reportes_servicios_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		info =""
		mostrar = False
		buscar = True
		mostrarf = False
		boton = False
		show= True
		pagina = request.GET.get('pagina','')
		query  = request.GET.get('q','')
		reparaciones=None
		nReparaciones=0
		repHist = None
		
		if query:
			qset=(Q(cliente__nombre__icontains=query) |
			 Q(sucursal__nombre__icontains=query) | 
			 Q(cliente__folio__icontains=query))
			ccosto = EquipoReparacion.objects.filter(qset)
		else:
			ccosto = EquipoReparacion.objects.all()

		paginator = Paginator(ccosto, 50)
		nReparaciones=len(ccosto)
		reparacionesp=None
		try:
			reparacionesp = paginator.page(pagina)
		except PageNotAnInteger:
			reparacionesp = paginator.page(1)
		except EmptyPage:
			reparacionesp = paginator.page(paginator.num_pages)


		if request.method == "GET":

			if request.GET.get('q'):
				
				buscar = True
				mostrarf = False
				mostrar = False

				ctx = {'reparaciones':reparacionesp,'show':show,'buscar':buscar,'info':info, 'nivel':nivel}
				return render_to_response('contabilidad/historialClienteReparacion.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('histRep'):
				query = request.GET.get('histRep', '')
				if query:
					ccosto = EquipoReparacion.objects.get(id = query)
					repHist = HistorialClienteReparacion.objects.filter(equipoReparacion__id=ccosto.id)
			
					mostrar = True
					buscar = False
					mostrarf = True
					show= False

		ctx = {'reparaciones':reparacionesp,'show':show,'buscar':buscar,'mostrarf':mostrarf,'mostrar':mostrar,'clirep':ccosto,'historial':repHist ,'info':info, 'nivel':nivel}
		return render_to_response('contabilidad/historialClienteReparacion.html',ctx,context_instance=RequestContext(request))
		
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo probado
@login_required(login_url='/')
def contabilidad_reportes_auditorias_realizadas_view(request):
	nivel=Permiso(request.user,[0,1,4])
	if nivel != -1:
		query  = request.GET.get('q','')
		pag1=request.GET.get('pag1','')
		msgs = Inventario.objects.filter(terminada=True).order_by('fxFinal').reverse().distinct()

		if query:
			qset=(Q(folio__icontains=query)|Q(fxInicio__icontains=query)|Q(fxFinal__icontains=query)|Q(sucursal__nombre__icontains=query)|Q(observaciones__icontains=query))
			msgs = Inventario.objects.filter(qset,terminada=True).order_by('fxFinal').distinct()
		
		paginator1 = Paginator(msgs, 50)
		p_Item=None
		
		try:
			p_Item = paginator1.page(pag1)
		except PageNotAnInteger:
			p_Item= paginator1.page(1)
		except EmptyPage:
			p_Item = paginator1.page(paginator1.num_pages)

		ctx={'inventarios':p_Item,'cosa':'Terminados','query':query,'nivel':nivel}
		return render_to_response('contabilidad/inventarioSucursales.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo probado
@login_required(login_url='/')
def contabilidad_reportes_auditorias_sin_realizar_view(request):
	nivel=Permiso(request.user,[0,1,4])
	if nivel != -1:
		query  = request.GET.get('q','')
		pag1=request.GET.get('pag1','')
		msgs = Inventario.objects.filter(terminada=False).order_by('fxFinal').reverse().distinct()

		if query:
			qset=(Q(folio__icontains=query)|Q(fxInicio__icontains=query)|Q(fxFinal__icontains=query)|Q(sucursal__nombre__icontains=query)|Q(observaciones__icontains=query))
			msgs = Inventario.objects.filter(qset,terminada=False).order_by('fxFinal').distinct()
		
		paginator1 = Paginator(msgs, 50)
		p_Item=None
		
		try:
			p_Item = paginator1.page(pag1)
		except PageNotAnInteger:
			p_Item= paginator1.page(1)
		except EmptyPage:
			p_Item = paginator1.page(paginator1.num_pages)

		ctx={'inventarios':p_Item,'cosa':'Pendientes','query':query,'nivel':nivel}
		return render_to_response('contabilidad/inventarioSucursales.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def contabilidad_listas_equipos_view(request):
	nivel=Permiso(request.user,[0,1,2,3,4])
	if nivel != -1:
		query=request.GET.get('q','')
		
		r_items=None
		info=''

		if query:
			qset=(Q(marca__marca__icontains=query)|
				Q(modelo__icontains=query)|
				Q(color__icontains=query) |
				Q(precioMenudeo__icontains=query))
			r_items=DetallesEquipo.objects.filter(qset).distinct()
		else:			
			qset=(Q(precioMenudeo=None))
			r_items=DetallesEquipo.objects.exclude(qset)
		

		ctx={'nivel':nivel, 'query':query, 'r_items':r_items, 'info':info}
		return render_to_response('contabilidad/listaPreciosEquipos.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def contabilidad_listas_accesorios_view(request):
	nivel=Permiso(request.user,[0,1,2,3,4])
	if nivel != -1:
		query=request.GET.get('q','')
		
		r_items=None
		info=''

		if query:
			qset=(Q(marca__marca__icontains=query)|
				Q(descripcion__icontains=query)|
				Q(seccion__seccion__icontains=query)|
				Q(precioMenudeo__icontains=query))
			r_items=DetallesAccesorio.objects.filter(qset).distinct()
		else:			
			qset=(Q(precioMenudeo=None)|Q(precioMayoreo=None))
			r_items=DetallesAccesorio.objects.exclude(qset)
		

		ctx={'nivel':nivel, 'query':query, 'r_items':r_items, 'info':info}
		return render_to_response('contabilidad/listaPreciosAccesorios.html', ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def contabilidad_listas_planes_view(request):
	nivel=Permiso(request.user,[0,1,2,3,4])
	if nivel != -1:
		query=request.GET.get('q','')
		
		r_items=None
		info=''

		r_items=Plan.objects.filter(activo=True)

		if query:
			qset=(Q(plan__icontains=query)|
				Q(costo__icontains=query)|
				Q(equiposGratis__icontains=query))
			r_items=Plan.objects.filter(qset,activo=True).distinct()
		
		ctx={'nivel':nivel, 'query':query, 'r_items':r_items, 'info':info}
		return render_to_response('contabilidad/listaPlanes.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

@login_required(login_url='/')
def usuarios_agregar_view(request):
	nivel=Permiso(request.user,[0,1,2,3,4])
	if nivel != -1:
		
		form = AddUsuarioForm()
		form2 = AddUserForm()
		info = ""
		if request.method == "POST":
			form = AddUsuarioForm(request.POST or None)
			form2 = AddUserForm(request.POST or None)
			if form.is_valid() and form2.is_valid():
				
				#crear user
				name_user 	= form2.cleaned_data['username']
				email_user 	= form2.cleaned_data['email']
				pass_user 	= form2.cleaned_data['password']

				create_user = User.objects.create_user(username= name_user, email= email_user, password=pass_user)

				#crear usuario
				a = Usuario()
				a.user = create_user
				a.empleado = form.cleaned_data['empleado']
				a.permiso = form.cleaned_data['permiso']
				a.save()

				create_user.name_user = a.empleado.nombre
				create_user.lastname = a.empleado.aPaterno+ " " + a.empleado.aMaterno
				create_user.save()

				form = AddUsuarioForm()
				form2 = AddUserForm()
				info = "Se creo el usuario :%s con el empleado: %s"%(a.user.username, a.empleado)
			
			else:
				info = "Por favor, Verifique su informacion"
				form= AddUsuarioForm(request.POST)
				form2 = AddUserForm(request.POST)
		
		ctx = {'form':form,'form2':form2 ,'info':info,'nivel':nivel}
		return render_to_response('contabilidad/addUser.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def usuarios_actualizar_view(request):
	nivel=Permiso(request.user,[0,1,2,3,4])
	if nivel != -1:
		q=request.GET.get('q','')
		pagina=request.GET.get('pagina','')
		usuario=None
		usuarios=None
		nUsuarios=0
		mensaje='Sin Resultados'
		
		ide=request.GET.get('ide','')
		#form = SetPasswordForm()
		info = ""

		if q:
			try:
				usuario=Usuario.objects.get(id=q)
				mensaje=''
				q=''
			except :
				qset=(Q(empleado__nombre__icontains=q)|
				Q(empleado__aPaterno__icontains=q)|
				Q(empleado__aMaterno__icontains=q)|
				Q(empleado__direccion__icontains=q)|
				Q(empleado__telefono__icontains=q)|
				Q(empleado__puesto__puesto__icontains=q)|
				Q(empleado__area__area__icontains=q)|
				Q(user__username__icontains=q)|
				Q(permiso__descripcion__icontains=q))
				usuarios=Usuario.objects.filter(qset)
		else:
			usuarios=Usuario.objects.all()

		if ide:
			form = None
			try:
				usuario = Usuario.objects.get(id= ide)
				form = UpdUserForm(initial={'key':usuario.id})
			except :
				info = "Los datos fueron movidos manualmente, intente nuevamente..."
			
			ctx = {'nivel':nivel,'form':form, 'info':info,'usuario':usuario}
			return render_to_response('contabilidad/updUser.html', ctx ,context_instance=RequestContext(request))
	
		
		if request.method == "POST":
			key = request.POST.get('key','')
			usuario = Usuario.objects.get(id= key)
			form = UpdUserForm(request.POST, instance=usuario.user)
			if form.is_valid():
				a = User.objects.get(id=usuario.user.id)
				a.set_password(form.cleaned_data['password'])
				a.is_active = form.cleaned_data['is_active']
				a.save()

				#form.save()
				info= "Sus Datos se han Actualizado Correctamente."

				ctx = {'nivel':nivel,'info':info,'usuario':usuario }
				return render_to_response('contabilidad/updUser.html', ctx ,context_instance=RequestContext(request))

			else:
				info = "Verifique sus datos"
				form= UpdUserForm(request.POST)
			
			ctx = {'nivel':nivel,'form':form, 'info':info,'usuario':usuario }
			return render_to_response('contabilidad/updUser.html', ctx ,context_instance=RequestContext(request))


		if usuarios:
			nUsuarios=len(usuarios)
			usuarios=Paginador(usuarios,50,pagina)
		ctx={'nivel':nivel, 'mensaje':mensaje, 'q':q, 'usuario':usuario, 'usuarios':usuarios, 'nUsuarios':nUsuarios}
		return render_to_response('contabilidad/usuariosReporte2.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def usuarios_vendedores_view(request):
	nivel=Permiso(request.user,[0,1,2,3,4])
	if nivel != -1:
		form = UpdVendedorSucursalForm()
		info = ""
		if request.method == "POST":
			upd = VendedorSucursal.objects.get(empleado=request.POST.get('empleado'))
			form = UpdVendedorSucursalForm(request.POST or None, instance=upd)

			if form.is_valid():
				form.save()

				info = "Sus Datos han sido Actualizados %s"%(upd)
			else:
				info = "Verifique sus datos"
				form= UpdVendedorSucursalForm(request.POST)
		ctx = {'nivel':nivel, 'form':form, 'info':info}
		return render_to_response('contabilidad/myVendedorSucursal.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#------------agregado para sanciones economicas
@login_required(login_url='/')
def gerencia_sancion_agregar_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		form = SancionForm()
		info = ""
		if request.method == "POST":
			form = SancionForm(request.POST or None)
			if form.is_valid():
				
				#crear Sancion
				a = Sancion()
				a.empleado = form.cleaned_data['empleado']
				a.descripcion = form.cleaned_data['descripcion']
				a.monto = form.cleaned_data['monto']
				a.save()
				
				#crear Cuenta para esa sancion al empleado
				today = datetime.now() #fecha actual
				d = today.strftime("%d%m%Y") # fecha con formato
				numero=CuentaEmpleado.objects.count()
				folio 		= '%s%s'%(numero+1,d)
					
				cuenta=CuentaEmpleado()
				cuenta.folio 		= folio
				cuenta.empleado 	= a.empleado
				cuenta.tipoCuenta 	= TipoCuenta.objects.get(tipo='Sancion')
				cuenta.monto 		= a.monto
				cuenta.observacion = a.descripcion + " Usuario: "+str(request.user)
				cuenta.adeudo  = a.monto
				cuenta.save()

				form = SancionForm()
				info = "Se ha registrado la Sancion. Se genero una cuenta al empleado : %s"%(cuenta)
			
			else:
				info = "Por favor, Verifique su informacion"
				form= SancionForm(request.POST)
		
		ctx = {'form':form,'info':info,'nivel':nivel}
		return render_to_response('contabilidad/sancionAdd.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def gerencia_sancion_consultar_view(request):
	nivel=Permiso(request.user,[0,1,2,3])
	if nivel != -1:
		query  = request.GET.get('q','')
		pag1=request.GET.get('pag','')
		info = ""
		if request.method == "POST":
			if request.POST.get('delete'):
				s = request.POST.get('delete','')
				if s:
					try :
						upd = Sancion.objects.get(id= s)
						upd.delete()
					except :
						info = "La informacion no es Correcta o ya se elimino previamente."
		
		sanciones = Sancion.objects.all().order_by('empleado__nombre')

		if query:
			qset=(Q(fxSancion__icontains=query) |
			 Q(empleado__nombre__icontains=query) | 
			 Q(empleado__aPaterno__icontains=query) | 
			 Q(empleado__aMaterno__icontains=query) | 
			 Q(empleado__curp__icontains=query) | 
			 Q(descripcion__icontains=query))
			sanciones = Sancion.objects.filter(qset).order_by('empleado__nombre')
		
		
		paginator1 = Paginator(sanciones, 50)

		pAm=None
		
		try:
			pAm = paginator1.page(pag1)
		except PageNotAnInteger:
			pAm= paginator1.page(1)
		except EmptyPage:
			pAm = paginator1.page(paginator1.num_pages)

		ctx={'sanciones':pAm,'query':query,'info':info,'nivel':nivel}
		return render_to_response('contabilidad/sancionConsultar.html', ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

