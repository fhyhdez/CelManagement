# -*- coding: utf-8 -*-
from django.db.models import Q
import re
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, date
import xlwt
from decimal import Decimal
from django.db import transaction
from django.contrib.auth.models import User
from djCell.apps.activaciones.models import TipoActivacion, ActivacionEquipo, ActivacionExpress, ActivacionPlan
from djCell.apps.personal.models import Area, Puesto, Empleado, Permiso, Usuario
from djCell.apps.productos.models import TiempoGarantia,Estatus,Marca,Gama,DetallesEquipo,Equipo,TipoIcc,DetallesExpres,Expres, Secciones,MarcaAccesorio,DetallesAccesorio,EstatusAccesorio,Accesorio, NominacionFicha,EstatusFicha,Ficha,  TiempoAire
from djCell.apps.sucursales.models import EstadoSucursal, TipoSucursal, Sucursal, VendedorSucursal
from djCell.apps.ventas.models import EstadoVenta, Venta,VentaEquipo,VentaExpres,VentaAccesorio,VentaFichas,VentaRecarga,VentaPlan,Renta, Cancelaciones, VentaMayoreo

from djCell.interface.activaciones.forms import addActivacionEquipoForm, addActivacionExpressForm, consEquipo, consExpres,reporteFecha,reporteCompleto

from djCell.apps.personal.models import Usuario
from djCell.operaciones.comunes	import Permiso
from djCell.operaciones.exceles import export_To_Excel_ActivacionG

