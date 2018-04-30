# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
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
from django.db import transaction
from django.contrib.auth.models import Group
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField, TextInput
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.forms.extras.widgets import SelectDateWidget

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from djCell.apps.personal.models import Usuario
from django.contrib.auth.models import User

from djCell.apps.almacen.models import AlmacenEquipo, AlmacenExpres, AlmacenAccesorio, AlmacenFicha
from djCell.apps.catalogos.models import Estado, Ciudad, Colonia, CP, Zona
from djCell.apps.clientes.models import ClienteFacturacion, ClienteServicio, Mayorista
from djCell.apps.comisiones.models import Comision
from djCell.apps.contabilidad.models import Nomina, TipoCuenta, CuentaEmpleado, HistorialEmpleado, Metas, Caja, Gastos,LineaCredito, HistLCredito, Cuenta
from djCell.apps.corteVta.models import GastosSucursal, CorteVenta, VentasCorte
from djCell.apps.movimientos.models import TipoMovimiento, Movimiento, ListaEquipo, ListaExpres, ListaAccesorio, ListaFichas, TransferenciaSaldo
from djCell.apps.personal.models import Area, Puesto, Empleado, Usuario
from djCell.apps.portabilidades.models import EstadoPortabilidad, Portabilidad,FlexeoEquipo
from djCell.apps.productos.models import TiempoGarantia,Estatus,Marca,Gama,DetallesEquipo,Equipo,TipoIcc,DetallesExpres,Expres,Secciones,MarcaAccesorio,DetallesAccesorio,EstatusAccesorio,Accesorio, NominacionFicha,EstatusFicha,Ficha,  TiempoAire, HistorialPreciosEquipos,HistorialPreciosAccesorios
from djCell.apps.servicios.models import TipoReparacion, EstadoReparacion,Reparacion, EquipoReparacion, HistorialClienteReparacion, comisionesReparacion
from djCell.apps.sucursales.models import EstadoSucursal, TipoSucursal, Sucursal, VendedorSucursal
from djCell.apps.ventas.models import EstadoVenta, Venta,VentaEquipo,VentaExpres,VentaAccesorio,VentaFichas,VentaRecarga,VentaPlan,Renta, Cancelaciones, VentaMayoreo,TipoPago, Anticipo
from djCell.apps.auditoria.models import ArqueoCaja

from djCell.interface.servicios.forms import addReparacionForm,updReparacion,addClienteServicioForm,updCostoPorta,updGratisFlexeo,addAbonoReparacion,AddVentaCaja,addGastosSucursal,updCorteVenta,addArqueoCaja,vtaReparacion
from djCell.interface.servicios.forms import vtaGratisFlexeo,vtaCostoPorta, vtaReparacionSW, vtaReparacionFis
from djCell.operaciones.comunes import Permiso, agregarCiudades
from djCell.operaciones.ventasgral import *

def inuSucursal(user):
	myusuario = Usuario.objects.get(user=user)
	myempleado 			= myusuario.empleado
	vendedorSucursal 	= VendedorSucursal.objects.get(empleado=myempleado)
	mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
	vendedor = []
	vendedor.append(myusuario.user.username)
	vendedor.append(mysucursal.nombre)

	return vendedor

def cveSucursal(user):
	_usuario = Usuario.objects.get(user=user)
	myempleado 			= _usuario.empleado
	vendedorSucursal 	= VendedorSucursal.objects.get(empleado=myempleado)
	mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

	return mysucursal.id

