# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from django.db.models import Q
import re
from datetime import datetime, timedelta
import time
from decimal import Decimal
from django import forms
import xlwt
from django.db import transaction
from django.contrib.auth.models import Group
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField, TextInput
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.forms.extras.widgets import SelectDateWidget

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth.models import User
from djCell.apps.activaciones.models import TipoActivacion, ActivacionEquipo, ActivacionExpress, ActivacionPlan
from djCell.apps.almacen.models import AlmacenEquipo, AlmacenExpres, AlmacenAccesorio, AlmacenFicha
from djCell.apps.apartados.models import EstadoApartado, Apartado, HistorialApartado
from djCell.apps.amonestaciones.models import TipoAmonestacion, Amonestacion, Sancion
from djCell.apps.auditoria.models import ArqueoCaja
from djCell.apps.catalogos.models import Estado, Ciudad, Colonia, CP, Zona
from djCell.apps.clientes.models import ClienteFacturacion, ClienteServicio, Mayorista
from djCell.apps.comisiones.models import Comision
from djCell.apps.contabilidad.models import Nomina, TipoCuenta, CuentaEmpleado, HistorialEmpleado, Metas, Caja, Gastos,LineaCredito, HistLCredito, Cuenta
from djCell.apps.corteVta.models import TipoGastoSucursal, GastosSucursal, CorteVenta, DiferenciasCorte, VentasCorte, RecargasVendidoCorte
from djCell.apps.credito.models import EstadoSubdistribuidor, EstadoCredito, Subdistribuidor, Credito, HistorialSubdistribuidor
from djCell.apps.facturacion.models import Facturacion, EstadoFacturacion
from djCell.apps.garantiasuc.models import EstadoGarantia, Garantia
from djCell.apps.mensajes.models import EstadoMensaje, SolicitudNuevoProducto 
from djCell.apps.movimientos.models import TipoMovimiento, Movimiento, ListaEquipo, ListaExpres, ListaAccesorio, ListaFichas, TransferenciaSaldo
from djCell.apps.papeletas.models import TipoProducto, Papeleta
from djCell.apps.personal.models import Area, Puesto, Empleado, Usuario
from djCell.apps.planes.models import EstadoSolicitud, Solicitud, TipoRelacion, Banco, Plan, DetallePlan, ServiciosPlan
from djCell.apps.portabilidades.models import EstadoPortabilidad, Portabilidad,FlexeoEquipo
from djCell.apps.productos.models import TiempoGarantia,Estatus,Marca,Gama,DetallesEquipo,Equipo,TipoIcc,DetallesExpres,Expres, Secciones,MarcaAccesorio,DetallesAccesorio,EstatusAccesorio,Accesorio, NominacionFicha,EstatusFicha,Ficha,  TiempoAire, HistorialPreciosEquipos,HistorialPreciosAccesorios,HistorialPreciosExpres
from djCell.apps.proveedor.models import Proveedor, FormaPago,  Factura
from djCell.apps.recargas.models import Monto,Recarga,SaldoSucursal, HistorialSaldo, SaldoStock
from djCell.apps.servicios.models import TipoReparacion, EstadoReparacion,Reparacion, EquipoReparacion, HistorialClienteReparacion, comisionesReparacion
from djCell.apps.stocks.models import StockEquipo, StockExpres, StockAccesorio, StockFicha
from djCell.apps.sucursales.models import EstadoSucursal, TipoSucursal, Sucursal, VendedorSucursal
from djCell.apps.ventas.models import EstadoVenta, Venta,VentaEquipo,VentaExpres,VentaAccesorio,VentaFichas,VentaRecarga,VentaPlan,Renta, Cancelaciones, VentaMayoreo,TipoPago, Anticipo


