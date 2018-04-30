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
from django.contrib.auth.models import Group
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField, TextInput
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.forms.extras.widgets import SelectDateWidget
from django.db import transaction

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth.models import User
from djCell.apps.activaciones.models import TipoActivacion, ActivacionEquipo, ActivacionExpress, ActivacionPlan
from djCell.apps.almacen.models import AlmacenEquipo, AlmacenExpres, AlmacenAccesorio, AlmacenFicha
from djCell.apps.catalogos.models import Estado, Ciudad, Colonia, CP, Zona
from djCell.apps.clientes.models import ClienteFacturacion, ClienteServicio, Mayorista
from djCell.apps.movimientos.models import TipoMovimiento, Movimiento, ListaEquipo, ListaExpres, ListaAccesorio, ListaFichas, TransferenciaSaldo
from djCell.apps.personal.models import Area, Puesto, Empleado, Usuario
from djCell.apps.planes.models import EstadoSolicitud, Solicitud, TipoRelacion, Banco, Plan, DetallePlan, ServiciosPlan
from djCell.apps.portabilidades.models import EstadoPortabilidad, Portabilidad,FlexeoEquipo
from djCell.apps.productos.models import TiempoGarantia,Estatus,Marca,Gama,DetallesEquipo,Equipo,TipoIcc,DetallesExpres,Expres,Secciones,MarcaAccesorio,DetallesAccesorio,EstatusAccesorio,Accesorio, NominacionFicha,EstatusFicha,Ficha,  TiempoAire, HistorialPreciosEquipos,HistorialPreciosAccesorios,HistorialPreciosExpres
from djCell.apps.proveedor.models import Proveedor, FormaPago,Factura
from djCell.apps.servicios.models import TipoReparacion, EstadoReparacion,Reparacion, EquipoReparacion, HistorialClienteReparacion, comisionesReparacion
from djCell.apps.stocks.models import StockEquipo, StockExpres, StockAccesorio, StockFicha
from djCell.apps.sucursales.models import EstadoSucursal, TipoSucursal, Sucursal, VendedorSucursal
from djCell.apps.papeletas.models import TipoProducto, Papeleta

from djCell.interface.planes.forms import updSolicitudPlanP,updEstadoPlan, activacionEquipo, addActivacionPlan, reporteFecha, updPorta, addPlan, addDetallePlan
from djCell.operaciones.comunes import Permiso, agregarCiudades
from djCell.operaciones.exceles import export_To_Excel_Planes

def nvofolioSolicitud():
	generarFolio = None
	today = datetime.now() #fecha actual
	dateFormat = today.strftime("%Y%m%d") # fecha con formato
	tam = len(dateFormat)
	fecha= ""
	for x in xrange(2,tam):
		fecha = fecha + dateFormat[x]

	nuevo = False
	while nuevo == False:
		pfff = str(time.time())
		omo = ""
		for x in xrange(7,10):
			omo = omo + pfff[x]
		generarFolio = 'S-'+ fecha +'-'+ omo
		try:
			v = Solicitud.objects.get(folio=generarFolio)
			nuevo = False
		except Solicitud.DoesNotExist:
			nuevo = True
	#'''
	return generarFolio

def cveSucursal(user):
	_usuario = Usuario.objects.get(user=user)
	myempleado 			= _usuario.empleado
	vendedorSucursal 	= VendedorSucursal.objects.get(empleado=myempleado)
	mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

	return mysucursal.id


def nuevoBanco(banco):
	n = None
	try:
		n = Banco.objects.get(banco=banco.title())
	except Banco.DoesNotExist:
		n = Banco()
		n.banco = banco.title()
		n.save()
	return n