def suc_Permisos(nivel,user,sucursal): #troll 
	ok = False
	try:
		_usuario 			= Usuario.objects.get(user=user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		if mysucursal.id == sucursal.id or nivel == 0  or nivel == 1 or nivel == 2 or nivel == 3:
			ok = True
		else:
			ok = False	
	except :
		pass

	return ok
		
#listo
@login_required(login_url='/')
def index_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:
		return render_to_response('servicios/index.html', {'nivel':nivel},context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo
@login_required(login_url="/")
def resultado_operacion_view(request):
	nivel=Permiso(request.user,[0,1,11,12])
	if nivel != -1:
		return render_to_response('servicios/transaccion.html',{'nivel':nivel},context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo poi
@login_required(login_url='/')
def servicios_catalogo_reparaciones_agregar_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:
		
		form = addReparacionForm()
		info = ""

		if request.method == "POST":

			form = addReparacionForm(request.POST or None)
			
			if form.is_valid():
				
				tipoReparacion = form.cleaned_data['tipoReparacion']
				descripcion	= form.cleaned_data['descripcion']
				monto 		= form.cleaned_data['monto']
				try:
					with transaction.atomic():
						a = Reparacion()
						a.tipoReparacion = TipoReparacion.objects.get(tipo=tipoReparacion)
						a.descripcion = descripcion
						a.monto = monto
						a.save()
						
						info ="Se ha Guardado con Exito"
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				form = addReparacionForm()
				
			else:
				form = addReparacionForm(request.POST)
				info ="Verifique la informacion, no se han registrado los datos"

		ctx = {'form':form,'info':info,'nivel':nivel}
		return render_to_response('servicios/addReparacionCatalogo.html', ctx, context_instance=RequestContext(request))	

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo poi
@login_required(login_url='/')
def servicios_catalogo_reparaciones_todos_view(request):
	nivel=Permiso(request.user,[0,1,10])
	
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
				return render_to_response('servicios/catalogoReparaciones.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('updRep'):
				itemSeleccionado = request.GET.get('updRep','')
				if itemSeleccionado:
					lerep = Reparacion.objects.get(id = itemSeleccionado)
					key = lerep.id
					form = updReparacion(instance=lerep)
					info = "Actualizar Reparacion"
					mostrarForm = True

				ctx = {'form':form, 'info':info,'key':key,'mostrar':mostrarForm,'nivel':nivel}
				return render_to_response('servicios/catalogoReparaciones.html',ctx,context_instance=RequestContext(request))

		if request.method == "POST":
			upd = Reparacion.objects.get(id=request.POST.get('key'))
			form = updReparacion(request.POST or None, instance=upd)
			mostrarForm = True
			if form.is_valid():
				try:
					with transaction.atomic():
						form.save()		
						info = "Se ha Actualizado correctamente. Pulse en Nueva Busqueda para ver el catalogo nuevamente. Gracias."
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."
				
				mostrarForm = False				
				ctx = {'form':form, 'info':info, 'mostrar':mostrarForm,'nivel':nivel}
				return render_to_response('servicios/catalogoReparaciones.html',ctx,context_instance=RequestContext(request))

			else:
				form = updReparacion(request.POST)
				info ="Verifique la informacion, no se han actualizado correctamente los datos"
				mostrarForm = True

		ctx = {"results": results,"query": query, 'form':form,'mostrar':mostrarForm ,'reparaciones':reparaciones ,'info':info, 'nivel':nivel}
		return render_to_response('servicios/catalogoReparaciones.html',ctx,context_instance=RequestContext(request))		
		
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo --
@login_required(login_url='/')
def servicios_solicitudes_flexeo_porta_view(request):
	nivel=Permiso(request.user,[0,1,10])
	
	if nivel != -1:
		
		query = ''
		results = []
		info =""
		scosto = FlexeoEquipo.objects.filter(portabilidad__cliente__tipoCliente__icontains='Portabilidad sin costo')
		ccosto = EquipoReparacion.objects.filter(cliente__tipoCliente__icontains='Portabilidad con costo')

		pag1=request.GET.get('pagCosto','')
		pag2=request.GET.get('pagSCosto','')
		paginator1 = Paginator(ccosto, 50)
		paginator2 = Paginator(scosto, 50)
		nCcosto=len(ccosto)
		nSCosto=len(scosto)
		pCosto=None
		pSCosto=None
		try:
			pCosto = paginator1.page(pag1)
			pSCosto = paginator2.page(pag2)
		except PageNotAnInteger:
			pCosto = paginator1.page(1)
			pSCosto = paginator2.page(1)
		except EmptyPage:
			pCosto = paginator1.page(paginator1.num_pages)
			pSCosto = paginator2.page(paginator2.num_pages)

		
		if request.method == "GET":
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					qset = (Q(cliente__nombre__icontains=query) | Q(sucursal__nombre__icontains=query) | Q(cliente__folio__icontains=query))
					results = Portabilidad.objects.filter(qset).distinct()
					if results:
						info = "Resultados"
				else:
					results = []
			
				ctx = {'pCosto':pCosto, 'pSCosto':pSCosto,"results": results,"query": query, 'scosto':scosto, 'ccosto':ccosto, 'info':info, 'nivel':nivel}
				return render_to_response('servicios/solicitudFlexeoPorta.html',ctx,context_instance=RequestContext(request))


		ctx = {'pCosto':pCosto, 'pSCosto':pSCosto, 'scosto':scosto, 'ccosto':ccosto,  'nivel':nivel}
		return render_to_response('servicios/solicitudFlexeoPorta.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo --
@login_required(login_url='/')
def servicios_solicitudes_flexeos_view(request):
	nivel=Permiso(request.user,[0,1,10])
	
	if nivel != -1:
		ccosto = EquipoReparacion.objects.filter(cliente__tipoCliente__icontains='Servicio', reparacion__tipoReparacion__tipo__icontains='flexeos')
		pagina=request.GET.get('pagina','')
		paginator = Paginator(ccosto, 50)
		nFlexeos=len(ccosto)
		flexeosp=None
		try:
			flexeosp = paginator.page(pagina)
		except PageNotAnInteger:
			flexeosp = paginator.page(1)
		except EmptyPage:
			flexeosp = paginator.page(paginator.num_pages)

		query = ''
		results = []
		info =""
		
		
		if request.method == "GET":
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					qset = (Q(cliente__nombre__icontains=query) | Q(sucursal__nombre__icontains=query) | Q(cliente__folio__icontains=query))
					results = EquipoReparacion.objects.filter(qset,cliente__tipoCliente__icontains='Servicio', reparacion__tipoReparacion__tipo__icontains='flexeos').distinct()
					if results:
						info = ""
				else:
					results = []

		ctx = {"results": results,"query": query, 'ccosto':ccosto,'flexeos':flexeosp ,'info':info, 'nivel':nivel}
		return render_to_response('servicios/solicitudFlexeoTecnico.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo --
@login_required(login_url='/')
def servicios_solicitudes_reparacion_fisica_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:
		
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

		ctx={'nivel':nivel, 'reparaciones':reparacionesp, 'query':query}

		return render_to_response('servicios/solicitudReparaciones.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo poi
@login_required(login_url='/')
def servicios_clientes_rep_nuevo_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		form = addClienteServicioForm()
		info = ""
		clientes = ClienteServicio.objects.all()
		
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
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."
				form = addClienteServicioForm()
				
				ctx = {'form':form,'clientes':clientes ,'info':info,'nivel':nivel}
				return render_to_response('servicios/addClienteReparacion.html', ctx, context_instance=RequestContext(request))

			else:
				form = addClienteServicioForm(request.POST)
				info ="Verifique la informacion, no se han registrado los datos"

		ctx = {'form':form,'clientes':clientes ,'info':info,'nivel':nivel}
		return render_to_response('servicios/addClienteReparacion.html', ctx, context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo ticket poi .
@login_required(login_url='/')
def servicios_clientes_rep_abonos_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		
		formC = addAbonoReparacion()
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
				return render_to_response('servicios/addAbonoCliente.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('upd'):
				query = request.GET.get('upd', '')
				if query:
					ccosto = EquipoReparacion.objects.get(id = query)
					repHist = HistorialClienteReparacion.objects.filter(equipoReparacion__id=ccosto.id)
			
					suma = 0
					for x in repHist:
						suma = suma + x.abono

					resta = ccosto.reparacion.monto - suma

					formC = addAbonoReparacion({'key':ccosto.id,'cliente':ccosto.cliente.nombre,
						'equipo':ccosto.marcaModelo,'fxIngreso':ccosto.fxIngreso, 'reparacion':ccosto.reparacion.descripcion,
						'costoRep':ccosto.reparacion.monto,'anticipos': suma,'faltante':resta })
					mostrar = True
					buscar = False
					mostrarf = True
					show= False

					ctx = {'reparaciones':reparacionesp,'show':show,'buscar':buscar,'mostrarf':mostrarf,'mostrar':mostrar,'formC':formC ,'info':info, 'nivel':nivel}
					return render_to_response('servicios/addAbonoCliente.html',ctx,context_instance=RequestContext(request))
			
			if request.GET.get('print'):
				vta = request.GET.get('print','')
				if vta:
					mivi = None
					try:
						v = Venta.objects.get(folioVenta=vta)
						ok = suc_Permisos(nivel,request.user,v.sucursal)
						if ok:
							mivi = listarTicket(vta)
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('servicios/ticket.html',ctx,context_instance=RequestContext(request))

		if request.method == "POST":
			formC = addAbonoReparacion( request.POST)
			today = datetime.now() #fecha actual
			dateFormat = today.strftime("%d-%m-%Y") # fecha con formato
			
			if formC.is_valid():
				key = formC.cleaned_data['key']
				abonar 	= formC.cleaned_data['abonar']
				faltante = formC.cleaned_data['faltante']
				b = None
				v = None
				try:
					with transaction.atomic():
						b = EquipoReparacion.objects.get(id = key)
						b.fxRevision = today
						b.save()
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				Cambio = 0
				Pagado = None
				if abonar > 0 and abonar >= faltante:
					Pagado = True
					Cambio = abonar - faltante
					try:
						with transaction.atomic():
							b.pagado = True
							b.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'


				elif abonar > 0 and abonar < faltante:
					Pagado = False
					
				else:
					formC = addAbonoReparacion( request.POST)
					mostrarf = True
					mostrar = True
					info ='Lo sentimos, El Abono debe ser mayor que cero.'	
					ctx = {'buscar':buscar,'mostrarf':mostrarf,'mostrar':mostrar,'formC':formC ,'info':info, 'nivel':nivel}
					return render_to_response('servicios/addAbonoCliente.html',ctx,context_instance=RequestContext(request))
				try:
					with transaction.atomic():
						v = Venta()
						v.folioVenta = nuevoFolio2(mysucursal.id)
						v.sucursal 	= mysucursal
						v.usuario 	= request.user
						if Pagado:
							v.total 	= faltante
						else:
							v.total 	= abonar
						v.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
						v.aceptada  	= True #gatito
						v.estado 	= EstadoVenta.objects.get(estado='Pagada')
						v.save()

						dv = Anticipo()
						dv.folioVenta 		= v
						dv.tipoAnticipo 	= 'Servicio - Abono'
						if Pagado:
							dv.monto 	= faltante
						else:
							dv.monto 	= abonar
						dv.observacion 	= "Cliente no. "+b.cliente.folio+" "+b.cliente.nombre
						dv.save()

						a =  HistorialClienteReparacion()
						a.equipoReparacion = b
						if Pagado:
							a.abono = faltante
						else:
							a.abono = abonar
						a.save()
						abonarCli=True
						info = "El abono se registro con Venta Folio: "+v.folioVenta+' Cambio: $'+str(Cambio)
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				mfolioVenta = v.folioVenta #ticket ya
				ctx = { 'folioVenta':mfolioVenta, 'buscar':True,'mostrarf':mostrarf,'info':info, 'nivel':nivel}
				return render_to_response('servicios/addAbonoCliente.html',ctx,context_instance=RequestContext(request))

			else:
				info = "Verifique sus datos, datos incorrectos."
				formC = addAbonoReparacion( request.POST)
				mostrarf = True
				mostrar = True

				ctx = {'mostrarf':mostrarf,'mostrar':mostrar,'formC':formC ,'info':info, 'nivel':nivel}
				return render_to_response('servicios/addAbonoCliente.html',ctx,context_instance=RequestContext(request))
			
		ctx = {'buscar':buscar,'mostrarf':mostrarf, 'boton':boton ,'mostrar':mostrar, 'formC':formC, 'info':info, 'nivel':nivel}
		return render_to_response('servicios/addAbonoCliente.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo --
@login_required(login_url='/')
def servicios_clientes_rep_historial_view(request):
	nivel=Permiso(request.user,[0,1,10])
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
				return render_to_response('servicios/historialClienteReparacion.html',ctx,context_instance=RequestContext(request))

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
		return render_to_response('servicios/historialClienteReparacion.html',ctx,context_instance=RequestContext(request))
		
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo poi
@login_required(login_url='/')
def servicios_seguimiento_flexeo_porta_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:
		
		formC = updCostoPorta()
		formS = updGratisFlexeo()
		info =""
		mostrar = False
		buscar = True
		mostrarf = False
		query = ''
		results = []
		scosto = FlexeoEquipo.objects.filter(portabilidad__cliente__tipoCliente__icontains='Portabilidad sin costo')
		ccosto = EquipoReparacion.objects.filter(cliente__tipoCliente__icontains='Portabilidad con costo')

		if request.method == "GET":

			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					qset = (Q(cliente__nombre__icontains=query) | Q(sucursal__nombre__icontains=query) | Q(cliente__folio__icontains=query))
					results = Portabilidad.objects.filter(qset).distinct()
					if results:
						info = "Resultados"

				else:
					results = []
				ctx = {'buscar':buscar,'mostrarf':mostrarf,"results": results,"query": query, 'scosto':scosto, 'ccosto':ccosto, 'info':info, 'nivel':nivel}
				return render_to_response('servicios/seguimientoFlexeoPorta.html',ctx,context_instance=RequestContext(request))

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

			ctx = {'buscar':buscar,'mostrarf':mostrarf, 'mostrar':mostrar, 'formS':formS, 'formC':formC,'boton':False ,'info':info, 'nivel':nivel}
			return render_to_response('servicios/seguimientoFlexeoPorta.html',ctx,context_instance=RequestContext(request))

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
						

						info = "Flexeo con costo. El Registro se ha actualizado con exito: " + ccosto.cliente.nombre
						boton = False
						buscar = True
						mostrarf = True
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				ctx = {'buscar':buscar,'mostrarf':mostrarf, 'boton':boton,'info':info, 'nivel':nivel}
				return render_to_response('servicios/seguimientoFlexeoPorta.html',ctx,context_instance=RequestContext(request))

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
						info = "Flexeo sin costo. El Registro se ha actualizado con exito: " + scosto.portabilidad.cliente.nombre
						boton = False
						buscar = True
						mostrarf = False
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				ctx = {'buscar':buscar,'mostrarf':mostrarf,'boton':boton,'info':info, 'nivel':nivel}
				return render_to_response('servicios/seguimientoFlexeoPorta.html',ctx,context_instance=RequestContext(request))

			else:
				info = "Verifique sus datos, actualizacion no realizada"
				formC = updCostoPorta( request.POST or None)
				formS = updGratisFlexeo( request.POST or None)
				mostrarf = True
				buscar = False
			
			ctx = {'buscar':buscar,'mostrarf':mostrarf, 'boton':boton ,'mostrar':mostrar, 'formS':formS, 'formC':formC, 'info':info, 'nivel':nivel}
			return render_to_response('servicios/seguimientoFlexeoPorta.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo --
@login_required(login_url='/')
def servicios_seguimiento_flexeos_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:
		
		formC = updCostoPorta()
		info =""
		mostrar = False
		buscar = True
		mostrarf = False
		boton = True
		query = ''
		results = []

		if request.method == "GET":

			if request.GET.get('q'):
				if request.GET.get('q'):
					query = request.GET.get('q', '')
				if query:
					qset = (Q(cliente__nombre__icontains=query) | Q(sucursal__nombre__icontains=query) | Q(cliente__folio__icontains=query))
					results = EquipoReparacion.objects.filter(qset,cliente__tipoCliente__icontains='Servicio', reparacion__tipoReparacion__tipo__icontains='flexeos').distinct()
					if results:
						info = ""
				else:
					results = []

				ctx = {'buscar':buscar,'mostrarf':mostrarf,"results": results,"query": query, 'info':info, 'nivel':nivel, 'formC':formC}
				return render_to_response('servicios/seguimientoFlexeoTecnico.html',ctx,context_instance=RequestContext(request))

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
					boton = False

				else:
					info = "Resultados - upd"+ str(query)

			ctx = {'buscar':buscar,'mostrarf':mostrarf,'mostrar':mostrar,'formC':formC, 'boton':boton ,'info':info, 'nivel':nivel}
			return render_to_response('servicios/seguimientoFlexeoTecnico.html',ctx,context_instance=RequestContext(request))

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

				ctx = {'buscar':buscar,'mostrarf':mostrarf, 'boton':boton,'info':info, 'nivel':nivel}
				return render_to_response('servicios/seguimientoFlexeoTecnico.html',ctx,context_instance=RequestContext(request))

			else:
				info = "Verifique sus datos, actualizacion no realizada"
				formC = updCostoPorta( request.POST)
				mostrarf = True
				buscar = False
				boton = True
			
			ctx = {'buscar':buscar,'mostrarf':mostrarf, 'boton':boton ,'mostrar':mostrar, 'formC':formC, 'info':info, 'nivel':nivel}
			return render_to_response('servicios/seguimientoFlexeoTecnico.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo --
@login_required(login_url='/')
def servicios_seguimiento_reparacion_fisica_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:
		
		formC = updCostoPorta()
		info =""
		mostrar = False
		buscar = True
		mostrarf = False
		boton = True
		query = ''
		results = []

		if request.method == "GET":

			if request.GET.get('q'):
				if request.GET.get('q'):
					query = request.GET.get('q', '')
				if query:
					qset = (Q(cliente__nombre__icontains=query) | Q(sucursal__nombre__icontains=query) | Q(cliente__folio__icontains=query))# | Q( reparacion__tipoReparacion__tipo__icontains='Reparacion Fisica') | Q( reparacion__tipoReparacion__tipo__icontains='Carga de Software')
					results = EquipoReparacion.objects.filter(qset,cliente__tipoCliente__icontains='Servicio').distinct()
					if results:
						info = ""
				else:
					results = []

				ctx = {'buscar':buscar,'mostrarf':mostrarf,"results": results,"query": query, 'info':info, 'nivel':nivel, 'formC':formC}
				return render_to_response('servicios/seguimientoReparacionesFisicas.html',ctx,context_instance=RequestContext(request))

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
					boton = False

				else:
					info = "Resultados - upd"+ str(query)

			ctx = {'buscar':buscar,'mostrarf':mostrarf,'mostrar':mostrar,'formC':formC, 'boton': boton ,'info':info, 'nivel':nivel}
			return render_to_response('servicios/seguimientoReparacionesFisicas.html',ctx,context_instance=RequestContext(request))

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

				ctx = {'buscar':buscar,'mostrarf':mostrarf, 'boton':boton,'info':info, 'nivel':nivel}
				return render_to_response('servicios/seguimientoReparacionesFisicas.html',ctx,context_instance=RequestContext(request))

			else:
				info = "Verifique sus datos, actualizacion no realizada"
				formC = updCostoPorta( request.POST)
				mostrarf = True
				buscar = False
				boton = True
			
			ctx = {'buscar':buscar,'mostrarf':mostrarf, 'boton':boton ,'mostrar':mostrar, 'formC':formC, 'info':info, 'nivel':nivel}
			return render_to_response('servicios/seguimientoReparacionesFisicas.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo ticket poi x
@login_required(login_url='/')
def servicios_ventas_flexeo_porta_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		query = ""
		results = ""
		buscar = True
		boton = True
		nvoSC = False
		nvoCC = False
		yaSC = False
		yaCC = False
		info=""
		formCC = vtaCostoPorta()
		formSC = vtaGratisFlexeo()
		form = addClienteServicioForm()

		if request.method == "GET":
			
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					
					qset = (Q(nombre__icontains=query)|Q(direccion__icontains=query)|Q(colonia__colonia__icontains=query)|Q(sucursal__nombre__icontains=query)|Q(folio__icontains=query)|Q(fxIngreso__icontains=query) )
					results = ClienteServicio.objects.filter(qset,tipoCliente__icontains='Portabilidad').distinct()

				else:
					results = []

				buscar = True
				ctx = {'query':query,'results':results,'buscar':buscar,'nivel':nivel,'info':info}
				return render_to_response('servicios/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))
				
			if request.GET.get('cliCCosto'):
				cliente = request.GET.get('cliCCosto','')
				if cliente:
					cli = ClienteServicio.objects.get(id=cliente)
					formCC = vtaCostoPorta({'key':cli.id,'cliente':cli.nombre})

					buscar = False
					yaCC = True
					boton = True
					ctx = {'yaCC':yaCC,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('cliSCosto'):
				cliente = request.GET.get('cliSCosto','')
				if cliente:
					cli = ClienteServicio.objects.get(id=cliente)
					formSC = vtaGratisFlexeo({'key':cli.id,'cliente':cli.nombre})

					buscar = False
					yaSC = True
					boton = True
					ctx = {'yaSC':yaSC,'formS':formSC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))
					
			if request.GET.get('nvoCCosto'):
				cliente = request.GET.get('nvoCCosto','')
				if cliente:
					formCC = vtaCostoPorta({'key':nvofolioCliente(),'cliente':'Nuevo'})

					buscar = False
					nvoCC = True
					boton = True
					ctx = {'nvoCC':nvoCC,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('nvoSCosto'):
				cliente = request.GET.get('nvoSCosto','')
				if cliente:					
					formSC = vtaGratisFlexeo({'key':nvofolioCliente(),'cliente':'Nuevo'})

					buscar = False
					nvoSC = True
					boton = True
					ctx = {'nvoSC':nvoSC,'form':form,'formS':formSC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('print'):
				vta = request.GET.get('print','')
				if vta:
					mivi = None
					try:
						v = Venta.objects.get(folioVenta=vta)
						ok = suc_Permisos(nivel,request.user,v.sucursal)
						if ok:
							mivi = listarTicket(vta)
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('servicios/ticket.html',ctx,context_instance=RequestContext(request))

		if 'regNvoSC' in request.POST:
			formSC = vtaGratisFlexeo(request.POST)
			form = addClienteServicioForm(request.POST)

			if formSC.is_valid() and form.is_valid():
				#nuevo cliente , porta gratis
				nombre 		= form.cleaned_data['nombre']
				direccion 	= form.cleaned_data['direccion']
				colonia 	= form.cleaned_data['colonia']
				ciudad  	= form.cleaned_data['ciudad']
				estado 		= form.cleaned_data['estado']
				
				key 		= formSC.cleaned_data['key']
				marcaModelo = formSC.cleaned_data['marcaModelo']
				noaportar 	= formSC.cleaned_data['noaportar']
				observaciones 	= formSC.cleaned_data['observaciones']

				zzz = agregarCiudades(colonia,ciudad,estado,None)
				try:
					with transaction.atomic():
						a = ClienteServicio()
						a.nombre 		= (nombre).title()
						a.direccion 	= (direccion).title()
						a.colonia = Colonia.objects.get(id=zzz[0])
						a.ciudad = Ciudad.objects.get(id[1])
						a.sucursal 	= mysucursal
						a.tipoCliente = 'Portabilidad sin costo'
						a.folio	=key
						a.save()
						
						b = Portabilidad()
						b.cliente 	= a
						b.noaPortar 	= noaportar
						b.flexearEquipo = True
						b.estado 		= EstadoPortabilidad.objects.get(estado='En Sucursal - Sin enviar')
						b.sucursal 	= mysucursal
						b.fxRevision	= datetime.now()
						b.save()

						c = FlexeoEquipo()
						c.portabilidad 	= b
						c.marcaModelo 	= marcaModelo
						c.observaciones = observaciones
						c.estado 		= EstadoReparacion.objects.get(estado='En Sucursal - Sin enviar')
						c.fxRevision	= datetime.now()
						c.save()

						info="Se ha registrado la entrada de un equipo para flexeo por portabilidad sin costo. Folio Cliente: "+str(a.folio)
						boton= False
						nvoSC = True
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				ctx = {'nvoSC':nvoSC,'boton':boton,'nivel':nivel,'info':info}
				return render_to_response('servicios/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

			else:
				formSC = vtaGratisFlexeo(request.POST)
				form = addClienteServicioForm(request.POST)
				buscar = False
				nvoSC = True
				boton = True
				info = "you got an error"
			
			ctx = {'nvoSC':nvoSC,'form':form,'formS':formSC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
			return render_to_response('servicios/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

		if 'regNvoCC' in request.POST:
			formCC = vtaCostoPorta(request.POST)
			form = addClienteServicioForm(request.POST)

			if form.is_valid() and formCC.is_valid():
				#nuevo cliente, porta con costo
				nombre 		= form.cleaned_data['nombre']
				direccion 	= form.cleaned_data['direccion']
				colonia 	= form.cleaned_data['colonia']
				ciudad  	= form.cleaned_data['ciudad']
				estado 		= form.cleaned_data['estado']
				#

				key 		= formCC.cleaned_data['key']
				noaportar 	= formCC.cleaned_data['noaportar']
				marcaModelo = formCC.cleaned_data['marcaModelo']
				imei 		= formCC.cleaned_data['imei']
				observacion = formCC.cleaned_data['observacion']
				anticipo 	= formCC.cleaned_data['anticipo']
				reparacion 	= formCC.cleaned_data['reparacion']

				#
				monto = Reparacion.objects.get(id=reparacion).monto
				payv = None
				Cambio = 0
				pago = 0
				if anticipo >= monto:
					payv = True
					Cambio = anticipo - monto
					pago =monto
				elif anticipo > 0 and anticipo < monto:
					payv = False
					pago = anticipo
				else:
					info = "No se ha registrado la informacion, complete los campos correctamente. El anticipo debe ser mayor que Cero."
					formCC = vtaCostoPorta(request.POST)
					form = addClienteServicioForm(request.POST)
					buscar = False
					nvoCC = True
					boton = True

					ctx = {'nvoCC':nvoCC,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

				zzz = agregarCiudades(colonia,ciudad,estado,None)
				try:	
					with transaction.atomic():
						a = ClienteServicio()
						a.nombre 		= (nombre).title()
						a.direccion 	= (direccion).title()
						a.colonia 		= Colonia.objects.get(id=zzz[0])
						a.ciudad 		= Ciudad.objects.get(id=zzz[1])
						a.sucursal 		= mysucursal
						a.tipoCliente 	= 'Portabilidad con costo'
						a.folio	= key
						a.save()

						b = Portabilidad()
						b.cliente 	= a
						b.noaPortar 	= noaportar
						b.flexearEquipo = True
						b.estado 		= EstadoPortabilidad.objects.get(estado='En Sucursal - Sin enviar')
						b.sucursal 	= mysucursal
						b.fxRevision	= datetime.now()
						b.save()

						c =EquipoReparacion()
						c.marcaModelo = marcaModelo
						c.imei 		= imei
						c.falla 		= "Portabilidad con Costo - Equipo Flexeo"
						c.observacion = observacion
						c.cliente 	= a
						c.reparacion 	= Reparacion.objects.get(id=reparacion)
						c.anticipo = pago
						c.sucursal 	= mysucursal
						c.estado 		= EstadoReparacion.objects.get(estado='En Sucursal - Sin enviar')
						c.fxRevision	= datetime.now()
						if payv:
							c.pagado = True
						else:
							c.pagado = False
						c.save()

						zum = comisionesReparacion()
						zum.usuario = request.user
						zum.reparacion  = c
						zum.save()

						d = HistorialClienteReparacion()
						d.equipoReparacion = c
						d.abono	= anticipo
						d.save()

						v = Venta() 
						v.folioVenta = nuevoFolio2(str(mysucursal.id)+'S')
						v.sucursal 	= mysucursal
						v.usuario 	= request.user
						v.total 	= pago
						v.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
						if payv:
							v.estado 	= EstadoVenta.objects.get(estado='Pagada')
						else:
							v.estado 	= EstadoVenta.objects.get(estado='Proceso')
						v.aceptada  	= True #gatito
						v.save()

						dv = Anticipo()
						dv.folioVenta 		= v
						dv.tipoAnticipo 	= 'Portabilidad con costo'
						dv.monto 			= pago
						dv.observacion 	= "Cliente no. "+c.cliente.folio+" "+c.cliente.nombre
						dv.save()
						
						info="Se ha registrado la entrada de un equipo para flexeo por portabilidad con costo.Folio cliente: "+str(a.folio)+" Folio de Venta: "+ v.folioVenta+" Cambio: $"+str(Cambio)
						mfolioVenta = v.folioVenta #ticket ya
						boton= False
						nvoCC = True
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				ctx = {'folioVenta':mfolioVenta,'nvoCC':nvoCC,'boton':boton,'nivel':nivel,'info':info}
				return render_to_response('servicios/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))
			else:
				info = "No se registro. Verifique sus datos."
				formCC = vtaCostoPorta(request.POST)
				form = addClienteServicioForm(request.POST)
				buscar = False
				nvoCC = True
				boton = True
			ctx = {'nvoCC':nvoCC,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
			return render_to_response('servicios/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

		if 'regSC' in request.POST:
			formSC = vtaGratisFlexeo(request.POST)

			if formSC.is_valid():#cliente conocido , porta gratis
				key 	= formSC.cleaned_data['key']
				marcaModelo = formSC.cleaned_data['marcaModelo']
				noaportar = formSC.cleaned_data['noaportar']
				observaciones 	= formSC.cleaned_data['observaciones']

				a = ClienteServicio.objects.get(id=key)
				try:
					with transaction.atomic():
						b = Portabilidad()
						b.cliente 	= a
						b.noaPortar 	= noaportar
						b.flexearEquipo = True
						b.estado 		= EstadoPortabilidad.objects.get(estado='En Sucursal - Sin enviar')
						b.sucursal 	= mysucursal
						b.fxRevision	= datetime.now()
						b.save()

						c = FlexeoEquipo()
						c.portabilidad 	= b
						c.marcaModelo 	= marcaModelo
						c.observaciones = observaciones
						c.estado 		= EstadoReparacion.objects.get(estado='En Sucursal - Sin enviar')
						c.fxRevision	= datetime.now()
						c.save()


						info="Se ha registrado la entrada de un equipo para flexeo por portabilidad sin costo. Folio Cliente: "+str(a.folio)
						boton= False
						yaSC = True
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				ctx = {'yaSC':yaSC,'boton':boton,'nivel':nivel,'info':info}
				return render_to_response('servicios/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

			else:
				formSC = vtaGratisFlexeo(request.POST)
				buscar = False
				yaSC = True
				boton = True
			ctx = {'yaSC':yaSC,'form':form,'formS':formSC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
			return render_to_response('servicios/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

		if 'regCC' in request.POST:
			formCC = vtaCostoPorta(request.POST)
			if formCC.is_valid():#cliente conocido, porta con costo

				key 	= formCC.cleaned_data['key']
				noaportar 	= formCC.cleaned_data['noaportar']
				marcaModelo = formCC.cleaned_data['marcaModelo']
				imei 		= formCC.cleaned_data['imei']
				observacion = formCC.cleaned_data['observacion']
				anticipo 	= formCC.cleaned_data['anticipo']
				reparacion 	= formCC.cleaned_data['reparacion']

				monto = Reparacion.objects.get(id=reparacion).monto
				payv = None
				v = None
				Cambio = 0
				pago = 0
				if anticipo >= monto:
					payv = True
					Cambio = anticipo - monto
					pago =monto
				elif anticipo > 0 and anticipo < monto:
					payv = False
					pago = anticipo					
				else:
					info = "No se ha registrado la informacion, complete los campos correctamente. El anticipo debe ser mayor que Cero."
					formCC = vtaCostoPorta(request.POST)
					buscar = False
					yaCC = True
					boton = True
					ctx = {'yaCC':yaCC,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

				a = ClienteServicio.objects.get(id=key)
				try:
					with transaction.atomic():
						b = Portabilidad()
						b.cliente 	= a
						b.noaPortar 	= noaportar
						b.flexearEquipo = True
						b.estado 		= EstadoPortabilidad.objects.get(estado='En Sucursal - Sin enviar')
						b.sucursal 	= mysucursal
						b.fxRevision	= datetime.now()
						b.save()

						c =EquipoReparacion()
						c.marcaModelo = marcaModelo
						c.imei 		= imei
						c.falla 		= "Portabilidad con Costo - Equipo Flexeo"
						c.observacion = observacion
						c.cliente 	= a
						c.reparacion 	= Reparacion.objects.get(id=reparacion)
						c.anticipo = pago
						c.sucursal 	= mysucursal
						c.estado 		= EstadoReparacion.objects.get(estado='En Sucursal - Sin enviar')
						c.fxRevision	= datetime.now()
						if payv:
							c.pagado = True
						else:
							c.pagado = False
						c.save()

						zum = comisionesReparacion()
						zum.usuario = request.user
						zum.reparacion  = c
						zum.save()

						d = HistorialClienteReparacion()
						d.equipoReparacion = c
						d.abono	= anticipo
						d.save()

						v = Venta()
						v.folioVenta = nuevoFolio2(str(mysucursal.id)+'S')
						v.sucursal 	= mysucursal
						v.usuario 	= request.user
						v.total 	= pago
						v.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
						if payv:
							v.estado 	= EstadoVenta.objects.get(estado='Pagada')
						else:
							v.estado 	= EstadoVenta.objects.get(estado='Proceso')
						v.aceptada  	= True
						v.save()

						dv = Anticipo()
						dv.folioVenta 		= v
						dv.tipoAnticipo 	= 'Portabilidad con costo'
						dv.monto 			= pago
						dv.observacion 	= "Cliente no. "+c.cliente.folio+" "+c.cliente.nombre
						dv.save()

						info="Se ha registrado la entrada de un equipo para flexeo por portabilidad con costo. Folio de Venta: "+ v.folioVenta+" Cambio: $"+str(Cambio)
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				mfolioVenta = v.folioVenta #ticket ya
				buscar = False
				yaCC = True
				boton = False
				ctx = {'folioVenta':mfolioVenta,'yaCC':yaCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
				return render_to_response('servicios/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))
				
			else:
				info = "No se registro. Verifique sus datos."
				formCC = vtaCostoPorta(request.POST)
				buscar = False
				yaCC = True
				boton = True
			ctx = {'yaCC':yaCC,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
			return render_to_response('servicios/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))	
		
		ctx = {'query':query,'results':results,'buscar':buscar,'nivel':nivel,'info':info}
		return render_to_response('servicios/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo ticket poi x
@login_required(login_url='/')
def servicios_ventas_flexeos_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		query = ""
		results = ""
		buscar = True
		boton = True
		nvoCC = False
		yaCC = False
		info=""
		formCC = vtaReparacion()
		form = addClienteServicioForm()

		if request.method == "GET":
			
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					
					qset = (Q(nombre__icontains=query)|Q(direccion__icontains=query)|Q(colonia__colonia__icontains=query)|Q(sucursal__nombre__icontains=query)|Q(folio__icontains=query)|Q(fxIngreso__icontains=query) )
					results = ClienteServicio.objects.filter(qset,tipoCliente__icontains='Servicio').distinct()

				else:
					results = []

				buscar = True
				ctx = {'query':query,'results':results,'buscar':buscar,'nivel':nivel,'info':info}
				return render_to_response('servicios/vtaFlexeoTecnico.html',ctx,context_instance=RequestContext(request))
				
			if request.GET.get('cliCCosto'):
				cliente = request.GET.get('cliCCosto','')
				if cliente:
					cli = ClienteServicio.objects.get(id=cliente)
					formCC = vtaReparacion({'key':cli.id,'cliente':cli.nombre,'falla':'Flexeo Tecnico' })

					buscar = False
					yaCC = True
					boton = True
					ctx = {'yaCC':yaCC,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaFlexeoTecnico.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('nvoCCosto'):
				cliente = request.GET.get('nvoCCosto','')
				if cliente:
					formCC = vtaReparacion({'key':nvofolioCliente(),'cliente':'Nuevo','falla':'Flexeo Tecnico'})

					buscar = False
					nvoCC = True
					boton = True
					ctx = {'nvoCC':nvoCC,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaFlexeoTecnico.html',ctx,context_instance=RequestContext(request))
			
			if request.GET.get('print'):
				vta = request.GET.get('print','')
				if vta:
					mivi = None
					try:
						v = Venta.objects.get(folioVenta=vta)
						ok = suc_Permisos(nivel,request.user,v.sucursal)
						if ok:
							mivi = listarTicket(vta)
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('servicios/ticket.html',ctx,context_instance=RequestContext(request))

		if 'regNvoCC' in request.POST:
			formCC = vtaReparacion(request.POST)
			form = addClienteServicioForm(request.POST)

			if form.is_valid() and formCC.is_valid():
				#nuevo cliente, porta con costo
				nombre 		= form.cleaned_data['nombre']
				direccion 	= form.cleaned_data['direccion']
				colonia 	= form.cleaned_data['colonia']
				ciudad  	= form.cleaned_data['ciudad']
				estado 		= form.cleaned_data['estado']
				#

				key 		= formCC.cleaned_data['key']
				marcaModelo = formCC.cleaned_data['marcaModelo']
				imei 		= formCC.cleaned_data['imei']
				falla 		= formCC.cleaned_data['falla']
				observacion = formCC.cleaned_data['observacion']
				anticipo 	= formCC.cleaned_data['anticipo']
				reparacion 	= formCC.cleaned_data['reparacion']

				#
				monto = Reparacion.objects.get(id=reparacion).monto
				payv = None
				Cambio = 0
				pago = 0
				if anticipo >= monto:
					payv = True
					Cambio = anticipo - monto
					pago =monto
				elif anticipo > 0 and anticipo < monto:
					payv = False
					pago = anticipo
				else:
					info = "No se ha registrado la informacion, complete los campos correctamente. El anticipo debe ser mayor que Cero."
					formCC = vtaReparacion(request.POST)
					form = addClienteServicioForm(request.POST)
					buscar = False
					nvoCC = True
					boton = True

					ctx = {'nvoCC':nvoCC,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaFlexeoTecnico.html',ctx,context_instance=RequestContext(request))
				v = None
				zzz = agregarCiudades(colonia,ciudad,estado,None)
				try:
					with transaction.atomic():
						a = ClienteServicio()
						a.nombre 		= (nombre).title()
						a.direccion 	= (direccion).title()
						a.colonia 		= Colonia.objects.get(id=zzz[0])
						a.ciudad 		= Ciudad.objects.get(id=zzz[1])
						a.sucursal 		= mysucursal
						a.tipoCliente 	= 'Servicio'
						a.folio	= key
						a.save()

						c =EquipoReparacion()
						c.marcaModelo = marcaModelo
						c.imei 		= imei
						c.falla 		= falla
						c.observacion = observacion
						c.cliente 	= a
						c.reparacion 	= Reparacion.objects.get(id=reparacion)
						c.anticipo = pago
						c.sucursal 	= mysucursal
						c.estado 		= EstadoReparacion.objects.get(estado='En Sucursal - Sin enviar')
						c.fxRevision	= datetime.now()
						if payv:
							c.pagado = True
						else:
							c.pagado = False
						c.save()

						zum = comisionesReparacion()
						zum.usuario = request.user
						zum.reparacion  = c
						zum.save()

						d = HistorialClienteReparacion()
						d.equipoReparacion = c
						d.abono	= anticipo
						d.save()

						v = Venta()
						v.folioVenta = nuevoFolio2(str(mysucursal.id)+'S')
						v.sucursal 	= mysucursal
						v.usuario 	= request.user
						v.total 	= pago
						v.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
						if payv:
							v.estado 	= EstadoVenta.objects.get(estado='Pagada')
						else:
							v.estado 	= EstadoVenta.objects.get(estado='Proceso')
						v.aceptada  	= True
						v.save()

						dv = Anticipo()
						dv.folioVenta 		= v
						dv.tipoAnticipo 	= 'Servicio: Flexeo'
						dv.monto 			= pago
						dv.observacion 	= "Cliente no. "+c.cliente.folio+" "+c.cliente.nombre
						dv.save()
						
						info="Se ha registrado la entrada de un equipo para flexeo Tecnico.Folio cliente: "+str(a.folio)+" Folio de Venta: "+ v.folioVenta+" Cambio: $"+str(Cambio)
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				mfolioVenta = v.folioVenta #ticket ya
				boton= False
				nvoCC = True
				ctx = {'folioVenta':mfolioVenta, 'nvoCC':nvoCC,'boton':boton,'nivel':nivel,'info':info}
				return render_to_response('servicios/vtaFlexeoTecnico.html',ctx,context_instance=RequestContext(request))
			else:
				info = "No se registro. Verifique sus datos."
				formCC = vtaReparacion(request.POST)
				form = addClienteServicioForm(request.POST)
				buscar = False
				nvoCC = True
				boton = True
			ctx = {'nvoCC':nvoCC,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
			return render_to_response('servicios/vtaFlexeoTecnico.html',ctx,context_instance=RequestContext(request))

		if 'regCC' in request.POST:
			formCC = vtaReparacion(request.POST)
			if formCC.is_valid():#cliente conocido, porta con costo
				key 	= formCC.cleaned_data['key']
				marcaModelo = formCC.cleaned_data['marcaModelo']
				imei 		= formCC.cleaned_data['imei']
				falla 		= formCC.cleaned_data['falla']
				observacion = formCC.cleaned_data['observacion']
				anticipo 	= formCC.cleaned_data['anticipo']
				reparacion 	= formCC.cleaned_data['reparacion']

				monto = Reparacion.objects.get(id=reparacion).monto
				payv = None
				Cambio = 0
				pago = 0
				if anticipo >= monto:
					payv = True
					Cambio = anticipo - monto
					pago =monto
				elif anticipo > 0 and anticipo < monto:
					payv = False
					pago = anticipo					
				else:
					info = "No se ha registrado la informacion, complete los campos correctamente. El anticipo debe ser mayor que Cero."
					formCC = vtaReparacion(request.POST)
					buscar = False
					yaCC = True
					boton = True
					ctx = {'yaCC':yaCC,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaFlexeoTecnico.html',ctx,context_instance=RequestContext(request))

				a = ClienteServicio.objects.get(id=key)
				v = None
				try:
					with transaction.atomic():
						c =EquipoReparacion()
						c.marcaModelo = marcaModelo
						c.imei 		= imei
						c.falla 		= "Portabilidad con Costo - Equipo Flexeo"
						c.observacion = observacion
						c.cliente 	= a
						c.reparacion 	= Reparacion.objects.get(id=reparacion)
						c.anticipo = pago
						c.sucursal 	= mysucursal
						c.estado 		= EstadoReparacion.objects.get(estado='En Sucursal - Sin enviar')
						c.fxRevision	= datetime.now()
						if payv:
							c.pagado = True
						else:
							c.pagado = False
						c.save()

						zzz = comisionesReparacion()
						zzz.usuario = request.user
						zzz.reparacion  = c
						zzz.save()

						d = HistorialClienteReparacion()
						d.equipoReparacion = c
						d.abono	= anticipo
						d.save()

						v = Venta()
						v.folioVenta = nuevoFolio2(str(mysucursal.id)+'S')
						v.sucursal 	= mysucursal
						v.usuario 	= request.user
						v.total 	= pago
						v.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
						if payv:
							v.estado 	= EstadoVenta.objects.get(estado='Pagada')
						else:
							v.estado 	= EstadoVenta.objects.get(estado='Proceso')
						v.aceptada  	= True
						v.save()

						dv = Anticipo()
						dv.folioVenta 		= v
						dv.tipoAnticipo 	= 'Servicio: Flexeo'
						dv.monto 			= pago
						dv.observacion 	= "Cliente no. "+c.cliente.folio+" "+c.cliente.nombre
						dv.save()

						info="Se ha registrado la entrada de un equipo para flexeo por portabilidad con costo. Folio de Venta: "+ v.folioVenta+" Cambio: $"+str(Cambio)+" Cliente: "+str(a.folio)
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				mfolioVenta = v.folioVenta #ticket ya
				buscar = False
				yaCC = True
				boton = False
				ctx = {'folioVenta':mfolioVenta, 'yaCC':yaCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
				return render_to_response('servicios/vtaFlexeoTecnico.html',ctx,context_instance=RequestContext(request))
				
			else:
				info = "No se registro. Verifique sus datos."
				formCC = vtaReparacion(request.POST)
				buscar = False
				yaCC = True
				boton = True
			ctx = {'yaCC':yaCC,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
			return render_to_response('servicios/vtaFlexeoTecnico.html',ctx,context_instance=RequestContext(request))	
		
		ctx = {'query':query,'results':results,'buscar':buscar,'nivel':nivel,'info':info}
		return render_to_response('servicios/vtaFlexeoTecnico.html',ctx,context_instance=RequestContext(request))
	
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo ticket poi x
@login_required(login_url='/')
def servicios_ventas_reparacion_fisica_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		query = ""
		results = ""
		buscar = True
		boton = True
		nvoCC = False
		yaCC = False
		info=""
		formCC = vtaReparacionFis()
		form = addClienteServicioForm()

		if request.method == "GET":
			
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					
					qset = (Q(nombre__icontains=query)|Q(direccion__icontains=query)|Q(colonia__colonia__icontains=query)|Q(sucursal__nombre__icontains=query)|Q(folio__icontains=query)|Q(fxIngreso__icontains=query) )
					results = ClienteServicio.objects.filter(qset,tipoCliente__icontains='Servicio').distinct()

				else:
					results = []

				buscar = True
				ctx = {'query':query,'results':results,'buscar':buscar,'nivel':nivel,'info':info}
				return render_to_response('servicios/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))
				
			if request.GET.get('cliCCosto'):
				cliente = request.GET.get('cliCCosto','')
				if cliente:
					cli = ClienteServicio.objects.get(id=cliente)
					formCC = vtaReparacionFis({'key':cli.id,'cliente':cli.nombre,'falla':'Reparacion Fisica' })

					buscar = False
					yaCC = True
					boton = True
					ctx = {'yaCC':yaCC,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('nvoCCosto'):
				cliente = request.GET.get('nvoCCosto','')
				if cliente:
					formCC = vtaReparacionFis({'key':nvofolioCliente(),'cliente':'Nuevo','falla':'reparacion Fisica'})

					buscar = False
					nvoCC = True
					boton = True
					ctx = {'nvoCC':nvoCC,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))
			
			if request.GET.get('print'):
				vta = request.GET.get('print','')
				if vta:
					mivi = None
					try:
						v = Venta.objects.get(folioVenta=vta)
						ok = suc_Permisos(nivel,request.user,v.sucursal)
						if ok:
							mivi = listarTicket(vta)
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('servicios/ticket.html',ctx,context_instance=RequestContext(request))

		if 'regNvoCC' in request.POST:
			formCC = vtaReparacionFis(request.POST)
			form = addClienteServicioForm(request.POST)

			if form.is_valid() and formCC.is_valid():
				#nuevo cliente, porta con costo
				nombre 		= form.cleaned_data['nombre']
				direccion 	= form.cleaned_data['direccion']
				colonia 	= form.cleaned_data['colonia']
				ciudad  	= form.cleaned_data['ciudad']
				estado 		= form.cleaned_data['estado']
				#

				key 		= formCC.cleaned_data['key']
				marcaModelo = formCC.cleaned_data['marcaModelo']
				imei 		= formCC.cleaned_data['imei']
				falla 		= formCC.cleaned_data['falla']
				observacion = formCC.cleaned_data['observacion']
				anticipo 	= formCC.cleaned_data['anticipo']
				reparacion 	= formCC.cleaned_data['reparacion']

				#
				monto = Reparacion.objects.get(id=reparacion).monto
				payv = None
				Cambio = 0
				pago = 0
				if anticipo >= monto:
					payv = True
					Cambio = anticipo - monto
					pago =monto
				elif anticipo > 0 and anticipo < monto:
					payv = False
					pago = anticipo
				else:
					info = "No se ha registrado la informacion, complete los campos correctamente. El anticipo debe ser mayor que Cero."
					formCC = vtaReparacionFis(request.POST)
					form = addClienteServicioForm(request.POST)
					buscar = False
					nvoCC = True
					boton = True

					ctx = {'nvoCC':nvoCC,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))
				v = None
				zzz = agregarCiudades(colonia,ciudad,estado,None)
				try:	
					with transaction.atomic():
						a = ClienteServicio()
						a.nombre 		= (nombre).title()
						a.direccion 	= (direccion).title()
						a.colonia 		= Colonia.objects.get(id=zzz[0])
						a.ciudad 		= Ciudad.objects.get(id=zzz[1])
						a.sucursal 		= mysucursal
						a.tipoCliente 	= 'Servicio'
						a.folio	= key
						a.save()

						c =EquipoReparacion()
						c.marcaModelo = marcaModelo
						c.imei 		= imei
						c.falla 		= falla
						c.observacion = observacion
						c.cliente 	= a
						c.reparacion 	= Reparacion.objects.get(id=reparacion)
						c.anticipo = pago
						c.sucursal 	= mysucursal
						c.estado 		= EstadoReparacion.objects.get(estado='En Sucursal - Sin enviar')
						c.fxRevision	= datetime.now()
						if payv:
							c.pagado = True
						else:
							c.pagado = False
						c.save()

						zum = comisionesReparacion()
						zum.usuario = request.user
						zum.reparacion  = c
						zum.save()

						d = HistorialClienteReparacion()
						d.equipoReparacion = c
						d.abono	= anticipo
						d.save()

						v = Venta()
						v.folioVenta = nuevoFolio2(str(mysucursal.id)+'S')
						v.sucursal 	= mysucursal
						v.usuario 	= request.user
						v.total 	= pago
						v.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
						if payv:
							v.estado 	= EstadoVenta.objects.get(estado='Pagada')
						else:
							v.estado 	= EstadoVenta.objects.get(estado='Proceso')
						v.aceptada  	= True
						v.save()

						dv = Anticipo()
						dv.folioVenta 		= v
						dv.tipoAnticipo 	= 'Servicio: Rep. Fisica'
						dv.monto 			= pago
						dv.observacion 	= "Cliente no. "+c.cliente.folio+" "+c.cliente.nombre
						dv.save()
						
						info="Se ha registrado la entrada de un equipo para flexeo Tecnico.Folio cliente: "+str(a.folio)+" Folio de Venta: "+ v.folioVenta+" Cambio: $"+str(Cambio)
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				mfolioVenta = v.folioVenta #ticket ya
				boton= False
				nvoCC = True
				ctx = {'folioVenta':mfolioVenta, 'nvoCC':nvoCC,'boton':boton,'nivel':nivel,'info':info}
				return render_to_response('servicios/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))
			else:
				info = "No se registro. Verifique sus datos."
				formCC = vtaReparacionFis(request.POST)
				form = addClienteServicioForm(request.POST)
				buscar = False
				nvoCC = True
				boton = True
			ctx = {'nvoCC':nvoCC,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
			return render_to_response('servicios/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))

		if 'regCC' in request.POST:
			formCC = vtaReparacionFis(request.POST)
			if formCC.is_valid():#cliente conocido, porta con costo

				key 	= formCC.cleaned_data['key']
				marcaModelo = formCC.cleaned_data['marcaModelo']
				imei 		= formCC.cleaned_data['imei']
				falla 		= formCC.cleaned_data['falla']
				observacion = formCC.cleaned_data['observacion']
				anticipo 	= formCC.cleaned_data['anticipo']
				reparacion 	= formCC.cleaned_data['reparacion']

				monto = Reparacion.objects.get(id=reparacion).monto
				payv = None
				Cambio = 0
				pago = 0
				if anticipo >= monto:
					payv = True
					Cambio = anticipo - monto
					pago =monto
				elif anticipo > 0 and anticipo < monto:
					payv = False
					pago = anticipo					
				else:
					info = "No se ha registrado la informacion, complete los campos correctamente. El anticipo debe ser mayor que Cero."
					formCC = vtaReparacionFis(request.POST)
					buscar = False
					yaCC = True
					boton = True
					ctx = {'yaCC':yaCC,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))

				a = ClienteServicio.objects.get(id=key)
				v = None
				try:
					with transaction.atomic():
						c =EquipoReparacion()
						c.marcaModelo = marcaModelo
						c.imei 		= imei
						c.falla 		= formCC.cleaned_data['falla']
						c.observacion = observacion
						c.cliente 	= a
						c.reparacion 	= Reparacion.objects.get(id=reparacion)
						c.anticipo = pago
						c.sucursal 	= mysucursal
						c.estado 		= EstadoReparacion.objects.get(estado='En Sucursal - Sin enviar')
						c.fxRevision	= datetime.now()
						if payv:
							c.pagado = True
						else:
							c.pagado = False
						c.save()

						zzz = comisionesReparacion()
						zzz.usuario = request.user
						zzz.reparacion  = c
						zzz.save()

						d = HistorialClienteReparacion()
						d.equipoReparacion = c
						d.abono	= anticipo
						d.save()

						v = Venta()
						v.folioVenta = nuevoFolio2(str(mysucursal.id)+'S')
						v.sucursal 	= mysucursal
						v.usuario 	= request.user
						v.total 	= pago
						v.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
						if payv:
							v.estado 	= EstadoVenta.objects.get(estado='Pagada')
						else:
							v.estado 	= EstadoVenta.objects.get(estado='Proceso')
						v.aceptada  	= True
						v.save()

						dv = Anticipo()
						dv.folioVenta 		= v
						dv.tipoAnticipo 	= 'Servicio: Rep. Fisica'
						dv.monto 			= pago
						dv.observacion 	= "Cliente no. "+c.cliente.folio+" "+c.cliente.nombre
						dv.save()

						info="Se ha registrado la entrada de un equipo. Folio de Venta: "+ v.folioVenta+" Cambio: $"+str(Cambio)+" Cliente: "+str(a.folio)
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				mfolioVenta = v.folioVenta #ticket ya
				buscar = False
				yaCC = True
				boton = False
				ctx = {'folioVenta':mfolioVenta, 'yaCC':yaCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
				return render_to_response('servicios/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))
				
			else:
				info = "No se registro. Verifique sus datos."
				formCC = vtaReparacionFis(request.POST)
				buscar = False
				yaCC = True
				boton = True
			ctx = {'yaCC':yaCC,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
			return render_to_response('servicios/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))	
		
		ctx = {'query':query,'results':results,'buscar':buscar,'nivel':nivel,'info':info}
		return render_to_response('servicios/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))
	
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo ticket poi x
@login_required(login_url='/')
def servicios_ventas_carga_software_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		query = ""
		results = ""
		buscar = True
		boton = True
		nvoCC = False
		yaCC = False
		info=""
		formCC = vtaReparacionSW()
		form = addClienteServicioForm()

		if request.method == "GET":
			
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					
					qset = (Q(nombre__icontains=query)|Q(direccion__icontains=query)|Q(colonia__colonia__icontains=query)|Q(sucursal__nombre__icontains=query)|Q(folio__icontains=query)|Q(fxIngreso__icontains=query) )
					results = ClienteServicio.objects.filter(qset,tipoCliente__icontains='Servicio').distinct()

				else:
					results = []

				buscar = True
				ctx = {'query':query,'results':results,'buscar':buscar,'nivel':nivel,'info':info}
				return render_to_response('servicios/vtaCargaSoftware.html',ctx,context_instance=RequestContext(request))
				
			if request.GET.get('cliCCosto'):
				cliente = request.GET.get('cliCCosto','')
				if cliente:
					cli = ClienteServicio.objects.get(id=cliente)
					formCC = vtaReparacionSW({'key':cli.id,'cliente':cli.nombre,'falla':'Carga de Software' })

					buscar = False
					yaCC = True
					boton = True
					ctx = {'yaCC':yaCC,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaCargaSoftware.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('nvoCCosto'):
				cliente = request.GET.get('nvoCCosto','')
				if cliente:
					formCC = vtaReparacionSW({'key':nvofolioCliente(),'cliente':'Nuevo','falla':'Carga de Software'})

					buscar = False
					nvoCC = True
					boton = True
					ctx = {'nvoCC':nvoCC,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaCargaSoftware.html',ctx,context_instance=RequestContext(request))
			
			if request.GET.get('print'):
				vta = request.GET.get('print','')
				if vta:
					mivi = None
					try:
						v = Venta.objects.get(folioVenta=vta)
						ok = suc_Permisos(nivel,request.user,v.sucursal)
						if ok:
							mivi = listarTicket(vta)
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('servicios/ticket.html',ctx,context_instance=RequestContext(request))

		if 'regNvoCC' in request.POST:
			formCC = vtaReparacionSW(request.POST)
			form = addClienteServicioForm(request.POST)

			if form.is_valid() and formCC.is_valid():
				#nuevo cliente, porta con costo
				nombre 		= form.cleaned_data['nombre']
				direccion 	= form.cleaned_data['direccion']
				colonia 	= form.cleaned_data['colonia']
				ciudad  	= form.cleaned_data['ciudad']
				estado 		= form.cleaned_data['estado']
				#

				key 		= formCC.cleaned_data['key']
				marcaModelo = formCC.cleaned_data['marcaModelo']
				imei 		= formCC.cleaned_data['imei']
				falla 		= formCC.cleaned_data['falla']
				observacion = formCC.cleaned_data['observacion']
				anticipo 	= formCC.cleaned_data['anticipo']
				reparacion 	= formCC.cleaned_data['reparacion']

				#
				monto = Reparacion.objects.get(id=reparacion).monto
				payv = None
				Cambio = 0
				pago = 0
				if anticipo >= monto:
					payv = True
					Cambio = anticipo - monto
					pago =monto
				elif anticipo > 0 and anticipo < monto:
					payv = False
					pago = anticipo
				else:
					info = "No se ha registrado la informacion, complete los campos correctamente. El anticipo debe ser mayor que Cero."
					formCC = vtaReparacionSW(request.POST)
					form = addClienteServicioForm(request.POST)
					buscar = False
					nvoCC = True
					boton = True

					ctx = {'nvoCC':nvoCC,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaCargaSoftware.html',ctx,context_instance=RequestContext(request))
				v = None
				zzz = agregarCiudades(colonia,ciudad,estado,None)
				try:	
					with transaction.atomic():
						a = ClienteServicio()
						a.nombre 		= (nombre).title()
						a.direccion 	= (direccion).title()
						a.colonia 		= Colonia.objects.get(id=zzz[0])
						a.ciudad 		= Ciudad.objects.get(id=zzz[1])
						a.sucursal 		= mysucursal
						a.tipoCliente 	= 'Servicio'
						a.folio	= key
						a.save()

						c =EquipoReparacion()
						c.marcaModelo = marcaModelo
						c.imei 		= imei
						c.falla 		= falla
						c.observacion = observacion
						c.cliente 	= a
						c.reparacion 	= Reparacion.objects.get(id=reparacion)
						c.anticipo = pago
						c.sucursal 	= mysucursal
						c.estado 		= EstadoReparacion.objects.get(estado='En Sucursal - Sin enviar')
						c.fxRevision	= datetime.now()
						if payv:
							c.pagado = True
						else:
							c.pagado = False
						c.save()

						zum = comisionesReparacion()
						zum.usuario = request.user
						zum.reparacion  = c
						zum.save()

						d = HistorialClienteReparacion()
						d.equipoReparacion = c
						d.abono	= anticipo
						d.save()

						v = Venta()
						v.folioVenta = nuevoFolio2(str(mysucursal.id)+'S')
						v.sucursal 	= mysucursal
						v.usuario 	= request.user
						v.total 	= pago
						v.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
						if payv:
							v.estado 	= EstadoVenta.objects.get(estado='Pagada')
						else:
							v.estado 	= EstadoVenta.objects.get(estado='Proceso')
						v.aceptada  	= True
						v.save()

						dv = Anticipo()
						dv.folioVenta 		= v
						dv.tipoAnticipo 	= 'Servicio: C. Software'
						dv.monto 			= pago
						dv.observacion 	= "Cliente no. "+c.cliente.folio+" "+c.cliente.nombre
						dv.save()
						
						info="Se ha registrado la entrada de un equipo.Folio cliente: "+str(a.folio)+" Folio de Venta: "+ v.folioVenta+" Cambio: $"+str(Cambio)
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				mfolioVenta = v.folioVenta #ticket ya
				boton= False
				nvoCC = True
				ctx = {'folioVenta':mfolioVenta, 'nvoCC':nvoCC,'boton':boton,'nivel':nivel,'info':info}
				return render_to_response('servicios/vtaCargaSoftware.html',ctx,context_instance=RequestContext(request))
			else:
				info = "No se registro. Verifique sus datos."
				formCC = vtaReparacionSW(request.POST)
				form = addClienteServicioForm(request.POST)
				buscar = False
				nvoCC = True
				boton = True
			ctx = {'nvoCC':nvoCC,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
			return render_to_response('servicios/vtaCargaSoftware.html',ctx,context_instance=RequestContext(request))

		if 'regCC' in request.POST:
			formCC = vtaReparacionSW(request.POST)
			if formCC.is_valid():#cliente conocido, porta con costo

				key 	= formCC.cleaned_data['key']
				marcaModelo = formCC.cleaned_data['marcaModelo']
				imei 		= formCC.cleaned_data['imei']
				falla 		= formCC.cleaned_data['falla']
				observacion = formCC.cleaned_data['observacion']
				anticipo 	= formCC.cleaned_data['anticipo']
				reparacion 	= formCC.cleaned_data['reparacion']

				monto = Reparacion.objects.get(id=reparacion).monto
				payv = None
				Cambio = 0
				pago = 0
				if anticipo >= monto:
					payv = True
					Cambio = anticipo - monto
					pago =monto
				elif anticipo > 0 and anticipo < monto:
					payv = False
					pago = anticipo					
				else:
					info = "No se ha registrado la informacion, complete los campos correctamente. El anticipo debe ser mayor que Cero."
					formCC = vtaReparacionSW(request.POST)
					buscar = False
					yaCC = True
					boton = True
					ctx = {'yaCC':yaCC,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaCargaSoftware.html',ctx,context_instance=RequestContext(request))

				a = ClienteServicio.objects.get(id=key)
				v = None
				try:
					with transaction.atomic():
						c =EquipoReparacion()
						c.marcaModelo = marcaModelo
						c.imei 		= imei
						c.falla 		= formCC.cleaned_data['falla']
						c.observacion = observacion
						c.cliente 	= a
						c.reparacion 	= Reparacion.objects.get(id=reparacion)
						c.anticipo = pago
						c.sucursal 	= mysucursal
						c.estado 		= EstadoReparacion.objects.get(estado='En Sucursal - Sin enviar')
						c.fxRevision	= datetime.now()
						if payv:
							c.pagado = True
						else:
							c.pagado = False
						c.save()

						zzz = comisionesReparacion()
						zzz.usuario = request.user
						zzz.reparacion  = c
						zzz.save()

						d = HistorialClienteReparacion()
						d.equipoReparacion = c
						d.abono	= anticipo
						d.save()

						v = Venta()
						v.folioVenta = nuevoFolio2(str(mysucursal.id)+'S')
						v.sucursal 	= mysucursal
						v.usuario 	= request.user
						v.total 	= pago
						v.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
						if payv:
							v.estado 	= EstadoVenta.objects.get(estado='Pagada')
						else:
							v.estado 	= EstadoVenta.objects.get(estado='Proceso')
						v.aceptada  	= True
						v.save()

						dv = Anticipo()
						dv.folioVenta 		= v
						dv.tipoAnticipo 	= 'Servicio: Carga Software'
						dv.monto 			= pago
						dv.observacion 	= "Cliente no. "+c.cliente.folio+" "+c.cliente.nombre
						dv.save()

						info="Se ha registrado la entrada de un equipo. Folio de Venta: "+ v.folioVenta+" Cambio: $"+str(Cambio)+" Cliente: "+str(a.folio)
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				mfolioVenta = v.folioVenta #ticket ya
				buscar = False
				yaCC = True
				boton = False
				ctx = {'folioVenta':mfolioVenta, 'yaCC':yaCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
				return render_to_response('servicios/vtaCargaSoftware.html',ctx,context_instance=RequestContext(request))
				
			else:
				info = "No se registro. Verifique sus datos."
				formCC = vtaReparacionSW(request.POST)
				buscar = False
				yaCC = True
				boton = True
			ctx = {'yaCC':yaCC,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info}
			return render_to_response('servicios/vtaCargaSoftware.html',ctx,context_instance=RequestContext(request))	
		
		ctx = {'query':query,'results':results,'buscar':buscar,'nivel':nivel,'info':info}
		return render_to_response('servicios/vtaCargaSoftware.html',ctx,context_instance=RequestContext(request))
	
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo ticket poi
@login_required(login_url='/')
def servicios_ventas_accesorios_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:

		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		
		form = AddVentaCaja()
		
		resultAdd = ""
		queryAcc = ""
		show = True
		info=""
		vta = nuevoFolio2(str(mysucursal.id)+'S')
		form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas(vta)})
		accVendido = None
		try:
			accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
		except VentaAccesorio.DoesNotExist:
			accVendido = None
		
		if request.method == "GET":
			m=None
			if request.GET.get('addAcc'):
				queryAcc = request.GET.get('qAcc','')
				vta = request.GET.get('vtaGral','')
				
				resultAdd = addAccVta1(queryAcc, request.GET.get('mcPrecio'),mysucursal, vta, request.user)
				updVta(vta,mysucursal,request.user)
				form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas(vta)})
				try:
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
				except VentaAccesorio.DoesNotExist:
					accVendido = None
				show=True
				ctx = {'show':show,'accVendido':accVendido,'vtaForm':form ,'resultAdd':resultAdd,'queryAcc':queryAcc,'vtaGenerada':vta,'nivel':nivel,'info':info}				
				return render_to_response('servicios/vtaAccesorios.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('print'):
				vta = request.GET.get('print','')
				if vta:
					mivi = None
					try:
						v = Venta.objects.get(folioVenta=vta)
						ok = suc_Permisos(nivel,request.user,v.sucursal)
						if ok:
							mivi = listarTicket(vta)
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('servicios/ticket.html',ctx,context_instance=RequestContext(request))

		if 'cobrar' in request.POST:
			form = AddVentaCaja(request.POST)
			if form.is_valid():
				ifolioVenta = form.cleaned_data['folioVenta']
				efectivo 	= form.cleaned_data['efectivo']
				total 		= form.cleaned_data['total']

				if efectivo >= total and total > 0:
					try:
						with transaction.atomic():
							vtaGral =  Venta.objects.get(folioVenta=ifolioVenta)
							vtaGral.total 		= total
							vtaGral.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
							vtaGral.aceptada  	= True
							vtaGral.estado 		= EstadoVenta.objects.get(estado='Pagada')
							vtaGral.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

					vta= nuevoFolio2(str(mysucursal.id)+'S')
					form = AddVentaCaja({'folioVenta':vta,'total':0})
					show= False
					info=" Venta "+vtaGral.estado.estado+" - " + vtaGral.folioVenta +" Cambio: $ "+str(efectivo - total)
					mfolioVenta = vtaGral.folioVenta #ticket ya
					
					ctx = {'folioVenta':mfolioVenta,'show':show,'vtaGenerada':vta,'vtaForm':form,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaAccesorios.html',ctx,context_instance=RequestContext(request))
				else:
					show = True
					info = "El pago debe ser mayor o igual al monto total a pagar. Debe ingresar por lo menos un producto a la venta"
					form = AddVentaCaja(request.POST)
					ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaAccesorios.html',ctx,context_instance=RequestContext(request))
			else:
				form = AddVentaCaja(request.POST)
				info = "Ingrese $monto del cliente a pagar. Debe ingresar al menos un producto a la venta"
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('servicios/vtaAccesorios.html',ctx,context_instance=RequestContext(request))

		if 'cancelar' in request.POST:
			form = AddVentaCaja(request.POST)

			if form.is_valid():
				ifolioVenta 	= form.cleaned_data['folioVenta']
				efectivo 	= form.cleaned_data['efectivo']
				total 		= form.cleaned_data['total']

				if total > 0:
					try:
						with transaction.atomic():
							vtaGral =  Venta.objects.get(folioVenta=ifolioVenta)
							vtaGral.total 		= total
							vtaGral.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
							vtaGral.aceptada 	= False
							vtaGral.estado 		= EstadoVenta.objects.get(estado='Cancelada')
							vtaGral.save()

							results = cancelaProductos(vtaGral.id) # Poner productos en cancelacion
							
							info="Venta Cancelada: "+ vtaGral.folioVenta + "- En espera de autorizacion. "+results
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

					form = AddVentaCaja()
					vta= nuevoFolio2(str(mysucursal.id)+'S')
					form = AddVentaCaja({'folioVenta':vta,'total':0})
					show=False
					ctx = {'show':show,'vtaGenerada':vta,'vtaForm':form,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaAccesorios.html',ctx,context_instance=RequestContext(request))
				else:
					form = AddVentaCaja(request.POST)
					info = "Debe ingresar al menos un producto a la venta."
					ctx = {'show':show,'accVendido':accVendido,'vtaForm':form ,'resultAdd':resultAdd,'queryAcc':queryAcc,'vtaGenerada':vta,'nivel':nivel,'info':info}
					return render_to_response('servicios/vtaAccesorios.html',ctx,context_instance=RequestContext(request))
			else:
				form = AddVentaCaja(request.POST)
				info = "Ingrese el monto que pago el cliente, si en dado caso se cancelo, ponga un 0. Debe ingresar por lo menos un producto a la venta."
				ctx = {'show':show,'accVendido':accVendido,'vtaForm':form ,'resultAdd':resultAdd,'queryAcc':queryAcc,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('servicios/vtaAccesorios.html',ctx,context_instance=RequestContext(request))
		
		ctx = {'show':show,'vtaGenerada':vta,'vtaForm':form,'nivel':nivel,'info':info}
		return render_to_response('servicios/vtaAccesorios.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo --
@login_required(login_url='/')
def servicios_corte_vta_caja_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:

		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		#corte activo
		corteActivo = generarCorte(mysucursal,None, request.user)
		#llenamos el corte activo de la sucursal
		fillCorte(corteActivo,mysucursal)
		#actualizamos el corte activo
		updCorte(corteActivo)
		
		manana = datetime.today() + timedelta(days=1) # mañana
		hoy = datetime.today() - timedelta(days=1)
		#filtrar los cortes de la sucursal  de hoy y mañana
		Cortes = CorteVenta.objects.filter(sucursal=mysucursal,fxCorte__range=[hoy,manana])
		vtasCorte = VentasCorte.objects.all()
		accVendido = None
		vtaAnticipo = None
		try:
			accVendido = VentaAccesorio.objects.all()
			vtaAnticipo = Anticipo.objects.all()
		except VentaAccesorio.DoesNotExist:
			accVendido = None
		except Anticipo.DoesNotExist:
			vtaAnticipo = None

		verificarForm = AuthenticationForm()
		arqForm = addArqueoCaja()
		info =""
		if request.method == "GET":
			if request.GET.get('mopen'):
				query = request.GET.get('mopen','')
				if query:
					Cortes = CorteVenta.objects.filter(sucursal=mysucursal,cerrado=False)
					
			if request.GET.get('arqueo'):
				query = request.GET.get('arqueo','')
				if query:
					#dirigir identificacion de empleado - auditor
					info="Debe identificarse el usuario que auditara el arqueo."
					verificarForm = AuthenticationForm()
					ctx = {'verificarForm':verificarForm ,'nivel':nivel}
					return render_to_response('servicios/myVerificacionUser.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('cancelaciones'):
				query = request.GET.get('cancelaciones','')
				if query:
					vtaCanceladas = Venta.objects.filter(sucursal=mysucursal,aceptada=False,activa=True)
					ctx = {'anticipo':vtaAnticipo,'accVendido':accVendido,'vtaCanceladas':vtaCanceladas,'nivel':nivel}
					return render_to_response('servicios/cancelacionServ.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('print'):
				corte = request.GET.get('print','')
				if corte:
					mivi = None
					try:
						Cortes = CorteVenta.objects.get(folioCorteVta=corte)
						ok = suc_Permisos(nivel,request.user,Cortes.sucursal)
						if ok:
							mivi = listarCorte(corte) #papitas call method
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('servicios/ticketCorte.html',ctx,context_instance=RequestContext(request))

		if 'addArqueo' in request.POST:
			arqForm = addArqueoCaja(request.POST)
			if arqForm.is_valid():
				
				auditor 		= arqForm.cleaned_data['auditor']
				totalCaja 		= arqForm.cleaned_data['totalCaja']
				totalArqueo 	= arqForm.cleaned_data['totalArqueo']
				observaciones 	= arqForm.cleaned_data['observaciones']

				audita = Usuario.objects.get(user__username=auditor)
				dif = totalArqueo - totalCaja

				try:
					with transaction.atomic():
						a = ArqueoCaja()
						a.sucursal 		= mysucursal
						a.vendedor 		= request.user
						a.auditor 		= audita.empleado
						a.totalCaja 	= totalCaja
						a.totalArqueo 	= totalArqueo
						a.observaciones = observaciones
						a.difArqueo	= dif
						if dif < 0:
							a.addCtaEmpleado = True
							#crear Cuenta para esa sancion al empleado
							today = datetime.now() #fecha actual
							d = today.strftime("%d%m%Y") # fecha con formato
							numero=CuentaEmpleado.objects.count()
							folio 		= '%s%s'%(numero+1,d)

							cuenta=CuentaEmpleado()
							cuenta.folio 		= folio
							cuenta.empleado 	= Usuario.objects.get(user=request.user).empleado
							cuenta.tipoCuenta 	= TipoCuenta.objects.get(tipo='Diferencia en Arqueo')
							cuenta.monto 		= (dif)*-1
							cuenta.observacion =  "Arqueo realizado por Usuario: "+str(auditor)+" Fecha:"+datetime.now().strftime("%Y - %m - %d %H:%M")
							cuenta.adeudo  = (dif)*-1
							cuenta.save()
							info = info + "Se detecto un arqueo negativo por lo que se genero un adeudo al empleado"
							info = info +" cuenta "+str(cuenta)+" Folio "+str(cuenta.folio)
							a.observaciones = observaciones + " || Arqueo realizado por usuario: "+str(auditor)+" con diferencia "+str(dif)+" se agrego cuenta con folio "+str(cuenta.folio)
						else:
							a.addCtaEmpleado = False
							if dif > 0:
								a.observaciones = observaciones + " || Arqueo realizado por usuario: "+str(auditor) + " sobrante informativo "+str(dif)
								info = info +" Se agregaron observaciones con sobrante de "+str(dif)
							else:
								info = info +" Arqueo sin diferencias "
						a.save()

						info =info +" || Se ha registrado el arqueo: "+ str(a)
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				

				ctx = {'info':info,'nivel':nivel}
				return render_to_response('servicios/myAddArqueo.html',ctx,context_instance=RequestContext(request))
			else:
				info="Ingrese "
				arqForm = addArqueoCaja(request.POST)
				ctx = {'arqForm':arqForm,'info':info,'nivel':nivel}
				return render_to_response('servicios/myAddArqueo.html',ctx,context_instance=RequestContext(request))

		if 'identificarse' in request.POST:
			
			verificarForm = AuthenticationForm(request.POST)
			
			if verificarForm.is_valid:
			
				usuario=request.POST['username']
				clave=request.POST['password']

				acceso=authenticate(username=usuario,password=clave)
				
				if acceso is not None:
					if acceso.is_active:
						try:
							auditor = Usuario.objects.get(user__username=usuario)
							## tipo de empleado (auditor, analista, contador, admingral), no inicia sesion solo se verifica sus datos
							nivel = Permiso(auditor.user,[1,2,3,4])
							if nivel != -1:
								#mandar formulario de arqueo
								caja = updCaja(mysucursal)
								arq = arqueoCaja(mysucursal)
								#llenamos datos iniciales
								arqForm = addArqueoCaja({'vendedor':request.user,'auditor':usuario,'totalCaja':caja })
								ctx = {'arqForm':arqForm,'arq':arq,'info':info,'nivel':nivel}
								return render_to_response('servicios/myAddArqueo.html',ctx,context_instance=RequestContext(request))			
							else:
								info = "No tiene privilegios para entrar a esta seccion."
						except :
							pass
							info = "El usuario no Existe o no Esta Activo. Consulte a un Administrador"
					else:
						info = 'no activo'
				else:
					info = "El usuario no Existe o no Esta Activo. Consulte a un Administrador"
			else:
				info = "Lo sentimos, los datos ingresados no corresponden al personal autorizado, intente nuevamente."
			
			verificarForm =  AuthenticationForm(request.POST)
			ctx = {'verificarForm':verificarForm,'info':info,'nivel':nivel}
			return render_to_response('servicios/myVerificacionUser.html',ctx,context_instance=RequestContext(request))
		
		ctx = {'vtasCorte':vtasCorte,'Cortes':Cortes,'anticipo':vtaAnticipo,'accVendido':accVendido,'nivel':nivel}
		return render_to_response('servicios/myCorteVentas.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo --
@login_required(login_url='/')
def servicios_corte_vta_gastos_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		corteActivo = None
		grrr=request.GET.get('thisCorte','')
		if grrr:
			#corte activo sin cerrar
			corteActivo = grrr
			#llenamos el corte activo de la sucursal
			fillCorte(corteActivo,mysucursal)
			#actualizamos el corte activo
			updCorte(corteActivo)			
		
		else:
			#corte activo del dia
			corteActivo = generarCorte(mysucursal,None, request.user)
			#llenamos el corte activo de la sucursal
			fillCorte(corteActivo,mysucursal)
			#actualizamos el corte activo
			updCorte(corteActivo)
			
		
		tiene = CorteVenta.objects.get(folioCorteVta=corteActivo).total

		form = addGastosSucursal()
		info = ""
		
		if request.method == "POST":
			form = addGastosSucursal(request.POST or None)
			if form.is_valid():

				tipoGasto 	= form.cleaned_data['tipoGasto']
				gasto 		= form.cleaned_data['gasto']
				observacion = form.cleaned_data['observacion']				
				if gasto <= tiene:
					try:
						with transaction.atomic():
							a = GastosSucursal()
							a.tipoGasto = tipoGasto
							a.gasto 	= gasto
							a.sucursal 	= mysucursal
							a.usuario 	= request.user
							a.observacion = observacion
							a.corteVenta  = CorteVenta.objects.get(folioCorteVta=corteActivo)
							a.save()
							info = "Se ha registrado el gasto al Corte Activo : "+corteActivo
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				else:
					info = "No se puede registrar el gasto, el corte contiene un total menor al gasto. Corte: "+corteActivo
				form = addGastosSucursal()
				ctx = {'corte':corteActivo,'form':form,'info':info,'nivel':nivel}
				return render_to_response('servicios/myAddGastos.html',ctx,context_instance=RequestContext(request))
			
			else:
				info = "Ingrese Datos al formulario"
				form= addGastosSucursal(request.POST)
		
		ctx = {'corte':corteActivo,'form':form,'info':info,'nivel':nivel}
		return render_to_response('servicios/myAddGastos.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo --r
@login_required(login_url='/')
def servicios_corte_vta_cerrar_corte_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:

		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		
		corteActivo = None
		verificarForm = AuthenticationForm()
		form = updCorteVenta()

		show = True
		info = ""
		cerrar = True
		grrr=request.GET.get('thisCorte','')
		q = request.POST.get('thisCorte','')
		if q:
			grrr = q
		if grrr or q:
			#corte activo sin cerrar
			if grrr:
				corteActivo = grrr
			if q:
				corteActivo = q
			#llenamos el corte activo de la sucursal
			#fillCorte(corteActivo,mysucursal)
			#actualizamos el corte activo
			#updCorte(corteActivo)
			c = CorteVenta.objects.get(folioCorteVta=corteActivo)
			form = updCorteVenta({'folioCorteVta':c.folioCorteVta,'sucursal':c.sucursal.nombre,'totalVta':c.totalVta,'totalGastos':c.totalGastos,'total':c.total})
		
		else:
			#corte activo del dia
			corteActivo = generarCorte(mysucursal,None, request.user)
			#llenamos el corte activo de la sucursal
			fillCorte(corteActivo,mysucursal)
			#actualizamos el corte activo
			updCorte(corteActivo)
			c = CorteVenta.objects.get(folioCorteVta=corteActivo)
			form = updCorteVenta({'folioCorteVta':c.folioCorteVta,'sucursal':c.sucursal.nombre,'totalVta':c.totalVta,'totalGastos':c.totalGastos,'total':c.total})
		
		if request.method == "GET":
			m=None
			if request.GET.get('tomorrow'):
				t = request.GET.get('tomorrow','')
				if t:
					corte = generarCorte(mysucursal,'manana', request.user)
					info = 'El corte de venta se ha generado correctamente. Folio: '+ corte
					show= False
					cerrar = False
					ctx = {'cerrar':cerrar,'show':show,'info':info,'nivel':nivel}
					return render_to_response('servicios/myCerrarCorte.html',ctx,context_instance=RequestContext(request))
			

			if request.GET.get('hoy'):
				t = request.GET.get('hoy','')
				if t:
					corte = generarCorte(mysucursal,None, request.user)
					info = 'El corte de venta se ha generado correctamente. Folio: '+ corte
					show= False
					cerrar = False
					ctx = {'cerrar':cerrar,'show':show,'info':info,'nivel':nivel}
					return render_to_response('servicios/myCerrarCorte.html',ctx,context_instance=RequestContext(request))
		
		if 'cerrar' in request.POST:
			form = updCorteVenta(request.POST or None)
			if form.is_valid():
				folioCorteVta 	= form.cleaned_data['folioCorteVta']
				observacion 	= form.cleaned_data['observacion']
				try:
					with transaction.atomic():
						upd = CorteVenta.objects.get(folioCorteVta=folioCorteVta)
						upd.observacion = observacion
						upd.cierraCorte = request.user
						upd.cerrado 	= True
						upd.save()
						info = 'El corte de venta se ha cerrado correctamente. Folio: '+ upd.folioCorteVta
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				show =  False
				cerrar = True
				ctx = {'cerrar':cerrar,'show':show,'info':info,'nivel':nivel}
				return render_to_response('servicios/myCerrarCorte.html',ctx,context_instance=RequestContext(request))
			
			else:
				info = "Verifique sus datos."
				form= updCorteVenta(request.POST)
				show = True
				cerrar = True
				ctx = {'cerrar':cerrar,'cerrarForm':form,'show':show,'info':info,'nivel':nivel}
				return render_to_response('servicios/myCerrarCorte.html',ctx,context_instance=RequestContext(request))

		if 'identificarse' in request.POST:
			
			verificarForm = AuthenticationForm(request.POST)
			
			if verificarForm.is_valid:
			
				usuario=request.POST['username']
				clave=request.POST['password']

				acceso=authenticate(username=usuario,password=clave)
				
				if acceso is not None:
					if acceso.is_active:
						try:
							vendedor = Usuario.objects.get(user__username=usuario)
							nivel=Permiso(request.user,[1,2,3,4,10]) # permisos para poder cerrar el corte, superiores y servicios
							if nivel != -1:
								q = request.POST.get('thisCorte','')
								ctx = {'thisCorte':q ,'cerrarForm':form,'show':show,'info':info,'nivel':nivel}
								return render_to_response('servicios/myCerrarCorte.html',ctx,context_instance=RequestContext(request))
							else:
								info ="El usuario no tiene Permiso para realizar esta operacion"
						except Usuario.DoesNotExist:
								pass
					else:
						info = "Usuario no Activo"
				else:
					info = "Usuario o contraseña incorrectos"
			else:
				info = "Lo sentimos, los datos ingresados no corresponden al personal autorizado, intente nuevamente."
			
			verificarForm =  AuthenticationForm(request.POST)
			ctx = {'thisCorte':grrr,'verificarForm':verificarForm,'info':info,'nivel':nivel}
			return render_to_response('servicios/myVerificacionUser.html',ctx,context_instance=RequestContext(request))

		ctx = {'thisCorte':grrr,'verificarForm':verificarForm,'info':info,'nivel':nivel}
		return render_to_response('servicios/myVerificacionUser.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo --
@login_required(login_url='/')
def servicios_inventario_accesorios_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		
		pagina=request.GET.get('pagina','')
		b_item=request.GET.get('item','')
		items=None
		nItems=0
		if b_item:
			qset=(Q(accesorio__codigoBarras__icontains=b_item)|
			Q(accesorio__detallesAccesorio__marca__marca__icontains=b_item)|
			Q(accesorio__detallesAccesorio__descripcion__icontains=b_item))
			items=AlmacenAccesorio.objects.filter(qset,sucursal=mysucursal,estado=True).order_by('accesorio__codigoBarras')
		else:
			items=AlmacenAccesorio.objects.filter(sucursal=mysucursal,estado=True)
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

		return render_to_response('servicios/existenciasAccesorio.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo --
@login_required(login_url='/')
def servicios_inventario_refacciones_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		
		pagina=request.GET.get('pagina','')
		b_item=request.GET.get('item','')
		items=None
		nItems=0
		if b_item:
			qset=(Q(accesorio__codigoBarras__icontains=b_item)|
			Q(accesorio__detallesAccesorio__marca__marca__icontains=b_item)|
			Q(accesorio__detallesAccesorio__descripcion__icontains=b_item))
			items=AlmacenAccesorio.objects.filter(qset,accesorio__detallesAccesorio__seccion__seccion__icontains='REFACCIONES',sucursal=mysucursal,estado=True).order_by('accesorio__codigoBarras')
		else:
			items=AlmacenAccesorio.objects.filter(sucursal=mysucursal,accesorio__detallesAccesorio__seccion__seccion__icontains='REFACCIONES',estado=True)
		paginator = Paginator(items, 50)
		nItems=len(items)
		itemsp=None
		try:
			itemsp = paginator.page(pagina)
		except PageNotAnInteger:
			itemsp = paginator.page(1)
		except EmptyPage:
			itemsp = paginator.page(paginator.num_pages)

		ctx={'nivel':nivel,'cosa':'REFACCIONES' ,'items':itemsp, 'b_item':b_item,  'nItems':nItems}

		return render_to_response('servicios/existenciasAccesorio.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo --
@login_required(login_url='/')
def servicios_inventario_eq_obsoletos_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		
		pagina=request.GET.get('pagina','')
		b_item=request.GET.get('item','')
		items=None
		nItems=0
		if b_item:
			qset=(Q(accesorio__codigoBarras__icontains=b_item)|
			Q(accesorio__detallesAccesorio__marca__marca__icontains=b_item)|
			Q(accesorio__detallesAccesorio__descripcion__icontains=b_item))
			items=AlmacenAccesorio.objects.filter(qset,accesorio__detallesAccesorio__seccion__seccion__icontains='EQUIPOS OBSOLETOS',sucursal=mysucursal,estado=True).order_by('accesorio__codigoBarras')
		else:
			items=AlmacenAccesorio.objects.filter(sucursal=mysucursal,accesorio__detallesAccesorio__seccion__seccion__icontains='EQUIPOS OBSOLETOS',estado=True)
		paginator = Paginator(items, 50)
		nItems=len(items)
		itemsp=None
		try:
			itemsp = paginator.page(pagina)
		except PageNotAnInteger:
			itemsp = paginator.page(1)
		except EmptyPage:
			itemsp = paginator.page(paginator.num_pages)

		ctx={'nivel':nivel,'cosa':'EQUIPOS OBSOLETOS' ,'items':itemsp, 'b_item':b_item,  'nItems':nItems}

		return render_to_response('servicios/existenciasAccesorio.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo --
@login_required(login_url='/')
def servicios_reportes_caja_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:

		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		#corte activo
		corteActivo = generarCorte(mysucursal,None, request.user)
		#llenamos el corte activo de la sucursal
		fillCorte(corteActivo,mysucursal)
		#actualizamos el corte activo
		updCorte(corteActivo)
		info=""
		#mandar formulario de arqueo
		caja = updCaja(mysucursal)
		
		today = datetime.now()
		dateFormat2 = today.strftime("%Y-%m-%d")

		vtaRealizadas = Venta.objects.filter(sucursal=mysucursal,fecha__startswith=dateFormat2)
		accVendido = None
		vtaAnticipo = None
		try:
			accVendido = VentaAccesorio.objects.all()
			vtaAnticipo = Anticipo.objects.all()
		except VentaAccesorio.DoesNotExist:
			accVendido = None
		except Anticipo.DoesNotExist:
			vtaAnticipo = None

		ctx = {'caja':caja,'cosa':'Realizadas','vtaRealizadas':vtaRealizadas,'accVendido':accVendido,'anticipo':vtaAnticipo,'info':info,'nivel':nivel}
		return render_to_response('servicios/allCaja.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#lista --
@login_required(login_url='/')
def servicios_autorizacion_cancelaciones_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:

		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		#corte activo
		corteActivo = generarCorte(mysucursal,None, request.user)
		#llenamos el corte activo de la sucursal
		fillCorte(corteActivo,mysucursal)
		#actualizamos el corte activo
		updCorte(corteActivo)
		info=""
		#mandar formulario de arqueo
		caja = updCaja(mysucursal)
		
		today = datetime.now()
		dateFormat2 = today.strftime("%Y-%m-%d")

		vtaRealizadas = Venta.objects.filter(sucursal=mysucursal,aceptada=False)
		accVendido = None
		vtaAnticipo = None
		try:
			accVendido = VentaAccesorio.objects.all()
			vtaAnticipo = Anticipo.objects.all()
		except VentaAccesorio.DoesNotExist:
			accVendido = None
		except Anticipo.DoesNotExist:
			vtaAnticipo = None

		ctx = {'caja':caja,'cosa':'Canceladas','vtaRealizadas':vtaRealizadas,'accVendido':accVendido,'anticipo':vtaAnticipo,'info':info,'nivel':nivel}
		return render_to_response('servicios/allCaja.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#lista --
@login_required(login_url='/')
def servicios_lista_accesorios_view(request):
	nivel=Permiso(request.user,[0,1,10])
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
		return render_to_response('servicios/listaPrecioAcces.html', ctx,context_instance=RequestContext(request))
	
	else:
		return HttpResponseRedirect('/NoTienePermiso')

# --
@login_required(login_url='/')
def servicios_transferencia_view(request):
	nivel=Permiso(request.user,[0,1,10])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)
		query  = request.GET.get('q','')
		pag1=request.GET.get('pagina','')
		msgs = Movimiento.objects.filter(sucursalDestino__id=suc,tipoMovimiento__nombre='Transferencia').order_by('-fx_movimiento')

		if query:
			msgs = Movimiento.objects.filter(sucursalDestino__id=suc,folio__icontains=query,tipoMovimiento__nombre='Transferencia').order_by('-fx_movimiento')
		
		paginator1 = Paginator(msgs, 50)
		pMovs=None
	
		try:
			pMovs = paginator1.page(pag1)
		except PageNotAnInteger:
			pMovs= paginator1.page(1)
		except EmptyPage:
			pMovs = paginator1.page(paginator1.num_pages)

		if request.method == "GET":
			if request.GET.get('revisar'):
				s = request.GET.get('revisar','')
				if s:
					mov = Movimiento.objects.get(id=s)
					transEq = ListaEquipo.objects.filter(movimiento__id=s, confirmacion=True)
					transEx = ListaExpres.objects.filter(movimiento__id=s, confirmacion=True)
					transAc = ListaAccesorio.objects.filter(movimiento__id=s, confirmacion=True)
					transFic = ListaFichas.objects.filter(movimiento__id=s, confirmacion=True)
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__id=s)

					ctx={'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('servicios/confirmacionProductos.html',ctx,context_instance=RequestContext(request))
			
			if request.GET.get('confirmar'):
				s = request.GET.get('confirmar','')
				if s:
					mov = Movimiento.objects.get(id=s)
					transEq = ListaEquipo.objects.filter(movimiento__id=s)
					transEx = ListaExpres.objects.filter(movimiento__id=s)
					transAc = ListaAccesorio.objects.filter(movimiento__id=s)
					transFic = ListaFichas.objects.filter(movimiento__id=s)
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__id=s)

					ctx={'mostrar':True,'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('servicios/confirmacionProductos.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('aceptEq'):
				s = request.GET.get('aceptEq','')
				m = request.GET.get('transfGral','')
				if s:
					mov = Movimiento.objects.get(folio=m)
					try:
						with transaction.atomic():
							upd = ListaEquipo.objects.get(id=s)
							upd.confirmacion = True
							upd.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

					transEq = ListaEquipo.objects.filter(movimiento__folio=m)
					transEx = ListaExpres.objects.filter(movimiento__folio=m)
					transAc = ListaAccesorio.objects.filter(movimiento__folio=m)
					transFic = ListaFichas.objects.filter(movimiento__folio=m)
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__folio=m)

					ctx={'mostrar':True,'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('servicios/confirmacionProductos.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('aceptEx'):
				s = request.GET.get('aceptEx','')
				m = request.GET.get('transfGral','')
				if s:
					mov = Movimiento.objects.get(folio=m)
					try:
						with transaction.atomic():
							upd = ListaExpres.objects.get(id=s)
							upd.confirmacion = True
							upd.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

					transEq = ListaEquipo.objects.filter(movimiento__folio=m)
					transEx = ListaExpres.objects.filter(movimiento__folio=m)
					transAc = ListaAccesorio.objects.filter(movimiento__folio=m)
					transFic = ListaFichas.objects.filter(movimiento__folio=m)
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__folio=m)

					ctx={'mostrar':True,'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('servicios/confirmacionProductos.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('aceptAc'):
				s = request.GET.get('aceptAc','')
				m = request.GET.get('transfGral','')
				if s:
					mov = Movimiento.objects.get(folio=m)
					try:
						with transaction.atomic():
							upd = ListaAccesorio.objects.get(id=s)
							upd.confirmacion = True
							upd.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

					transEq = ListaEquipo.objects.filter(movimiento__folio=m)
					transEx = ListaExpres.objects.filter(movimiento__folio=m)
					transAc = ListaAccesorio.objects.filter(movimiento__folio=m)
					transFic = ListaFichas.objects.filter(movimiento__folio=m)
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__folio=m)

					ctx={'mostrar':True,'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('servicios/confirmacionProductos.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('aceptFic'):
				s = request.GET.get('aceptFic','')
				m = request.GET.get('transfGral','')
				if s:
					mov = Movimiento.objects.get(folio=m)
					try:
						with transaction.atomic():
							upd = ListaFichas.objects.get(id=s)
							upd.confirmacion = True
							upd.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

					transEq = ListaEquipo.objects.filter(movimiento__folio=m)
					transEx = ListaExpres.objects.filter(movimiento__folio=m)
					transAc = ListaAccesorio.objects.filter(movimiento__folio=m)
					transFic = ListaFichas.objects.filter(movimiento__folio=m)
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__folio=m)

					ctx={'mostrar':True,'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('servicios/confirmacionProductos.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('aceptSaldo'):
				s = request.GET.get('aceptSaldo','')
				m = request.GET.get('transfGral','')
				if s:
					mov = Movimiento.objects.get(folio=m)
					try:
						with transaction.atomic():
							upd = TransferenciaSaldo.objects.get(id=s)
							upd.confirmacion = True
							upd.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

					transEq = ListaEquipo.objects.filter(movimiento__folio=m)
					transEx = ListaExpres.objects.filter(movimiento__folio=m)
					transAc = ListaAccesorio.objects.filter(movimiento__folio=m)
					transFic = ListaFichas.objects.filter(movimiento__folio=m)
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__folio=m)

					ctx={'mostrar':True,'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('servicios/confirmacionProductos.html',ctx,context_instance=RequestContext(request))

		if request.method == "POST":
			cerrar = request.POST.get('transfGral')
			try:
				with transaction.atomic():
					mov = Movimiento.objects.get(folio=cerrar)
					mov.usuarioDestino = request.user
					mov.confirmacion = True
					mov.save()
			except :
				info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

			transEq = ListaEquipo.objects.filter(movimiento__folio=mov.folio, confirmacion=False)
			transEx = ListaExpres.objects.filter(movimiento__folio=mov.folio, confirmacion=False)
			transAc = ListaAccesorio.objects.filter(movimiento__folio=mov.folio, confirmacion=False)
			transFic = ListaFichas.objects.filter(movimiento__folio=mov.folio, confirmacion=False)
			transSaldo = TransferenciaSaldo.objects.filter(movimiento__folio=mov.folio)
			mensaje = "Transferencia con Productos no Aceptados: "+mov.folio
			try:
				with transaction.atomic():
					for x in transEq:
						e = Equipo.objects.get(id=x.equipo.id)
						e.estatus = Estatus.objects.get(estatus='Sin Confirmar')
						e.save()
						try:
							u = AlmacenEquipo.objects.get(equipo=x.equipo,estado=True,sucursal__id=x.equipo.sucursal.id)
							u.estado = False
							u.save()	
						except :
							pass
						
						mensaje = mensaje + ' Equipo '+x.equipo.detallesEquipo.marca.marca+' '+x.equipo.detallesEquipo.modelo+' imei: ' +str(x.equipo.imei)+' icc: ' +str(x.equipo.icc)
			except :
				info='Nota de equipos. Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

			try:
				with transaction.atomic():
					for x in transEx:
						e = Expres.objects.get(id=x.expres.id)
						e.estatus = Estatus.objects.get(estatus='Sin Confirmar')
						e.save()
						try:
							u = AlmacenExpres.objects.get(expres=x.expres,estado=True,sucursal__id=x.expres.sucursal.id)
							u.estado = False
							u.save()	
						except :
							pass
						
						mensaje = mensaje + ' Expres icc:'+str(x.expres.icc)
			except :
				info='Nota de Expres. Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

			try:
				with transaction.atomic():
					for x in transAc:
						e = Accesorio.objects.get(id=x.accesorio.id)
						e.estatus = EstatusAccesorio.objects.get(estatus='Sin Confirmar')
						e.save()
						try:
							u = AlmacenAccesorio.objects.get(accesorio=x.accesorio,estado=True,sucursal__id=x.accesorio.sucursal.id)
							u.estado = False
							u.save()	
						except :
							pass
						
						mensaje = mensaje + ' Accesorio codigo de Barras '+str(x.accesorio.codigoBarras)+' '+x.accesorio.detallesAccesorio
			except :
				info='Nota de Accesorios. Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

			try:
				with transaction.atomic():
					for x in transFic:
						e = Ficha.objects.get(id=x.ficha.id)
						e.estatus = EstatusFicha.objects.get(estatus='Sin Confirmar')
						e.save()
						try:
							u = AlmacenFicha.objects.get(ficha=x.ficha,estado=True,sucursal__id=x.ficha.sucursal.id)
							u.estado = False
							u.save()	
						except :
							pass
						
						mensaje = mensaje + ' Fichas: Nominacion $'+str(x.ficha.nominacion.nominacion)+' Serie: '+str(x.ficha.folio)
			except :
				info='Nota de Fichas. Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

			try:
				with transaction.atomic():
					for x in transSaldo:
						mensaje = mensaje + ' Saldo no Confirmado monto : $ '+str(x.monto)
			except :
				info='Nota de Saldo. Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

			if transEq or transEx or transAc or transFic or transSaldo:
				try:
					with transaction.atomic():
						a = SolicitudNuevoProducto()
						a.folio = folioMensage(suc)
						a.nuevoProducto = mensaje
						a.sucursal 	= Sucursal.objects.get(id=suc)
						a.usuario 	= request.user
						a.estado 	= EstadoMensaje.objects.get(estado='Sin revisar')
						a.save()
				except :
					info='Mensaje. Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

			info = "La Transferencia se ha Guardado correctamente. Si no se aceptaron productos, se muestran a continuacion. "+mensaje

			ctx={'transferencias':pMovs,'query':query,'nivel':nivel}
			return render_to_response('servicios/transferencias.html',ctx,context_instance=RequestContext(request))

		ctx={'transferencias':pMovs,'query':query,'nivel':nivel}
		return render_to_response('servicios/transferencias.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')