#right here
from djCell.interface.admingral.forms import reporteCompleto, reporteFecha, addDetallePlan, addPlan, updReparacion, addClienteServicioForm, addAbonoReparacion, updCostoPorta, updGratisFlexeo, AmonestacionForm, setMetas, SancionForm, AddUsuarioForm, AddUserForm, UpdUserForm, UpdVendedorSucursalForm
from djCell.operaciones.comunes import Permiso, agregarCiudades
from djCell.operaciones.exceles import export_To_Excel_ActivacionG,exportPapeletas
from djCell.operaciones.ventasgral import sumaVentasActivas,sumaCortesActivos,fillCancelaciones,back_almacenItems,reembolso,liberarProductos
from djCell.operaciones.vistas import Paginador		
#listo #yet
@login_required(login_url='/')
def index_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		return render_to_response('admingral/index.html', {'nivel':nivel},context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def ventas_gerencia_reportes_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		query  = request.GET.get('q','')
		pag1=request.GET.get('pag','')
		
		eventos = Sucursal.objects.all()#.exclude(id=mysucursal.id).order_by('nombre')

		if query:
			qset=(Q(nombre__icontains=query) |
			 Q(encargado__nombre__icontains=query) | 
			 Q(encargado__aPaterno__icontains=query) | 
			 Q(encargado__aMaterno__icontains=query) | 
			 Q(encargado__curp__icontains=query) | 
			 Q(zona__zona__icontains=query) | 
			 Q(direccion__icontains=query))
			eventos = Sucursal.objects.filter(qset).exclude(id=mysucursal.id).order_by('nombre')
			
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
					return render_to_response('admingral/reporteSucursalesActivas.html', ctx,context_instance=RequestContext(request))
							
		ctx={'Sucursal':pSucursales,'query':query,'nivel':nivel}
		return render_to_response('admingral/reporteSucursalesActivas.html', ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def ventas_gerencia_eventos_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		info = ""
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
					try:
						with transaction.atomic():
							upd = Sucursal.objects.get(id= s)
							upd.estado = EstadoSucursal.objects.get(estado='Inactiva')
							upd.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

			if request.GET.get('act'):
				s = request.GET.get('act','')
				if s:
					try:
						with transaction.atomic():
							upd = Sucursal.objects.get(id= s)
							upd.estado = EstadoSucursal.objects.get(estado='Activa')
							upd.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

		ctx={'Sucursal':pSucursales,'info':info ,'query':query,'nivel':nivel}
		return render_to_response('admingral/reporteEventos.html', ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def ventas_gerencia_amonestacion_agregar_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		form = AmonestacionForm()
		info = ""
		if request.method == "POST":
			form = AmonestacionForm(request.POST or None)
			if form.is_valid():
				empleado = form.cleaned_data['empleado']
				tipoAmonestacion = form.cleaned_data['tipoAmonestacion']
				comentario = form.cleaned_data['comentario']
				try:
					with transaction.atomic():
						a = Amonestacion()
						a.empleado = empleado
						a.tipoAmonestacion = tipoAmonestacion
						a.comentario = comentario
						a.save()
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
				form = AmonestacionForm()
				info = "Se ha registrado la Amonestacion."
			
			else:
				info = "Por favor, Verifique su informacion"
				form= AmonestacionForm(request.POST)
		
		ctx = {'form':form,'info':info,'nivel':nivel}
		return render_to_response('admingral/amonestaciones.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def ventas_gerencia_amonestacion_consultar_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		query  = request.GET.get('q','')
		pag1=request.GET.get('pag','')

		if request.method == "GET":
			if request.GET.get('delete'):
				s = request.GET.get('delete','')
				if s:
					try:
						with transaction.atomic():
							upd = Amonestacion.objects.get(id= s)
							upd.delete()
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
					
		amonestaciones = Amonestacion.objects.all().order_by('tipoAmonestacion')

		if query:
			qset=(Q(fxAmonestacion__icontains=query) |
			 Q(empleado__nombre__icontains=query) | 
			 Q(empleado__aPaterno__icontains=query) | 
			 Q(empleado__aMaterno__icontains=query) | 
			 Q(empleado__curp__icontains=query) | 
			 Q(tipoAmonestacion__tipo__icontains=query))
			amonestaciones = Amonestacion.objects.filter(qset).order_by('empleado')
		
		
		paginator1 = Paginator(amonestaciones, 50)

		pAm=None
		
		try:
			pAm = paginator1.page(pag1)
		except PageNotAnInteger:
			pAm= paginator1.page(1)
		except EmptyPage:
			pAm = paginator1.page(paginator1.num_pages)


		ctx={'amonestaciones':pAm,'query':query,'nivel':nivel}
		return render_to_response('admingral/consultaAmonestaciones.html', ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def ventas_apartados_clientes_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		query  = request.GET.get('q','')
		pag1=request.GET.get('pagina','')
		info = ""
		msgs = ClienteServicio.objects.filter(tipoCliente='Apartado').order_by('fxIngreso').reverse()

		if query:
			qset = (Q(nombre__icontains=query) | Q(direccion__icontains=query) | Q(folio__icontains=query)  | 
				Q(colonia__colonia__icontains=query) | Q(ciudad__ciudad__icontains=query))
			msgs = ClienteServicio.objects.filter(qset,tipoCliente='Apartado').order_by('fxIngreso').reverse()
		
		paginator1 = Paginator(msgs, 50)
		pMensages=None
		
		try:
			pMensages = paginator1.page(pag1)
		except PageNotAnInteger:
			pMensages= paginator1.page(1)
		except EmptyPage:
			pMensages = paginator1.page(paginator1.num_pages)

		ctx = {"results": pMensages,"query": query, 'info':info, 'nivel':nivel}
		return render_to_response('admingral/catalogoClienteApartados.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def ventas_apartados_historial_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		query  = request.GET.get('q','')
		pag1=request.GET.get('pagina','')
		
		msgs = ClienteServicio.objects.filter(tipoCliente='Apartado').order_by('fxIngreso').reverse()

		if query:
			qset = (Q(nombre__icontains=query) | Q(direccion__icontains=query) | Q(folio__icontains=query)  | 
				Q(colonia__colonia__icontains=query) | Q(ciudad__ciudad__icontains=query))
			msgs = ClienteServicio.objects.filter(qset,tipoCliente='Apartado').order_by('fxIngreso').reverse()
		
		paginator1 = Paginator(msgs, 50)
		pMensages=None
		
		try:
			pMensages = paginator1.page(pag1)
		except PageNotAnInteger:
			pMensages= paginator1.page(1)
		except EmptyPage:
			pMensages = paginator1.page(paginator1.num_pages)

		buscar  = True
		query 	= ''
		apartados = False
		mostrar = False
		resultsCli 	= []
		info 		= ""
		
		if request.method == "GET":
			if request.GET.get('veA'):
				elCliente = request.GET.get('veA','')
				if elCliente:
					dequien = ClienteServicio.objects.get(id=elCliente)
					apartadosCli = Apartado.objects.filter(clienteApartado__id=elCliente)
					buscar = False
					apartados = True

					ctx = {'apartados':apartados, 'buscar':buscar,"apartadosCli": apartadosCli,"dequien": dequien,'info':info,'nivel':nivel}
					return render_to_response('admingral/historialApartado.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('histA'):
				elapa = request.GET.get('histA','')
				if elapa:
					grrr = Apartado.objects.get(id=elapa)
					hist = HistorialApartado.objects.filter(apartado=grrr)
					suma = 0
					for x in hist:
						suma = suma + x.abono
					resta = grrr.equipo.precioMenudeo - suma
					buscar = False
					mostrar = True
					ctx = {'elapa':grrr,'historial':hist,'sumaHist':suma,'restaHist':resta,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel}
					return render_to_response('admingral/historialApartado.html',ctx,context_instance=RequestContext(request))
			
		
		ctx = {'buscar':buscar,"results":pMensages,"query": query,'info':info,'nivel':nivel}
		return render_to_response('admingral/historialApartado.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def ventas_caja_sucursales_view(request):
	nivel=Permiso(request.user,[0,1])
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
		return render_to_response('admingral/cajaSucursales.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def ventas_metas_asignar_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		info = ""
		query  = request.GET.get('q','')
		pag1=request.GET.get('pagina','')
		qset2 = (Q(puesto__puesto__icontains='encargado') | Q(puesto__puesto__icontains='vendedor'))
		omen = Empleado.objects.filter(qset2,estadoEmpleado=True).order_by('curp')
		msgs = []
		i = 0
		for x in omen:
			try:
				zen = Metas.objects.get(empleado__id=x.id)
			except :
				msgs.append([x,setMetas(),i])
				i = i + 1
		form = setMetas()
		if query:
			qset=(Q(curp__icontains=query) |
			 Q(nombre__icontains=query) | 
			 Q(aPaterno__icontains=query) | 
			 Q(aMaterno__icontains=query))
			omen = Empleado.objects.filter(qset2,qset,estadoEmpleado=True).order_by('curp')
			msgs = []
			i = 0
			for x in omen:
				try:
					zen = Metas.objects.get(empleado__id=x.id)
					msgs.append([x,setMetas(instance=zen),i])	
					i = i + 1
				except :
					msgs.append([x,setMetas(),i])
					i = i + 1

		if request.method == "POST":
			form = setMetas(request.POST or None)
			key=request.POST.get('empSelec','')
			indice=request.POST.get('indice','')
			if form.is_valid():
				metaEquipo 	= form.cleaned_data['metaEquipo']
				metaPlanes 	= form.cleaned_data['metaPlanes']
				metaServicios = form.cleaned_data['metaServicios']
				a = None
				try:
					a = Metas.objects.get(empleado__id=key)
					a.metaEquipo 	= metaEquipo
					a.metaPlanes 	= metaPlanes
					a.metaServicios = metaServicios
					a.save()
				except Metas.DoesNotExist:
					a = Metas()
					a.empleado = Empleado.objects.get(id=key)
					a.metaEquipo 	= metaEquipo
					a.metaPlanes 	= metaPlanes
					a.metaServicios = metaServicios
					a.save()
				info = "Se registro meta del empleado: "+a.empleado.curp.upper()+' '+a.empleado.nombre.title()+' '+a.empleado.aPaterno.title()+' '+a.empleado.aMaterno.title()
				
			else:
				a  = Empleado.objects.get(id=key)
				info = "Por Favor, ingrese un >>numero<< en metas a adjuntar al empleado. "+a.nombre.title()+' '+a.aPaterno.title()+' '+a.aMaterno.title()
		
		paginator1 = Paginator(msgs, 50)
		pMensages=None
		
		try:
			pMensages = paginator1.page(pag1)
		except PageNotAnInteger:
			pMensages= paginator1.page(1)
		except EmptyPage:
			pMensages = paginator1.page(paginator1.num_pages)

		ctx = {'empleados':pMensages,'info':info,'nivel':nivel}
		return render_to_response('admingral/theMetas.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def ventas_metas_consultar_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		info = ""
		query  = request.GET.get('q','')
		smes  = request.GET.get('mes','')
		pag1=request.GET.get('pagina','')
		qset2 = (Q(empleado__puesto__puesto__icontains='encargado') | Q(empleado__puesto__puesto__icontains='vendedor'))
		omen = Metas.objects.filter(qset2,empleado__estadoEmpleado=True).order_by('empleado')
		msgs = []
		today = datetime.now() #fecha actual
		dateFormat = today.strftime("%Y-%m")
		for x in omen:
			sumaE = 0
			sumaP = 0
			sumaS = 0
			try:
				ev = VentaEquipo.objects.filter(venta__aceptada=True,venta__fecha__icontains=dateFormat)
				for y in ev:
					try:
						zen = ActivacionEquipo.objects.get(equipo=y.equipo, empleado=x.empleado)
						sumaE = sumaE + 1
					except :
						pass
				sumaP = ActivacionPlan.objects.filter(ejecutivo=x.empleado, fxActivacion__icontains=dateFormat).count()
				try:
					u = Usuario.objects.get(empleado=x.empleado)
					sumaS = comisionesReparacion.objects.filter(user=u.user,equipoReparacion__fxIngreso=dateFormat).count()
				except :
					pass
			except :
				pass
			msgs.append([x,sumaE,sumaP,sumaS])			

		if query:
			qset=(Q(empleado__curp__icontains=query) |
			 Q(empleado__nombre__icontains=query) | 
			 Q(empleado__aPaterno__icontains=query) | 
			 Q(empleado__aMaterno__icontains=query))
			info = smes
			if smes:
				dateFormat = smes
			else:
				dateFormat = "Todos"
			omen = Metas.objects.filter(qset,qset2,empleado__estadoEmpleado=True).order_by('empleado')
			msgs = []
			for x in omen:
				sumaE = 0
				sumaP = 0
				sumaS = 0
				try:
					ev = VentaEquipo.objects.filter(venta__aceptada=True,venta__fecha__icontains=smes)
					for y in ev:
						try:
							zen = ActivacionEquipo.objects.get(equipo=y.equipo, empleado=x.empleado)
							sumaE = sumaE + 1
						except :
							pass
					sumaP = ActivacionPlan.objects.filter(ejecutivo=x.empleado, fxActivacion__icontains=smes).count()
					try:
						u = Usuario.objects.get(empleado=x.empleado)
						sumaS = comisionesReparacion.objects.filter(user=u.user,equipoReparacion__fxIngreso=smes).count()
					except :
						pass
				except :
					pass
				msgs.append([x,sumaE,sumaP,sumaS])

		paginator1 = Paginator(msgs, 50)
		pMensages=None
		
		try:
			pMensages = paginator1.page(pag1)
		except PageNotAnInteger:
			pMensages= paginator1.page(1)
		except EmptyPage:
			pMensages = paginator1.page(paginator1.num_pages)

		ctx = {'empleados':pMensages,'mes':dateFormat ,'info':info,'nivel':nivel}
		return render_to_response('admingral/theMetasReporte.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

#------------agregado para sanciones economicas
@login_required(login_url='/')
def gerencia_sancion_agregar_view(request):
	nivel=Permiso(request.user,[0,1])
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
		return render_to_response('admingral/sancionAdd.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def gerencia_sancion_consultar_view(request):
	nivel=Permiso(request.user,[0,1])
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
		return render_to_response('admingral/sancionConsultar.html', ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet morles cr 
@login_required(login_url='/')
def activaciones_reporte_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		form = reporteCompleto()
		info = ""
		query = "Activados" #+str(datetime.now().date())
		resultsExp = []
		resultsEq  = []
		
		ae = ActivacionEquipo.objects.all() #filter(fxActivacion__icontains=datetime.now().date())
		ax = ActivacionExpress.objects.all() #filter(fxActivacion__icontains=datetime.now().date())

		for x in ae:
			resultsEq.append([x.tipoActivacion.tipo, x.equipo.detallesEquipo.marca.marca.title()+' '+x.equipo.detallesEquipo.modelo.title(),str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion)])
		for x in ax:
			resultsExp.append([x.tipoActivacion.tipo,str(x.express.icc),x.express.noCell,x.empleado.curp,str(x.fxActivacion)])

		pag1=request.GET.get('pagina1','')
		pag2=request.GET.get('pagina2','')
		
		if request.method == "POST":
			form = reporteCompleto(request.POST or None)
			if form.is_valid():
				fxInicio 	= request.POST.get('fxInicio','')
				fxFinal 	= request.POST.get('fxFinal','')
				vendido 	= form.cleaned_data['vendido']
				tipo = form.cleaned_data['tipoActivacion']
				resultsExp = []
				resultsEq  = []
				
				if vendido:
					if fxFinal:
						eq = ActivacionEquipo.objects.filter(fxActivacion__range=[fxInicio,fxFinal],tipoActivacion__tipo__icontains=tipo)
						for x in eq:
							try:
								g1=VentaEquipo.objects.get(venta__aceptada=True,equipo = x.equipo)
								if g1:
									pass
								else:
									resultsEq.append([x.sucursal, x.tipoActivacion.tipo,x.equipo.detallesEquipo.marca.marca.title()+' '+x.equipo.detallesEquipo.modelo.title(),str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion)])
							except :
								resultsEq.append([x.sucursal, x.tipoActivacion.tipo,x.equipo.detallesEquipo.marca.marca.title()+' '+x.equipo.detallesEquipo.modelo.title(),str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion)])
								
						ex = ActivacionExpress.objects.filter(fxActivacion__range=[fxInicio,fxFinal],tipoActivacion__tipo__icontains=tipo)
						for x in ex:
							try:
								g1=VentaExpres.objects.get(venta__aceptada=True,expres = x.express)
								if g1:
									pass
								else:
									resultsExp.append([x.sucursal, x.tipoActivacion.tipo,str(x.express.icc),x.express.noCell,x.empleado.curp,str(x.fxActivacion)])
							except :
								resultsExp.append([x.sucursal, x.tipoActivacion.tipo,str(x.express.icc),x.express.noCell,x.empleado.curp,str(x.fxActivacion)])

						query = "Entre fechas de Activaciones no Vendidas: "+str(fxInicio)+" y "+str(fxFinal)+" Activacion : "+str(tipo)

					else:
						eq = ActivacionEquipo.objects.filter(fxActivacion__icontains=fxInicio,tipoActivacion__tipo__icontains=tipo)
						for x in eq:
							try:
								g1=VentaEquipo.objects.get(venta__aceptada=True,equipo = x.equipo)
								if g1:
									pass
								else:
									resultsEq.append([x.sucursal, x.tipoActivacion.tipo, x.equipo.detallesEquipo.marca.marca.title()+' '+x.equipo.detallesEquipo.modelo.title(),str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion)])
							except :
								resultsEq.append([x.sucursal, x.tipoActivacion.tipo, x.equipo.detallesEquipo.marca.marca.title()+' '+x.equipo.detallesEquipo.modelo.title(),str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion)])
								
						ex = ActivacionExpress.objects.filter(fxActivacion__icontains=fxInicio,tipoActivacion__tipo__icontains=tipo)
						for x in ex:
							try:
								g1=VentaExpres.objects.get(venta__aceptada=True,expres = x.express)
								if g1:
									pass
								else:
									resultsExp.append([x.sucursal, x.tipoActivacion.tipo,str(x.express.icc),x.express.noCell,x.empleado.curp,str(x.fxActivacion)])
							except :
								resultsExp.append([x.sucursal, x.tipoActivacion.tipo,str(x.express.icc),x.express.noCell,x.empleado.curp,str(x.fxActivacion)])

						query = "Fecha : "+str(fxInicio)+" Activacion : "+str(tipo)+" Activaciones no vendidas."
				
				elif fxFinal:
					ae = ActivacionEquipo.objects.filter(fxActivacion__range=[fxInicio,fxFinal],tipoActivacion__tipo__icontains=tipo)
					ax = ActivacionExpress.objects.filter(fxActivacion__range=[fxInicio,fxFinal],tipoActivacion__tipo__icontains=tipo)
					for x in ae:
						resultsEq.append([x.sucursal, x.tipoActivacion.tipo, x.equipo.detallesEquipo.marca.marca.title()+' '+x.equipo.detallesEquipo.modelo.title(),str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion)])
					for x in ax:
						resultsExp.append([x.sucursal, x.tipoActivacion.tipo,str(x.express.icc),x.express.noCell,x.empleado.curp,str(x.fxActivacion)])
					query = "Entre fechas : "+str(fxInicio)+" y "+str(fxFinal)+" Activacion : "+str(tipo)

				else:
					ae = ActivacionEquipo.objects.filter(fxActivacion__icontains=fxInicio,tipoActivacion__tipo__icontains=tipo)
					ax = ActivacionExpress.objects.filter(fxActivacion__icontains=fxInicio,tipoActivacion__tipo__icontains=tipo)
					for x in ae:
						resultsEq.append([x.sucursal, x.tipoActivacion.tipo, x.equipo.detallesEquipo.marca.marca.title()+' '+x.equipo.detallesEquipo.modelo.title(),str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion)])
					for x in ax:
						resultsExp.append([x.sucursal, x.tipoActivacion.tipo,str(x.express.icc),x.express.noCell,x.empleado.curp,str(x.fxActivacion)])

					query = "Fecha : "+str(fxInicio)+" Activacion : "+str(tipo)
				
				exportar = request.POST.get('excel','')
				if exportar == 'Exportar':
					result = resultsEq
					result2 = resultsExp
					try:
						return export_To_Excel_ActivacionG(query,result,result2,'Todos')
					except :
						info = "No se genero su Archivo."

			else:
				form = 	reporteCompleto(request.POST or None)
				info = "Por favor, elija un tipo de Activacion y/o revise las fechas, sea en orden inicial y final."
		paginator1 = Paginator(resultsEq, 50)
		paginator2 = Paginator(resultsExp, 50)

		peq = None
		pex = None
		
		try:
			peq = paginator1.page(pag1)
		except PageNotAnInteger:
			peq= paginator1.page(1)
		except EmptyPage:
			peq = paginator1.page(paginator1.num_pages)

		try:
			pex = paginator2.page(pag2)
		except PageNotAnInteger:
			pex= paginator2.page(1)
		except EmptyPage:
			pex = paginator2.page(paginator2.num_pages)
		
		ctx = {'form':form,'query':query, 'info':info, 'resultsEq':peq, 'resultsExp': pex,'nivel':nivel}
		return render_to_response('admingral/gerente_reporteConsultar.html',ctx,context_instance=RequestContext(request))		
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def planes_solicitudes_todos_view(request):
	nivel=Permiso(request.user,[0,1])
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

		paginator = Paginator(gaara, 30)
		
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
				return render_to_response('admingral/solicitudCompleta.html',ctx,context_instance=RequestContext(request))
					

		ctx = {'solicitudes':solicitudes,'query':query,'info':info, 'nivel':nivel}
		return render_to_response('admingral/seguimientoPlanes.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def planes_servicios_reportes_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		info =""
		
		pagina = request.GET.get('pagina','')
		gaara=None
		gaara = ServiciosPlan.objects.all().order_by('fxSolicitud').order_by('sucursal').order_by('solicitante').order_by('fxAtencion')

		if request.method == "POST":
			fxInicio 	= request.POST.get('fxInicio','')
			fxFinal 	= request.POST.get('fxFinal','')
			try:
				if fxFinal and fxInicio:
					gaara = ServiciosPlan.objects.filter(fxSolicitud__range=[fxInicio,fxFinal]).order_by('fxSolicitud').order_by('sucursal').order_by('solicitante').order_by('fxAtencion')
				else:
					gaara = ServiciosPlan.objects.filter(fxSolicitud__icontains=fxInicio).order_by('fxSolicitud').order_by('sucursal').order_by('solicitante').order_by('fxAtencion')
			except :
				info = "Seleccione un rango de fechas"				
		
		paginator = Paginator(gaara, 30)
		solicitudes=None
		try:
			solicitudes = paginator.page(pagina)
		except PageNotAnInteger:
			solicitudes = paginator.page(1)
		except EmptyPage:
			solicitudes = paginator.page(paginator.num_pages)
		
		ctx = {'solicitudes':solicitudes,'info':info, 'nivel':nivel}
		return render_to_response('admingral/reporteServicios.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #Yet
@login_required(login_url='/')
def planes_portabilidades_consultar_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		info =""
		buscar = True
		results = []

		pag1=request.GET.get('pagina','')
		
		msgs = Portabilidad.objects.all().order_by('fxIngreso').order_by('cliente').order_by('sucursal').order_by('estado')

		if request.method == "POST":
			fxInicio 	= request.POST.get('fxInicio','')
			fxFinal 	= request.POST.get('fxFinal','')
			try:
				if fxFinal and fxInicio:
					msgs = Portabilidad.objects.filter(fxIngreso__range=[fxInicio,fxFinal]).order_by('cliente').order_by('sucursal').order_by('estado')
					query = "Entre fechas : "+str(fxInicio)+" y "+str(fxFinal)
				else:
					msgs = Portabilidad.objects.filter(fxIngreso__icontains=fxInicio).order_by('cliente').order_by('sucursal').order_by('estado')
					query = "De Fecha : "+str(fxInicio)
			except :
				info = "Seleccione un rango de fechas inicial y final correctamente."
		
		paginator1 = Paginator(msgs, 50)

		pPortas=None
		
		try:
			pPortas = paginator1.page(pag1)
		except PageNotAnInteger:
			pPortas= paginator1.page(1)
		except EmptyPage:
			pPortas = paginator1.page(paginator1.num_pages)
		
		ctx = {'buscar':buscar,"results": pPortas,'info':info, 'nivel':nivel}
		return render_to_response('admingral/solicitudPortabilidad.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def planes_planes_nuevo_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		info = ""
		form = addPlan()
		form2 = addDetallePlan()

		if request.method == "POST":
			form = addPlan(request.POST or None)
			form2 = addDetallePlan(request.POST or None)
			if form.is_valid() and form2.is_valid():
				llamaPaga	= form2.cleaned_data['llamaPaga']
			  	recibePaga	= form2.cleaned_data['recibePaga']
			  	tarjCred 	= form2.cleaned_data['tarjCred']
			  	plazoMin	= form2.cleaned_data['plazoMin']
			  	plazoLibre	= form2.cleaned_data['plazoLibre']
			  	minInc		= form2.cleaned_data['minInc']
			  	minAd	 	= form2.cleaned_data['minAd']
			  	pagoVent	= form2.cleaned_data['pagoVent']
			  	pico	 	= form2.cleaned_data['pico']
			  	noPico	 	= form2.cleaned_data['noPico']
			  	minRoaming	= form2.cleaned_data['minRoaming']
			  	minNal	 	= form2.cleaned_data['minNal']
			  	cargoFijo	= form2.cleaned_data['cargoFijo']
			  	otros	 	= form2.cleaned_data['otros']
			  	limConsumo	= form2.cleaned_data['limConsumo']
			  	program	 	= form2.cleaned_data['program']
			  	enGarantia	= form2.cleaned_data['enGarantia']

			  	plan 			= form.cleaned_data['plan']
				costo 			= form.cleaned_data['costo']
				tiempoGarantia 	= form.cleaned_data['tiempoGarantia']
				equiposGratis 	= form.cleaned_data['equiposGratis']
				comision		= form.cleaned_data['comision']
				try:
					with transaction.atomic():
						a = DetallePlan()
						a.llamaPaga	= llamaPaga
					  	a.recibePaga = recibePaga
					  	a.tarjCred 	= tarjCred
					  	a.plazoMin	= plazoMin
					  	a.plazoLibre	= plazoLibre
					  	a.minInc		= minInc
					  	a.minAd	 	= minAd
					  	a.pagoVent	= pagoVent
					  	a.pico	 	= pico
					  	a.noPico	 	= noPico
					  	a.minRoaming	= minRoaming
					  	a.minNal	 	= minNal
					  	a.cargoFijo	= cargoFijo
					  	a.otros	 	= otros
					  	a.limConsumo	= limConsumo
					  	a.program	 	= program
					  	a.enGarantia	= enGarantia
					  	a.save()

						b = Plan()
						b.plan 			 = plan.title()
						b.costo 		 = costo
						b.tiempoGarantia = tiempoGarantia
						b.detallePlan 	= a
						b.equiposGratis = equiposGratis.title()
						b.comision	= comision
						b.save()
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'


				info = "Se ha registrado correctamente el plan "+ b.plan
				form = addPlan()
				form2 = addDetallePlan()

		ctx = {'nivel':nivel,'form':form,'form2':form2, 'info':info,}
		return render_to_response('admingral/addPlan.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def planes_planes_actualizar_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		r_items=None
		info=''
		query = request.GET.get('q','')
		pag1 =  request.GET.get('pagina','')
		r_items=Plan.objects.filter(activo=True)

		if query:
			qset=(Q(plan__icontains=query)|
				Q(costo__icontains=query)|
				Q(equiposGratis__icontains=query))
			r_items=Plan.objects.filter(qset,activo=True).distinct()

		if request.method == "GET":
			if request.GET.get('del'):
				s = request.GET.get('del','')
				if s:
					try:
						with transaction.atomic():
							upd = Plan.objects.get(id= s)
							upd.activo = False
							upd.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

			if request.GET.get('upd'):
				s = request.GET.get('upd','')
				if s:
					upd = Plan.objects.get(id= s)
					dup = DetallePlan.objects.get(id=upd.detallePlan.id)
					form = addPlan(instance=upd)
					form2 = addDetallePlan(instance=dup)
					ctx={'nivel':nivel,'form':form,'form2':form2,'cve':s,'info':info}
					return render_to_response('admingral/catalogoPlanes.html', ctx,context_instance=RequestContext(request))



		if request.method == "POST":
			ide=request.POST.get('updP','')
			upd = Plan.objects.get(id= ide)
			dup = DetallePlan.objects.get(id=upd.detallePlan.id)
			form = addPlan(request.POST, instance=upd)
			form2 = addDetallePlan(request.POST, instance=dup)
			if form.is_valid() and form2.is_valid():
				try:
					with transaction.atomic():
						form2.save()
						form.save()
						info = "Se ha actualizado correctamente el plan"
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
			else:
				form = addPlan(request.POST, instance=upd)
				form2 = addDetallePlan(request.POST, instance=dup)
				ctx={'nivel':nivel,'form':form,'form2':form2,'cve':s,'info':info}
				return render_to_response('admingral/catalogoPlanes.html', ctx,context_instance=RequestContext(request))


		paginator1 = Paginator(r_items, 50)
		pPlan =None
		try:
			pPlan  = paginator1.page(pag1)
		except PageNotAnInteger:
			pPlan = paginator1.page(1)
		except EmptyPage:
			pPlan  = paginator1.page(paginator1.num_pages)

		
		ctx={'nivel':nivel, 'query':query, 'r_items':pPlan, 'info':info}
		return render_to_response('admingral/catalogoPlanes.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def servicios_catalogo_reporte_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		
		form = updReparacion()
		query = ''
		results = []
		info =""
		mostrarForm = False
		catalogo = Reparacion.objects.all()
		itemSeleccionado = 0
		
		pagina=request.GET.get('pagina','')

		paginator = Paginator(catalogo, 50)
		nReparaciones=len(catalogo)
		reparaciones=None
		try:
			reparaciones = paginator.page(pagina)
		except PageNotAnInteger:
			reparaciones = paginator.page(1)
		except EmptyPage:
			reparaciones = paginator.page(paginator.num_pages)

		if request.method == "GET":
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					qset = (Q(descripcion__icontains=query) | Q(tipoReparacion__tipo__icontains=query))
					results = Reparacion.objects.filter(qset).distinct()
					if results:
						info = "Resultados"
				else:
					results = []
			
				ctx = {"results": results,"query": query, 'reparaciones':reparaciones ,'info':info, 'nivel':nivel}
				return render_to_response('admingral/catalogoReparaciones.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('updRep'):
				itemSeleccionado = request.GET.get('updRep','')
				if itemSeleccionado:
					lerep = Reparacion.objects.get(id = itemSeleccionado)
					
					form = updReparacion({'key':lerep.id, 'descripcion':lerep.descripcion,'monto':lerep.monto})
					info = "Actualizar Reparacion"
					mostrarForm = True

				ctx = {'form':form, 'info':info, 'mostrar':mostrarForm,'nivel':nivel}
				return render_to_response('admingral/catalogoReparaciones.html',ctx,context_instance=RequestContext(request))

		if request.method == "POST":

			form = updReparacion(request.POST or None)
			mostrarForm = True
			if form.is_valid():
				descripcion	= form.cleaned_data['descripcion']
				monto 		= form.cleaned_data['monto']
				activo 	= form.cleaned_data['activo']
				key = form.cleaned_data['key']
				
				try:
					upd = Reparacion.objects.get(id= key)
					#descripcion repetida en la misma seccion
					g = Reparacion.objects.get(descripcion=descripcion.title(),tipoReparacion__tipo=upd.tipoReparacion.tipo)
					if g:
						info ="Lo sentimos, ya se encuentra registrada una descripcion similar en los datos, en la misma seccion."
						mostrarForm = True
						form = updReparacion(request.POST)
					else:
						try:
							with transaction.atomic():
								upd = Reparacion.objects.get(id= key)
								upd.descripcion = descripcion.title()
								upd.monto = monto
								upd.activo = activo
								upd.save()
								info = "Se ha Actualizado correctamente."
								mostrarForm = False
						except :
							info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
						
				except :
					try:
						with transaction.atomic():
							upd = Reparacion.objects.get(id= key)
							upd.descripcion = descripcion.title()
							upd.monto = monto
							upd.activo = activo
							upd.save()
							info = "Se ha Actualizado correctamente."
							mostrarForm = False
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
				
				ctx = {'form':form, 'info':info, 'mostrar':mostrarForm,'reparaciones':reparaciones ,'nivel':nivel}
				return render_to_response('admingral/catalogoReparaciones.html',ctx,context_instance=RequestContext(request))

			else:
				form = updReparacion(request.POST)
				info ="Verifique la informacion, no se han actualizado correctamente los datos"
				mostrarForm = True

		ctx = {"results": results,"query": query, 'form':form,'mostrar':mostrarForm ,'reparaciones':reparaciones ,'info':info, 'nivel':nivel}
		return render_to_response('admingral/catalogoReparaciones.html',ctx,context_instance=RequestContext(request))		

	else:
		return HttpResponseRedirect('/NoTienePermiso')

# por desuso se borra - servicios_clientes_nuevo_view - se hace respaldo aparte


#listo #yet
@login_required(login_url='/')
def servicios_clientes_nuevo_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		form = addClienteServicioForm()
		info = ""
		clientes = ClienteServicio.objects.all().order_by('fxIngreso').reverse()[:5]
		
		if request.method == "POST":
			form = addClienteServicioForm(request.POST or None)
			if form.is_valid():
				
				nombre 		= form.cleaned_data['nombre']
				direccion 	= form.cleaned_data['direccion']
				colonia 	= form.cleaned_data['colonia']
				ciudad  	= form.cleaned_data['ciudad']
				estado  	= form.cleaned_data['estado']
				
				zzz = agregarCiudades(colonia,ciudad,estado,None)
				try:
					with transaction.atomic():
						a = ClienteServicio()
						a.nombre 		= (nombre).title()
						a.direccion 	= (direccion).title()
						a.colonia = Colonia.objects.get(id=zzz[0])
						a.ciudad = Ciudad.objects.get(id=zzz[1])
						a.sucursal 	= mysucursal
						a.tipoCliente = 'Servicio'
						a.folio = nvofolioCliente()
						a.save()

						info ="Se ha Guardado con Exito, Folio cliente: "+ a.folio
						form = addClienteServicioForm()
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
				
				ctx = {'form':form,'clientes':clientes ,'info':info,'nivel':nivel}
				return render_to_response('admingral/addClienteReparacion.html', ctx, context_instance=RequestContext(request))

			else:
				form = addClienteServicioForm(request.POST)
				info ="Verifique la informacion, no se han registrado los datos"

		ctx = {'form':form,'clientes':clientes ,'info':info,'nivel':nivel}
		return render_to_response('admingral/addClienteReparacion.html', ctx, context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def servicios_clientes_historial_view(request):
	nivel=Permiso(request.user,[0,1])
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
				return render_to_response('admingral/historialClienteReparacion.html',ctx,context_instance=RequestContext(request))

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
		return render_to_response('admingral/historialClienteReparacion.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def servicios_seguimiento_flexeo_porta_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		formC = updCostoPorta()
		formS = updGratisFlexeo()
		mostrar = False
		mostrarf = False
		buscar = True
		query = ''
		info =""
		scosto = FlexeoEquipo.objects.filter(portabilidad__cliente__tipoCliente__icontains='Portabilidad sin costo')
		ccosto = EquipoReparacion.objects.filter(cliente__tipoCliente__icontains='Portabilidad con costo')

		pag1=request.GET.get('pagCosto','')
		pag2=request.GET.get('pagSCosto','')
		query = request.GET.get('q', '')

		if query:
			qset = (Q(portabilidad__cliente__nombre__icontains=query) | 
				Q(portabilidad__cliente__folio__icontains=query) | 
				Q(portabilidad__cliente__direccion__icontains=query) | 
				Q(portabilidad__cliente__sucursal__nombre__icontains=query))
			qset2 = (Q(cliente__nombre__icontains=query) | 
				Q(cliente__folio__icontains=query) | 
				Q(cliente__direccion__icontains=query) | 
				Q(cliente__sucursal__nombre__icontains=query))
			scosto = FlexeoEquipo.objects.filter(qset,portabilidad__cliente__tipoCliente__icontains='Portabilidad sin costo')
			ccosto = EquipoReparacion.objects.filter(qset2,cliente__tipoCliente__icontains='Portabilidad con costo')

		paginator1 = Paginator(ccosto, 50)
		paginator2 = Paginator(scosto, 50)
		nCcosto=len(ccosto)
		nSCosto=len(scosto)
		pCosto=None
		pSCosto=None
		try:
			pCosto = paginator1.page(pag1)
		except PageNotAnInteger:
			pCosto = paginator1.page(1)
		except EmptyPage:
			pCosto = paginator1.page(paginator1.num_pages)

		try:
			pSCosto = paginator2.page(pag2)
		except PageNotAnInteger:
			pSCosto = paginator2.page(1)
		except EmptyPage:
			pSCosto = paginator2.page(paginator2.num_pages)

		if request.method == "GET":
			#con costo
			if request.GET.get('updCPorta'):
				query = request.GET.get('updCPorta', '')
				if query:
					ccosto = EquipoReparacion.objects.get(id = query)
					formC = updCostoPorta({'key':ccosto.id,'cliente':ccosto.cliente.nombre,
						'marcaModelo':ccosto.marcaModelo,'imei':ccosto.imei,'falla': ccosto.falla,
						'observacion':ccosto.observacion,'edoActual':ccosto.estado.estado })
					mostrar = False
					buscar = False
					mostrarf = True
					ctx = {'buscar':buscar,'mostrarf':mostrarf, 'mostrar':mostrar, 'formS':formS, 'formC':formC, 'info':info, 'nivel':nivel}
					return render_to_response('admingral/seguimientoFlexeoPorta.html',ctx,context_instance=RequestContext(request))

			#sin costo 
			if request.GET.get('updSPorta'):
				query = request.GET.get('updSPorta', '')
				if query:
					scosto = FlexeoEquipo.objects.get(id = query)
					formS = updGratisFlexeo({'key':scosto.id,'cliente':scosto.portabilidad.cliente.nombre ,
						'marcaModelo':scosto.marcaModelo, 'observaciones':scosto.observaciones,'edoActual':scosto.estado.estado})
					mostrar = True 
					buscar = False
					mostrarf = True

					ctx = {'buscar':buscar,'mostrarf':mostrarf, 'mostrar':mostrar, 'formS':formS, 'formC':formC, 'info':info, 'nivel':nivel}
					return render_to_response('admingral/seguimientoFlexeoPorta.html',ctx,context_instance=RequestContext(request))

		if request.method == "POST":
			
			formC = updCostoPorta( request.POST or None)
			formS = updGratisFlexeo( request.POST or None)
			today = datetime.now() #fecha actual
			dateFormat = today.strftime("%d-%m-%Y") # fecha con formato
			s = ' Revisado por: ' + str(request.user)
			
			if formC.is_valid():
				key 		= formC.cleaned_data['key']
				falla 		= formC.cleaned_data['falla']
				observacion = formC.cleaned_data['observacion']
				estado 		= formC.cleaned_data['estado']

				try:
					with transaction.atomic():
						ccosto = EquipoReparacion.objects.get(id = key)
						ccosto.falla 		= falla
						ccosto.observacion = observacion + str(s)
						ccosto.estado 		= EstadoReparacion.objects.get(id= estado) 
						ccosto.fxRevision 	= today
						ccosto.save()
						info = "Flexeo. El Registro se ha actualizado con exito: " + ccosto.cliente.nombre
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
				
				ctx = {'pCosto':pCosto, 'pSCosto':pSCosto,'buscar':True,'nivel':nivel,'info':info}
				return render_to_response('admingral/seguimientoFlexeoPorta.html',ctx,context_instance=RequestContext(request))

			elif formS.is_valid():
				key 		= formS.cleaned_data['key']
				observaciones = formS.cleaned_data['observaciones']
				fxCliente 	= formS.cleaned_data['fxCliente']
				estado 		= formS.cleaned_data['estado']
				try:
					with transaction.atomic():
						scosto = FlexeoEquipo.objects.get(id = key)
						scosto.observaciones = observaciones  + str(s)
						scosto.fxTecnico 	= today.strftime("%Y-%m-%d") 
						if fxCliente:
							scosto.fxCliente 	= fxCliente
						scosto.estado 		= EstadoReparacion.objects.get(id= estado) 
						scosto.fxRevision 	= today
						scosto.save()
						info = "Flexeo. El Registro se ha actualizado con exito: " + scosto.portabilidad.cliente.nombre
						buscar = True
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
				
				ctx = {'pCosto':pCosto, 'pSCosto':pSCosto,'buscar':True,'nivel':nivel,'info':info}
				return render_to_response('admingral/seguimientoFlexeoPorta.html',ctx,context_instance=RequestContext(request))

			else:
				info = "Verifique sus datos, actualizacion no realizada"
				formC = updCostoPorta( request.POST)
				formS = updGratisFlexeo( request.POST)
				mostrarf = True
				buscar = False
			
				ctx = {'buscar':buscar,'mostrarf':mostrarf, 'boton':boton ,'mostrar':mostrar, 'formS':formS, 'formC':formC, 'info':info, 'nivel':nivel}
				return render_to_response('admingral/seguimientoFlexeoPorta.html',ctx,context_instance=RequestContext(request))

		ctx = {'pCosto':pCosto, 'pSCosto':pSCosto,'query':query,'buscar':True,'nivel':nivel,'info':info}
		return render_to_response('admingral/seguimientoFlexeoPorta.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def servicios_seguimiento_flexeos_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		formC = updCostoPorta()
		info =""
		buscar = True
		mostrar = False
		mostrarf = False
		query = ''
		results = []

		ccosto = EquipoReparacion.objects.filter(cliente__tipoCliente__icontains='Servicio', reparacion__tipoReparacion__tipo__icontains='flexeos')
		pagina=request.GET.get('pagina','')
		query = request.GET.get('q', '')
		if query:
			qset = (Q(cliente__nombre__icontains=query) | Q(sucursal__nombre__icontains=query) | Q(cliente__folio__icontains=query))
			ccosto = EquipoReparacion.objects.filter(qset,cliente__tipoCliente__icontains='Servicio', reparacion__tipoReparacion__tipo__icontains='flexeos').distinct()

		paginator = Paginator(ccosto, 50)
		nFlexeos=len(ccosto)
		flexeosp=None
		try:
			flexeosp = paginator.page(pagina)
		except PageNotAnInteger:
			flexeosp = paginator.page(1)
		except EmptyPage:
			flexeosp = paginator.page(paginator.num_pages)

		if request.method == "GET":
			if request.GET.get('upd'):
				query = request.GET.get('upd', '')
				if query:
					ccosto = EquipoReparacion.objects.get(id = query)
					formC = updCostoPorta({'key':ccosto.id,'cliente':ccosto.cliente.nombre,
						'marcaModelo':ccosto.marcaModelo,'imei':ccosto.imei,'falla': ccosto.falla,
						'observacion':ccosto.observacion,'edoActual':ccosto.estado.estado })
					mostrar = True
					buscar = False
					mostrarf = True
					ctx = {'buscar':buscar,'mostrarf':mostrarf,'mostrar':mostrar,'formC':formC ,'info':info, 'nivel':nivel}
					return render_to_response('admingral/seguimientoFlexeoTecnico.html',ctx,context_instance=RequestContext(request))

		if request.method == "POST":
			
			formC = updCostoPorta( request.POST or None)
			today = datetime.now() #fecha actual
			dateFormat = today.strftime("%d-%m-%Y") # fecha con formato
			s = ' Revisado por: ' + str(request.user)
			
			if formC.is_valid():
				key 		= formC.cleaned_data['key']
				falla 		= formC.cleaned_data['falla']
				observacion = formC.cleaned_data['observacion']
				estado 		= formC.cleaned_data['estado']
				try:
					with transaction.atomic():
						ccosto = EquipoReparacion.objects.get(id = key)
						ccosto.falla 		= falla
						ccosto.observacion = observacion + str(s)
						ccosto.estado 		= EstadoReparacion.objects.get(id= estado) 
						ccosto.fxRevision 	= today
						ccosto.save()
						

						info = "Flexeo con costo. El Registro se ha actualizado con exito: " + ccosto.cliente.nombre
						boton = False
						buscar = True
						mostrarf = False
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'


				ctx = {'buscar':True,'flexeos':flexeosp,'info':info, 'nivel':nivel}
				return render_to_response('admingral/seguimientoFlexeoTecnico.html',ctx,context_instance=RequestContext(request))

			else:
				info = "Verifique sus datos, actualizacion no realizada"
				formC = updCostoPorta( request.POST)
				mostrarf = True
				buscar = False
				boton = True
				
				ctx = {'mostrarf':mostrarf,'mostrar':mostrar,'formC':formC ,'info':info, 'nivel':nivel}
				return render_to_response('admingral/seguimientoFlexeoTecnico.html',ctx,context_instance=RequestContext(request))
			
		ctx = {'buscar':True,'flexeos':flexeosp,'info':info, 'nivel':nivel}
		return render_to_response('admingral/seguimientoFlexeoTecnico.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def servicios_seguimiento_reparaciones_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		
		formC = updCostoPorta()
		info =""
		mostrar = False
		buscar = True
		mostrarf = False
		query = ''
		results = []
		ccosto = None
		pagina = request.GET.get('pagina','')
		query  = request.GET.get('q','')
		reparaciones=None
		nReparaciones=0
		if query:
			qset=(Q(cliente__nombre__icontains=query) |
			 Q(sucursal__nombre__icontains=query) | 
			 Q(cliente__folio__icontains=query))
			ccosto = EquipoReparacion.objects.filter(qset, cliente__tipoCliente__icontains='Servicio')
		else:
			qset = (Q(reparacion__tipoReparacion__tipo__icontains='Carga de Software')|Q(reparacion__tipoReparacion__tipo__icontains='Reparacion Fisica'))
			ccosto = EquipoReparacion.objects.filter(qset, cliente__tipoCliente__icontains='Servicio')	

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
			if request.GET.get('upd'):
				query = request.GET.get('upd', '')
				if query:
					ccosto = EquipoReparacion.objects.get(id = query)
					formC = updCostoPorta({'key':ccosto.id,'cliente':ccosto.cliente.nombre,
						'marcaModelo':ccosto.marcaModelo,'imei':ccosto.imei,'falla': ccosto.falla,
						'observacion':ccosto.observacion,'edoActual':ccosto.estado.estado })
					mostrar = True
					buscar = False
					mostrarf = True

					ctx = {'buscar':buscar,'mostrarf':mostrarf,'mostrar':mostrar,'formC':formC ,'info':info, 'nivel':nivel}
					return render_to_response('admingral/seguimientoReparacionesFisicas.html',ctx,context_instance=RequestContext(request))

		if request.method == "POST":
			
			formC = updCostoPorta( request.POST or None)
			today = datetime.now() #fecha actual
			dateFormat = today.strftime("%d-%m-%Y") # fecha con formato
			s = ' Revisado por: ' + str(request.user)
			
			if formC.is_valid():
				key 		= formC.cleaned_data['key']
				falla 		= formC.cleaned_data['falla']
				observacion = formC.cleaned_data['observacion']
				estado 		= formC.cleaned_data['estado']
				try:
					with transaction.atomic():
						ccosto = EquipoReparacion.objects.get(id = key)
						ccosto.falla 		= falla
						ccosto.observacion = observacion + str(s)
						ccosto.estado 		= EstadoReparacion.objects.get(id= estado) 
						ccosto.fxRevision 	= today
						ccosto.save()

						info = "El Registro se ha actualizado con exito: " + ccosto.cliente.nombre
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				ctx = {'buscar':True,'reparaciones':reparacionesp,'info':info, 'nivel':nivel}
				return render_to_response('admingral/seguimientoReparacionesFisicas.html',ctx,context_instance=RequestContext(request))

			else:
				info = "Verifique sus datos, actualizacion no realizada"
				formC = updCostoPorta( request.POST)
				mostrarf = True
				buscar = False
				boton = True
				ctx = {'buscar':buscar,'mostrarf':mostrarf, 'boton':boton ,'mostrar':mostrar, 'formC':formC, 'info':info, 'nivel':nivel}
				return render_to_response('servicios/seguimientoReparacionesFisicas.html',ctx,context_instance=RequestContext(request))

		ctx = {'buscar':True,'reparaciones':reparacionesp,'query':query,'info':info, 'nivel':nivel}
		return render_to_response('admingral/seguimientoReparacionesFisicas.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def servicios_inventario_accesorios_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		pagina=request.GET.get('pagina','')
		b_item=request.GET.get('item','')
		items=None
		nItems=0
		if b_item:
			qset=(Q(accesorio__codigoBarras__icontains=b_item)|
			Q(accesorio__detallesAccesorio__marca__marca__icontains=b_item)|
			Q(sucursal__nombre__icontains=b_item)|
			Q(accesorio__detallesAccesorio__descripcion__icontains=b_item))
			items=AlmacenAccesorio.objects.filter(qset,sucursal__tipoSucursal__tipo='Servicios',estado=True).order_by('accesorio__codigoBarras')
		else:
			qset=(Q(accesorio__detallesAccesorio__seccion__seccion__icontains='REFACCIONES')|Q(accesorio__detallesAccesorio__seccion__seccion__icontains='EQUIPOS OBSOLETOS'))
			items=AlmacenAccesorio.objects.filter(estado=True,sucursal__tipoSucursal__tipo='Servicios').exclude(qset)#
		paginator = Paginator(items, 50)
		nItems=len(items)
		itemsp=None
		try:
			itemsp = paginator.page(pagina)
		except PageNotAnInteger:
			itemsp = paginator.page(1)
		except EmptyPage:
			itemsp = paginator.page(paginator.num_pages)

		ctx={'nivel':nivel,'cosa':'Accesorios','items':itemsp, 'b_item':b_item,  'nItems':nItems}
		return render_to_response('admingral/existenciasAccesorioServicios.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def servicios_inventario_refacciones_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		pagina=request.GET.get('pagina','')
		b_item=request.GET.get('item','')
		items=None
		nItems=0
		if b_item:
			qset=(Q(accesorio__codigoBarras__icontains=b_item)|
			Q(accesorio__detallesAccesorio__marca__marca__icontains=b_item)|
			Q(sucursal__nombre__icontains=b_item)|
			Q(accesorio__detallesAccesorio__descripcion__icontains=b_item))
			items=AlmacenAccesorio.objects.filter(qset,sucursal__tipoSucursal__tipo='Servicios',accesorio__detallesAccesorio__seccion__seccion__icontains='REFACCIONES',estado=True).order_by('accesorio__codigoBarras')
		else:
			qset=(Q(accesorio__detallesAccesorio__seccion__seccion__icontains='EQUIPOS OBSOLETOS'))
			items=AlmacenAccesorio.objects.filter(sucursal__tipoSucursal__tipo='Servicios',accesorio__detallesAccesorio__seccion__seccion__icontains='REFACCIONES',estado=True).exclude(qset)
		paginator = Paginator(items, 50)
		nItems=len(items)
		itemsp=None
		try:
			itemsp = paginator.page(pagina)
		except PageNotAnInteger:
			itemsp = paginator.page(1)
		except EmptyPage:
			itemsp = paginator.page(paginator.num_pages)

		ctx={'nivel':nivel,'cosa':'Refacciones','items':itemsp, 'b_item':b_item,  'nItems':nItems}

		return render_to_response('admingral/existenciasAccesorioServicios.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo #yet
@login_required(login_url='/')
def servicios_inventario_eqobsoletos_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		pagina=request.GET.get('pagina','')
		b_item=request.GET.get('item','')
		items=None
		nItems=0
		if b_item:
			qset=(Q(accesorio__codigoBarras__icontains=b_item)|
			Q(accesorio__detallesAccesorio__marca__marca__icontains=b_item)|
			Q(sucursal__nombre__icontains=b_item)|
			Q(accesorio__detallesAccesorio__descripcion__icontains=b_item))
			items=AlmacenAccesorio.objects.filter(qset,sucursal__tipoSucursal__tipo='Servicios',accesorio__detallesAccesorio__seccion__seccion__icontains='EQUIPOS OBSOLETOS',estado=True).order_by('accesorio__codigoBarras')
		else:
			qset=(Q(accesorio__detallesAccesorio__seccion__seccion__icontains='REFACCIONES'))
			items=AlmacenAccesorio.objects.filter(sucursal__tipoSucursal__tipo='Servicios',accesorio__detallesAccesorio__seccion__seccion__icontains='EQUIPOS OBSOLETOS',estado=True).exclude(qset)
		paginator = Paginator(items, 50)
		nItems=len(items)
		itemsp=None
		try:
			itemsp = paginator.page(pagina)
		except PageNotAnInteger:
			itemsp = paginator.page(1)
		except EmptyPage:
			itemsp = paginator.page(paginator.num_pages)

		ctx={'nivel':nivel,'cosa':'Equipos Obsoletos','items':itemsp, 'b_item':b_item,  'nItems':nItems}

		return render_to_response('admingral/existenciasAccesorioServicios.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

def folioMensage(sucursal):
	generarFolio = None
	today = datetime.now() #fecha actual
	dateFormat = today.strftime("%Y-%m-%d") # fecha con formato
	i = 1
	nuevo = False
	while nuevo == False:
		
		dateFormat2 = today.strftime("%Y.%m.%d")
		generarFolio = 'M'+ str(sucursal) +'-' + str(dateFormat2) + '-' +str(i)
		try:
			v = SolicitudNuevoProducto.objects.get(folio=generarFolio)
			nuevo = False
			i = i + 1
		except SolicitudNuevoProducto.DoesNotExist:
			nuevo = True
	#'''
	return generarFolio

def miSucursal(user):
	_usuario = Usuario.objects.get(user=user)
	myempleado 			= _usuario.empleado
	vendedorSucursal 	= VendedorSucursal.objects.get(empleado=myempleado)
	mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

	return mysucursal

#listo #yet
@login_required(login_url='/')
def reportes_pro_sin_mov_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		info = ""
		query  = request.GET.get('q','')
		pag1=request.GET.get('pagina','')
		msgs = []
		fx2 = datetime.now().date()
		#equipos
		eq = AlmacenEquipo.objects.filter(estado=True).distinct()
		for x in eq:
			fx1 = (x.fxTransf).date()
			diff = fx2 - fx1
			item = 'Equipo '+x.equipo.detallesEquipo.marca.marca+' '+x.equipo.detallesEquipo.modelo+' '+x.equipo.detallesEquipo.color+' '+str(x.equipo.imei)
			if diff.days >= 64 and diff.days < 90:
				msgs.append([diff.days,2,item,x.sucursal.nombre,str(x.equipo.imei),'equipo'])
			else:
				msgs.append([diff.days,3,item,x.sucursal.nombre,str(x.equipo.imei),'equipo'])
		#express
		ex = AlmacenExpres.objects.filter(estado=True).distinct()
		for x in ex:
			fx1 = (x.fxTransf).date()
			diff = fx2 - fx1
			item = 'Expres '+str(x.expres.icc)
			if diff.days >= 64 and diff.days < 90:
				msgs.append([diff.days,2,item,x.sucursal.nombre,str(x.expres.icc),'expres'])
			else:
				msgs.append([diff.days,3,item,x.sucursal.nombre,str(x.expres.icc),'expres'])
		#accesorios
		ac = AlmacenAccesorio.objects.filter(estado=True).distinct()
		for x in ac:
			fx1 = (x.fxTransf).date()
			diff = fx2 - fx1
			item = 'Accesorio '+x.accesorio.detallesAccesorio.seccion.seccion+' '+x.accesorio.detallesAccesorio.marca.marca+' '+x.accesorio.detallesAccesorio.descripcion+' '+str(x.accesorio.codigoBarras)
			if diff.days >= 64 and diff.days < 90:
				msgs.append([diff.days,2,item,x.sucursal.nombre,str(x.accesorio.codigoBarras),'accesorio'])
			else:
				msgs.append([diff.days,3,item,x.sucursal.nombre,str(x.accesorio.codigoBarras),'accesorio'])
		#fichas
		fic = AlmacenFicha.objects.filter(estado=True).distinct()
		for x in fic:
			fx1 = (x.fxTransf).date()
			diff = fx2 - fx1
			item = 'Ficha '+str(x.ficha.nominacion.nominacion)+' '+str(x.ficha.folio)
			if diff.days >= 64 and diff.days < 90:
				msgs.append([diff.days,2,item,x.sucursal.nombre,str(x.ficha.folio),'ficha'])
			else:
				msgs.append([diff.days,3,item,x.sucursal.nombre,str(x.ficha.folio),'ficha'])

		if query:
			msgs = []
			xqset=(Q(sucursal__nombre__icontains=query)|Q(expres__icc__icontains=query))
			fqset=(Q(sucursal__nombre__icontains=query)|Q(ficha__folio__icontains=query))
			eqset=(Q(sucursal__nombre__icontains=query)|
				Q(equipo__detallesEquipo__marca__marca__icontains=query)|
				Q(equipo__detallesEquipo__modelo__icontains=query)|
				Q(equipo__detallesEquipo__color__icontains=query)|
				Q(equipo__imei__icontains=query))
			acset=(Q(sucursal__nombre__icontains=query)|
				Q(accesorio__detallesAccesorio__seccion__seccion__icontains=query)|
				Q(accesorio__codigoBarras__icontains=query)|
				Q(accesorio__detallesAccesorio__marca__marca__icontains=query))
			#equipos
			eq = AlmacenEquipo.objects.filter(eqset,estado=True).distinct()
			for x in eq:
				fx1 = (x.fxTransf).date()
				diff = fx2 - fx1
				item = 'Equipo '+x.equipo.detallesEquipo.marca.marca+' '+x.equipo.detallesEquipo.modelo+' '+x.equipo.detallesEquipo.color+' '+str(x.equipo.imei)
				if diff.days >= 64 and diff.days < 90:
					msgs.append([diff.days,2,item,x.sucursal.nombre,str(x.equipo.imei),'equipo'])
				else:
					msgs.append([diff.days,3,item,x.sucursal.nombre,str(x.equipo.imei),'equipo'])
			#express
			ex = AlmacenExpres.objects.filter(xqset,estado=True).distinct()
			for x in ex:
				fx1 = (x.fxTransf).date()
				diff = fx2 - fx1
				item = 'Expres '+str(x.expres.icc)
				if diff.days >= 64 and diff.days < 90:
					msgs.append([diff.days,2,item,x.sucursal.nombre,str(x.expres.icc),'expres'])
				else:
					msgs.append([diff.days,3,item,x.sucursal.nombre,str(x.expres.icc),'expres'])
			#accesorios
			ac = AlmacenAccesorio.objects.filter(acset,estado=True).distinct()
			for x in ac:
				fx1 = (x.fxTransf).date()
				diff = fx2 - fx1
				item = 'Accesorio '+x.accesorio.detallesAccesorio.seccion.seccion+' '+x.accesorio.detallesAccesorio.marca.marca+' '+x.accesorio.detallesAccesorio.descripcion+' '+str(x.accesorio.codigoBarras)
				if diff.days >= 64 and diff.days < 90:
					msgs.append([diff.days,2,item,x.sucursal.nombre,str(x.accesorio.codigoBarras),'accesorio'])
				else:
					msgs.append([diff.days,3,item,x.sucursal.nombre,str(x.accesorio.codigoBarras),'accesorio'])
			#fichas
			fic = AlmacenFicha.objects.filter(fqset,estado=True).distinct()
			for x in fic:
				fx1 = (x.fxTransf).date()
				diff = fx2 - fx1
				item = 'Ficha '+str(x.ficha.nominacion.nominacion)+' '+str(x.ficha.folio)
				if diff.days >= 64 and diff.days < 90:
					msgs.append([diff.days,2,item,x.sucursal.nombre,str(x.ficha.folio),'ficha'])
				else:
					msgs.append([diff.days,3,item,x.sucursal.nombre,str(x.ficha.folio),'ficha'])

		if request.method == "GET":
			if request.GET.get('upd'):
				s = request.GET.get('upd','')
				a = request.GET.get('tipoP','')
				if a and s:
					sucursal = miSucursal(request.user)
					n = None
					#producto tipo
					if a == 'equipo':
						#if True:
						#	if True:
						try:
							with transaction.atomic():
								x = Equipo.objects.get(imei=s)
								item = 'Equipo '+x.detallesEquipo.marca.marca+' '+x.detallesEquipo.modelo+' '+x.detallesEquipo.color+' '+str(x.imei)
								n = SolicitudNuevoProducto()
								n.folio = folioMensage(sucursal.id)
								n.nuevoProducto 	= "El producto "+item+" Se solicita Cambio de sucursal."
								n.sucursal 	= sucursal
								n.usuario 	= request.user
								n.estado	= EstadoMensaje.objects.get(estado__icontains='Sin revisar')
								n.save()
						except :
							info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

					elif a == 'expres':
						try:
							with transaction.atomic():
								x = Expres.objects.get(icc=s)
								item = 'expres '+str(x.icc)
								n = SolicitudNuevoProducto()
								n.folio = folioMensage(sucursal.id)
								n.nuevoProducto 	= "El producto "+item+" Se solicita Cambio de sucursal."
								n.sucursal 	= sucursal
								n.usuario 	= request.user
								n.estado	= EstadoMensaje.objects.get(estado__icontains='Sin revisar')
								n.save()
						except :
							info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'


					elif a == 'accesorio':
						try:
							with transaction.atomic():
								x = Accesorio.objects.get(codigoBarras=s)
								item = 'Accesorio '+x.detallesAccesorio.seccion.seccion+' '+x.detallesAccesorio.marca.marca+' '+x.detallesAccesorio.descripcion+' '+str(x.codigoBarras)
								n = SolicitudNuevoProducto()
								n.folio = folioMensage(sucursal.id)
								n.nuevoProducto 	= "El producto "+item+" Se solicita Cambio de sucursal."
								n.sucursal 	= sucursal
								n.usuario 	= request.user
								n.estado	= EstadoMensaje.objects.get(estado__icontains='Sin revisar')
								n.save()
						except :
							info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'


					elif a == 'ficha':
						try:
							with transaction.atomic():
								x = Ficha.objects.get(folio=s)
								item = 'ficha '+str(x.nominacion.nominacion)+' '+str(x.folio)
								n = SolicitudNuevoProducto()
								n.folio = folioMensage(sucursal.id)
								n.nuevoProducto 	= "El producto "+item+" Se solicita Cambio de sucursal."
								n.sucursal 	= sucursal
								n.usuario 	= request.user
								n.estado	= EstadoMensaje.objects.get(estado__icontains='Sin revisar')
								n.save()
						except :
							info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

					info = " Mensaje enviado a almacen, folio de su mensaje: "+str(n)

		msgs.sort(reverse=True)
		paginator1 = Paginator(msgs, 50)
		pMensages=None
		
		try:
			pMensages = paginator1.page(pag1)
		except PageNotAnInteger:
			pMensages= paginator1.page(1)
		except EmptyPage:
			pMensages = paginator1.page(paginator1.num_pages)

		ctx = {'productos':pMensages,'query':query ,'info':info,'nivel':nivel}
		return render_to_response('admingral/sinMovimiento.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def departamentos_reporte_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		info = ""
		query  = request.GET.get('q','')
		pag1=request.GET.get('pagina','')
		msgs = []
		msgs = Empleado.objects.filter(estadoEmpleado=True)
		if query:
			qset=(Q(curp__icontains=query) |
			 Q(nombre__icontains=query) | 
			 Q(aPaterno__icontains=query) | 
			 Q(aMaterno__icontains=query)|
			 Q(area__area__icontains=query) | 
			 Q(puesto__puesto__icontains=query))
			msgs = Empleado.objects.filter(qset,estadoEmpleado=True).order_by('area').order_by('puesto').order_by('nombre').distinct()

		paginator1 = Paginator(msgs, 25)
		pMensages=None
		
		try:
			pMensages = paginator1.page(pag1)
		except PageNotAnInteger:
			pMensages= paginator1.page(1)
		except EmptyPage:
			pMensages = paginator1.page(paginator1.num_pages)

		ctx = {'empleados':pMensages,'query':query,'info':info,'nivel':nivel}
		return render_to_response('admingral/departamentosEmpleados.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def sucursales_reporte_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		query  = request.GET.get('q','')
		pag1=request.GET.get('pag','')
		
		eventos = Sucursal.objects.all()#.exclude(id=mysucursal.id).order_by('nombre')

		if query:
			qset=(Q(nombre__icontains=query) |
			 Q(encargado__nombre__icontains=query) | 
			 Q(encargado__aPaterno__icontains=query) | 
			 Q(encargado__aMaterno__icontains=query) | 
			 Q(encargado__curp__icontains=query) | 
			 Q(zona__zona__icontains=query) | 
			 Q(direccion__icontains=query))
			eventos = Sucursal.objects.filter(qset) #.exclude(id=mysucursal.id).order_by('nombre')
			
		paginator1 = Paginator(eventos, 25)
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
					return render_to_response('admingral/reporteSucursalesActivas.html', ctx,context_instance=RequestContext(request))
							
		ctx={'Sucursal':pSucursales,'query':query,'nivel':nivel}
		return render_to_response('admingral/reporteSucursalesActivas.html', ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def sucursales_vendedores_view(request):
	nivel=Permiso(request.user,[0,1])
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
		
		
		paginator1 = Paginator(vd, 25)

		pAm=None
		
		try:
			pAm = paginator1.page(pag1)
		except PageNotAnInteger:
			pAm= paginator1.page(1)
		except EmptyPage:
			pAm = paginator1.page(paginator1.num_pages)


		ctx={'empleado':pAm,'query':query,'nivel':nivel}
		return render_to_response('admingral/reporteVendedores.html', ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def admin_contab_metas_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		info = ""
		query  = request.GET.get('q','')
		smes  = request.GET.get('mes','')
		pag1=request.GET.get('pagina','')
		qset2 = (Q(empleado__puesto__puesto__icontains='encargado') | Q(empleado__puesto__puesto__icontains='vendedor'))
		omen = Metas.objects.filter(qset2,empleado__estadoEmpleado=True).order_by('empleado')
		msgs = []
		today = datetime.now() #fecha actual
		dateFormat = today.strftime("%Y-%m")
		for x in omen:
			sumaE = 0
			sumaP = 0
			sumaS = 0
			try:
				ev = VentaEquipo.objects.filter(venta__aceptada=True,venta__fecha__icontains=dateFormat)
				for y in ev:
					try:
						zen = ActivacionEquipo.objects.get(equipo=y.equipo, empleado=x.empleado)
						sumaE = sumaE + 1
					except :
						pass
				sumaP = ActivacionPlan.objects.filter(ejecutivo=x.empleado, fxActivacion__icontains=dateFormat).count()
				try:
					u = Usuario.objects.get(empleado=x.empleado)
					sumaS = comisionesReparacion.objects.filter(user=u.user,equipoReparacion__fxIngreso=dateFormat).count()
				except :
					pass
			except :
				pass
			msgs.append([x,sumaE,sumaP,sumaP])			

		form = setMetas()
		if query:
			qset=(Q(empleado__curp__icontains=query) |
			 Q(empleado__nombre__icontains=query) | 
			 Q(empleado__aPaterno__icontains=query) | 
			 Q(empleado__aMaterno__icontains=query))
			if smes:
				dateFormat = smes
			else:
				dateFormat = "Todos"
			omen = Metas.objects.filter(qset,qset2,empleado__estadoEmpleado=True).order_by('empleado')
			msgs = []
			for x in omen:
				sumaE = 0
				sumaP = 0
				sumaS = 0
				try:
					ev = VentaEquipo.objects.filter(venta__aceptada=True,venta__fecha__icontains=smes)
					for y in ev:
						try:
							zen = ActivacionEquipo.objects.get(equipo=y.equipo, empleado=x.empleado)
							sumaE = sumaE + 1
						except :
							pass
					sumaP = ActivacionPlan.objects.filter(ejecutivo=x.empleado, fxActivacion__icontains=smes).count()
					try:
						u = Usuario.objects.get(empleado=x.empleado)
						sumaS = comisionesReparacion.objects.filter(user=u.user,equipoReparacion__fxIngreso=smes).count()
					except :
						pass
				except :
					pass
				msgs.append([x,sumaE,sumaP,sumaP])

		paginator1 = Paginator(msgs, 50)
		pMensages=None
		
		try:
			pMensages = paginator1.page(pag1)
		except PageNotAnInteger:
			pMensages= paginator1.page(1)
		except EmptyPage:
			pMensages = paginator1.page(paginator1.num_pages)

		ctx = {'empleados':pMensages,'mes':dateFormat ,'info':info,'nivel':nivel}
		return render_to_response('admingral/theMetasReporte.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

#acceso directo desde conta/
@login_required(login_url='/')
def admin_contab_edo_cta_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		return render_to_response('admingral/index.html', {'nivel':nivel},context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#acceso directo desde conta/
@login_required(login_url='/')
def admin_contab_nomina_view(request):
	nivel=Permiso(request.user,[0,1])
	if nivel != -1:
		return render_to_response('admingral/index.html', {'nivel':nivel},context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def autorizaciones_cancelaciones_view(request):
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
					return render_to_response('admingral/productosCancelados.html',ctx,context_instance=RequestContext(request))
				else:
					info = "Oops!, alguien ha modificado la informacion, regrese a la pagina principal para verificar."
					ctx = {'rentaVendido':rentaVendido,'planVendido':planVendido,'anticipo':menosAnticipo,
					'accVendido':accVendido,'vtaCanceladas':vtaCanceladas,'recVendido':recVendido,'ficVendido':ficVendido,
					'expVendido':expVendido,'eqVendido':eqVendido,'nivel':nivel}
					return render_to_response('admingral/productosCancelados.html',ctx,context_instance=RequestContext(request))

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
		return render_to_response('admingral/autorizacionCancelaciones.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def autorizaciones_papelera_view(request):
	nivel=Permiso(request.user,[0,1])
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
		
		paginator1 = Paginator(msgs, 30)
		pMensages=None
		
		try:
			pMensages = paginator1.page(pag1)
		except PageNotAnInteger:
			pMensages= paginator1.page(1)
		except EmptyPage:
			pMensages = paginator1.page(paginator1.num_pages)

		ctx={'cancelaciones':pMensages,'query':query,'info':info,'nivel':nivel}
		return render_to_response('admingral/bandejaCancelaciones.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def admin_sucursales_papeletas_view(request):
	nivel=Permiso(request.user,[0,1,9])
	if nivel != -1:
		info =""
		query = ""
		pagina = request.GET.get('pagina','')
		gaara=None
		gaara = Papeleta.objects.all().order_by('fxActivacion').reverse()

		if request.method == "POST":
			fxInicio 	= request.POST.get('fxInicio','')
			fxFinal 	= request.POST.get('fxFinal','')
			try:
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
			except :
				info = "Seleccione un rango de fechas"
		
		paginator = Paginator(gaara, 50)
		p_Item=None
		try:
			p_Item = paginator.page(pagina)
		except PageNotAnInteger:
			p_Item = paginator.page(1)
		except EmptyPage:
			p_Item = paginator.page(paginator.num_pages)
		
		ctx = {'papeletas':p_Item,'query':query ,'info':info, 'nivel':nivel}
		return render_to_response('admingral/reportePapeletas.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def usuarios_agregar_view(request):
	nivel=Permiso(request.user,[0,1])
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
		return render_to_response('admingral/addUser.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def usuarios_actualizar_view(request):
	nivel=Permiso(request.user,[0,1])
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
			return render_to_response('admingral/updUser.html', ctx ,context_instance=RequestContext(request))
	
		
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
				return render_to_response('admingral/updUser.html', ctx ,context_instance=RequestContext(request))

			else:
				info = "Verifique sus datos"
				form= UpdUserForm(request.POST)
			
			ctx = {'nivel':nivel,'form':form, 'info':info,'usuario':usuario }
			return render_to_response('admingral/updUser.html', ctx ,context_instance=RequestContext(request))


		if usuarios:
			nUsuarios=len(usuarios)
			usuarios=Paginador(usuarios,50,pagina)
		ctx={'nivel':nivel, 'mensaje':mensaje, 'q':q, 'usuario':usuario, 'usuarios':usuarios, 'nUsuarios':nUsuarios}
		return render_to_response('admingral/usuariosReporte.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

@login_required(login_url='/')
def usuarios_vendedores_view(request):
	nivel=Permiso(request.user,[0,1])
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
		return render_to_response('admingral/myVendedorSucursal.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