@login_required(login_url='/')
def index_view(request):
	nivel=Permiso(request.user,[0,1,8])
	if nivel != -1:
		return render_to_response('activaciones/index.html', {'nivel':nivel},context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

@login_required(login_url="/")
def resultado_activacion_view(request):
	nivel=Permiso(request.user,[0,1,8])
	if nivel != -1:
		return render_to_response('activaciones/transaccion.html',{'nivel':nivel},context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')
		

@login_required(login_url='/')
def activaciones_equipo_buscar_view(request):
	nivel=Permiso(request.user,[0,1,8])
	if nivel != -1:
		
		form = addActivacionEquipoForm()
		form2 = consEquipo()
		query = ''
		results = []
		info =""
		mostrarForm = False
		numVerificador = False
		isActivo = ActivacionEquipo()
		if request.method == "GET":
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					qset = (Q(imei__icontains=query))
					results = Equipo.objects.filter(qset).distinct()
					if results:
						isActivo = ActivacionEquipo.objects.filter(equipo__imei__icontains=query).distinct()
					else:
						results = []
				else:
					info = "Por Favor, Seleccione el equipo antes de activar."
			
				ctx = {"results": results,"query": query,'form':form, 'form2':form2, 'nivel':nivel, 'info':info, 'mostrar':mostrarForm, 'eqActivado':isActivo, 'nivel':nivel}
				return render_to_response('activaciones/consEquipo.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('activarImei'):
				equipoSeleccionado = request.GET.get('activarImei','')
				if equipoSeleccionado:
					eq = None
					try:
						eq = Equipo.objects.get(imei=equipoSeleccionado)
					except :
						pass
					cast = "%s" % (eq.icc)
					noicc = len(cast)
					if noicc == 18 :
						numVerificador = True
					form2 = consEquipo({'imei':equipoSeleccionado,'icc':eq.icc })
					info = ""
					mostrarForm = True

			ctx = {"results": results,"query": query,'form':form,'numVerificador':numVerificador,'form2':form2, 'nivel':nivel, 'info':info, 'mostrar':mostrarForm,'eqActivado':isActivo,'nivel':nivel}
			return render_to_response('activaciones/consEquipo.html',ctx,context_instance=RequestContext(request))

		if request.method == "POST":

			form = addActivacionEquipoForm(request.POST or None)
			form2 = consEquipo(request.POST or None)
			mostrarForm = True
			if form.is_valid() and form2.is_valid():
				
				tipoActivacion 	= form.cleaned_data['tipoActivacion']
				empleado 		= form.cleaned_data['empleado']
			
				noCell 			= form2.cleaned_data['noCell'] 
				imei 			= form2.cleaned_data['imei']				
				
				txt=str(noCell)
				re1='(\\d{10})'

				rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
				m = rg.search(txt)
				if m:
					try:
						with transaction.atomic():
							a = ActivacionEquipo()
							a.equipo 		= Equipo.objects.get(imei=form2.cleaned_data['imei'])
							a.tipoActivacion = tipoActivacion
							a.usuario 		= request.user
							a.empleado 		= empleado
							a.sucursal 		= Equipo.objects.get(imei=form2.cleaned_data['imei']).sucursal
							a.save()
									
							activando = Equipo.objects.get(imei=form2.cleaned_data['imei'])
							activando.noCell = noCell
							activando.estatus = Estatus.objects.get(estatus='Activado')
							activando.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

					num = request.POST.get('nVerif','')
					if num:
						try:
							with transaction.atomic():
								upd = Equipo.objects.get(imei=form2.cleaned_data['imei'])
								n =  '%s%s'%(upd.icc,num)
							 	upd.icc = Decimal(n)
							 	upd.save()
					 	except :
							info='Lo sentimos, la información para actualizar la icc de equipo, enviada no se almaceno por problemas de integridad de datos'
					
					info ="La Activacion se ha Guardado con Exito"
					
					ctx = {'nivel':nivel, 'info':info}
					return render_to_response('activaciones/consEquipo.html',ctx,context_instance=RequestContext(request))
				
				else:
					info = "Verifique el Numero de Celular, el formato es de 10 digitos"

			else:
				form = addActivacionEquipoForm(request.POST)
				form2 = consEquipo(request.POST)
				num = request.POST.get('nVerif','')
				if num:
					numVerificador = True
				info ="Verifique la informacion en el numero de celular asignado"

		ctx = {"results": results,"query": query,'form':form,'numVerificador':numVerificador,'form2':form2, 'nivel':nivel, 'info':info,'mostrar':mostrarForm,'eqActivado':isActivo,'nivel':nivel}
		return render_to_response('activaciones/consEquipo.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		

@login_required(login_url='/')
def activaciones_express_buscar_view(request):
	nivel=Permiso(request.user,[0,1,8])
	if nivel != -1:
		
		form = addActivacionExpressForm()
		form2 = consExpres()
		query = ''
		results = []
		info =""
		mostrarForm = False
		numVerificador = False
		isActivo = ActivacionExpress()
		if request.method == "GET":
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					qset = (Q(icc__icontains=query))
					results = Expres.objects.filter(qset).distinct()
					if results:
						info = "Resultados"
						isActivo = ActivacionExpress.objects.all()
				else:
					results = []
			
				ctx = {"results": results,"query": query,'form':form, 'form2':form2, 'nivel':nivel, 'info':info, 'mostrar':mostrarForm, 'exActivado':isActivo,'nivel':nivel}
				return render_to_response('activaciones/consExpress.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('activarIcc'):
				expressSeleccionado = request.GET.get('activarIcc','')
				if expressSeleccionado:
					ex = None
					try:
						ex = Expres.objects.get(icc=expressSeleccionado)
					except :
						pass
					cast = "%s" % (ex.icc)
					noicc = len(cast)
					if noicc == 18 :
						numVerificador = True
					form2 = consExpres({'icc':expressSeleccionado})
					info = ""
					mostrarForm = True

			ctx = {"results": results,'numVerificador':numVerificador,"query": query,'form':form, 'form2':form2, 'nivel':nivel, 'info':info, 'mostrar':mostrarForm,'exActivado':isActivo,'nivel':nivel}
			return render_to_response('activaciones/consExpress.html',ctx,context_instance=RequestContext(request))

		if request.method == "POST":

			form = addActivacionExpressForm(request.POST or None)
			form2 = consExpres(request.POST or None)
			mostrarForm = True
			if form.is_valid() and form2.is_valid():
				
				tipoActivacion 	= form.cleaned_data['tipoActivacion']
				empleado 		= form.cleaned_data['empleado']
			
				noCell 			= form2.cleaned_data['noCell'] 
				icc 			= form2.cleaned_data['icc']
				
				txt=str(noCell)

				re1='(\\d{10})'

				rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
				m = rg.search(txt)
				if m:
					try:
						with transaction.atomic():
							a = ActivacionExpress()
							a.express 		= Expres.objects.get(icc=form2.cleaned_data['icc'])
							a.tipoActivacion = tipoActivacion
							a.usuario 		= request.user
							a.empleado 		= empleado
							a.sucursal 		= Expres.objects.get(icc=form2.cleaned_data['icc']).sucursal
							a.save()
								
							activando = Expres.objects.get(icc=form2.cleaned_data['icc'])
							activando.noCell = noCell
							activando.estatus = Estatus.objects.get(estatus='Activado')
							activando.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
					
					num = request.POST.get('nVerif','')
					if num:
						try:
							with transaction.atomic():
							 	upd = Expres.objects.get(icc=form2.cleaned_data['icc'])
							 	n =  '%s%s'%(upd.icc,num)
							 	upd.icc = Decimal(n)
							 	upd.save() 
						except :
							info='Lo sentimos, la información enviada para actualizar la icc del express, no se almaceno, por problemas de integridad de datos'
						
					info ="La Activacion se ha Guardado con Exito"
					
					ctx = {'nivel':nivel, 'info':info}
					return render_to_response('activaciones/consExpress.html',ctx,context_instance=RequestContext(request))			
				
				else:
					info = "Verifique el Numero de Celular, el formato es de 10 digitos"

			else:
				form = addActivacionExpressForm(request.POST)
				form2 = consExpres(request.POST)
				num = request.POST.get('nVerif','')
				if num:
					numVerificador = True
				info ="Verifique la informacion en el numero de celular asignado"

		ctx = {"results": results,"query": query,'form':form,'numVerificador':numVerificador,'form2':form2, 'nivel':nivel, 'info':info,'mostrar':mostrarForm,'exActivado':isActivo,'nivel':nivel}
		return render_to_response('activaciones/consExpress.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')
	
#listo cr
@login_required(login_url='/')
def activaciones_reporte_view(request):
	nivel=Permiso(request.user,[0,1,8])
	if nivel != -1:
		info = ""
		query = ""
		resultsExp = []
		resultsEq  = []

		if request.method == "POST":
			fxInicio 	= request.POST.get('fxInicio','')
			fxFinal 	= request.POST.get('fxFinal','')
			if True:
				
				if fxFinal:
					resultsEq = ActivacionEquipo.objects.filter(fxActivacion__range=[fxInicio,fxFinal])
					resultsExp = ActivacionExpress.objects.filter(fxActivacion__range=[fxInicio,fxFinal])
					query = "Entre fechas : "+str(fxInicio)+" y "+str(fxFinal)
				else:
					resultsEq = ActivacionEquipo.objects.filter(fxActivacion__icontains=fxInicio)
					resultsExp = ActivacionExpress.objects.filter(fxActivacion__icontains=fxInicio)
					query = "De fecha : "+str(fxInicio)
				exportar = request.POST.get('excel','')
				if exportar == 'Exportar':
					result = []
					result2 = []
					for x in resultsEq:
						result.append([x.sucursal, x.tipoActivacion.tipo,x.equipo.detallesEquipo.marca.marca+' '+x.equipo.detallesEquipo.modelo,str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
					for x in resultsExp:
						result2.append([x.sucursal, x.tipoActivacion.tipo,x.express.icc,x.express.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
					try:
						return export_To_Excel_ActivacionG(query,result,result2,'Todos')
					except :
						info = "No se genero su Archivo."
				
				ctx = {'query':query, 'info':info, 'resultsEq':resultsEq, 'resultsExp': resultsExp,'nivel':nivel}
				return render_to_response('activaciones/reporteActivaciones.html',ctx,context_instance=RequestContext(request))
			
			else:
				info = "Seleccione un rango de fechas"
				form= reporteFecha(request.POST)
				ctx = {'query':query, 'info':info, 'resultsEq':resultsEq, 'resultsExp': resultsExp,'nivel':nivel}
				return render_to_response('activaciones/reporteActivaciones.html',ctx,context_instance=RequestContext(request))
		
		ctx = {'query':query, 'info':info, 'resultsEq':resultsEq, 'resultsExp': resultsExp,'nivel':nivel}
		return render_to_response('activaciones/reporteActivaciones.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#listo cr
@login_required(login_url='/')
def activaciones_reportes_activados_view(request):
	nivel=Permiso(request.user,[0,1,8])
	if nivel != -1:
		info = ""
		query = ""
		resultsExp = []
		resultsEq  = []
		if request.method == "POST":
			fxInicio 	= request.POST.get('fxInicio','')
			fxFinal 	= request.POST.get('fxFinal','')
			if True:
				if fxFinal:
					resultsEq = ActivacionEquipo.objects.filter(fxActivacion__range=[fxInicio,fxFinal])
					resultsExp = ActivacionExpress.objects.filter(fxActivacion__range=[fxInicio,fxFinal])
					query = "Entre fechas : "+str(fxInicio)+" y "+str(fxFinal)
				else:
					resultsEq = ActivacionEquipo.objects.filter(fxActivacion__icontains=fxInicio)
					resultsExp = ActivacionExpress.objects.filter(fxActivacion__icontains=fxInicio)
					query = "De fecha : "+str(fxInicio)

				exportar = request.POST.get('excel','')
				if exportar == 'Exportar':
					result = []
					result2 = []
					for x in resultsEq:
						result.append([x.sucursal, x.tipoActivacion.tipo,x.equipo.detallesEquipo.marca.marca+' '+x.equipo.detallesEquipo.modelo,str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
					for x in resultsExp:
						result2.append([x.sucursal, x.tipoActivacion.tipo,x.express.icc,x.express.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
					try:
						return export_To_Excel_ActivacionG(query,result,result2,'Todos')
					except :
						info = "No se genero su Archivo."
				
				ctx = {'query':query, 'info':info, 'resultsEq':resultsEq, 'resultsExp': resultsExp,'nivel':nivel}
				return render_to_response('activaciones/reporteActivaciones.html',ctx,context_instance=RequestContext(request))
			
			else:
				info = "Seleccione un rango de fechas"
				form= reporteFecha(request.POST)
		
		ctx = {'query':query, 'info':info, 'resultsEq':resultsEq, 'resultsExp': resultsExp,'nivel':nivel}
		return render_to_response('activaciones/reporteActivaciones.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#listo 1
@login_required(login_url='/')
def activaciones_reportes_kit_view(request):
	nivel=Permiso(request.user,[0,1,8])
	if nivel != -1:
		info = ""
		query = ""
		resultsEq  = []

		if request.method == "POST":
			fxInicio 	= request.POST.get('fxInicio','')
			fxFinal 	= request.POST.get('fxFinal','')
			if True:
				if fxFinal:
					resultsEq = ActivacionEquipo.objects.filter(fxActivacion__range=[fxInicio,fxFinal],tipoActivacion__tipo__icontains='Kit')
					query = "Entre fechas : "+str(fxInicio)+" y "+str(fxFinal)
				else:
					resultsEq = ActivacionEquipo.objects.filter(fxActivacion__icontains=fxInicio,tipoActivacion__tipo__icontains='Kit')
					query = "De fecha : "+str(fxInicio)

				exportar = request.POST.get('excel','')
				if exportar == 'Exportar':
					result = []
					result2 = []
					for x in resultsEq:
						result.append([x.sucursal, x.tipoActivacion.tipo,x.equipo.detallesEquipo.marca.marca+' '+x.equipo.detallesEquipo.modelo,str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
					try:
						return export_To_Excel_ActivacionG(query,result,result2,'Kit')
					except :
						info = "No se genero su Archivo."

				ctx = {'query':query, 'info':info, 'resultsEq':resultsEq,'nivel':nivel}
				return render_to_response('activaciones/reporteKit.html',ctx,context_instance=RequestContext(request))
			
			else:
				info = "Seleccione un rango de fechas"
				form= reporteFecha(request.POST)
		
		ctx = {'query':query, 'info':info, 'resultsEq':resultsEq,'nivel':nivel}
		return render_to_response('activaciones/reporteKit.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')
		
#listo 1
@login_required(login_url='/')
def activaciones_reportes_tip_view(request):
	nivel=Permiso(request.user,[0,1,8])
	if nivel != -1:
		info = ""
		query = ""
		resultsEq  = []

		if request.method == "POST":
			fxInicio 	= request.POST.get('fxInicio','')
			fxFinal 	= request.POST.get('fxFinal','')
			if True:
				if fxFinal:
					resultsEq = ActivacionEquipo.objects.filter(fxActivacion__range=[fxInicio,fxFinal],tipoActivacion__tipo__icontains='Tip')
					query = "Entre fechas : "+str(fxInicio)+" y "+str(fxFinal)
				else:
					resultsEq = ActivacionEquipo.objects.filter(fxActivacion__icontains=fxInicio,tipoActivacion__tipo__icontains='Tip')
					query = "De fecha : "+str(fxInicio)

				exportar = request.POST.get('excel','')
				if exportar == 'Exportar':
					result = []
					result2 = []
					for x in resultsEq:
						result.append([x.sucursal, x.tipoActivacion.tipo,x.equipo.detallesEquipo.marca.marca+' '+x.equipo.detallesEquipo.modelo,str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
					try:
						return export_To_Excel_ActivacionG(query,result,result2,'Tip')
					except :
						info = "No se genero su Archivo."
				
				ctx = {'query':query, 'info':info, 'resultsEq':resultsEq,'nivel':nivel}
				return render_to_response('activaciones/reporteTip.html',ctx,context_instance=RequestContext(request))
			
			else:
				info = "Seleccione un rango de fechas"
				form= reporteFecha(request.POST)
		
		ctx = {'query':query, 'info':info, 'resultsEq':resultsEq,'nivel':nivel}
		return render_to_response('activaciones/reporteTip.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#listo 1
@login_required(login_url='/')
def activaciones_reportes_paq_g_view(request):
	nivel=Permiso(request.user,[0,1,8])
	if nivel != -1:
		info = ""
		query = ""
		resultsEq  = []

		if request.method == "POST":
			fxInicio 	= request.POST.get('fxInicio','')
			fxFinal 	= request.POST.get('fxFinal','')
			if True:
				if fxFinal:
					resultsEq = ActivacionEquipo.objects.filter(fxActivacion__range=[fxInicio,fxFinal],tipoActivacion__tipo__icontains='Paq. G')
					query = "Entre fechas : "+str(fxInicio)+" y "+str(fxFinal)
				else:
					resultsEq = ActivacionEquipo.objects.filter(fxActivacion__icontains=fxInicio,tipoActivacion__tipo__icontains='Paq. G')
					query = "De fecha : "+str(fxInicio)

				exportar = request.POST.get('excel','')
				if exportar == 'Exportar':
					result = []
					result2 = []
					for x in resultsEq:
						result.append([x.sucursal, x.tipoActivacion.tipo,x.equipo.detallesEquipo.marca.marca+' '+x.equipo.detallesEquipo.modelo,str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
					
					try:
						return export_To_Excel_ActivacionG(query,result,result2,'PaqG')
					except :
						info = "No se genero su Archivo."
				
				ctx = {'query':query, 'info':info, 'resultsEq':resultsEq,'nivel':nivel}
				return render_to_response('activaciones/reportePG.html',ctx,context_instance=RequestContext(request))
			
			else:
				info = "Seleccione un rango de fechas"
				form= reporteFecha(request.POST)
		
		ctx = {'query':query, 'info':info, 'resultsEq':resultsEq,'nivel':nivel}
		return render_to_response('activaciones/reportePG.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#listo
@login_required(login_url='/')
def activaciones_reportes_otros_view(request):
	nivel=Permiso(request.user,[0,1,8])
	if nivel != -1:
		info = ""
		query = ""
		resultsEq  = []

		if request.method == "POST":
			fxInicio 	= request.POST.get('fxInicio','')
			fxFinal 	= request.POST.get('fxFinal','')
			if True:
				if fxFinal:
					resultsEq = ActivacionEquipo.objects.filter(fxActivacion__range=[fxInicio,fxFinal],tipoActivacion__tipo__icontains='Otros')
					resultsExp = ActivacionExpress.objects.filter(fxActivacion__range=[fxInicio,fxFinal],tipoActivacion__tipo__icontains='Otros')
					query = "Entre fechas : "+str(fxInicio)+" y "+str(fxFinal)
				else:
					resultsEq = ActivacionEquipo.objects.filter(fxActivacion__icontains=fxInicio,tipoActivacion__tipo__icontains='Otros')
					resultsExp = ActivacionExpress.objects.filter(fxActivacion__icontains=fxInicio,tipoActivacion__tipo__icontains='Otros')
					query = "De fecha : "+str(fxInicio)

				exportar = request.POST.get('excel','')
				if exportar == 'Exportar':
					result = []
					result2 = []
					for x in resultsEq:
						result.append([x.sucursal, x.tipoActivacion.tipo,x.equipo.detallesEquipo.marca.marca+' '+x.equipo.detallesEquipo.modelo,str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion)])
					for x in resultsExp:
						result2.append([x.sucursal, x.tipoActivacion.tipo,x.express.icc,x.express.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
					try:
						return export_To_Excel_ActivacionG(query,result,result2,'Otros')
					except :
						info = "No se genero su Archivo."
				
				ctx = {'query':query, 'info':info, 'resultsEq':resultsEq, 'resultsExp':resultsExp,'nivel':nivel}
				return render_to_response('activaciones/reporteOtros.html',ctx,context_instance=RequestContext(request))
			
			else:
				info = "Seleccione un rango de fechas"
				form= reporteFecha(request.POST)
		
		ctx = {'query':query, 'info':info, 'resultsEq':resultsEq,'nivel':nivel}
		return render_to_response('activaciones/reporteOtros.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#listo
@login_required(login_url='/')
def activaciones_reportes_consultar_view(request):
	nivel=Permiso(request.user,[0,1,8])
	if nivel != -1:
		form = reporteCompleto()
		info = ""
		query = ""
		resultsExp = []
		resultsEq  = []
		if request.method == "POST":
			form = reporteCompleto(request.POST or None)

			if form.is_valid():
				fxInicio 	= request.POST.get('fxInicio','')
				fxFinal 	= request.POST.get('fxFinal','')
				tipo = form.data.get('tipoActivacion')

				if fxFinal:
					resultsEq = ActivacionEquipo.objects.filter(fxActivacion__range=[fxInicio,fxFinal],tipoActivacion__tipo__icontains=tipo)
					resultsExp = ActivacionExpress.objects.filter(fxActivacion__range=[fxInicio,fxFinal],tipoActivacion__tipo__icontains=tipo)
					query = "Entre fechas : "+str(fxInicio)+" y "+str(fxFinal)
				else:
					resultsEq = ActivacionEquipo.objects.filter(fxActivacion__icontains=fxInicio,tipoActivacion__tipo__icontains=tipo)
					resultsExp = ActivacionExpress.objects.filter(fxActivacion__icontains=fxInicio,tipoActivacion__tipo__icontains=tipo)
					query = "De fecha : "+str(fxInicio)

				exportar = request.POST.get('excel','')
				if exportar == 'Exportar':
					result = []
					result2 = []
					for x in resultsEq:
						result.append([x.sucursal, x.tipoActivacion.tipo,x.equipo.detallesEquipo.marca.marca+' '+x.equipo.detallesEquipo.modelo,str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
					for x in resultsExp:
						result2.append([x.sucursal, x.tipoActivacion.tipo,x.express.icc,x.express.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
					try:
						return export_To_Excel_ActivacionG(query,result,result2,'Todos')
					except :
						info = "No se genero su Archivo."
				
				ctx = {'form':form,'query':query, 'info':info, 'resultsEq':resultsEq, 'resultsExp': resultsExp, 'tipo':tipo ,'nivel':nivel}
				return render_to_response('activaciones/reporteConsultar.html',ctx,context_instance=RequestContext(request))
			
			else:
				info = "Seleccione un rango de fechas"
				form= reporteCompleto(request.POST)
		
		ctx = {'form':form,'query':query, 'info':info, 'resultsEq':resultsEq, 'resultsExp': resultsExp,'nivel':nivel}
		return render_to_response('activaciones/reporteConsultar.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#listo
@login_required(login_url='/')
def activaciones_reportes_activado_s_vta_view(request):
	nivel=Permiso(request.user,[0,1,8])
	if nivel != -1:
		form = reporteCompleto()
		info = ""
		query = ""
		resultsExp = []
		resultsEq  = []
		vtaEq = []
		vtaExp = []
		if request.method == "POST":
			form = reporteCompleto(request.POST or None)
			if form.is_valid():
				fxInicio 	= request.POST.get('fxInicio','')
				fxFinal 	= request.POST.get('fxFinal','')
				tipo = form.cleaned_data['tipoActivacion']
				resultsExp = []
				resultsEq  = []
				if fxFinal:
					eq = ActivacionEquipo.objects.filter(fxActivacion__range=[fxInicio,fxFinal],tipoActivacion__tipo__icontains=tipo)
					for x in eq:
						try:
							g1=VentaEquipo.objects.get(venta__aceptada=True,equipo = x.equipo)
							info = str(g1.equipo.imei)
							info=""
							if g1:
								pass
							else:
								resultsEq.append([ x.sucursal, x.tipoActivacion.tipo,x.equipo.detallesEquipo.marca.marca.title()+' '+x.equipo.detallesEquipo.modelo.title(),str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
						except :
							resultsEq.append([ x.sucursal, x.tipoActivacion.tipo,x.equipo.detallesEquipo.marca.marca.title()+' '+x.equipo.detallesEquipo.modelo.title(),str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
								
					ex = ActivacionExpress.objects.filter(fxActivacion__range=[fxInicio,fxFinal],tipoActivacion__tipo__icontains=tipo)
					for x in ex:
						try:
							g1=VentaExpres.objects.get(venta__aceptada=True,expres = x.express)
							if g1:
								pass
							else:
								resultsExp.append([x.sucursal,x.tipoActivacion.tipo,str(x.express.icc),x.express.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
						except :
							resultsExp.append([x.sucursal,x.tipoActivacion.tipo,str(x.express.icc),x.express.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
					query = "Entre fechas de Activaciones no Vendidas: "+str(fxInicio)+" y "+str(fxFinal)+" Activacion : "+str(tipo)
				else:
					eq = ActivacionEquipo.objects.filter(fxActivacion__icontains=fxInicio,tipoActivacion__tipo__icontains=tipo)
					for x in eq:
						try:
							g1=VentaEquipo.objects.get(venta__aceptada=True,equipo = x.equipo)
							if g1:
								pass
							else:
								resultsEq.append([x.sucursal, x.tipoActivacion.tipo, x.equipo.detallesEquipo.marca.marca.title()+' '+x.equipo.detallesEquipo.modelo.title(),str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
						except :
							resultsEq.append([x.sucursal, x.tipoActivacion.tipo, x.equipo.detallesEquipo.marca.marca.title()+' '+x.equipo.detallesEquipo.modelo.title(),str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
							
					ex = ActivacionExpress.objects.filter(fxActivacion__icontains=fxInicio,tipoActivacion__tipo__icontains=tipo)
					for x in ex:
						try:
							g1=VentaExpres.objects.get(venta__aceptada=True,expres = x.express)
							if g1:
								pass
							else:
								resultsExp.append([x.sucursal,x.tipoActivacion.tipo,str(x.express.icc),x.express.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
						except :
							resultsExp.append([x.sucursal,x.tipoActivacion.tipo,str(x.express.icc),x.express.noCell,x.empleado.curp,str(x.fxActivacion.strftime("%d-%m-%Y"))])
						query = "Fecha : "+str(fxInicio)+" Activacion : "+str(tipo)+" Activaciones no vendidas."
				
				exportar = request.POST.get('excel','')
				if exportar == 'Exportar':
					result = resultsEq
					result2 = resultsExp
					try:
						return export_To_Excel_ActivacionG(query,result,result2,'SinVta')
					except :
						info = "No se genero su Archivo."

				ctx = {'form':form,'query':query, 'info':info, 'resultsEq':resultsEq, 'resultsExp': resultsExp, 'tipo':tipo , 'vtaEq' :vtaEq ,'vtaExp' :vtaExp, 'nivel':nivel}
				return render_to_response('activaciones/reporteActSinVta.html',ctx,context_instance=RequestContext(request))
			
			else:
				info = "Seleccione un rango de fechas y/o tipo de activacion."
				form= reporteCompleto(request.POST)
		
		ctx = {'form':form,'query':query, 'info':info, 'resultsEq':resultsEq, 'resultsExp': resultsExp, 'vtaEq' :vtaEq ,'vtaExp' :vtaExp, 'nivel':nivel}
		return render_to_response('activaciones/reporteActSinVta.html',ctx,context_instance=RequestContext(request))


	else:
		return HttpResponseRedirect('/NoTienePermiso')