#listo
@login_required(login_url='/')
def index_view(request):
	nivel=Permiso(request.user,[0,1,9])
	if nivel != -1:
		return render_to_response('planes/index.html', {'nivel':nivel},context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def planes_solicitudes_todos_view(request):
	nivel=Permiso(request.user,[0,1,9])
	if nivel != -1:
		suc = cveSucursal(request.user)

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
				return render_to_response('planes/solicitudCompleta.html',ctx,context_instance=RequestContext(request))
					

		ctx = {'solicitudes':solicitudes,'query':query,'info':info, 'nivel':nivel}
		return render_to_response('planes/seguimientoPlanes.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def planes_solicitudes_consultar_view(request):
	nivel=Permiso(request.user,[0,1,9])
	if nivel != -1:
		suc = cveSucursal(request.user)

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

		paginator = Paginator(gaara, 50)
		
		solicitudes=None
		try:
			solicitudes = paginator.page(pagina)
		except PageNotAnInteger:
			solicitudes = paginator.page(1)
		except EmptyPage:
			solicitudes = paginator.page(paginator.num_pages)
		
		if request.method == "GET":
			if request.GET.get('upd'):
				s = request.GET.get('upd','')
				if s:
					x = Solicitud.objects.get(id=s)
					info = "Datos actualmente."
					form = updSolicitudPlanP({'fxSolicitud':x.fxSolicitud,'canalVta':x.canalVta,'folioSisAct':x.folioSisAct,'lineaSolicitadas':x.lineaSolicitadas,
					'vendedor':x.vendedor.curp ,'subdist':x.subdist ,'diTelcel':x.diTelcel,'lineaReferencia':x.lineaReferencia ,'fxConsultaBuro':x.fxConsultaBuro ,
					'folioConsultaBuro':x.folioConsultaBuro ,'observacionSolicitud':x.observacionSolicitud ,'nombre':x.nombre,	'aPat':x.aPat,	'aMat':x.aMat ,
				  	'fxNac':x.fxNac ,'nacionalidad':x.nacionalidad ,'email':x.email ,'tipoIdentif':x.tipoIdentif ,	'folIdent':x.folIdent , 	'formPago':x.formPago ,
				  	'banco':x.banco ,'numTc':x.numTc ,'calleP':x.calleP ,'noextP':x.noextP ,'nointP':x.nointP ,'coloniaP':x.coloniaP ,'cpP':x.cpP ,'calle1P':x.calle1P ,'calle2P':x.calle2P ,
					'ciudadP':x.ciudadP ,'countryP':x.countryP ,'telP':x.telP ,'refDomP':x.refDomP ,'puesto':x.puesto ,'antiguedad':x.antiguedad ,'ingresomens':x.ingresomens ,'empNegocio':x.empNegocio ,
				  	'giro':x.giro ,'ecalle':x.ecalle ,'enoext':x.enoext ,'enoint':x.enoint ,'ecolonia':x.ecolonia ,'ecp':x.ecp ,'ecalle1':x.ecalle1 ,'ecalle2':x.ecalle2 ,
				  	'eciudad':x.eciudad ,'ecountry':x.ecountry ,'etel':x.etel ,'eextension':x.eextension ,'numautos':x.numautos ,'modelo':x.modelo ,'casaPropia':x.casaPropia ,
				  	'casaValor':x.casaValor ,'renta':x.renta ,'banco1':x.banco1 ,'ctaBanco1':x.ctaBanco1 ,'telBanco1':x.telBanco1 ,'banco2':x.banco2 ,
					'ctaBanco2':x.ctaBanco2 ,'telBanco2':x.telBanco2 ,'banco1Comercial':x.banco1Comercial,'ctaBanco1Comercial':x.ctaBanco1Comercial ,'telBanco1Comercial':x.telBanco1Comercial ,
					'banco2Comercial':x.banco2Comercial ,'ctaBanco2Comercial':x.ctaBanco2Comercial ,'telBanco2Comercial':x.telBanco2Comercial ,'nombreApellidos1':x.nombreApellidos1 ,
					'direccRef1':x.direccRef1 ,'telOfiRef1':x.telOfiRef1 ,'tipoRef1':x.tipoRef1 ,'nombreApellidos2':x.nombreApellidos2 ,'direccRef2':x.direccRef2 ,
					'telOfiRef2':x.telOfiRef2 ,'tipoRef2':x.tipoRef2 ,'nombreApellidos3':x.nombreApellidos3 ,'direccRef3':x.direccRef3 ,
					'telOfiRef3':x.telOfiRef3 ,'tipoRef3':x.tipoRef3 ,'equipoSolicitado':x.equipoSolicitado ,'planS':x.plan ,'observacion':x.observacion ,
					'folio':x.folio})
	
				else:
					info="Oops! lo sentimos, alguien ha cambiado la Solicitud manualmente...regrese a la pagina principal."
				ctx = {'cosa':'Actualizacion de ' ,'form':form,'nivel':nivel,'info':info}
				return render_to_response('planes/addSolicitudPlan.html',ctx,context_instance=RequestContext(request))
		
		if request.method == "POST":
			form = updSolicitudPlanP(request.POST or None)
			if form.is_valid():
				try:
					with transaction.atomic():
						z1 = agregarCiudades(form.cleaned_data['coloniaP'],form.cleaned_data['ciudadP'],form.cleaned_data['countryP'],form.cleaned_data['cpP'])	
						z2 = agregarCiudades(form.cleaned_data['ecolonia'],form.cleaned_data['eciudad'],form.cleaned_data['ecountry'],form.cleaned_data['ecp'])
						
						
						a = Solicitud.objects.get(folio=form.cleaned_data['folio'])
						a.fxSolicitud = form.cleaned_data['fxSolicitud']
						a.canalVta 	= form.cleaned_data['canalVta']
						a.folioSisAct = form.cleaned_data['folioSisAct']
						a.lineaSolicitadas = form.cleaned_data['lineaSolicitadas']
						a.subdist 	= form.cleaned_data['subdist']
						a.diTelcel 	= form.cleaned_data['diTelcel']
						a.lineaReferencia = form.cleaned_data['lineaReferencia']
						#Datos personales
						a.nombre 	 = form.cleaned_data['nombre'].title()
					  	a.aPat 		 = form.cleaned_data['aPat'].title()
					  	a.aMat 		 = form.cleaned_data['aMat'].title()
					  	a.fxNac 	 = form.cleaned_data['fxNac']
					  	a.nacionalidad  = form.cleaned_data['nacionalidad'].title()
					  	a.email 		 = form.cleaned_data['email']
					  	a.tipoIdentif  = form.cleaned_data['tipoIdentif'].title()
					  	a.folIdent 	 = form.cleaned_data['folIdent'].title()
					  	a.formPago 	= FormaPago.objects.get(id=form.cleaned_data['formPago'])
					  	a.banco 	= nuevoBanco(form.cleaned_data['banco'])
					  	a.numTc 		 = form.cleaned_data['numTc']
					  	# domicilio
					  	a.calleP  	= form.cleaned_data['calleP'].title()
					  	a.noextP 	= form.cleaned_data['noextP']
					  	a.nointP 	= form.cleaned_data['nointP']
					  	a.coloniaP 	= Colonia.objects.get(id=z1[0])
					  	a.cpP 		= CP.objects.get(id=z1[2])
					  	a.calle1P 	= form.cleaned_data['calle1P']
					  	a.calle2P 	= form.cleaned_data['calle2P']
					  	a.ciudadP 	= Ciudad.objects.get(id=z1[1])
					  	a.countryP 	= Estado.objects.get(id=form.cleaned_data['countryP'])
					  	a.telP 		= form.cleaned_data['telP']
					  	a.refDomP 	= form.cleaned_data['refDomP'].title()
						# ocupacion
						a.puesto 		= (form.cleaned_data['puesto']).title()
					  	a.antiguedad 	= form.cleaned_data['antiguedad']
					  	a.ingresomens 	= form.cleaned_data['ingresomens']
					  	a.empNegocio 	= form.cleaned_data['empNegocio']
					  	a.giro 			= form.cleaned_data['giro']
					  	# domicilio del empleo
					  	a.ecalle 		= form.cleaned_data['ecalle'].title()
					  	a.enoext 		= form.cleaned_data['enoext']
					  	a.enoint 		= form.cleaned_data['enoint']
					  	a.ecolonia 	= Colonia.objects.get(id=z2[0])
					  	a.ecp 		= CP.objects.get(id=z2[2])
					  	a.ecalle1 	= form.cleaned_data['ecalle1']
					  	a.ecalle2 	= form.cleaned_data['ecalle2']
					  	a.eciudad 	= Ciudad.objects.get(id=z2[1])
					  	a.ecountry 	= Estado.objects.get(id=form.cleaned_data['ecountry'])
					  	a.etel 		= form.cleaned_data['etel']
					  	a.eextension = form.cleaned_data['eextension']
						#Evaluacion economica
						a.numautos	= form.cleaned_data['numautos']
					  	a.modelo		= form.cleaned_data['modelo']
					  	a.casaPropia	= form.cleaned_data['casaPropia']
					  	a.casaValor	= form.cleaned_data['casaValor']
					  	a.renta		= form.cleaned_data['renta']
						#banco y referencia
						a.banco1 		= nuevoBanco(form.cleaned_data['banco1'])
						a.ctaBanco1 	= form.cleaned_data['ctaBanco1']
						a.telBanco1 	= form.cleaned_data['telBanco1']
						a.banco2 		= nuevoBanco(form.cleaned_data['banco2'])
						a.ctaBanco2 	= form.cleaned_data['ctaBanco2']
						a.telBanco2 	= form.cleaned_data['telBanco1']
						a.banco1Comercial = nuevoBanco(form.cleaned_data['banco1Comercial'])
						a.ctaBanco1Comercial = form.cleaned_data['ctaBanco1Comercial']
						a.telBanco1Comercial = form.cleaned_data['telBanco1Comercial']
						a.banco2Comercial = nuevoBanco(form.cleaned_data['banco2Comercial'])
						a.ctaBanco2Comercial = form.cleaned_data['ctaBanco2Comercial']
						a.telBanco2Comercial = form.cleaned_data['telBanco2Comercial']
						#referenciaPersonal
						a.nombreApellidos1 = form.cleaned_data['nombreApellidos1']
						a.direccRef1	= form.cleaned_data['direccRef1']
						a.telOfiRef1	= form.cleaned_data['telOfiRef1']
						a.tipoRef1 	= TipoRelacion.objects.get(id=form.cleaned_data['tipoRef1'])
						a.nombreApellidos2 = form.cleaned_data['nombreApellidos2']
						a.direccRef2	= form.cleaned_data['direccRef2']
						a.telOfiRef2	= form.cleaned_data['telOfiRef2']
						a.tipoRef2 	= TipoRelacion.objects.get(id=form.cleaned_data['tipoRef2'])
						a.nombreApellidos3 = form.cleaned_data['nombreApellidos3']
						a.direccRef3	= form.cleaned_data['direccRef3']
						a.telOfiRef3	= form.cleaned_data['telOfiRef3']
						a.tipoRef3 	= TipoRelacion.objects.get(id=form.cleaned_data['tipoRef3'])
						#equipo solicitado
						a.equipoSolicitado = form.cleaned_data['equipoSolicitado']
						#sucursal donde se solicita
						a.sucursal 	= Sucursal.objects.get(id=suc)
						#plan solicitado
						a.plan 		= Plan.objects.get(id=form.cleaned_data['planS'])
						a.fxModificacion = datetime.now()
						a.estado 		= EstadoSolicitud.objects.get(id=form.cleaned_data['estadoS'])
						a.observacion = form.cleaned_data['observacion']
						a.folio = nvofolioSolicitud()
						a.save()
						info ="La Solicitud se ha Guardado correctamente. En espera por revision. "
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
				ctx = {'nivel':nivel,'info':info}
				return render_to_response('planes/addSolicitudPlan.html',ctx,context_instance=RequestContext(request))
			else:
				info = "La informacion, contiene algunos errores, favor de verificar."
				form = updSolicitudPlanP(request.POST)
				ctx = {'form':form,'nivel':nivel,'info':info}
				return render_to_response('planes/addSolicitudPlan.html',ctx,context_instance=RequestContext(request))
					

		ctx = {'solicitudes':solicitudes,'query':query,'info':info, 'nivel':nivel}
		return render_to_response('planes/seguimientoPlanes.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def planes_seguimiento_view(request):
	nivel=Permiso(request.user,[0,1,9])
	if nivel != -1:
		suc = cveSucursal(request.user)

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

		paginator = Paginator(gaara, 50)
		
		solicitudes=None
		try:
			solicitudes = paginator.page(pagina)
		except PageNotAnInteger:
			solicitudes = paginator.page(1)
		except EmptyPage:
			solicitudes = paginator.page(paginator.num_pages)
		form = updEstadoPlan()
		if request.method == "GET":
			if request.GET.get('updEdo'):
				s = request.GET.get('updEdo','')
				if s:
					try:
						with transaction.atomic():
							x = Solicitud.objects.get(id=s)
							x.estado = EstadoSolicitud.objects.get(id= request.GET.get('estadoS'))
							x.fxModificacion = datetime.now()
							x.save()
							info = "Se Actualizo Correctamente."
							form = updEstadoPlan()
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
	
				else:
					info="Oops! lo sentimos, alguien ha cambiado la Solicitud manualmente...regrese a la pagina principal."
				ctx = {'solicitudes':solicitudes,'form':form,'query':query,'info':info, 'nivel':nivel}
				return render_to_response('planes/seguimientoPlanes2.html',ctx,context_instance=RequestContext(request))
		
		ctx = {'solicitudes':solicitudes,'form':form,'query':query,'info':info, 'nivel':nivel}
		return render_to_response('planes/seguimientoPlanes2.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def planes_activar_actualizar_view(request):
	nivel=Permiso(request.user,[0,1,9])
	if nivel != -1:
		
		info =""
		buscar = True
		pagina = request.GET.get('pagina','')
		query  = request.GET.get('q','')
		planActivados =  ActivacionPlan.objects.all()
		gaara=None
		if query:
			qset=(Q(folio__icontains=query)| Q(sucursal__nombre__icontains=query) |Q(fxSolicitud__icontains=query) |Q(vendedor__curp__icontains=query) |
				Q(nombre__icontains=query) |Q(aPat__icontains=query) |Q(aMat__icontains=query) |Q(plan__plan__icontains=query) |
				Q(plan__costo__icontains=query) |Q(estado__estado__icontains=query) |Q(fxModificacion__icontains=query))

			gaara = Solicitud.objects.filter(qset).order_by('folio').order_by('fxSolicitud').order_by('nombre').order_by('sucursal')
		else:
			gaara = Solicitud.objects.all().order_by('folio').order_by('fxSolicitud').order_by('nombre').order_by('sucursal')

		paginator = Paginator(gaara, 50)
		
		solicitudes=None
		try:
			solicitudes = paginator.page(pagina)
		except PageNotAnInteger:
			solicitudes = paginator.page(1)
		except EmptyPage:
			solicitudes = paginator.page(paginator.num_pages)

		if request.method == "GET":
			if request.GET.get('actEq'):
				query = request.GET.get('actEq', '')
				if query:
					laSolicitud = query

					ctx = {'laSolicitud':query,'info':info,'nivel':nivel}
					return render_to_response('planes/activacionPlanEquipo.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('actS'):
				query = request.GET.get('actS', '')
				if query:
					p = Solicitud.objects.get(id=query)
					form = addActivacionPlan({'solicitud':p.folio,'plan':p.plan.id,'difEquipo': 0,'difContado':0,'finanMeses':0,'noActcliente':'No' })
					ctx = {'form':form,'mostrar':True ,'info':info, 'nivel':nivel}
					return render_to_response('planes/activacionPlanS.html',ctx,context_instance=RequestContext(request))
			
			if request.GET.get('qEq'):
				query = request.GET.get('qEq', '')
				laSolicitud = request.GET.get('actESolicitud','')
				results = []
				if query:
					qset = (Q(imei__icontains=query))
					results = Equipo.objects.filter(qset).distinct()
					if results:
						isActivo = ActivacionEquipo.objects.filter(equipo__imei__icontains=query).distinct()
					else:
						results = []
				else:
					info = "Por Favor, Seleccione el equipo antes de activar."
			
				ctx = {"results": results,"laSolicitud":laSolicitud,"queryEq": query, 'info':info, 'eqActivado':isActivo, 'nivel':nivel}
				return render_to_response('planes/activacionPlanEquipo.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('activarImei'):
				laSolicitud = request.GET.get('actESolicitud','')
				equipoSeleccionado = request.GET.get('activarImei','')
				if equipoSeleccionado:
					p = Solicitud.objects.get(id=laSolicitud)
					form = addActivacionPlan({'solicitud':p.folio,'plan':p.plan.id, 'difEquipo': 0,'difContado':0,'finanMeses':0,'noActcliente':'No'})
					form2 = activacionEquipo({'imei':equipoSeleccionado})
					info = ""
					mostrar = True
					ctx = {'form':form, 'form2':form2, 'info':info, 'mostrar':mostrar,'nivel':nivel}
					return render_to_response('planes/activacionPlanEquipo.html',ctx,context_instance=RequestContext(request))

		if 'actEqSolicitud' in request.POST:
			form = addActivacionPlan(request.POST)
			form2 = activacionEquipo(request.POST)

			if form.is_valid() and form2.is_valid():

				plan 		= form.cleaned_data['plan']
				solicitud 	= form.cleaned_data['solicitud']
				form_act 	= form.cleaned_data['form_act']
				difEquipo 	= form.cleaned_data['difEquipo']
				difContado 	= form.cleaned_data['difContado']
				finanMeses 	= form.cleaned_data['finanMeses']
				numGratis 	= form.cleaned_data['numGratis']
				lada		= form.cleaned_data['lada']
				actSno		= form.cleaned_data['actSno']
				noActcliente= form.cleaned_data['noActcliente']
				hraCdom		= form.cleaned_data['hraCdom']
				hraRef		= form.cleaned_data['hraRef']
				
				noCell 			= form2.cleaned_data['noCell'] 
				imei 			= form2.cleaned_data['imei']
				
				sucp = Solicitud.objects.get(folio=solicitud).sucursal
				empp = Solicitud.objects.get(folio=solicitud).vendedor
				txt=str(noCell)
				re1='(\\d{10})'
				rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
				m = rg.search(txt)

				if m:
					try:
						with transaction.atomic():
							a = ActivacionEquipo()
							a.equipo 		= Equipo.objects.get(imei=form2.cleaned_data['imei'])
							a.tipoActivacion = TipoActivacion.objects.get(tipo='Plan')
							a.usuario 		= request.user
							a.empleado 		= empp
							a.sucursal 		= sucp
							a.save()
								
							activando = Equipo.objects.get(imei=form2.cleaned_data['imei'])
							activando.noCell = noCell
							activando.estatus = Estatus.objects.get(estatus='Activado')
							activando.save() 

							p = ActivacionPlan()
							p.equipo 		= activando
							p.plan 			= Plan.objects.get(id=plan)
							p.solicitud 	= Solicitud.objects.get(folio=solicitud)
						  	p.sucursal 		= sucp
						  	p.ejecutivo 	= empp
						  	p.form_act 		= form_act
							p.difEquipo 	= difEquipo
						  	p.difContado	= difContado
						  	p.finanMeses	= finanMeses
						  	p.numGratis 	= numGratis
						  	p.lada  		= lada
						  	p.actSno  		= actSno
						  	p.noActcliente 	= noCell #noActcliente
							p.hraCdom  		= hraCdom
						  	p.hraRef  		= hraRef
						  	p.save()

						  	so = Solicitud.objects.get(folio=solicitud)
						  	so.activado = True
						  	so.save()


					  		info = "La activacion del Plan se ha realizado correctamente, Folio: "+ p.solicitud.folio+" Equipo con No.: "+str(activando.noCell)
				  	except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
					
				  	ctx = {'solicitudes':solicitudes,'buscar':True,'planActivados':planActivados,'query':query,'info':info, 'nivel':nivel}
					return render_to_response('planes/activacionPlanS.html',ctx,context_instance=RequestContext(request))
				else:
					form = addActivacionPlan(request.POST)
					form2 = activacionEquipo(request.POST)
					info = "El Numero asociado como telefono es incorrecto. Favor de verificar los datos."
					ctx = {'form':form, 'form2':form2, 'info':info, 'mostrar':mostrar,'nivel':nivel}
					return render_to_response('planes/activacionPlanEquipo.html',ctx,context_instance=RequestContext(request))
			else:
				form = addActivacionPlan(request.POST)
				form2 = activacionEquipo(request.POST)
				info = "La informacion contiene errores. Favor de verificar los datos."
				ctx = {'form':form, 'form2':form2, 'info':info, 'mostrar':True,'nivel':nivel}
				return render_to_response('planes/activacionPlanEquipo.html',ctx,context_instance=RequestContext(request))

		if 'actSolicitud' in request.POST:
			form = addActivacionPlan(request.POST)
			
			if form.is_valid():
				try:
					with transaction.atomic():
						plan 		= form.cleaned_data['plan']
						solicitud 	= form.cleaned_data['solicitud']
						form_act 	= form.cleaned_data['form_act']
						difEquipo 	= form.cleaned_data['difEquipo']
						difContado 	= form.cleaned_data['difContado']
						finanMeses 	= form.cleaned_data['finanMeses']
						numGratis 	= form.cleaned_data['numGratis']
						lada		= form.cleaned_data['lada']
						actSno		= form.cleaned_data['actSno']
						noActcliente= form.cleaned_data['noActcliente']
						hraCdom		= form.cleaned_data['hraCdom']
						hraRef		= form.cleaned_data['hraRef']
						
						sucp = Solicitud.objects.get(folio=solicitud).sucursal
						empp = Solicitud.objects.get(folio=solicitud).vendedor

						p = ActivacionPlan()
						p.equipo 		= None
						p.plan 			= Plan.objects.get(id=plan)
						p.solicitud 	= Solicitud.objects.get(folio=solicitud)
						p.sucursal 		= sucp
						p.ejecutivo 	= empp
						p.form_act 		= form_act
						p.difEquipo 	= difEquipo
						p.difContado	= difContado
						p.finanMeses	= finanMeses
						p.numGratis 	= numGratis
						p.lada  		= lada
						p.actSno  		= actSno
						p.noActcliente 	= noActcliente
						p.hraCdom  		= hraCdom
						p.hraRef  		= hraRef
						p.save()

						so = Solicitud.objects.get(folio=solicitud)
						so.activado = True
						so.save()

						info = "La activacion del Plan se ha realizado correctamente, Folio: "+ p.solicitud.folio
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
				
				ctx = {'solicitudes':solicitudes,'buscar':True,'query':query,'info':info, 'nivel':nivel}
				return render_to_response('planes/activacionPlanS.html',ctx,context_instance=RequestContext(request))
				
			else:
				form = addActivacionPlan(request.POST)
				info = "La informacion contiene errores. Favor de verificar los datos."
				ctx = {'form':form,'mostrar':True,'info':info, 'nivel':nivel}
				return render_to_response('planes/activacionPlanEquipo.html',ctx,context_instance=RequestContext(request))

		
		ctx = {'solicitudes':solicitudes,'planActivados':planActivados,'buscar':True,'query':query,'info':info, 'nivel':nivel}
		return render_to_response('planes/activacionPlanS.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def planes_activar_consultar_view(request):
	nivel=Permiso(request.user,[0,1,9])
	if nivel != -1:
		form = reporteFecha({'fxInicio':datetime.now().date()})
		info = ""
		query = ""
		
		results = []
		if request.method == "POST":
			form = reporteFecha(request.POST)
			if form.is_valid():
				fxInicio 	= form.cleaned_data['fxInicio']
				fxFinal 	= form.cleaned_data['fxFinal']
				if fxFinal:
					results = ActivacionPlan.objects.filter(fxActivacion__range=[fxInicio,fxFinal])
					query = "Entre fechas : "+str(fxInicio)+" y "+str(fxFinal)
				else:
					results = ActivacionPlan.objects.filter(fxActivacion__icontains=fxInicio)
					query = "De fecha : "+str(fxInicio)

				exportar = request.POST.get('excel','')
				if exportar == 'Exportar':
					result = []
					header = ['SUCURSAL','FECHA','FOLIO','SOLICITUD','EJECUTIVO','EQUIPO','IMEI','ICC','Asignado','PLAN','ACTIVACION','DIF. EQUIPO','DIF. CONTADO','FINANCIAMIENTO','NUMERO GRATIS','LADA','MISMO NUMERO','NO ASGINADO','HORARIO CLIENTE DOMICILIO','HORIARIO REFERENCIAS']
					for x in results:
						try:
							result.append([x.sucursal.nombre.upper(),str(x.fxActivacion),x.solicitud.folio, x.solicitud.nombre.title()+' '+x.solicitud.aPat.title()+' '+x.solicitud.aMat.title(),x.ejecutivo.curp.upper(),x.equipo.detallesEquipo.marca.marca.title()+' '+x.equipo.detallesEquipo.modelo.title(),str(x.equipo.imei),str(x.equipo.icc),str(x.equipo.noCell),x.solicitud.plan.plan.title()+' $ '+str(x.solicitud.plan.costo),str(x.form_act),str(x.difEquipo),str(x.difContado), str(x.finanMeses),str(x.numGratis),str(x.lada),str(x.actSno),str(x.noActcliente),str(x.hraCdom),str(x.hraRef)])
						except :
							result.append([x.sucursal.nombre.upper(),str(x.fxActivacion),x.solicitud.folio, x.solicitud.nombre.title()+' '+x.solicitud.aPat.title()+' '+x.solicitud.aMat.title(),x.ejecutivo.curp.upper(),'No se Asocio Equipo' ,'' ,'','',x.solicitud.plan.plan.title()+' $ '+str(x.solicitud.plan.costo),str(x.form_act),str(x.difEquipo),str(x.difContado), str(x.finanMeses),str(x.numGratis),str(x.lada),str(x.actSno),str(x.noActcliente),str(x.hraCdom),str(x.hraRef)])
						
					try:
						return export_To_Excel_Planes(query,header,result)
					except :
						info = "No se genero su Archivo."
				
				ctx = {'form':form,'query':query, 'info':info, 'results':results,'nivel':nivel}
				return render_to_response('planes/reporteActivacion.html',ctx,context_instance=RequestContext(request))
			
			else:
				info = "Seleccione un rango de fechas, inicial y final"
				form= reporteFecha(request.POST)
		
		ctx = {'form':form,'query':query, 'info':info, 'results':results,'nivel':nivel}
		return render_to_response('planes/reporteActivacion.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def planes_servicios_solicitudes_view(request):
	nivel=Permiso(request.user,[0,1,9])
	if nivel != -1:
		suc = cveSucursal(request.user)

		info =""
		pagina = request.GET.get('pagina','')
		query  = request.GET.get('q','')
		gaara=None
		if query:
			qset=(Q(solicitante__folio__icontains=query)| Q(sucursal__nombre__icontains=query) |Q(fxSolicitud__icontains=query) |
				Q(solicitante__nombre__icontains=query) |Q(solicitante__aPat__icontains=query) |Q(solicitante__aMat__icontains=query) |
				Q(solicitante__plan__plan__icontains=query)|Q(servicioRequiere__icontains=query)|
				Q(fxAtencion__icontains=query) |Q(fxSolicitud__icontains=query))
			gaara = ServiciosPlan.objects.filter(qset).order_by('fxSolicitud').order_by('sucursal').order_by('solicitante').order_by('fxAtencion')
		else:
			gaara = ServiciosPlan.objects.all().order_by('fxSolicitud').order_by('sucursal').order_by('solicitante').order_by('fxAtencion')
		info = "Resultados de: "+query
		paginator = Paginator(gaara, 50)
		
		solicitudes=None
		try:
			solicitudes = paginator.page(pagina)
		except PageNotAnInteger:
			solicitudes = paginator.page(1)
		except EmptyPage:
			solicitudes = paginator.page(paginator.num_pages)

		if request.method == "GET":
			if request.GET.get('upd'):
				s = request.GET.get('upd','')
				if s:
					try:
						with transaction.atomic():
							x = ServiciosPlan.objects.get(id=s)
							x.atendido = True
							x.fxAtencion = datetime.now()
							x.save()
							info = "Se Actualizo Correctamente."
					except :
						info ='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
				else:
					info="Oops! lo sentimos, alguien ha cambiado la Solicitud manualmente...regrese a la pagina principal."
				
		
		ctx = {'solicitudes':solicitudes,'query':query,'info':info, 'nivel':nivel}
		return render_to_response('planes/solicitudServicio.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def planes_servicios_reporte_view(request):
	nivel=Permiso(request.user,[0,1,9])
	if nivel != -1:
		suc = cveSucursal(request.user)
		form = reporteFecha()
		info =""
		
		pagina = request.GET.get('pagina','')
		gaara=None
		gaara = ServiciosPlan.objects.all().order_by('fxSolicitud').order_by('sucursal').order_by('solicitante').order_by('fxAtencion')

		if request.method == "POST":
			form = reporteFecha(request.POST)
			if form.is_valid():
				fxInicio 	= form.cleaned_data['fxInicio']
				fxFinal 	= form.cleaned_data['fxFinal']
				if fxFinal and fxInicio:
					gaara = ServiciosPlan.objects.filter(fxSolicitud__range=[fxInicio,fxFinal]).order_by('fxSolicitud').order_by('sucursal').order_by('solicitante').order_by('fxAtencion')
				else:
					gaara = ServiciosPlan.objects.filter(fxSolicitud__icontains=fxInicio).order_by('fxSolicitud').order_by('sucursal').order_by('solicitante').order_by('fxAtencion')
			else:
				info = "Seleccione un rango de fechas"
				form= reporteFecha(request.POST)
		
		paginator = Paginator(gaara, 50)
		solicitudes=None
		try:
			solicitudes = paginator.page(pagina)
		except PageNotAnInteger:
			solicitudes = paginator.page(1)
		except EmptyPage:
			solicitudes = paginator.page(paginator.num_pages)
		
		ctx = {'solicitudes':solicitudes,'form':form ,'info':info, 'nivel':nivel}
		return render_to_response('planes/reporteServicios.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def planes_portabilidades_solicitudes_view(request):
	nivel=Permiso(request.user,[0,1,9])
	if nivel != -1:
		
		info =""
		buscar = True
		query = ''
		results = []
		query  = request.GET.get('q','')
		pag1=request.GET.get('pagina','')
		
		msgs = Portabilidad.objects.all().order_by('fxIngreso')

		if query:
			qset = (Q(cliente__nombre__icontains=query) |
					Q(sucursal__nombre__icontains=query) |
					Q(noaPortar__icontains=query) |
					Q(estado__estado__icontains=query) |
					Q(cliente__folio__icontains=query))
			msgs = Portabilidad.objects.filter(qset).distinct().order_by('fxIngreso')
		
		
		paginator1 = Paginator(msgs, 50)

		pPortas=None
		
		try:
			pPortas = paginator1.page(pag1)
		except PageNotAnInteger:
			pPortas= paginator1.page(1)
		except EmptyPage:
			pPortas = paginator1.page(paginator1.num_pages)
		
		ctx = {'buscar':buscar,"results": pPortas,"query": query, 'info':info, 'nivel':nivel}
		return render_to_response('planes/solicitudPortabilidad.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def planes_portabilidades_consultar_view(request):
	nivel=Permiso(request.user,[0,1,9])
	if nivel != -1:
		
		info =""
		buscar = True
		query = ''
		results = []
		query  = request.GET.get('q','')
		pag1=request.GET.get('pagina','')
		
		msgs = Portabilidad.objects.all().order_by('fxIngreso')

		if query:
			qset = (Q(cliente__nombre__icontains=query) |
					Q(sucursal__nombre__icontains=query) |
					Q(noaPortar__icontains=query) |
					Q(estado__estado__icontains=query) |
					Q(cliente__folio__icontains=query))
			msgs = Portabilidad.objects.filter(qset).distinct().order_by('fxIngreso')
		
		
		paginator1 = Paginator(msgs, 50)

		pPortas=None
		
		try:
			pPortas = paginator1.page(pag1)
		except PageNotAnInteger:
			pPortas= paginator1.page(1)
		except EmptyPage:
			pPortas = paginator1.page(paginator1.num_pages)

		
		if request.method == "GET":
			if request.GET.get('updPorta'):
				query = request.GET.get('updPorta', '')
				if query:
					x = Portabilidad.objects.get(id = query)
					form = updPorta({'key':x.id,'cliente':x.cliente.nombre,'actualmente':x.estado.estado})
					mostrarf = True
					
					ctx = {'mostrarf':mostrarf,'form':form ,'info':info, 'nivel':nivel}
					return render_to_response('planes/solicitudPortabilidad.html',ctx,context_instance=RequestContext(request))

		if request.method == "POST":
			form = updPorta( request.POST)
			if form.is_valid():
				try:
					with transaction.atomic():
						key 		= form.cleaned_data['key']
						estado 		= form.cleaned_data['estado']

						upd =  Portabilidad.objects.get(id=key)
						upd.fxRevision = datetime.now()
						upd.estado = EstadoPortabilidad.objects.get(id=estado)
						upd.save()

						info = "El Registro se ha actualizado con exito: " + upd.cliente.folio
						buscar = True
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
				
				ctx = {'buscar':buscar,'info':info, 'nivel':nivel}
				return render_to_response('planes/solicitudPortabilidad.html',ctx,context_instance=RequestContext(request))

			else:
				info = "Verifique sus datos, actualizacion no realizada"
				form = updPorta( request.POST)
				mostrarf = True
				
		ctx = {'buscar':buscar,'results':pPortas,'query':query,'info':info,'nivel':nivel}
		return render_to_response('planes/solicitudPortabilidad.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def planes_catalogo_planes_nuevo_view(request):
	nivel=Permiso(request.user,[0,1,9])
	if nivel != -1:
		info = ""
		form = addPlan()
		form2 = addDetallePlan()

		if request.method == "POST":
			form = addPlan(request.POST or None)
			form2 = addDetallePlan(request.POST or None)
			if form.is_valid() and form2.is_valid():
				try:
					with transaction.atomic():
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
						info = "Se ha registrado correctamente el plan "+ b.plan
						form = addPlan()
						form2 = addDetallePlan()
				except :
					info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

		ctx = {'nivel':nivel,'form':form,'form2':form2, 'info':info,}
		return render_to_response('planes/addPlan.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def planes_catalogo_planes_consultar_view(request):
	nivel=Permiso(request.user,[0,1,9])
	if nivel != -1:
		r_items=None
		info=''
		query = request.GET.get('q','')
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
					upd = Plan.objects.get(id= s)
					upd.activo = False
					upd.save()
					'''#if True:
					try:
						with transaction.atomic():
						#if True:
							upd = Plan.objects.get(id= s)
							upd.activo = False
							upd.save()
					except :
					#else:
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'#'''
		
		ctx={'nivel':nivel, 'query':query, 'r_items':r_items, 'info':info}
		return render_to_response('planes/catalogoPlanes.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def planes_reportes_portabilidades_view(request):
	nivel=Permiso(request.user,[0,1,9])
	if nivel != -1:
		info =""
		query = ''
		msgs = Portabilidad.objects.all().order_by('fxIngreso')	
		pPortas=None
		form = reporteFecha()
		if request.method == "POST":
			form = reporteFecha(request.POST or None)
			if form.is_valid():
				fxInicio = form.cleaned_data['fxInicio']
				fxFinal =  form.cleaned_data['fxFinal']
				
				if fxFinal:
					msgs = Portabilidad.objects.filter(fxIngreso__range=[fxInicio,fxFinal]).distinct()
				else:
					msgs = Portabilidad.objects.filter(fxIngreso__icontains=fxInicio).distinct()

		pag1=request.GET.get('pagina','')

		paginator1 = Paginator(msgs, 50)

		try:
			pPortas = paginator1.page(pag1)
		except PageNotAnInteger:
			pPortas= paginator1.page(1)
		except EmptyPage:
			pPortas = paginator1.page(paginator1.num_pages)

		
		ctx = {"form":form ,"results": pPortas,"query": query, 'info':info, 'nivel':nivel}
		return render_to_response('planes/allPortas.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def planes_reportes_planes_solicitados_view(request):
	nivel=Permiso(request.user,[0,1,9])
	if nivel != -1:
		info =""
		pagina = request.GET.get('pagina','')
		form = reporteFecha()
		gaara = Solicitud.objects.all().order_by('folio').order_by('fxSolicitud').order_by('nombre').order_by('sucursal')

		if request.method == "GET":
			if request.GET.get('pop'):
				s = request.GET.get('pop','')
				
				if s:
					grrr = Solicitud.objects.get(id=s)
					info = "Datos actualmente."
				else:
					info="Oops! lo sentimos, alguien ha cambiado la Solicitud manualmente...regrese a la pagina principal."
				ctx = {'grrr':grrr,'info':info, 'nivel':nivel}
				return render_to_response('planes/solicitudCompleta.html',ctx,context_instance=RequestContext(request))

		if request.method == "POST":
			form = reporteFecha(request.POST or None)
			if form.is_valid():
				fxInicio = form.cleaned_data['fxInicio']
				fxFinal =  form.cleaned_data['fxFinal']
				
				if fxFinal:
					gaara = Solicitud.objects.filter(fxSolicitud__range=[fxInicio,fxFinal]).order_by('folio').order_by('fxSolicitud').order_by('nombre').order_by('sucursal')
					info = "Resultados de las fechas: "+str(fxInicio)+" y "+str(fxFinal)
				else:
					gaara = Solicitud.objects.filter(fxSolicitud__icontains=fxInicio).order_by('folio').order_by('fxSolicitud').order_by('nombre').order_by('sucursal')
					info = "Resultados de la fecha: "+str(fxInicio)
		
		paginator = Paginator(gaara, 20)
		solicitudes=None
		try:
			solicitudes = paginator.page(pagina)
		except PageNotAnInteger:
			solicitudes = paginator.page(1)
		except EmptyPage:
			solicitudes = paginator.page(paginator.num_pages)
		
		ctx = {"form":form,'solicitudes':solicitudes,'info':info, 'nivel':nivel}
		return render_to_response('planes/allSolicitudes.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def planes_reportes_actualizar_solicitud_view(request):
	nivel=Permiso(request.user,[0,1,9])
	if nivel != -1:
		suc = cveSucursal(request.user)
		form = reporteFecha()
		info =""
		
		pagina = request.GET.get('pagina','')
		gaara=None
		gaara = ServiciosPlan.objects.all().order_by('fxSolicitud').order_by('sucursal').order_by('solicitante').order_by('fxAtencion')

		if request.method == "POST":
			form = reporteFecha(request.POST)
			if form.is_valid():
				fxInicio 	= form.cleaned_data['fxInicio']
				fxFinal 	= form.cleaned_data['fxFinal']
				if fxFinal and fxInicio:
					gaara = ServiciosPlan.objects.filter(fxSolicitud__range=[fxInicio,fxFinal]).order_by('fxSolicitud').order_by('sucursal').order_by('solicitante').order_by('fxAtencion')
				else:
					gaara = ServiciosPlan.objects.filter(fxSolicitud__icontains=fxInicio).order_by('fxSolicitud').order_by('sucursal').order_by('solicitante').order_by('fxAtencion')
			else:
				info = "Seleccione un rango de fechas"
				form= reporteFecha(request.POST)
		
		paginator = Paginator(gaara, 50)
		solicitudes=None
		try:
			solicitudes = paginator.page(pagina)
		except PageNotAnInteger:
			solicitudes = paginator.page(1)
		except EmptyPage:
			solicitudes = paginator.page(paginator.num_pages)
		
		ctx = {'solicitudes':solicitudes,'form':form,'info':info, 'nivel':nivel}
		return render_to_response('planes/reporteServicios.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo #yet
@login_required(login_url='/')
def planes_reportes_por_entregar_view(request):
	nivel=Permiso(request.user,[0,1,9])
	if nivel != -1:
		info =""
		query = ''
		msgs = ActivacionPlan.objects.all().order_by('fxActivacion')	
		pPortas=None
		form = reporteFecha()
		if request.method == "POST":
			form = reporteFecha(request.POST or None)
			if form.is_valid():
				fxInicio = form.cleaned_data['fxInicio']
				fxFinal =  form.cleaned_data['fxFinal']
				
				if fxFinal:
					msgs = ActivacionPlan.objects.filter(fxActivacion__range=[fxInicio,fxFinal])
					query = "Entre fechas : "+str(fxInicio)+" y "+str(fxFinal)
				else:
					msgs = ActivacionPlan.objects.filter(fxActivacion__icontains=fxInicio)
					query = "De fecha : "+str(fxInicio)

		pag1=request.GET.get('pagina','')

		paginator1 = Paginator(msgs, 50)

		try:
			pPortas = paginator1.page(pag1)
		except PageNotAnInteger:
			pPortas= paginator1.page(1)
		except EmptyPage:
			pPortas = paginator1.page(paginator1.num_pages)
		
		ctx = {'form':form,'query':query, 'info':info, 'results':pPortas,'nivel':nivel, 'hide':False}
		return render_to_response('planes/reporteActivacion.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo probado
def exportPapeletas(query,result,header):
	wb = xlwt.Workbook(encoding = 'utf-8')
	ws0 = wb.add_sheet('papeletas')
	ws0.write(0, 0,query)
	nCol = len(header)
	col = 0
	no = len(result)
	for x in header:
		ws0.write(2, col, x)
		col = col + 1
	row = 3
	for i in range(no):
		col = 0
		for j in range(nCol):
			item = result[i][j].encode('utf-8')
			ws0.write(row, col,item )
			col = col + 1
		row = row + 1
	
	filename = "reportePapeletas_%s.xls" % (datetime.now().date())
	response = HttpResponse(mimetype='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename='+filename
	wb.save(response)
	return response


@login_required(login_url='/')
def planes_sucursales_papeletas_view(request):
	nivel=Permiso(request.user,[0,1,9])
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
		return render_to_response('planes/reportePapeletas.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')