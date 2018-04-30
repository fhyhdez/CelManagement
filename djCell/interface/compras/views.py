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
from datetime import datetime, timedelta, date
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

from djCell.apps.almacen.models import AlmacenEquipo, AlmacenExpres, AlmacenAccesorio, AlmacenFicha
from djCell.apps.auditoria.models import ArqueoCaja
from djCell.apps.catalogos.models import Ciudad,CP,Colonia, Estado
from djCell.apps.clientes.models import ClienteFacturacion, ClienteServicio, Mayorista
from djCell.apps.contabilidad.models import Nomina, TipoCuenta, CuentaEmpleado, HistorialEmpleado, Metas, Caja, Gastos,LineaCredito, HistLCredito, Cuenta
from djCell.apps.corteVta.models import GastosSucursal, CorteVenta, DiferenciasCorte, VentasCorte,RecargasVendidoCorte
from djCell.apps.credito.models import EstadoSubdistribuidor, EstadoCredito, Subdistribuidor, Credito, HistorialSubdistribuidor
from djCell.apps.garantiasuc.models import EstadoGarantia, Garantia
from djCell.apps.mensajes.models import EstadoMensaje, SolicitudNuevoProducto 
from djCell.apps.movimientos.models import TipoMovimiento, Movimiento, ListaEquipo, ListaExpres, ListaAccesorio, ListaFichas, TransferenciaSaldo
from djCell.apps.papeletas.models import Papeleta
from djCell.apps.personal.models import Empleado, Usuario
from djCell.apps.productos.models import TiempoGarantia,Estatus,Marca,Gama,DetallesEquipo,Equipo,TipoIcc,DetallesExpres,Expres, Secciones,MarcaAccesorio,DetallesAccesorio,EstatusAccesorio,Accesorio, NominacionFicha,EstatusFicha,Ficha,  TiempoAire
from djCell.apps.proveedor.models import Proveedor, FormaPago,  Factura
from djCell.apps.recargas.models import Monto,Recarga,SaldoSucursal, HistorialSaldo, SaldoStock
from djCell.apps.stocks.models import StockEquipo, StockExpres, StockAccesorio, StockFicha
from djCell.apps.sucursales.models import EstadoSucursal, TipoSucursal, Sucursal, VendedorSucursal
from djCell.apps.ventas.models import EstadoVenta, Venta,VentaEquipo,VentaExpres,VentaAccesorio,VentaFichas,VentaRecarga,VentaPlan,Renta, Cancelaciones, VentaMayoreo,TipoPago, Anticipo
from djCell.apps.productos.models import HistorialPreciosEquipos,HistorialPreciosAccesorios, HistorialPreciosExpres

from djCell.interface.compras.forms import addFacturaForm,addDetallesEquipoForm,addEquipoForm
from djCell.interface.compras.forms import addDetallesAccesorioForm,addAccesorioForm
from djCell.interface.compras.forms import addDetallesExpresForm,addExpresForm
from djCell.interface.compras.forms import addFichaForm,addTiempoAireForm, MarcaForm, MarcaAccesorioForm
from djCell.interface.compras.forms import MovimientoForm, MovimientoDForm, ListaEquipoForm,ListaAccesorioForm,ListaExpresForm,ListaFichasForm,TransferenciaSaldoForm
from djCell.interface.compras.forms import DetallesEquipoForm, DetallesAccesorioForm
from djCell.interface.compras.forms import SaldoStockForm,StockEquipoForm,StockAccesorioForm,StockExpresForm,StockFichaForm

#fa was here
# si quieres agregar todos porque no usas *  ? asi seria mas rapido y menos confuso
from djCell.interface.compras.forms import ProveedorForm, addCliente,addMayorista,addSubdistribuidor,updCliente,updMayorista,updSubdistribuidor, updGarantia,addAbonoCredito, AddVentaCaja,AsignarMayorista,AddVentaRecarga,AddVentaCredito,AsignarACredito, addGastosSucursal, updCorteVenta,addArqueoCaja, reporteFecha, addSecciones

from djCell.operaciones.comunes import *
from djCell.operaciones.compras import *
from djCell.operaciones.exceles import *
from djCell.operaciones.ventasgral import *
		
#yet
@login_required(login_url='/')
def index_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		return render_to_response('compras/index.html', {'nivel':nivel},context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#yet
@login_required(login_url='/')
def operacion_exitosa_view(request):
	return render_to_response('compras/operacionExitosa.html',{'informacion':'operacion_exitosa_view'},context_instance=RequestContext(request))

#ok not bad, cr probado
@login_required(login_url='/')
def compras_compras_generar_view(request):
	nivel=Permiso(request.user,[0,1,5])
	if nivel != -1:
		form = reporteFecha({'fxInicio':datetime.now().date()})
		info =""
		
		pagina1 = request.GET.get('pagina1','')
		pagina2 = request.GET.get('pagina2','')
		pagina3 = request.GET.get('pagina3','')
		pagina4 = request.GET.get('pagina4','')
		
		eqGral = []
		acGral = []
		eqSuc = []
		acSuc = []

		eg = VentaEquipo.objects.filter(venta__aceptada=True)
		ag = VentaAccesorio.objects.filter(venta__aceptada=True)

		deq = DetallesEquipo.objects.all()
		dac = DetallesAccesorio.objects.all()

		for x in deq:
			suma = 0
			suc = ""
			for j in eg:
				if x == j.equipo.detallesEquipo:
					suma = suma + 1
					suc = j.venta.sucursal.nombre.title() 
			eqGral.append([suma,x.marca.marca.title()+' '+x.modelo.title()])
			eqSuc.append([suma,x.marca.marca.title()+' '+x.modelo.title(),suc])

		for x in dac:
			suma = 0
			suc = ""
			for j in ag:
				if x == j.accesorio.detallesAccesorio:
					suma = suma + 1
					suc = j.venta.sucursal.nombre.title() 
			acGral.append([suma,x.seccion.seccion.title()+' '+x.marca.marca.title()+' '+x.descripcion.title()])
			acSuc.append([suma,x.seccion.seccion.title()+' '+x.marca.marca.title()+' '+x.descripcion.title(),suc])

		if request.method == "POST":
			form = reporteFecha(request.POST)
			if form.is_valid():
				fxInicio 	= form.cleaned_data['fxInicio']
				fxFinal 	= form.cleaned_data['fxFinal']
				eqGral = []
				acGral = []
				eqSuc = []
				acSuc = []
				if fxFinal and fxInicio:
					query = "Entre fechas : "+str(fxInicio)+" y "+str(fxFinal)
					eg = VentaEquipo.objects.filter(venta__aceptada=True, venta__fecha__range=[fxInicio,fxFinal]).distinct()
					ag = VentaAccesorio.objects.filter(venta__aceptada=True, venta__fecha__range=[fxInicio,fxFinal]).distinct()	
					for x in deq:
						suma = 0
						suc = ""
						for j in eg:
							if x == j.equipo.detallesEquipo:
								suma = suma + 1
								suc = j.venta.sucursal.nombre.title() 
						eqGral.append([suma,x.marca.marca.title()+' '+x.modelo.title()])
						eqSuc.append([suma,x.marca.marca.title()+' '+x.modelo.title(),suc])

					for x in dac:
						suma = 0
						suc = ""
						for j in ag:
							if x == j.accesorio.detallesAccesorio:
								suma = suma + 1
								suc = j.venta.sucursal.nombre.title() 
						acGral.append([suma,x.seccion.seccion.title()+' '+x.marca.marca.title()+' '+x.descripcion.title()])
						acSuc.append([suma,x.seccion.seccion.title()+' '+x.marca.marca.title()+' '+x.descripcion.title(),suc])
				else:
					query = "De fecha : "+str(fxInicio)
					eg = VentaEquipo.objects.filter(venta__aceptada=True, venta__fecha__icontains=fxInicio).distinct()
					ag = VentaAccesorio.objects.filter(venta__aceptada=True,venta__fecha__icontains=fxInicio).distinct()	
					for x in deq:
						suma = 0
						suc = ""
						for j in eg:
							if x == j.equipo.detallesEquipo:
								suma = suma + 1
								suc = j.venta.sucursal.nombre.title() 
						eqGral.append([suma,x.marca.marca.title()+' '+x.modelo.title()])
						eqSuc.append([suma,x.marca.marca.title()+' '+x.modelo.title(),suc])

					for x in dac:
						suma = 0
						suc = ""
						for j in ag:
							if x == j.accesorio.detallesAccesorio:
								suma = suma + 1
								suc = j.venta.sucursal.nombre.title() 
						acGral.append([suma,x.seccion.seccion.title()+' '+x.marca.marca.title()+' '+x.descripcion.title()])
						acSuc.append([suma,x.seccion.seccion.title()+' '+x.marca.marca.title()+' '+x.descripcion.title(),suc])

				exportar = request.POST.get('excel','')
				if exportar == 'Exportar':
					#try:
					if True:
						eqGral.sort(reverse=True)
						acGral.sort(reverse=True)
						eqSuc.sort(reverse=True)
						acSuc.sort(reverse=True)
						return exportCompras(query,eqGral,acGral,eqSuc,acSuc,'Todos')
					#except :
					#	info = "No se genero su Archivo."

			else:
				info = "Seleccione un rango de fechas: inicial y final."
				form= reporteFecha(request.POST)
		
		eqGral.sort(reverse=True)
		acGral.sort(reverse=True)
		eqSuc.sort(reverse=True)
		acSuc.sort(reverse=True)
		paginator1 = Paginator(eqGral, 20)
		paginator2 = Paginator(eqSuc, 20)
		paginator3 = Paginator(acGral, 20)
		paginator4 = Paginator(acSuc, 20)
		eG=None
		eS=None
		aG=None
		aS=None
		try:
			eG = paginator1.page(pagina1)
		except PageNotAnInteger:
			eG = paginator1.page(1)
		except EmptyPage:
			eG = paginator1.page(paginator1.num_pages)

		try:
			eS = paginator2.page(pagina2)
		except PageNotAnInteger:
			eS = paginator2.page(1)
		except EmptyPage:
			eS = paginator2.page(paginator2.num_pages)

		try:
			aG = paginator3.page(pagina3)
		except PageNotAnInteger:
			aG = paginator3.page(1)
		except EmptyPage:
			aG = paginator3.page(paginator3.num_pages)

		try:
			aS = paginator4.page(pagina4)
		except PageNotAnInteger:
			aS = paginator4.page(1)
		except EmptyPage:
			aS = paginator4.page(paginator4.num_pages)
		
		ctx = {'eqGral':eG,'eqSuc':eS,'acGral':aG,'acSuc':aS,'form':form ,'info':info, 'nivel':nivel}
		return render_to_response('compras/generacionCompras.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet probado
@login_required(login_url='/')
def compras_compras_lista_precios_equipos_view(request):
	nivel=Permiso(request.user,[0,1,5])
	if nivel != -1:
		folio=request.GET.get('folio','')
		r_item=None
		r_items=None
		info=''
		mensaje=''
		actPrecForm=DetallesEquipoForm()

		if 'actualizar' in request.POST:
			folio=request.POST.get('folio','')
			item=None
			try:
				item = DetallesEquipo.objects.get(folio=folio)
			except :
				info='Folio Incorrecto, Modelo no encontrado'
			if item:
				actPrecForm=DetallesEquipoForm(request.POST, instance=item)
				if actPrecForm.is_valid():
					folio=actPrecForm.cleaned_data['folio']
					pmy=actPrecForm.cleaned_data['precioMayoreo']
					pmn=actPrecForm.cleaned_data['precioMenudeo']
					try:
						with transaction.atomic():
							item=DetallesEquipo.objects.get(folio=folio)
							historial=HistorialPreciosEquipos()
							historial.detallesEquipo 	= item
							historial.usuario 		= request.user
							historial.precioMayoreo	= pmy
							historial.precioMenudeo	= pmn
							historial.save()
							item.precioMayoreo=pmy
							item.precioMenudeo=pmn
							item.save()
							actPrecForm=DetallesEquipoForm()
							info='Modelo %s Actualizado Correctamente'%(item)
					except :
						info='Folio %s no Encontrado'%(folio)
					folio=''


		if folio:
			try:
				r_item=DetallesEquipo.objects.get(folio=folio)
			except :
				qset=(Q(gama__gama__icontains=folio)|
				Q(marca__marca__icontains=folio)|
				Q(modelo__icontains=folio)|
				Q(color__icontains=folio)|
				Q(folio__icontains=folio))
				r_items=DetallesEquipo.objects.filter(qset).distinct()
		else:
			qset=(Q(precioMenudeo=None)|Q(precioMayoreo=None))
			r_items=DetallesEquipo.objects.filter(qset).distinct()

		if r_item:
			actPrecForm=DetallesEquipoForm(initial={'folio':r_item.folio})

		ctx={'nivel':nivel, 'folio':folio, 'r_item':r_item, 'r_items':r_items, 'actPrecForm':actPrecForm, 'info':info}
		
		return render_to_response('compras/comprasListaPreciosEquipos.html', ctx, context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet probado
@login_required(login_url='/')
def compras_compras_lista_precios_accesorios_view(request):
	nivel=Permiso(request.user,[0,1,5])
	if nivel != -1:
		folio=request.GET.get('folio','')
		r_item=None
		r_items=None
		info=''
		actPrecForm=DetallesAccesorioForm()


		if 'actualizar' in request.POST:
			folio=request.POST.get('folio','')
			item=None
			try:
				item = DetallesAccesorio.objects.get(folio=folio)
			except :
				info='Folio Incorrecto, Modelo no encontrado'
			if item:
				actPrecForm=DetallesAccesorioForm(request.POST, instance=item)
				if actPrecForm.is_valid():
					folio=actPrecForm.cleaned_data['folio']
					pmy=actPrecForm.cleaned_data['precioMayoreo']
					pmn=actPrecForm.cleaned_data['precioMenudeo']
					try:
						with transaction.atomic():
							item=DetallesAccesorio.objects.get(folio=folio)
							historial=HistorialPreciosAccesorios()
							historial.detallesAccesorio 	= item
							historial.usuario 		= request.user
							historial.precioMayoreo	= pmy
							historial.precioMenudeo	= pmn
							historial.save()
							item.precioMayoreo=pmy
							item.precioMenudeo=pmn
							item.save()
							actPrecForm=DetallesAccesorioForm()
							info='Accesorio %s Actualizado Correctamente'%(item)
					except :
						info='Accesorio con Folio %s no Encontrado'%(folio)
					folio=''

		if folio:
			try:
				r_item=DetallesAccesorio.objects.get(folio=folio)
			except :
				qset=(Q(seccion__seccion__icontains=folio)|
				Q(marca__marca__icontains=folio)|
				Q(descripcion__icontains=folio)|
				Q(folio__icontains=folio))
				r_items=DetallesAccesorio.objects.filter(qset).distinct()
		else:
			qset=(Q(precioMenudeo=None)|Q(precioMayoreo=None))
			r_items=DetallesAccesorio.objects.filter(qset).distinct()

		if r_item:
			actPrecForm=DetallesAccesorioForm(initial={'folio':r_item.folio})

		ctx={'nivel':nivel, 'folio':folio, 'r_item':r_item, 'r_items':r_items, 'actPrecForm':actPrecForm, 'info':info}
		
		return render_to_response('compras/comprasListaPreciosAcces.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#yet probado
@login_required(login_url='/')
def compras_compras_lista_precios_express_view(request):
	nivel=Permiso(request.user,[0,1,5])
	mensaje=''
	if nivel != -1:
		exp=addDetallesExpresForm(prefix='expres')
		virgen=addDetallesExpresForm(prefix='virgen')
		try:
			exp_in=DetallesExpres.objects.get(descripcion='Expres')
			exp=addDetallesExpresForm(prefix='expres', initial={'tiempoGarantia':exp_in.tiempoGarantia,'precioMayoreo':exp_in.precioMayoreo,'precioMenudeo':exp_in.precioMenudeo})
		except :
			pass
		try:
			vir_in=DetallesExpres.objects.get(descripcion='Virgen')
			virgen=addDetallesExpresForm(prefix='virgen', initial={'tiempoGarantia':vir_in.tiempoGarantia,'precioMayoreo':vir_in.precioMayoreo,'precioMenudeo':vir_in.precioMenudeo})
		except :
			pass

		if 'actualizar' in request.POST:
			exp=addDetallesExpresForm(request.POST, prefix='expres')
			if exp.is_valid():
				try:
					with transaction.atomic():
						try:
							detExp=DetallesExpres.objects.get(descripcion='Expres')
						except :
							detExp=DetallesExpres()
							detExp.descripcion='Expres'
							try:
								tipo=TipoIcc.objects.get(tipoIcc='Expres')
							except :
								tipo=TipoIcc()
								tipo.tipoIcc='Expres'
								tipo.save()
							detExp.tipoIcc=tipo
							try:
								tiempo=TiempoGarantia.objects.get(dias=0)
							except :
								tiempo=TiempoGarantia()
								tiempo.dias=0
							detExp.tiempoGarantia=tiempo
							detExp.save()
						detExp.precioMayoreo=exp.cleaned_data['precioMayoreo']
						detExp.precioMenudeo=exp.cleaned_data['precioMenudeo']
						detExp.save()
						historial=HistorialPreciosExpres()
						historial.detalles 	= detExp
						historial.usuario 		= request.user
						historial.precioMayoreo	= detExp.precioMayoreo
						historial.precioMenudeo	= detExp.precioMenudeo
						historial.save()
						mensaje='Precios Express Actualizados'
				except :
					mensaje='ERROR: Precios Express No Actualizados'
					
			virgen=addDetallesExpresForm(request.POST, prefix='virgen')
			if virgen.is_valid():
				try:
					with transaction.atomic():
						try:
							detExp=DetallesExpres.objects.get(descripcion='Virgen')
						except :
							detExp=DetallesExpres()
							detExp.descripcion='Virgen'
							try:
								tipo=TipoIcc.objects.get(tipoIcc='Virgen')
							except :
								tipo=TipoIcc()
								tipo.tipoIcc='Virgen'
								tipo.save()
							detExp.tipoIcc=tipo
							try:
								tiempo=TiempoGarantia.objects.get(dias=0)
							except :
								tiempo=TiempoGarantia()
								tiempo.dias=0
							detExp.tiempoGarantia=tiempo
							detExp.save()
						detExp.precioMayoreo=virgen.cleaned_data['precioMayoreo']
						detExp.precioMenudeo=virgen.cleaned_data['precioMenudeo']
						detExp.save()
						historial=HistorialPreciosExpres()
						historial.detalles 	= detExp
						historial.usuario 		= request.user
						historial.precioMayoreo	= detExp.precioMayoreo
						historial.precioMenudeo	= detExp.precioMenudeo
						historial.save()
						mensaje='%s , Precios de Virgenes Actualizados'%(mensaje)
				except :
					mensaje='%s , Precios de Virgenes NO Actualizados'%(mensaje) 

		ctx={'nivel':nivel,  'exp':exp, 'virgen':virgen, 'mensaje':mensaje}
		return render_to_response('compras/comprasListaPreciosExpres.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#listo - #yet - probado
@login_required(login_url='/')
def compras_compras_pedidos_view(request):
	nivel=Permiso(request.user,[0,1,5,6])
	if nivel != -1:
		info = ""
		query  = request.GET.get('q','')
		pag1=request.GET.get('pag','')
		
		msgs = SolicitudNuevoProducto.objects.filter(Q(estado__estado__icontains='Sin revisar')|Q(estado__estado__icontains='Revisado')).order_by('estado')

		if query:
			qset=(Q(folio__icontains=query) |
			 Q(nuevoProducto__icontains=query) | 
			 Q(estado__estado__icontains=query) | 
			 Q(sucursal__nombre__icontains=query))
			msgs = SolicitudNuevoProducto.objects.filter(qset).order_by('estado')
		
		
		paginator1 = Paginator(msgs, 50)

		pMensages=None
		
		try:
			pMensages = paginator1.page(pag1)
		except PageNotAnInteger:
			pMensages= paginator1.page(1)
		except EmptyPage:
			pMensages = paginator1.page(paginator1.num_pages)

		if request.method == "GET":
			if request.GET.get('elim'):
				s = request.GET.get('elim','')
				if s:
					try:
						with transaction.atomic():
							upd = SolicitudNuevoProducto.objects.get(id= s)
							upd.estado = EstadoMensaje.objects.get(estado__icontains='Eliminado')
							upd.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
	
			if request.GET.get('lei'):
				s = request.GET.get('lei','')
				if s:
					try:
						with transaction.atomic():
							upd = SolicitudNuevoProducto.objects.get(id= s)
							upd.estado = EstadoMensaje.objects.get(estado__icontains='Revisado')
							upd.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

		ctx={'Mensajes':pMensages,'info':info,'query':query,'nivel':nivel}
		return render_to_response('compras/mySeguimientoPedidos.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet - probado
@login_required(login_url='/')
def compras_compras_stocks_asignar_equipos_view(request):
	nivel=Permiso(request.user,[0,1,5])
	if nivel != -1:

		b_sucursal=request.GET.get('sucursal','')
		b_detalle=request.GET.get('detalle','')
		r_sucu=None
		r_sucus=None
		r_detalle=None
		r_detalles=None
		stockItem=StockEquipoForm()
		detalles=DetallesEquipo.objects.all()
		info = ""
		if b_sucursal:
			pass
		else:
			_usuario=Usuario.objects.get(user=request.user)
			_empleado=_usuario.empleado
			vSucural=VendedorSucursal.objects.get(empleado=_empleado)
			_sucursal=vSucural.sucursal
			b_sucursal=_sucursal.nombre
		if b_sucursal:
			try:
				r_sucu=Sucursal.objects.get(nombre=b_sucursal)
				if len(detalles)>len(StockEquipo.objects.filter(sucursal=r_sucu)):
					for detalle in detalles:
						if StockEquipo.objects.filter(sucursal=r_sucu, detalle=detalle).exists():
							pass
						else:
							stock=StockEquipo()
							stock.sucursal 	= r_sucu
							stock.detalle 	= detalle
							stock.save()

			except :
				qset=(Q(tipoSucursal__tipo__icontains=b_sucursal)|
				Q(nombre__icontains=b_sucursal)|
				Q(encargado__nombre__icontains=b_sucursal)|
				Q(noCelOfi__icontains=b_sucursal)|
				Q(direccion__icontains=b_sucursal))
				r_sucus=Sucursal.objects.filter(qset).distinct()

		if b_detalle:
			try:
				r_detalle=DetallesEquipo.objects.get(id=b_detalle)
			except :
				pass

		stockItem=StockEquipoForm(initial={'sucursal':r_sucu, 'detalle':r_detalle})

		if 'actualizar' in request.POST:
			stockItem=StockEquipoForm(request.POST)
			if stockItem.is_valid():
				_sucursal=stockItem.cleaned_data['sucursal']
				_detalle=stockItem.cleaned_data['detalle']
				_stockMin=stockItem.cleaned_data['stockMin']
				_stockMax=stockItem.cleaned_data['stockMax']
				try:
					with transaction.atomic():
						itemStock=StockEquipo.objects.get(sucursal=_sucursal, detalle=_detalle)
						itemStock.stockMin=_stockMin
						itemStock.stockMax=_stockMax
						itemStock.save()
						r_sucu=_sucursal
				except :
					stockItem.save()
				b_sucursal=_sucursal.nombre
				stockItem=StockEquipoForm(initial={'sucursal':_sucursal})
				info = "Se ha Guardado correctamente."

		if r_sucu and r_detalle==None:
			qset=(Q(stockMin=None)|
			Q(stockMax=None))
			r_detalles=StockEquipo.objects.filter(qset, sucursal=r_sucu).distinct()


		ctx={'nivel':nivel,'info':info,'stockItem':stockItem, 'b_sucursal':b_sucursal, 'r_sucus':r_sucus, 'r_detalles':r_detalles}

		return render_to_response('compras/stockEquipo.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet probado
@login_required(login_url='/')
def compras_compras_stocks_asignar_accesorios_view(request):
	nivel=Permiso(request.user,[0,1,5])
	if nivel != -1:

		b_sucursal=request.GET.get('sucursal','')
		b_detalle=request.GET.get('detalle','')
		r_sucu=None
		r_sucus=None
		r_detalle=None
		r_detalles=None
		stockItem=StockAccesorioForm()
		detalles=DetallesAccesorio.objects.all()
		info = ""
		if b_sucursal:
			pass
		else:
			_usuario=Usuario.objects.get(user=request.user)
			_empleado=_usuario.empleado
			vSucural=VendedorSucursal.objects.get(empleado=_empleado)
			_sucursal=vSucural.sucursal
			b_sucursal=_sucursal.nombre
		if b_sucursal:
			try:
				r_sucu=Sucursal.objects.get(nombre=b_sucursal)
				if len(detalles)>len(StockAccesorio.objects.filter(sucursal=r_sucu)):
					for detalle in detalles:
						if StockAccesorio.objects.filter(sucursal=r_sucu, detalle=detalle).exists():
							pass
						else:
							stock=StockAccesorio()
							stock.sucursal 	= r_sucu
							stock.detalle 	= detalle
							stock.save()

			except :
				qset=(Q(tipoSucursal__tipo__icontains=b_sucursal)|
				Q(nombre__icontains=b_sucursal)|
				Q(encargado__nombre__icontains=b_sucursal)|
				Q(noCelOfi__icontains=b_sucursal)|
				Q(direccion__icontains=b_sucursal))
				r_sucus=Sucursal.objects.filter(qset).distinct()

		if b_detalle:
			try:
				r_detalle=DetallesAccesorio.objects.get(id=b_detalle)
			except :
				pass

		stockItem=StockAccesorioForm(initial={'sucursal':r_sucu, 'detalle':r_detalle})

		if 'actualizar' in request.POST:
			stockItem=StockAccesorioForm(request.POST)
			if stockItem.is_valid():
				_sucursal=stockItem.cleaned_data['sucursal']
				_detalle=stockItem.cleaned_data['detalle']
				_stockMin=stockItem.cleaned_data['stockMin']
				_stockMax=stockItem.cleaned_data['stockMax']
				try:
					with transaction.atomic():
						itemStock=StockAccesorio.objects.get(sucursal=_sucursal, detalle=_detalle)
						itemStock.stockMin=_stockMin
						itemStock.stockMax=_stockMax
						itemStock.save()
						r_sucu=_sucursal
				except :
					stockItem.save()
				info = "Se ha Guardado correctamente."
				b_sucursal=_sucursal.nombre
				stockItem=StockAccesorioForm(initial={'sucursal':_sucursal})

		if r_sucu and r_detalle==None:
			qset=(Q(stockMin=None)|
			Q(stockMax=None))
			r_detalles=StockAccesorio.objects.filter(qset, sucursal=r_sucu).distinct()


		ctx={'nivel':nivel,"info":info,'stockItem':stockItem, 'b_sucursal':b_sucursal, 'r_sucus':r_sucus, 'r_detalles':r_detalles}

		return render_to_response('compras/stockAcces.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet probado
@login_required(login_url='/')
def compras_compras_stocks_asignar_express_view(request):
	nivel=Permiso(request.user,[0,1,5])
	if nivel != -1:

		b_sucursal=request.GET.get('sucursal','')
		r_sucu=None
		r_sucus=None
		stockItem=StockExpresForm()
		info = ""
		if b_sucursal:
			pass
		else:
			_usuario=Usuario.objects.get(user=request.user)
			_empleado=_usuario.empleado
			vSucural=VendedorSucursal.objects.get(empleado=_empleado)
			_sucursal=vSucural.sucursal
			b_sucursal=_sucursal.nombre
		if b_sucursal:
			try:
				r_sucu=Sucursal.objects.get(nombre=b_sucursal)
				if StockExpres.objects.filter(sucursal=r_sucu).exists():
					pass
				else:
					stock=StockExpres()
					stock.sucursal 	= r_sucu
					stock.save()

			except :
				qset=(Q(tipoSucursal__tipo__icontains=b_sucursal)|
				Q(nombre__icontains=b_sucursal)|
				Q(encargado__nombre__icontains=b_sucursal)|
				Q(noCelOfi__icontains=b_sucursal)|
				Q(direccion__icontains=b_sucursal))
				r_sucus=Sucursal.objects.filter(qset).distinct()


		stockItem=StockExpresForm(initial={'sucursal':r_sucu})

		if 'actualizar' in request.POST:
			stockItem=StockExpresForm(request.POST)
			if stockItem.is_valid():
				_sucursal=stockItem.cleaned_data['sucursal']
				_stockMin=stockItem.cleaned_data['stockMin']
				_stockMax=stockItem.cleaned_data['stockMax']
				try:
					with transaction.atomic():
						itemStock=StockExpres.objects.get(sucursal=_sucursal)
						itemStock.stockMin=_stockMin
						itemStock.stockMax=_stockMax
						itemStock.save()
				except :
					stockItem.save()
				info = "Se ha Guardado correctamente."
				stockItem=StockExpresForm()


		ctx={'nivel':nivel,'info':info ,'stockItem':stockItem, 'b_sucursal':b_sucursal, 'r_sucus':r_sucus}

		return render_to_response('compras/stockExpres.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet probado
@login_required(login_url='/')
def compras_compras_stocks_asignar_fichas_view(request):
	nivel=Permiso(request.user,[0,1,5])
	if nivel != -1:

		b_sucursal=request.GET.get('sucursal','')
		b_detalle=request.GET.get('detalle','')
		r_sucu=None
		r_sucus=None
		r_detalle=None
		r_detalles=None
		stockItem=StockFichaForm()
		detalles=NominacionFicha.objects.all()
		info = ""
		if b_sucursal:
			pass
		else:
			_usuario=Usuario.objects.get(user=request.user)
			_empleado=_usuario.empleado
			vSucural=VendedorSucursal.objects.get(empleado=_empleado)
			_sucursal=vSucural.sucursal
			b_sucursal=_sucursal.nombre
		if b_sucursal:
			try:
				r_sucu=Sucursal.objects.get(nombre=b_sucursal)
				if len(detalles)>len(StockFicha.objects.filter(sucursal=r_sucu)):
					for detalle in detalles:
						if StockFicha.objects.filter(sucursal=r_sucu, nominacion=detalle).exists():
							pass
						else:
							stock=StockFicha()
							stock.sucursal 	= r_sucu
							stock.nominacion 	= detalle
							stock.save()

			except :
				qset=(Q(tipoSucursal__tipo__icontains=b_sucursal)|
				Q(nombre__icontains=b_sucursal)|
				Q(encargado__nombre__icontains=b_sucursal)|
				Q(noCelOfi__icontains=b_sucursal)|
				Q(direccion__icontains=b_sucursal))
				r_sucus=Sucursal.objects.filter(qset).distinct()

		if b_detalle:
			try:
				r_detalle=NominacionFicha.objects.get(id=b_detalle)
			except :
				pass

		stockItem=StockFichaForm(initial={'sucursal':r_sucu, 'nominacion':r_detalle})

		if 'actualizar' in request.POST:
			stockItem=StockFichaForm(request.POST)
			if stockItem.is_valid():
				_sucursal=stockItem.cleaned_data['sucursal']
				_detalle=stockItem.cleaned_data['nominacion']
				_stockMin=stockItem.cleaned_data['stockMin']
				_stockMax=stockItem.cleaned_data['stockMax']
				try:
					with transaction.atomic():
						itemStock=StockFicha.objects.get(sucursal=_sucursal, nominacion=_detalle)
						itemStock.stockMin=_stockMin
						itemStock.stockMax=_stockMax
						itemStock.save()
						r_sucu=_sucursal
				except :
					stockItem.save()
				info = "Se ha Guardado correctamente."
				b_sucursal=_sucursal.nombre
				stockItem=StockFichaForm(initial={'sucursal':_sucursal})

		if r_sucu and r_detalle==None:
			qset=(Q(stockMin=None)|
			Q(stockMax=None))
			r_detalles=StockFicha.objects.filter(qset, sucursal=r_sucu).distinct()


		ctx={'nivel':nivel,'info':info ,'stockItem':stockItem, 'b_sucursal':b_sucursal, 'r_sucus':r_sucus, 'r_detalles':r_detalles}

		return render_to_response('compras/stockFichas.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet probado
@login_required(login_url='/')
def compras_compras_stocks_asignar_recargas_view(request):
	nivel=Permiso(request.user,[0,1,5])
	if nivel != -1:

		b_sucursal=request.GET.get('sucursal','')
		r_sucu=None
		r_sucus=None
		stockItem=SaldoStockForm()
		info=""
		if b_sucursal:
			pass
		else:
			_usuario=Usuario.objects.get(user=request.user)
			_empleado=_usuario.empleado
			vSucural=VendedorSucursal.objects.get(empleado=_empleado)
			_sucursal=vSucural.sucursal
			b_sucursal=_sucursal.nombre

		if b_sucursal:
			try:
				r_sucu=Sucursal.objects.get(nombre=b_sucursal)
				if SaldoStock.objects.filter(sucursal=r_sucu).exists():
					pass
				else:
					stock=SaldoStock()
					stock.sucursal 	= r_sucu
					stock.save()

			except :
				qset=(Q(tipoSucursal__tipo__icontains=b_sucursal)|
				Q(nombre__icontains=b_sucursal)|
				Q(encargado__nombre__icontains=b_sucursal)|
				Q(noCelOfi__icontains=b_sucursal)|
				Q(direccion__icontains=b_sucursal))
				r_sucus=Sucursal.objects.filter(qset).distinct()


		stockItem=SaldoStockForm(initial={'sucursal':r_sucu})

		if 'actualizar' in request.POST:
			stockItem=SaldoStockForm(request.POST)
			if stockItem.is_valid():
				_sucursal=stockItem.cleaned_data['sucursal']
				_stockMin=stockItem.cleaned_data['minimo']
				_stockMax=stockItem.cleaned_data['maximo']
				try:
					with transaction.atomic():
						itemStock=SaldoStock.objects.get(sucursal=_sucursal)
						itemStock.minimo=_stockMin
						itemStock.maximo=_stockMax
						itemStock.save()
				except :
					stockItem.save()
				info = "Se ha Guardado correctamente."
				stockItem=SaldoStockForm()

		ctx={'nivel':nivel,'info':info ,'stockItem':stockItem, 'b_sucursal':b_sucursal, 'r_sucus':r_sucus}

		return render_to_response('compras/stockSaldo.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#yet probado 
@login_required(login_url='/')
def compras_compras_stocks_actualizar_equipos_view(request):
	nivel=Permiso(request.user,[0,1,5])
	if nivel != -1:

		b_sucursal=request.GET.get('sucursal','')
		b_detalle=request.GET.get('detalle','')
		r_sucu=None
		r_sucus=None
		r_detalle=None
		r_detalles=None
		p_max=0
		p_min=0
		stockItem=StockEquipoForm()
		info = ""
		if b_sucursal:
			pass
		else:
			_usuario=Usuario.objects.get(user=request.user)
			_empleado=_usuario.empleado
			vSucural=VendedorSucursal.objects.get(empleado=_empleado)
			_sucursal=vSucural.sucursal
			b_sucursal=_sucursal.nombre
		if b_sucursal:
			try:
				r_sucu=Sucursal.objects.get(nombre=b_sucursal)

			except :
				qset=(Q(tipoSucursal__tipo__icontains=b_sucursal)|
				Q(nombre__icontains=b_sucursal)|
				Q(encargado__nombre__icontains=b_sucursal)|
				Q(noCelOfi__icontains=b_sucursal)|
				Q(direccion__icontains=b_sucursal))
				r_sucus=Sucursal.objects.filter(qset).distinct()

		if b_detalle:
			try:
				r_detalle=DetallesEquipo.objects.get(id=b_detalle)
			except :
				qset=(Q(detalle__gama__gama__icontains=b_detalle)|
				Q(detalle__modelo__icontains=b_detalle)|
				Q(detalle__marca__marca__icontains=b_detalle))
				r_detalles=StockEquipo.objects.filter(qset,sucursal=r_sucu)
		try:
			stock=StockEquipo.objects.get(sucursal=r_sucu, detalle=r_detalle)
			p_max=stock.stockMax
			p_min=stock.stockMin
		except :
			pass
			

		stockItem=StockEquipoForm(initial={'sucursal':r_sucu, 'detalle':r_detalle, 'stockMin':p_min, 'stockMax':p_max})

		if 'actualizar' in request.POST:
			stockItem=StockEquipoForm(request.POST)
			if stockItem.is_valid():
				_sucursal=stockItem.cleaned_data['sucursal']
				_detalle=stockItem.cleaned_data['detalle']
				_stockMin=stockItem.cleaned_data['stockMin']
				_stockMax=stockItem.cleaned_data['stockMax']
				try:
					with transaction.atomic():
						itemStock=StockEquipo.objects.get(sucursal=_sucursal, detalle=_detalle)
						itemStock.stockMin=_stockMin
						itemStock.stockMax=_stockMax
						itemStock.save()
						r_sucu=_sucursal
				except :
					stockItem.save()
				info = "Se ha Guardado correctamente."
				b_sucursal=_sucursal.nombre
				stockItem=StockFichaForm(initial={'sucursal':_sucursal})

		if r_sucu and r_detalle==None:
			if r_detalles:
				pass
			else:
				r_detalles=StockEquipo.objects.filter( sucursal=r_sucu).distinct()


		ctx={'nivel':nivel,'info':info ,'stockItem':stockItem, 'b_sucursal':b_sucursal, 'b_detalle':b_detalle, 'r_sucus':r_sucus, 'r_detalles':r_detalles}

		return render_to_response('compras/stockEquipoA.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet probado
@login_required(login_url='/')
def compras_compras_stocks_actualizar_accesorios_view(request):
	nivel=Permiso(request.user,[0,1,5])
	if nivel != -1:

		b_sucursal=request.GET.get('sucursal','')
		b_detalle=request.GET.get('detalle','')
		r_sucu=None
		r_sucus=None
		r_detalle=None
		r_detalles=None
		p_max=0
		p_min=0
		stockItem=StockAccesorioForm()
		detalles=DetallesAccesorio.objects.all()
		info=""
		if b_sucursal:
			pass
		else:
			_usuario=Usuario.objects.get(user=request.user)
			_empleado=_usuario.empleado
			vSucural=VendedorSucursal.objects.get(empleado=_empleado)
			_sucursal=vSucural.sucursal
			b_sucursal=_sucursal.nombre
		if b_sucursal:
			try:
				r_sucu=Sucursal.objects.get(nombre=b_sucursal)


			except :
				qset=(Q(tipoSucursal__tipo__icontains=b_sucursal)|
				Q(nombre__icontains=b_sucursal)|
				Q(encargado__nombre__icontains=b_sucursal)|
				Q(noCelOfi__icontains=b_sucursal)|
				Q(direccion__icontains=b_sucursal))
				r_sucus=Sucursal.objects.filter(qset).distinct()

		if b_detalle:
			try:
				r_detalle=DetallesAccesorio.objects.get(id=b_detalle)
			except :
				qset=(Q(detalle__descripcion__icontains=b_detalle)|
				Q(detalle__seccion__seccion__icontains=b_detalle)|
				Q(detalle__marca__marca__icontains=b_detalle))
				r_detalles=StockAccesorio.objects.filter(qset,sucursal=r_sucu)
		try:
			stock=StockAccesorio.objects.get(sucursal=r_sucu, detalle=r_detalle)
			p_max=stock.stockMax
			p_min=stock.stockMin
		except :
			pass

		stockItem=StockAccesorioForm(initial={'sucursal':r_sucu, 'detalle':r_detalle, 'stockMin':p_min, 'stockMax':p_max})

		if 'actualizar' in request.POST:
			stockItem=StockAccesorioForm(request.POST)
			if stockItem.is_valid():
				_sucursal=stockItem.cleaned_data['sucursal']
				_detalle=stockItem.cleaned_data['detalle']
				_stockMin=stockItem.cleaned_data['stockMin']
				_stockMax=stockItem.cleaned_data['stockMax']
				try:
					with transaction.atomic():
						itemStock=StockAccesorio.objects.get(sucursal=_sucursal, detalle=_detalle)
						itemStock.stockMin=_stockMin
						itemStock.stockMax=_stockMax
						itemStock.save()
						r_sucu=_sucursal
				except :
					stockItem.save()
				info = "Se ha Guardado correctamente."
				b_sucursal=_sucursal.nombre
				stockItem=StockAccesorioForm(initial={'sucursal':_sucursal})

		if r_sucu and r_detalle==None:
			if r_detalles:
				pass
			else:
				r_detalles=StockAccesorio.objects.filter( sucursal=r_sucu).distinct()

		ctx={'nivel':nivel,'info':info ,'stockItem':stockItem, 'b_sucursal':b_sucursal, 'b_detalle':b_detalle, 'r_sucus':r_sucus, 'r_detalles':r_detalles}

		return render_to_response('compras/stockAccesA.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet probado
@login_required(login_url='/')
def compras_compras_stocks_actualizar_express_view(request):
	nivel=Permiso(request.user,[0,1,5])
	if nivel != -1:

		b_sucursal=request.GET.get('sucursal','')
		r_sucu=None
		r_sucus=None
		p_max=0
		p_min=0
		stockItem=StockExpresForm()
		info = ""
		if b_sucursal:
			pass
		else:
			_usuario=Usuario.objects.get(user=request.user)
			_empleado=_usuario.empleado
			vSucural=VendedorSucursal.objects.get(empleado=_empleado)
			_sucursal=vSucural.sucursal
			b_sucursal=_sucursal.nombre
		if b_sucursal:
			try:
				r_sucu=Sucursal.objects.get(nombre=b_sucursal)

			except :
				qset=(Q(tipoSucursal__tipo__icontains=b_sucursal)|
				Q(nombre__icontains=b_sucursal)|
				Q(encargado__nombre__icontains=b_sucursal)|
				Q(noCelOfi__icontains=b_sucursal)|
				Q(direccion__icontains=b_sucursal))
				r_sucus=Sucursal.objects.filter(qset).distinct()
		try:
			stock=StockExpres.objects.get(sucursal=r_sucu)
			p_max=stock.stockMax
			p_min=stock.stockMin
		except :
			pass


		stockItem=StockExpresForm(initial={'sucursal':r_sucu, 'stockMin':p_min, 'stockMax':p_max})

		if 'actualizar' in request.POST:
			stockItem=StockExpresForm(request.POST)
			if stockItem.is_valid():
				_sucursal=stockItem.cleaned_data['sucursal']
				_stockMin=stockItem.cleaned_data['stockMin']
				_stockMax=stockItem.cleaned_data['stockMax']
				try:
					with transaction.atomic():
						itemStock=StockExpres.objects.get(sucursal=_sucursal)
						itemStock.stockMin=_stockMin
						itemStock.stockMax=_stockMax
						itemStock.save()
				except :
					stockItem.save()
				info = "Se ha Guardado correctamente."
				stockItem=StockExpresForm()


		ctx={'nivel':nivel,'info':info ,'stockItem':stockItem, 'b_sucursal':b_sucursal, 'r_sucus':r_sucus}

		return render_to_response('compras/stockExpresA.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet probado
@login_required(login_url='/')
def compras_compras_stocks_actualizar_fichas_view(request):
	nivel=Permiso(request.user,[0,1,5])
	if nivel != -1:

		b_sucursal=request.GET.get('sucursal','')
		b_detalle=request.GET.get('detalle','')
		r_sucu=None
		r_sucus=None
		r_detalle=None
		r_detalles=None
		p_max=0
		p_min=0
		stockItem=StockFichaForm()
		detalles=NominacionFicha.objects.all()
		info=""
		if b_sucursal:
			pass
		else:
			_usuario=Usuario.objects.get(user=request.user)
			_empleado=_usuario.empleado
			vSucural=VendedorSucursal.objects.get(empleado=_empleado)
			_sucursal=vSucural.sucursal
			b_sucursal=_sucursal.nombre
		if b_sucursal:
			try:
				r_sucu=Sucursal.objects.get(nombre=b_sucursal)

			except :
				qset=(Q(tipoSucursal__tipo__icontains=b_sucursal)|
				Q(nombre__icontains=b_sucursal)|
				Q(encargado__nombre__icontains=b_sucursal)|
				Q(noCelOfi__icontains=b_sucursal)|
				Q(direccion__icontains=b_sucursal))
				r_sucus=Sucursal.objects.filter(qset).distinct()

		if b_detalle:
			try:
				r_detalle=NominacionFicha.objects.get(id=b_detalle)
			except :
				pass

		try:
			stock=StockFicha.objects.get(sucursal=r_sucu, nominacion=r_detalle)
			p_max=stock.stockMax
			p_min=stock.stockMin
		except :
			pass

		stockItem=StockFichaForm(initial={'sucursal':r_sucu, 'nominacion':r_detalle, 'stockMin':p_min, 'stockMax':p_max})

		if 'actualizar' in request.POST:
			stockItem=StockFichaForm(request.POST)
			if stockItem.is_valid():
				_sucursal=stockItem.cleaned_data['sucursal']
				_detalle=stockItem.cleaned_data['nominacion']
				_stockMin=stockItem.cleaned_data['stockMin']
				_stockMax=stockItem.cleaned_data['stockMax']
				try:
					with transaction.atomic():
						itemStock=StockFicha.objects.get(sucursal=_sucursal, nominacion=_detalle)
						itemStock.stockMin=_stockMin
						itemStock.stockMax=_stockMax
						itemStock.save()
						r_sucu=_sucursal
				except :
					stockItem.save()
				info = "Se ha Guardado correctamente."
				b_sucursal=_sucursal.nombre
				stockItem=StockFichaForm(initial={'sucursal':_sucursal})

		if r_sucu and r_detalle==None:
			r_detalles=StockFicha.objects.filter(sucursal=r_sucu).distinct()


		ctx={'nivel':nivel,'info':info ,'stockItem':stockItem, 'b_sucursal':b_sucursal, 'b_detalle':b_detalle, 'r_sucus':r_sucus, 'r_detalles':r_detalles}

		return render_to_response('compras/stockFichasA.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet probado
@login_required(login_url='/')
def compras_compras_stocks_actualizar_recargas_view(request):
	nivel=Permiso(request.user,[0,1,5])
	if nivel != -1:

		b_sucursal=request.GET.get('sucursal','')
		r_sucu=None
		r_sucus=None
		p_max=0
		p_min=0
		stockItem=SaldoStockForm()
		info=""
		if b_sucursal:
			pass
		else:
			_usuario=Usuario.objects.get(user=request.user)
			_empleado=_usuario.empleado
			vSucural=VendedorSucursal.objects.get(empleado=_empleado)
			_sucursal=vSucural.sucursal
			b_sucursal=_sucursal.nombre
		if b_sucursal:
			try:
				r_sucu=Sucursal.objects.get(nombre=b_sucursal)
			except :
				qset=(Q(tipoSucursal__tipo__icontains=b_sucursal)|
				Q(nombre__icontains=b_sucursal)|
				Q(encargado__nombre__icontains=b_sucursal)|
				Q(noCelOfi__icontains=b_sucursal)|
				Q(direccion__icontains=b_sucursal))
				r_sucus=Sucursal.objects.filter(qset).distinct()
		try:
			stock=SaldoStock.objects.get(sucursal=r_sucu)
			p_max=stock.maximo
			p_min=stock.minimo
		except :
			pass

		stockItem=SaldoStockForm(initial={'sucursal':r_sucu, 'minimo':p_min, 'maximo':p_max})

		if 'actualizar' in request.POST:
			stockItem=SaldoStockForm(request.POST)
			if stockItem.is_valid():
				_sucursal=stockItem.cleaned_data['sucursal']
				_stockMin=stockItem.cleaned_data['minimo']
				_stockMax=stockItem.cleaned_data['maximo']
				try:
					with transaction.atomic():
						itemStock=SaldoStock.objects.get(sucursal=_sucursal)
						itemStock.minimo=_stockMin
						itemStock.maximo=_stockMax
						itemStock.save()
				except :
					stockItem.save()
				info = "Se ha Guardado correctamente."
				stockItem=SaldoStockForm()

		ctx={'nivel':nivel,'info':info,'stockItem':stockItem, 'b_sucursal':b_sucursal, 'r_sucus':r_sucus}

		return render_to_response('compras/stockSaldoA.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')
	

#yet probado
@login_required(login_url='/')
def compras_compras_stocks_todos_view(request):
	nivel=Permiso(request.user,[0,1,5])
	if nivel != -1:

		b_sucursal=request.GET.get('sucursal','')
		r_sucu=None
		r_sucus=None
		r_equipos=None
		r_expres=None
		r_accesorios=None
		r_fichas=None
		r_saldo=None
		if b_sucursal:
			pass
		else:
			_usuario=Usuario.objects.get(user=request.user)
			_empleado=_usuario.empleado
			vSucural=VendedorSucursal.objects.get(empleado=_empleado)
			_sucursal=vSucural.sucursal
			b_sucursal=_sucursal.nombre
		if b_sucursal:
			try:
				r_sucu=Sucursal.objects.get(nombre=b_sucursal)
				r_equipos=StockEquipo.objects.filter(sucursal=r_sucu).distinct()
				r_accesorios=StockAccesorio.objects.filter(sucursal=r_sucu).distinct()
				r_fichas=StockFicha.objects.filter(sucursal=r_sucu).distinct()
				r_expres=StockExpres.objects.filter(sucursal=r_sucu).distinct()
				r_saldo=SaldoStock.objects.filter(sucursal=r_sucu).distinct()



			except :
				qset=(Q(tipoSucursal__tipo__icontains=b_sucursal)|
				Q(nombre__icontains=b_sucursal)|
				Q(encargado__nombre__icontains=b_sucursal)|
				Q(noCelOfi__icontains=b_sucursal)|
				Q(direccion__icontains=b_sucursal))
				r_sucus=Sucursal.objects.filter(qset).distinct()


		ctx={'nivel':nivel,  'b_sucursal':b_sucursal,  'r_sucus':r_sucus, 'r_equipos':r_equipos, 'r_expres':r_expres,'r_accesorios':r_accesorios, 'r_fichas':r_fichas, 'r_saldo':r_saldo}

		return render_to_response('compras/stockTodos.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#listo - #yet -  probado
@login_required(login_url='/')
def compras_compras_clientes_subdistribuidor_view(request):
	nivel=Permiso(request.user,[0,1,5,6])
	if nivel != -1:
		
		form = addCliente()
		form2 = addSubdistribuidor()
		info = ""

		formU = updCliente()
		formU2 = updSubdistribuidor()
		mostrar = True
		if request.method == "GET":
			if request.GET.get('upd'):
				itemSeleccionado = request.GET.get('upd','')
				if itemSeleccionado:
					y = Subdistribuidor.objects.get(id = itemSeleccionado)
					x = ClienteFacturacion.objects.get(id = y.cliente.id )
					
					formU = updCliente({'key':itemSeleccionado,'rfc':x.rfc,'razonSocial':x.razonSocial,'direccion':x.direccion,'cp':x.cp,'colonia':x.colonia,'ciudad':x.ciudad})
					formU2 = updSubdistribuidor({'limCredito': y.limCredito,'edo':y.edo})
					info = ""

				ctx = {'mostrar':True, 'form':formU,'form2':formU2,'info':info,'myurl':'/compras/compras/clientes/subdistribuidor/' ,'nivel':nivel}
				return render_to_response('compras/myUpdClientes.html',ctx,context_instance=RequestContext(request))

		if 'actualizar' in request.POST:

			formU = updCliente(request.POST or None)
			formU2 = updSubdistribuidor(request.POST or None)
			
			if formU.is_valid() and formU2.is_valid():
				
				key 		= formU.cleaned_data['key']
				rfc 		= formU.cleaned_data['rfc']
				razonSocial = formU.cleaned_data['razonSocial']
				direccion 	= formU.cleaned_data['direccion']
				colonia 	= formU.cleaned_data['colonia']
				ciudad 		= formU.cleaned_data['ciudad']
				cp 			= formU.cleaned_data['cp']
				estado 		= formU.cleaned_data['estado']


				limCredito 	= formU2.cleaned_data['limCredito']
				edo 		= formU2.cleaned_data['edo']

				zzz = agregarCiudades(colonia,ciudad,estado,cp)
				
				txt=str(rfc).upper()

				re1='[A-Z]{3,4}-[0-9]{2}[0-1][0-9][0-3][0-9]-[A-Z0-9]?[A-Z0-9]?[0-9A-Z]?'

				rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
				m = rg.search(txt)
				grrr = ClienteFacturacion.objects.filter(rfc=rfc)
				if m and grrr.count() == 0:
					try:
						with transaction.atomic():
							b = Subdistribuidor.objects.get(id=key)
							b.limCredito = limCredito
							b.edo 		 = EstadoSubdistribuidor.objects.get(id=edo)
							b.save()

							a = ClienteFacturacion.objects.get(id= b.cliente.id)
							a.rfc 			= (rfc).upper()
							a.razonSocial 	= (razonSocial).title()
							a.direccion 	= (direccion).title()
							a.colonia 		= Colonia.objects.get(id=zzz[0])
							a.ciudad 		= Ciudad.objects.get(id=zzz[1])
							a.cp 			= CP.objects.get(id=zzz[2])
							a.estado 		= Estado.objects.get(id = estado)
							a.save()

							mostrar = False
							info ="Se ha Actualizado con Exito: " + a.razonSocial
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				elif m and grrr != 0:
					try:
						with transaction.atomic():
							b = Subdistribuidor.objects.get(id = key)
							b.limCredito = limCredito
							b.edo 		 = EstadoSubdistribuidor.objects.get(id=edo)
							b.save()
							
							a = ClienteFacturacion.objects.get(id= b.cliente.id)
							a.razonSocial 	= (razonSocial).title()
							a.direccion 	= (direccion).title()
							a.colonia 		= Colonia.objects.get(id=zzz[0])
							a.ciudad 		= Ciudad.objects.get(id=zzz[1])
							a.cp 			= CP.objects.get(id=zzz[2])
							a.estado 		= Estado.objects.get(id= estado)
							a.save()

							info ="Se ha Actualizado con Exito: " + b.cliente.razonSocial
							formU = updCliente()
							formU2 = updSubdistribuidor()
							mostrar = False
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
					
				else:
					formU = updCliente( request.POST)
					formU2 = updSubdistribuidor(request.POST)
					info ="Lo sentimos, el RFC que intenta dar tiene un formato erroneo."	

			else:
				formU = updCliente( request.POST)
				formU2 = updSubdistribuidor(request.POST)
				info ="Verifique la informacion, no se han registrado los datos"

		
			ctx = {'mostrar':mostrar ,'form':formU,'form2':formU2,'myurl':'/compras/compras/clientes/subdistribuidor/','mycli':'Subdistribuidor' ,'info':info,'nivel':nivel}
			return render_to_response('compras/myUpdClientes.html', ctx, context_instance=RequestContext(request))
		
		if 'guardar' in request.POST:

			form = addCliente(request.POST or None)
			form2 = addSubdistribuidor(request.POST or None)
			
			if form.is_valid() and form2.is_valid():
				
				rfc 		= (form.cleaned_data['rfc']).upper()
				razonSocial = form.cleaned_data['razonSocial']
				direccion 	= form.cleaned_data['direccion']
				colonia 	= form.cleaned_data['colonia']
				ciudad 		= form.cleaned_data['ciudad']
				cp 			= form.cleaned_data['cp']
				estado 		= form.cleaned_data['estado']


				limCredito 	= form2.cleaned_data['limCredito']
				edo 		= form2.cleaned_data['edo']

				_usuario 			= Usuario.objects.get(user=request.user)
			  	_empleado 			= _usuario.empleado
			  	vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
			  	mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
				
				zzz = agregarCiudades(colonia,ciudad,estado,cp)
								
				txt=str(rfc).upper()

				re1='[A-Z]{3,4}-[0-9]{2}[0-1][0-9][0-3][0-9]-[A-Z0-9]?[A-Z0-9]?[0-9A-Z]?'

				rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
				m = rg.search(txt)
				grrr = ClienteFacturacion.objects.filter(rfc=rfc)
				if m and grrr.count() == 0:
					try:
						with transaction.atomic():
							a = ClienteFacturacion()
							a.rfc 			= (rfc).upper()
							a.razonSocial 	= (razonSocial).title()
							a.direccion 	= (direccion).title()
							a.colonia 		= Colonia.objects.get(id=zzz[0])
							a.ciudad 		= Ciudad.objects.get(id=zzz[1])
							a.cp 			= CP.objects.get(id=zzz[2])
							a.estado 		= Estado.objects.get(id= estado)
							a.save()

							b = Subdistribuidor()
							b.cliente 	 = a
							b.limCredito = limCredito
							b.edo 		 = edo #EstadoSubdistribuidor.objects.get(estado__icontains=edo)
							b.save()
							info ="Se ha Guardado con Exito: " + a.razonSocial
							#limpiando el formulario
							form = addCliente()
							form2 = addSubdistribuidor()
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

				elif m and grrr != 0:
					try:
						with transaction.atomic():
							b = Subdistribuidor()
							b.cliente 	 = ClienteFacturacion.objects.get(rfc=rfc)
							b.limCredito = limCredito
							b.edo 		 = edo #EstadoSubdistribuidor.objects.get(estado__icontains=edo)
							b.save()

							info ="Se ha Guardado con Exito: " + b.cliente.razonSocial
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
					else:
						transaction.commit()#'''
					

				else:
					form = addCliente( request.POST)
					form2 = addSubdistribuidor(request.POST)
					info ="Lo sentimos, el RFC que intenta dar tiene un formato erroneo."	

			else:
				form = addCliente( request.POST)
				form2 = addSubdistribuidor(request.POST)
				info ="Verifique la informacion, no se han registrado los datos"

		
		ctx = {'form':form,'form2':form2,'myurl':'/compras/compras/clientes/subdistribuidor/','mycli':'Subdistribuidor' ,'info':info,'nivel':nivel}
		return render_to_response('compras/myAddCliente.html', ctx, context_instance=RequestContext(request))

		
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo - #yet probado
@login_required(login_url='/')
def compras_compras_clientes_mayorista_view(request):
	nivel=Permiso(request.user,[0,1,5,6])
	if nivel != -1:
		form = addCliente()
		form2 = addMayorista()
		info = ""
		cadena=""
		
		formU = updCliente()
		formU2 = updMayorista()
		mostrar = True
		if request.method == "GET":
			if request.GET.get('upd'):
				itemSeleccionado = request.GET.get('upd','')
				if itemSeleccionado:
					y = Mayorista.objects.get(id = itemSeleccionado)
					x = ClienteFacturacion.objects.get(id = y.cliente.id )
					
					formU = updCliente({'key':itemSeleccionado,'rfc':x.rfc,'razonSocial':x.razonSocial,'direccion':x.direccion,'cp':x.cp,'colonia':x.colonia,'ciudad':x.ciudad})
					formU2 = updMayorista({'descuentoFichas': y.descuentoFichas,'descuentoRecargas':y.descuentoRecargas})
					info = ""

					ctx = {'mostrar':True, 'form':formU,'form2':formU2,'info':info,'myurl':'/compras/compras/clientes/subdistribuidor/' ,'nivel':nivel}
					return render_to_response('compras/myUpdClientes.html',ctx,context_instance=RequestContext(request))

		if 'actualizar' in request.POST:
			formU = updCliente(request.POST or None)
			formU2 = updMayorista(request.POST or None)
			
			if formU.is_valid() and formU2.is_valid():
				key 		= formU.cleaned_data['key']
				rfc 		= formU.cleaned_data['rfc']
				razonSocial = formU.cleaned_data['razonSocial']
				direccion 	= formU.cleaned_data['direccion']
				colonia 	= formU.cleaned_data['colonia']
				ciudad 		= formU.cleaned_data['ciudad']
				cp 			= formU.cleaned_data['cp']
				estado 		= formU.cleaned_data['estado']


				descuentoFichas 	= formU2.cleaned_data['descuentoFichas']
				descuentoRecargas	= formU2.cleaned_data['descuentoRecargas']

				zzz = agregarCiudades(colonia,ciudad,estado,cp)
				
				txt=str(rfc).upper()
				re1='[A-Z]{3,4}-[0-9]{2}[0-1][0-9][0-3][0-9]-[A-Z0-9]?[A-Z0-9]?[0-9A-Z]?'

				rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
				m = rg.search(txt)
				grrr = ClienteFacturacion.objects.filter(rfc=rfc)
				if m and grrr.count() == 0:
					try:
						with transaction.atomic():
							b = Mayorista.objects.get(id=key)
							b.descuentoFichas = descuentoFichas
							b.descuentoRecargas = descuentoRecargas
							b.save()

							a = ClienteFacturacion.objects.get(id= b.cliente.id)
							a.rfc 			= (rfc).upper()
							a.razonSocial 	= (razonSocial).title()
							a.direccion 	= (direccion).title()
							a.colonia 		= Colonia.objects.get(id=zzz[0])
							a.ciudad 		= Ciudad.objects.get(id=zzz[1])
							a.cp 			= CP.objects.get(id=zzz[2])
							a.estado 		= Estado.objects.get(id= estado)
							a.save()

							mostrar = False
							info ="Se ha Actualizado con Exito: " + a.razonSocial+" RFC: "+ a.rfc
					except :
						info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."
				elif m and grrr != 0:
					try:
						with transaction.atomic():
							b = Mayorista.objects.get(id=key)
							b.descuentoFichas = descuentoFichas
							b.descuentoRecargas = descuentoRecargas
							b.save()
							
							a = ClienteFacturacion.objects.get(id= b.cliente.id)
							a.razonSocial 	= (razonSocial).title()
							a.direccion 	= (direccion).title()
							a.colonia 		= Colonia.objects.get(colonia__icontains=colonia.title())
							a.ciudad 		= Ciudad.objects.get(ciudad__icontains=ciudad.title())
							a.cp 			= CP.objects.get(cp__icontains=cp)
							a.estado 		= Estado.objects.get(id= estado)
							a.save()

							info ="Se ha Actualizado con Exito: " + b.cliente.razonSocial+" RFC: "+ a.rfc

							mostrar = False
					except :
						info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada." 
				else:
					formU = updCliente( request.POST)
					formU2 = updMayorista(request.POST)
					info ="Lo sentimos, el RFC que intenta dar tiene un formato erroneo."	

			else:
				formU = updCliente( request.POST)
				formU2 = updMayorista(request.POST)
				info ="Verifique la informacion, no se han registrado los datos"

		
			ctx = {'mostrar':mostrar ,'form':formU,'form2':formU2,'myurl':'/compras/compras/clientes/mayorista/','mycli':'Mayorista' ,'info':info,'nivel':nivel}
			return render_to_response('compras/myUpdClientes.html', ctx, context_instance=RequestContext(request))
		
		if 'guardar' in request.POST:
			form = addCliente(request.POST or None)
			form2 = addMayorista(request.POST or None)
			
			if form.is_valid() and form2.is_valid():
				
				rfc 		= form.cleaned_data['rfc']
				razonSocial = form.cleaned_data['razonSocial']
				direccion 	= form.cleaned_data['direccion']
				colonia 	= form.cleaned_data['colonia']
				ciudad 		= form.cleaned_data['ciudad']
				cp 			= form.cleaned_data['cp']
				estado 		= form.cleaned_data['estado']


				descuentoFichas = form2.cleaned_data['descuentoFichas']
				descuentoRecargas = form2.cleaned_data['descuentoRecargas']
				conrfc = form2.cleaned_data['conrfc']

				_usuario 			= Usuario.objects.get(user=request.user)
			  	_empleado 			= _usuario.empleado
			  	vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
			  	mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

				txt=str(rfc).upper()
				re1='[A-Z]{3,4}-[0-9]{2}[0-1][0-9][0-3][0-9]-[A-Z0-9]?[A-Z0-9]?[0-9A-Z]?'
				zzz = agregarCiudades(colonia,ciudad,estado,cp)

				rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
				m = rg.search(txt)
				grrr = ClienteFacturacion.objects.filter(rfc=rfc)
				tama = Mayorista.objects.filter(cliente__rfc=rfc)
				if conrfc == False:
					try:
						with transaction.atomic():
							provisional = nvoMayorista(razonSocial)

							a = ClienteFacturacion()
							a.rfc 			= provisional
							a.razonSocial 	= (razonSocial).title()
							a.direccion 	= (direccion).title()
							a.colonia 		= Colonia.objects.get(id=zzz[0])
							a.ciudad 		= Ciudad.objects.get(id=zzz[1])
							a.cp 			= CP.objects.get(id=zzz[2])
							a.estado 		= Estado.objects.get(id= estado)
							a.save()

							b =  Mayorista()
							b.cliente 		= a
							b.descuentoFichas = descuentoFichas
							b.descuentoRecargas = descuentoRecargas
							b.save()
							info ="Se genero una clave RFC provisional. Se ha Guardado con Exito: " + a.razonSocial
							form = addCliente()
							form2 = addMayorista()
					except :
						info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."
						
				elif m and grrr.count() == 0:
					try:
						with transaction.atomic():
							a = ClienteFacturacion()
							a.rfc 			= (rfc).upper()
							a.razonSocial 	= (razonSocial).title()
							a.direccion 	= (direccion).title()
							a.colonia 		= Colonia.objects.get(id=zzz[0])
							a.ciudad 		= Ciudad.objects.get(id=zzz[1])
							a.cp 			= CP.objects.get(id=zzz[2])
							a.estado 		= Estado.objects.get(id= estado)
							a.save()

							b =  Mayorista()
							b.cliente 		= a
							b.descuentoFichas = descuentoFichas
							b.descuentoRecargas = descuentoRecargas
							b.save()
							info ="Se ha Guardado con Exito: " + a.razonSocial
							form = addCliente()
							form2 = addMayorista()
					except :
						info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

				elif m and grrr.count() != 0 and tama.count() == 0:
					try:
						with transaction.atomic():
							b =  Mayorista()
							b.cliente 	 = ClienteFacturacion.objects.get(rfc=rfc)
							b.descuentoFichas = descuentoFichas
							b.descuentoRecargas = descuentoRecargas
							b.save()

							info ="Se ha Guardado con Exito: " + b.cliente.razonSocial
							form = addCliente()
							form2 = addMayorista()
					except :
						info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

				else:
					form = addCliente( request.POST)
					form2 = addMayorista(request.POST)
					info ="Lo sentimos, el RFC que intenta dar tiene un formato erroneo. o ya esta asociado a un mayorista."	

			else:
				form = addCliente( request.POST)
				form2 = addMayorista(request.POST)
				info ="Verifique la informacion, no se han registrado los datos"

		ctx = {'form':form,'form2':form2,'myurl':'/compras/compras/clientes/mayorista/','mycli':'Mayorista' ,'info':info,'nivel':nivel}
		return render_to_response('compras/myAddCliente.html', ctx, context_instance=RequestContext(request))
		#'''
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#listo - #yet probado
@login_required(login_url='/')
def compras_compras_clientes_catalogos_view(request):
	nivel=Permiso(request.user,[0,1,5,6])
	if nivel != -1:

		query  = request.GET.get('q','')
		pag1=request.GET.get('pagSub','')
		pag2=request.GET.get('pagMay','')

		subs = Subdistribuidor.objects.all()
		mays = Mayorista.objects.all()

		if query:
			qset=(Q(cliente__rfc__icontains=query) |
			 Q(cliente__razonSocial__icontains=query) | 
			 Q(cliente__direccion__icontains=query))
			subs = Subdistribuidor.objects.filter(qset)
			mays = Mayorista.objects.filter(qset)
		
		
		paginator1 = Paginator(subs, 25)
		paginator2 = Paginator(mays, 25)
		nSub=len(subs)
		nMays=len(mays)
		pSubdist=None
		pMays=None
		
		try:
			pSubdist = paginator1.page(pag1)
			pMays = paginator2.page(pag2)
		except PageNotAnInteger:
			pSubdist = paginator1.page(1)
			pMays = paginator2.page(1)
		except EmptyPage:
			pSubdist = paginator1.page(paginator1.num_pages)
			pMays = paginator2.page(paginator2.num_pages)
		

		ctx={'Subdist':pSubdist,'query':query,'Mayorista':pMays,'nivel':nivel}
		return render_to_response('compras/myCatalogoClientes.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#------------------------
@login_required(login_url='/')
def compras_proveedor_nuevo_view(request):
	nivel=Permiso(request.user,[0,1,5,6])
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
				provee = fProveedor.save()
				fProveedor = ProveedorForm()
				mensaje = 'Proveedor %s, Agregado/Modificado Correctamente'%(provee)
				provee=None
		
		ctx={'nivel':nivel, 'fProveedor':fProveedor, 'mensaje':mensaje, 'provee':provee}
		return render_to_response('compras/proveedorAdd.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')



@login_required(login_url='/')
def compras_proveedor_catalogo_view(request):
	nivel=Permiso(request.user,[0,1,5,6])
	if nivel != -1:
		mensaje=''
		q=request.GET.get('filtro','')
		pagina=request.GET.get('pagina','')

		buscador=Busqueda(q)
		proveedores=ReporteProveedores (pagina, q, 'Reporte de Proveedores')
		
		ctx={'nivel':nivel, 'buscador':buscador, 'proveedores':proveedores}
		return render_to_response('compras/proveedoresReporte.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')



		
#listo - #yet ticket probado
@login_required(login_url='/')
def compras_compras_credito_abonar_view(request):
	nivel=Permiso(request.user,[0,1,5,6])
	if nivel != -1:
		
		formC = addAbonoCredito()
		info =""
		buscar = True
		show= True
		mostrarf = False
		mostrar = False
		
		query  = request.GET.get('q','')
		pag1=request.GET.get('pagSub','')
		subs = Subdistribuidor.objects.all()

		query2  = request.GET.get('q2','')
		subcli  = request.GET.get('noSub','')
		pag2=request.GET.get('pagCred','')
		creds=None
		myCS=None
		if subcli:
			creds = Credito.objects.filter(subdist__id = subcli)
			myCS =Subdistribuidor.objects.get(id = subcli)
		else:
			creds = Credito.objects.all()

		if query:
			qset=(Q(cliente__rfc__icontains=query) |
			 Q(cliente__razonSocial__icontains=query) | 
			 Q(cliente__direccion__icontains=query))
			subs = Subdistribuidor.objects.filter(qset)
		
		if query2:
			qset=(Q(folioc__icontains=query2))
			creds = Credito.objects.filter(qset,subdist__id=subcli)

		paginator1 = Paginator(subs, 25)
		nSub=len(subs)
		pSubdist=None
		
		paginator2 = Paginator(creds, 25)
		nCreds=len(creds)
		pCreds=None
		
		try:
			pSubdist = paginator1.page(pag1)
			pCreds = paginator2.page(pag2)
		except PageNotAnInteger:
			pSubdist = paginator1.page(1)
			pCreds = paginator2.page(1)
		except EmptyPage:
			pSubdist = paginator1.page(paginator1.num_pages)
			pCreds = paginator2.page(paginator2.num_pages)

		if request.method == "GET":

			if request.GET.get('q'):
				
				ctx = {'Subdist':pSubdist,'info':info, 'nivel':nivel}
				return render_to_response('compras/myAbonoSubdistribuidor.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('q2'):
				
				buscar = True
				show = True
				mostrarf = False
				mostrar = False

				ctx = {'sub':myCS,'query2':query2,'Creditos':pCreds,'buscar':buscar,'show':show,'mostrarf':mostrarf,'mostrar':mostrar,'info':info, 'nivel':nivel}
				return render_to_response('compras/myCreditoAbonar.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('cred'):
				
				buscar = True
				show = True
				mostrarf = False
				mostrar = False
				myCS =Subdistribuidor.objects.get(id = request.GET.get('cred', ''))

				ctx = {'sub':myCS,'query2':query2,'Creditos':pCreds,'buscar':buscar,'show':show,'mostrarf':mostrarf,'mostrar':mostrar,'info':info, 'nivel':nivel}
				return render_to_response('compras/myCreditoAbonar.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('abonar'):
				query = request.GET.get('abonar', '')
				if query:
					ctas = Credito.objects.get(id = query)
					chist = HistorialSubdistribuidor.objects.filter(credito__id=ctas.id)
			
					suma = 0
					for x in chist:
						suma = suma + x.abono

					resta = ctas.totalvta - suma

					formC = addAbonoCredito({'key':ctas.id,'subdistribuidor':ctas.subdist.cliente.razonSocial,
						'credito':ctas.folioc,'fxCredito':ctas.fxCredito,'totalvta':ctas.totalvta,'anticipos': suma,'faltante':resta })

					buscar = False
					show= False
					mostrarf = True
					mostrar = True

				ctx = {'show':show,'buscar':buscar,'mostrar':mostrar,'mostrarf':mostrarf,'formC':formC,'info':info, 'nivel':nivel}
				return render_to_response('compras/myCreditoAbonar.html',ctx,context_instance=RequestContext(request))

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
					return render_to_response('compras/ticket.html',ctx,context_instance=RequestContext(request))

		if request.method == "POST":
			
			formC = addAbonoCredito(request.POST)
			today = datetime.now() #fecha actual
			dateFormat = today.strftime("%Y-%m-%d") # fecha con formato
			
			if formC.is_valid():
				key = formC.cleaned_data['key']
				abonar 	= formC.cleaned_data['abonar']
				ctas = Credito.objects.get(id = key)
				chist = HistorialSubdistribuidor.objects.filter(credito__id=key)
				mfolioVenta = None
				suma = 0
				for x in chist:
					suma = suma + x.abono

				resta = ctas.totalvta - suma
				total = resta - abonar

				if abonar > 0 and abonar <= resta:
					try:
						with transaction.atomic():
							_usuario 			= Usuario.objects.get(user=request.user)
					  		_empleado 			= _usuario.empleado
					  		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
					  		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

							v = Venta()
							v.folioVenta = nuevoFolio('C',request.user,None)  #generar folio de venta
							v.sucursal 	= mysucursal
							v.usuario 	= request.user
							v.total 	= abonar
							v.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
							v.estado 	= EstadoVenta.objects.get(estado='Pagada')
							v.save()

							if total == 0:
								b = Credito.objects.get(id = key)
								b.edo = EstadoCredito.objects.get(estado='Pagado')
								b.save()

								a =  HistorialSubdistribuidor()
								a.credito = b
								a.abono = abonar
								a.save()
								
								dv = Anticipo()
								dv.folioVenta 		= v
								dv.tipoAnticipo 	= 'Liquidacion de Credito '+b.folioc
								dv.monto 			= abonar
								dv.save()
							else:
								b = Credito.objects.get(id = key)
								fx1 = (b.fxCredito).date()
								fx2 = datetime.now().date() 
								diff = fx2 - fx1
								diff = b.plazo - diff.days
								if b.edo.estado == 'Cobrar':
									b.edo = EstadoCredito.objects.get(estado='Cobrar')
								elif diff <= 0:
									b.edo = EstadoCredito.objects.get(estado='Cobrar')
								else:
									b.edo = EstadoCredito.objects.get(estado='Adeudo')
								b.save()

								a =  HistorialSubdistribuidor()
								a.credito = b
								a.abono = abonar
								a.save()

								dv = Anticipo()
								dv.folioVenta 		= v
								dv.tipoAnticipo 	= 'Abono de Credito '+b.folioc
								dv.monto 			= abonar
								dv.save()

							info = "Se genero una venta por el abono registrado. Venta con Folio: "+ str(v.folioVenta)
							mostrarf= False
							mostrar = False
							show=False
							buscar = True
							mfolioVenta = v.folioVenta
					except :
						info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

				else:
					info = "El abono debe ser mayor o igual al faltante del total de la reparacion"
					
					formC = addAbonoCredito( request.POST)
					mostrar = True
					buscar = False
					mostrarf = True
					show= False

				ctx = {'folioVenta':mfolioVenta ,'sub':myCS,'query2':query2,'Creditos':pCreds,'show':show,'buscar':buscar,'mostrar':mostrar,'mostrarf':mostrarf,'formC':formC,'info':info, 'nivel':nivel}
				return render_to_response('compras/myCreditoAbonar.html',ctx,context_instance=RequestContext(request))

			else:
				info = "Verifique sus datos, actualizacion no realizada"
				formC = addAbonoReparacion( request.POST)
				mostrarf = True
				buscar = False
				boton = True
				show = False

			ctx = {'show':show,'buscar':buscar,'mostrar':mostrar,'mostrarf':mostrarf,'formC':formC,'info':info, 'nivel':nivel}
			return render_to_response('compras/myCreditoAbonar.html',ctx,context_instance=RequestContext(request))


		ctx = {'Subdist':pSubdist,'info':info, 'nivel':nivel}
		return render_to_response('compras/myAbonoSubdistribuidor.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#listo - #yet probado
@login_required(login_url='/')
def compras_compras_credito_vencidos_view(request):
	nivel=Permiso(request.user,[0,1,5,6])
	if nivel != -1:
		
		info =""
		buscar = True
		show= True
		mostrarf = False
		
		query2  = request.GET.get('q2','')
		pag2=request.GET.get('pagCred','')
		
		creds= Credito.objects.filter(edo__estado__icontains='Cobrar')
		
		if query2:
			qset=(Q(folioc__icontains=query2))
			creds = Credito.objects.filter(qset,edo__estado__icontains='Cobrar')

		paginator2 = Paginator(creds, 25)
		nCreds=len(creds)
		pCreds=None
		
		try:
			pCreds = paginator2.page(pag2)
		except PageNotAnInteger:
			pCreds = paginator2.page(1)
		except EmptyPage:
			pCreds = paginator2.page(paginator2.num_pages)

		if request.method == "GET":

			if request.GET.get('q2'):
				buscar = True
				show= True
				mostrarf = False
				
				ctx = {'query2':query2,'Creditos':pCreds,'info':info,'buscar':buscar,'show':show,'mostrarf':mostrarf ,'nivel':nivel}
				return render_to_response('compras/myCreditoVencido.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('subdist'):
				buscar = False
				show= False
				mostrarf = True
				
				myCS =Subdistribuidor.objects.get(id = Credito.objects.get(id = request.GET.get('subdist', '')).subdist.id )
				cred = Credito.objects.get(id = request.GET.get('subdist',''))
				ncs = Credito.objects.filter(subdist__id= myCS.id )
				sab = HistorialSubdistribuidor.objects.filter(credito__id=cred.id)

				fx1 = (cred.fxCredito).date()
				fx2 = datetime.now().date() 
				diff = fx2 - fx1

				diff = cred.plazo - diff.days

				utilizado = 0
				for x in ncs:
					utilizado = utilizado + x.totalvta

				abonado = 0
				for x in sab:
					abonado = abonado + x.abono

				resta = cred.totalvta - abonado



				ctx = {'dias':diff ,'utilizado':utilizado,'abonado':abonado,'resta':resta,'sub':myCS,'Cred':cred,'info':info,'buscar':buscar,'show':show,'mostrarf':mostrarf , 'nivel':nivel}
				return render_to_response('compras/myCreditoVencido.html',ctx,context_instance=RequestContext(request))



		ctx = {'Creditos':pCreds,'info':info,'buscar':buscar,'show':show, 'nivel':nivel}
		return render_to_response('compras/myCreditoVencido.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#listo - #yet probado
@login_required(login_url='/')
def compras_compras_credito_historial_view(request):
	nivel=Permiso(request.user,[0,1,5,6])
	if nivel != -1:
		
		info =""
		buscar = True
		show= True
		mostrarf = False
		
		query  = request.GET.get('q','')
		pag1=request.GET.get('pagSub','')
		subs = Subdistribuidor.objects.all()

		query2  = request.GET.get('q2','')
		subcli  = request.GET.get('noSub','')
		pag2=request.GET.get('pagCred','')
		creds=None
		myCS=None
		if subcli:
			creds = Credito.objects.filter(subdist__id = subcli)
			myCS =Subdistribuidor.objects.get(id = subcli)
		else:
			creds = Credito.objects.all()

		if query:
			qset=(Q(cliente__rfc__icontains=query) |
			 Q(cliente__razonSocial__icontains=query) | 
			 Q(cliente__direccion__icontains=query))
			subs = Subdistribuidor.objects.filter(qset)
		
		if query2:
			qset=(Q(folioc__icontains=query2))
			creds = Credito.objects.filter(qset,subdist__id=subcli)

		paginator1 = Paginator(subs, 25)
		nSub=len(subs)
		pSubdist=None
		
		paginator2 = Paginator(creds, 25)
		nCreds=len(creds)
		pCreds=None
		
		try:
			pSubdist = paginator1.page(pag1)
			pCreds = paginator2.page(pag2)
		except PageNotAnInteger:
			pSubdist = paginator1.page(1)
			pCreds = paginator2.page(1)
		except EmptyPage:
			pSubdist = paginator1.page(paginator1.num_pages)
			pCreds = paginator2.page(paginator2.num_pages)

		if request.method == "GET":

			if request.GET.get('q'):
				
				ctx = {'Subdist':pSubdist,'query':query,'info':info, 'nivel':nivel}
				return render_to_response('compras/mySearchSubdistribuidor.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('q2'):
				buscar = True
				show= True
				mostrarf = False
				
				ctx = {'sub':myCS,'query2':query2,'Creditos':pCreds,'info':info,'buscar':buscar,'show':show,'mostrarf':mostrarf ,'nivel':nivel}
				return render_to_response('compras/mySearchCredito.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('cred'):
				buscar = True
				show= True
				mostrarf = False
				
				myCS =Subdistribuidor.objects.get(id = request.GET.get('cred', ''))
				

				ctx = {'sub':myCS,'query2':query2,'Creditos':pCreds,'info':info,'buscar':buscar,'show':show,'mostrarf':mostrarf , 'nivel':nivel}
				return render_to_response('compras/mySearchCredito.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('hist'):
				buscar = False
				show= False
				mostrarf = True
				historial = HistorialSubdistribuidor.objects.filter(credito__id = request.GET.get('hist',''))
				myCS =Subdistribuidor.objects.get(id = Credito.objects.get(id = request.GET.get('hist', '')).subdist.id )
				cred = Credito.objects.get(id= request.GET.get('hist', ''))

				ctx = {'Historial':historial,'cred':cred ,'sub':myCS,'query2':query2,'Creditos':pCreds,'info':info,'buscar':buscar,'show':show,'mostrarf':mostrarf , 'nivel':nivel}
				return render_to_response('compras/mySearchCredito.html',ctx,context_instance=RequestContext(request))


		ctx = {'Subdist':pSubdist,'info':info, 'nivel':nivel}
		return render_to_response('compras/mySearchSubdistribuidor.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#yet probado
@login_required(login_url='/')
def compras_almacen_registrar_fact_view(request):
	#Permisos de acceso
	nivel=Permiso(request.user,[0,1,5,6])
	if nivel != -1:
		#datos de busquedas y consultas
		b_folio=request.GET.get('q','')
		b_factura=None
		b_facturas=None
		info = "" 
		form = addFacturaForm({'fxFactura':datetime.now().date()})

		if b_folio:
			#obtencion de la factura
			try:
				b_factura=Factura.objects.get(folio=b_folio)
				#form = addFacturaForm(initial={'conFactura': b_factura.conFactura, 'documento': b_factura.documento, 'folio': b_factura.folio, 'proveedor': b_factura.proveedor, 'fxFactura': b_factura.fxFactura, 'formaPago': b_factura.formaPago, 'subTotal': b_factura.subTotal, 'descuento': b_factura.descuento, 'iva': b_factura.iva, 'montoTotal': b_factura.montoTotal, 'tipoFactura': b_factura.  'observacion': b_factura.observacion})
			except :
				b_facturas=ListaFacturas(b_folio)
		#datos del formulario agregar
		if 'guardar' in request.POST:
			form = addFacturaForm(request.POST or None)
			if form.is_valid():
				try:
					a = Factura()
					a.conFactura 	= form.cleaned_data['conFactura']
					a.documento 	= form.cleaned_data['documento']
					a.folio 		= form.cleaned_data['folio']
					a.proveedor 	= form.cleaned_data['proveedor']
					a.fxFactura 	= form.cleaned_data['fxFactura']
					a.formaPago 	= form.cleaned_data['formaPago']
					a.subTotal 		= form.cleaned_data['subTotal']
					a.descuento 	= form.cleaned_data['descuento']
					a.iva 			= form.cleaned_data['iva']
					a.montoTotal 	= form.cleaned_data['montoTotal']
					#a.tipoFactura 	= form.cleaned_data['tipoFactura']
					a.observacion 	= form.cleaned_data['observacion']
					a.usuario 		= request.user
					a.save()
					return HttpResponseRedirect('/compras/almacen/equipos/?factura=%s'%(a.folio))
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."
					form = addFacturaForm({'fxFactura':datetime.now().date()})
			else:
				info = "La informacion contiene errores, favor de verificar."
				form = addFacturaForm(request.POST or None)

		ctx = {'nivel':nivel,'b_folio':b_folio ,'form':form, 'informacion':info, 'b_factura':b_factura, 
		'b_facturas':b_facturas}
		return render_to_response('compras/addFacturaCompras.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')
	

#yet probado
@login_required(login_url='/')
def compras_almacen_equipos_view(request):
	nivel=Permiso(request.user,[0,1,5,6])
	if nivel != -1:

		mensaje = ''
		glovales=''
		r_factura=None
		r_detalle=None

		try:
			sucursal=Sucursal.objects.get(nombre='Almacen Central')
		except :
			sucursal=None

		b_factura=request.GET.get('factura','')
		if not b_factura:
			b_factura=request.POST.get('factura','')
		if b_factura:
			try:
				r_factura=Factura.objects.get(folio=b_factura)
			except :
				pass

		b_detalles=request.GET.get('detalles','')
		if not b_detalles:
			b_detalles=request.POST.get('detalles','')
		if b_detalles:
			try:
				r_detalle=DetallesEquipo.objects.get(id=b_detalles)
			except :
				pass

		try:
			estatus=Estatus.objects.get(estatus="Existente")
		except :
			estatus=Estatus()
			estatus.estatus="Existente"
			estatus.save()

		f_equipo=addEquipoForm(initial={'detallesEquipo': r_detalle, 'factura': r_factura})

		if 'equipos' in request.POST:
			f_equipo = addEquipoForm(request.POST)

			if f_equipo.is_valid():
				_factura=f_equipo.cleaned_data['factura']
				_detalles=f_equipo.cleaned_data['detallesEquipo']
				_importe=f_equipo.cleaned_data['importeFactura']
				_accesorios=f_equipo.cleaned_data['accesorioEqu']

				for x in range(20):
					imei=request.POST.get('%s-imei'%(x),'')
					icc=request.POST.get('%s-icc'%(x),'')
					if not icc:
						icc=0
					if imei:
						if Equipo.objects.filter(imei=imei).exists():
							mensaje='%sYa existe un equipos con el imei: %s<br>'%(mensaje,imei)# un equipo con el imei  ya existe
						else:
							if Expres.objects.filter(icc=icc).exists():
								mensaje='%sYa existe un Expres con el icc: %s, el imei %s y el icc%s no se Registraron<br>'%(mensaje,icc, imei, icc)#'%sEquipo %s no se pudo agregar, porque el expres con la icc %s ya se encuentra registrada. - - - '%(errores,f_equipos[0].cleaned_data['imei'],_icc)
							else:
								try:
									_equipo=Equipo()
									_equipo.factura 	= _factura
									_equipo.imei 		= Decimal(imei)
									_equipo.detallesEquipo = _detalles
									_equipo.accesorioEqu = _accesorios
									_equipo.estatus 	= estatus
									_equipo.importeFactura = _importe
									_equipo.sucursal 	= sucursal
									with transaction.atomic():
										_equipo.save()
									almacenItems(0,_equipo,sucursal,None)
									mensaje='%sSe registro con exito el equipo %s <br>'%(mensaje, _equipo)
									if icc:
										try:
											_express=Expres()
											_express.factura 	= _factura
											_express.icc 		= Decimal(icc)
											_express.sucursal 	= sucursal
											#aclarar esta parte con Fatima
											try:
												detExp=DetallesExpres.objects.get(descripcion='Equipo')
											except :
												detExp=DetallesExpres()
												detExp.descripcion='Equipo'
												try:
													ticc=TipoIcc.objects.get(tipoIcc='Kit')
												except :
													ticc=TipoIcc()
													ticc.tipoIcc='Kit'
													with transaction.atomic():
														ticc.save()
												detExp.tipoIcc=ticc
												try:
													tgarn=TiempoGarantia.objects.get(dias=0)
												except :
													tgarn.TiempoGarantia()
													tgarn.dias=0
													with transaction.atomic():
														tgarn.save()
												detExp.tiempoGarantia=tgarn
												detExp.precioMayoreo=0
												detExp.precioMenudeo=0
												with transaction.atomic():
													detExp.save()
											_express.detallesExpres = detExp
											_express.estatus 		= estatus
											_express.importeFactura = 0
											with transaction.atomic():
												_express.save()
											_equipo.icc = _express.icc
											with transaction.atomic():
												_equipo.save()
											almacenItems(1,_express,sucursal,None)
											mensaje='%sTambien se Registro el Expres %s  ligado a %s<br>'%(mensaje,_express, _equipo)
										except :
											mensaje='%sNo se Registro icc: %s, verificar formato. El %s se registro sin la expres<br>'%(mensaje,icc, _equipo)
											#el icc no se pudo guadar, verifique sus datos, el equipo con imei se a guadado sin su express
								except :
									mensaje='%sNo se Registro imei: %s, ni el icc %s, verificar formato<br>'%(mensaje, imei, icc)
									#el equipo con imei no se puede guardar, verifique los datos'''

				b_factura=_factura.folio
				f_equipo=addEquipoForm(initial={'detallesEquipo': _detalles, 'factura': _factura, 'importeFactura':_importe})
			else:
				glovales='uno o mas campos es incorrecto. Verifique su informacion'


		ctx = {'glovales':glovales , 'mensaje':mensaje , 'b_factura':b_factura , 'f_equipo':f_equipo }
		return render_to_response('compras/addEquipoFactura.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#test modf - yay ya quedo updtd 
@login_required(login_url='/')
def compras_almacen_detalle_equipos_view(request):
	nivel=Permiso(request.user,[0,1,5,6])
	if nivel != -1:
		info = ""
		folio=None
		
		f_detalles=addDetallesEquipoForm({'folio':nvo_folio_detalles("EQ")})
		f_marca=None #MarcaForm(prefix='formulario')
		b_marca=None
		if 'detalles' in request.POST:
			f_detalles=addDetallesEquipoForm(request.POST or None)
			if f_detalles.is_valid():
				try:
					with transaction.atomic():
						f_detalles.save()
						info = 'La información se ha Guardado correctamente.'
						f_detalles=addDetallesEquipoForm({'folio':nvo_folio_detalles("EQ")})
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."
			else:
				f_detalles=addDetallesEquipoForm(request.POST)
				info = 'La información no fue correctamente enviada'
		
		if 'gmarca' in request.POST:
			f_marca=MarcaForm(request.POST,prefix='formulario')
			_marca=Marca()
			if f_marca.is_valid():
				try:
					with transaction.atomic():
						_marca=f_marca.save()
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."
			else:
				f_detalles=addDetallesEquipoForm(request.POST)
				info = 'La información no fue correctamente enviada'

			f_detalles=addDetallesEquipoForm(initial={'marca': _marca})
			f_marca=None
		
		if 'addmarca' in request.POST:
			f_detalles=addDetallesEquipoForm(request.POST)
			f_marca=MarcaForm(prefix='formulario')
		
		ctx = { 'nivel':nivel, 'informacion':info , 'f_detalles':f_detalles , 'f_marca':f_marca}
		return render_to_response('compras/addEquipoDetalle.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')



#yet probado
@login_required(login_url='/')
def compras_almacen_accesorios_view(request):
	nivel=Permiso(request.user,[0,1,5,6])
	if nivel != -1:
		info = ""
		b_factura=request.GET.get('factura','')
		b_detalles=request.GET.get('detalles','')
		b_marca=None
		r_factura=None
		r_detalle=None
		r_facturas=None
		r_detalles=None
		glovales=None
		guardados=''
		agregados=None

		estatus=None
		try:
			estatus=EstatusAccesorio.objects.get(estatus="Existente")
		except :
			estatus=EstatusAccesorio()
			estatus.estatus="Existente"
			estatus.save()


		sucursal=None
		try:
			sucursal=Sucursal.objects.get(nombre='Almacen Central')
		except :
			pass

		f_accesorios=[addAccesorioForm(),addAccesorioForm(),addAccesorioForm(),addAccesorioForm(),addAccesorioForm(),addAccesorioForm(),addAccesorioForm(),addAccesorioForm(),addAccesorioForm(),addAccesorioForm()]
		f_detalles=None
		f_marca=None
		f_secc =None
		if b_factura:
			try:
				r_factura=Factura.objects.get(folio=b_factura)
				agregados=ListaItems(2,None,Q(factura=r_factura),None)
			except:
				r_facturas=ListaFacturas(b_factura)
		if b_detalles:
			try:
				r_detalle=DetallesAccesorio.objects.get(id=b_detalles)		
			except:
				qset=(Q(marca__marca__icontains=b_detalles)|
				Q(descripcion__icontains=b_detalles)|
				Q(seccion__seccion__icontains=b_detalles))
				r_detalles=DetallesAccesorio.objects.filter(qset).distinct()

		x=0
		while x<len(f_accesorios):
			f_accesorios[x]=addAccesorioForm(prefix=x, initial={'detallesAccesorio': r_detalle, 'factura': r_factura})
			x+=1

		if 'accesorios' in request.POST:
			x=0
			while x<len(f_accesorios):
				f_accesorios[x] = addAccesorioForm(request.POST, prefix=x)
				x+=1
			if f_accesorios[0].is_valid():
				_factura=f_accesorios[0].cleaned_data['factura']
				_detalles=f_accesorios[0].cleaned_data['detallesAccesorio']
				_importe=f_accesorios[0].cleaned_data['precioFact']
				if _factura and _detalles and _importe:
					try:
						with transaction.atomic():
							_accesorio=Accesorio()
							_accesorio.factura 	= _factura
							_accesorio.codigoBarras 		= f_accesorios[0].cleaned_data['codigoBarras']
							_accesorio.detallesAccesorio = _detalles
							_accesorio.estatusAccesorio 	= estatus
							_accesorio.precioFact = _importe
							_accesorio.sucursal 	= sucursal
							_accesorio.save()
							b_factura=_factura.folio
							almacenItems(2,_accesorio,sucursal,None)
							guardados='%s %s.'%(guardados,_accesorio.codigoBarras)
							f_accesorios[0]=addAccesorioForm(prefix=0, initial={'detallesEquipo': _detalles, 'factura': _factura, 'importeFactura':_importe})
								
							x=1
							while x<len(f_accesorios):
								if f_accesorios[x].is_valid():
									_accesorio=Accesorio()
									_accesorio.factura 	= _factura
									_accesorio.codigoBarras = f_accesorios[x].cleaned_data['codigoBarras']
									_accesorio.detallesAccesorio = _detalles
									_accesorio.estatusAccesorio 	= estatus
									_accesorio.precioFact = _importe
									_accesorio.sucursal 	= sucursal
									_accesorio.save()
									almacenItems(2,_accesorio,sucursal,None)
									guardados='%s %s.'%(guardados,_accesorio.codigoBarras)
									f_accesorios[x]=addAccesorioForm(prefix=x)
								x+=1
							agregados=ListaItems(2,None,Q(factura=_factura),None)
					except :
						info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."
				else:
					glovales='Campos Obligatorios'
			else:
				pass


		elif 'detalles' in request.POST:
			f_detalles=addDetallesAccesorioForm(request.POST)
			if f_detalles.is_valid():
				f_detalles.save()
				f_detalles=None

		elif 'adddetalles' in request.POST:
			f_detalles=addDetallesAccesorioForm()

		elif 'gmarca' in request.POST:
			f_marca=MarcaAccesorioForm(request.POST,prefix='formulario')
			_marca=MarcaAccesorio()
			if f_marca.is_valid():
				_marca=f_marca.save()

			f_detalles=addDetallesAccesorioForm(initial={'marca': _marca})
			f_marca=None
		
		elif 'gsecc' in request.POST:
			f_secc=addSecciones(request.POST,prefix='formulario2')
			_secc =Secciones()
			if f_secc.is_valid():
				_secc.seccion = f_secc.cleaned_data['seccion'].upper()
				_secc.save()
				try:
					_secc=Secciones.objects.get(seccion=f_secc.cleaned_data['seccion'].upper())
				except :
					pass
				else:
					pass
				finally:
					pass
			f_detalles=addDetallesAccesorioForm(initial={'seccion': _secc})
			f_secc=None

		elif 'addmarca' in request.POST:
			f_detalles=addDetallesAccesorioForm(request.POST)
			f_marca=MarcaAccesorioForm(prefix='formulario')

		elif 'addsecc' in request.POST:
			f_detalles=addDetallesAccesorioForm(request.POST)
			f_secc =addSecciones(prefix='formulario2')

		ctx = {'glovales':glovales,'f_secc':f_secc ,'agregados':agregados, 'guardados':guardados, 'b_detalles':b_detalles , 'b_factura':b_factura , 'nivel':nivel, 'informacion':info , 'r_factura':r_factura , 'r_detalle':r_detalle , 'r_facturas':r_facturas , 'r_detalles':r_detalles , 'f_accesorios':f_accesorios , 'f_detalles':f_detalles , 'f_marca':f_marca}
		return render_to_response('compras/addAccesorioFactura.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#test 1 
@login_required(login_url='/')
def compras_almacen_detalle_accesorios_view(request):
	nivel=Permiso(request.user,[0,1,5,6])
	if nivel != -1:
		info = ""
		f_detalles=addDetallesAccesorioForm({'folio':nvo_folio_detalles("AC")})
		f_secc = None
		f_marca = None

		if 'detalles' in request.POST:#patita2
			f_detalles=addDetallesAccesorioForm(request.POST or None)
			if f_detalles.is_valid():
				try:
					with transaction.atomic():
						f_detalles.save()
						info = 'La información se ha Guardado correctamente'
						f_detalles=addDetallesAccesorioForm({'folio':nvo_folio_detalles("AC")})
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."
				
			else:
				f_detalles=addDetallesAccesorioForm(request.POST or None)
				info = 'La información no fue correctamente enviada'

		elif 'gmarca' in request.POST:
			f_marca=MarcaAccesorioForm(request.POST,prefix='formulario')
			_marca=MarcaAccesorio()
			if f_marca.is_valid():
				try:
					with transaction.atomic():
						_marca=f_marca.save()
						info = 'La información de Marca se ha Guardado correctamente'
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."
			else:
				f_detalles=addDetallesAccesorioForm(request.POST or None)
				info = 'La información no fue correctamente enviada (Marca)'
			f_detalles=addDetallesAccesorioForm(initial={'marca': _marca})
			f_marca=None
		
		elif 'gsecc' in request.POST:
			f_secc=addSecciones(request.POST,prefix='formulario2')
			_secc =Secciones()
			if f_secc.is_valid():
				_secc.seccion = f_secc.cleaned_data['seccion'].upper()
				_secc.save()
				try:
					_secc=Secciones.objects.get(seccion=f_secc.cleaned_data['seccion'].upper())
				except :
					pass
				else:
					pass
				finally:
					pass
				info = 'Se ha Guardado correctamente la seccion'
			else:
				f_detalles=addDetallesAccesorioForm(request.POST or None)
				info = 'La información no fue correctamente enviada (Marca)'
			f_detalles=addDetallesAccesorioForm(initial={'seccion': _secc})
			f_secc=None

		elif 'addmarca' in request.POST:
			f_detalles=addDetallesAccesorioForm(request.POST)
			f_marca=MarcaAccesorioForm(prefix='formulario')

		elif 'addsecc' in request.POST:
			f_detalles=addDetallesAccesorioForm(request.POST)
			f_secc =addSecciones(prefix='formulario2')

		ctx = {'f_secc':f_secc ,'nivel':nivel, 'informacion':info ,'f_detalles':f_detalles , 'f_marca':f_marca}
		return render_to_response('compras/addAccesorioDetalle.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')



#yet probado
@login_required(login_url='/')
def compras_almacen_express_view(request):
	nivel=Permiso(request.user,[0,1,5,6])
	if nivel != -1:
		info = ""
		b_factura=request.GET.get('factura','')
		b_detalles=request.GET.get('detalles','')
		b_marca=None
		r_factura=None
		r_detalle=None
		r_facturas=None
		r_detalles=None
		glovales=None
		estatus=None
		repetidas=''
		guardados=''
		agregados=None
		try:
			estatus=Estatus.objects.get(estatus="Existente")
		except :
			estatus=Estatus()
			estatus.estatus="Existente"
			estatus.save()
		sucursal=None
		try:
			sucursal=Sucursal.objects.get(nombre='Almacen Central')
		except :
			pass

		f_express=[addExpresForm(),addExpresForm(),addExpresForm(),addExpresForm(),addExpresForm(),addExpresForm(),addExpresForm(),addExpresForm(),addExpresForm(),addExpresForm(),addExpresForm()]
		if b_factura:
			try:
				r_factura=Factura.objects.get(folio=b_factura)
				agregados=ListaItems(1,None,Q(factura=r_factura),None)
			except:
				r_facturas=ListaFacturas(b_factura)

		if b_detalles:
			try:
				r_detalle=DetallesExpres.objects.get(id=b_detalles)		
			except:
				qset=(Q(descripcion__icontains=b_detalles)|
				Q(tipoIcc__tipoIcc__icontains=b_detalles))
				r_detalles=DetallesExpres.objects.filter(qset).distinct()

		x=0
		while x<len(f_express):
			f_express[x]=addExpresForm(prefix=x, initial={'detallesExpres': r_detalle, 'factura': r_factura})
			x+=1

		if 'expresss' in request.POST:
			x=0
			while x<len(f_express):
				f_express[x] = addExpresForm(request.POST, prefix=x)
				x+=1
			if f_express[0].is_valid():
				_factura=f_express[0].cleaned_data['factura']
				_detalles=f_express[0].cleaned_data['detallesExpres']
				_importe=f_express[0].cleaned_data['importeFactura']
				if _factura and _detalles and _importe:
					try:
						with transaction.atomic():
							_express=Expres()
							_express.factura 	= _factura
							_express.icc 		= f_express[0].cleaned_data['icc']
							_express.detallesExpres = _detalles
							_express.noCell 		= f_express[0].cleaned_data['noCell']
							_express.estatus 	= estatus
							_express.importeFactura = _importe
							_express.sucursal 	= sucursal
							_express.save()
							b_factura=_factura.folio
							almacenItems(1,_express,sucursal,None)
							guardados='%s %s.'%(guardados,_express.icc)
							f_express[0]=addExpresForm(prefix=0, initial={'detallesExpres': _detalles, 'factura': _factura, 'importeFactura':_importe})
								
							x=1
							while x<len(f_express):
								if f_express[x].is_valid():
									_express=Expres()
									_express.factura 	= _factura
									_express.icc 		= f_express[x].cleaned_data['icc']
									_express.detallesExpres = _detalles
									_express.noCell 		= f_express[x].cleaned_data['noCell']
									_express.estatus 	= estatus
									_express.importeFactura = _importe
									_express.sucursal 	= sucursal
									_express.save()
									almacenItems(1,_express,sucursal,None)
									guardados='%s %s.'%(guardados,_express.icc)
									f_express[x]=addExpresForm(prefix=x)
								x+=1
							agregados=ListaItems(1,None,Q(factura=_factura),None)
					except :
						info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."
				else:
					glovales='Campos Obligatorios'

		elif 'serial' in request.POST:
			f_express[0] = addExpresForm(request.POST, prefix=0)
			f_express[1] = addExpresForm(request.POST, prefix=1)
			if f_express[0].is_valid() and f_express[1].is_valid():
				_icc1= f_express[0].cleaned_data['icc']
				_icc2= f_express[1].cleaned_data['icc']
				_factura=f_express[0].cleaned_data['factura']
				b_factura=_factura.folio
				_detalles=f_express[0].cleaned_data['detallesExpres']
				_importe=f_express[0].cleaned_data['importeFactura']
				_noCell= f_express[0].cleaned_data['noCell']
				if _factura and _detalles and _importe:
					if _icc2<_icc1:
						ax=_icc1
						_icc1=_icc2
						_icc2=ax
					while _icc1<=_icc2:
						try:
							with transaction.atomic():
								if Expres.objects.filter(icc=_icc1).exists():
									repetidas='%s, %s.'%(repetidas, _icc1)
								else:
									_express=Expres()
									_express.factura 	= _factura
									_express.icc 		= _icc1
									_express.detallesExpres = _detalles
									_express.noCell 		= _noCell
									_express.estatus 	= estatus
									_express.importeFactura = _importe
									_express.sucursal 	= sucursal
									_express.save()
									almacenItems(1,_express,sucursal,None)
									guardados='%s %s.'%(guardados,_express.icc)
								_icc1+=1
						except :
							guardados = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."
					
					f_express[0]=addExpresForm(prefix=0, initial={'detallesExpres': _detalles, 'factura': _factura, 'importeFactura':_importe})
					x=1
					while x<len(f_express):
						f_express[x]=addExpresForm(prefix=x)
						x+=1
				else:
					glovales='Campos Obligatorios'
					

		ctx = {'glovales':glovales, 'agregados':agregados,'guardados':guardados,'repetidas':repetidas, 'b_detalles':b_detalles , 'b_factura':b_factura , 'nivel':nivel, 'informacion':info , 'r_factura':r_factura , 'r_detalle':r_detalle , 'r_facturas':r_facturas , 'r_detalles':r_detalles , 'f_express':f_express  }
		return render_to_response('compras/addExpressFactura.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#yet probado		
@login_required(login_url='/')
def compras_almacen_fichas_view(request):
	nivel=Permiso(request.user,[0,1,5,6])
	if nivel != -1:
		info = ""
		b_factura=request.GET.get('factura','')
		b_marca=None
		r_factura=None
		r_facturas=None
		glovales=None
		estatus=None
		guardados=''
		repetidas=''
		fichas=[]
		try:
			estatus=EstatusFicha.objects.get(estatus="Existente")
		except :
			estatus=EstatusFicha()
			estatus.estatus="Existente"
			estatus.save()
		sucursal=None
		try:
			sucursal=Sucursal.objects.get(nombre='Almacen Central')
		except :
			pass

		f_fichas=[addFichaForm(),addFichaForm()]
		#,addFichaForm(),addFichaForm(),addFichaForm(),addFichaForm(),addFichaForm(),addFichaForm(),addFichaForm(),addFichaForm()]
		if b_factura:
			try:
				r_factura=Factura.objects.get(folio=b_factura)
				b_fichas=ListaItems(3,None,Q(factura=r_factura),None)
				fichas=SerieFichas(b_fichas)
			except:
				r_facturas=ListaFacturas(b_factura)

		x=0
		while x<len(f_fichas):
			f_fichas[x]=addFichaForm(prefix=x, initial={'factura': r_factura})
			x+=1

		if 'fichas' in request.POST:
			x=0
			while x<len(f_fichas):
				f_fichas[x] = addFichaForm(request.POST, prefix=x)
				x+=1
			if f_fichas[0].is_valid() and f_fichas[0].cleaned_data['factura']:
				_factura=f_fichas[0].cleaned_data['factura']
				b_factura=_factura.folio
				_nominacion=f_fichas[0].cleaned_data['nominacion']
				_importe=f_fichas[0].cleaned_data['precioFac']

				if _factura and _nominacion and _importe:
					if f_fichas[1].is_valid():
						folio_1=int(f_fichas[0].cleaned_data['folio'])
						folio_2=int(f_fichas[1].cleaned_data['folio'])
						if folio_1<folio_2:
							pass
						else:
							ax=folio_2
							folio_2=folio_1
							folio_1=ax
						_importe=float(_importe)
						imp_unit=_importe/(folio_2-folio_1+1)
						while folio_1<=folio_2:
							try:
								with transaction.atomic():
									if Ficha.objects.filter(folio=folio_1).exists():
										repetidas='%s %s.'%(repetidas,_express.icc)
									else:
										_ficha=Ficha()
										_ficha.factura = _factura
										_ficha.folio 	= str(folio_1)
										_ficha.nominacion 	= _nominacion
										_ficha.precioFac 	= "%.2f" % round(imp_unit,2)
										_ficha.estatusFicha = estatus
										_ficha.sucursal 	= sucursal
										_ficha.save()
										almacenItems(3,_ficha,sucursal,None)
										guardados='%s %s.'%(guardados,_ficha.folio)
									folio_1+=1
							except :
								info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

						f_fichas[0]=addFichaForm( prefix=0, initial={'factura': _factura})
						f_fichas[1]=addFichaForm( prefix=1)
				else:
					glovales='Campos Obligatorios'

				b_fichas=ListaItems(3,None,Q(factura=_factura),None)
				fichas=SerieFichas(b_fichas)
				

		ctx = {'glovales':glovales ,'fichas':fichas, 'guardados':guardados, 'repetidas':repetidas, 'b_factura':b_factura , 'nivel':nivel, 'informacion':info , 'r_factura':r_factura ,  'r_facturas':r_facturas ,  'f_fichas':f_fichas }

		return render_to_response('compras/addFichasFactura.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#yet probado	
@login_required(login_url='/')
def compras_almacen_recargas_view(request):
	nivel=Permiso(request.user,[0,1,5,6])
	if nivel != -1:

		info = ""
		b_factura=request.GET.get('factura','')
		r_factura=None
		r_facturas=None
		glovales=None
		sucursal=None
		agregados=None
		try:
			sucursal=Sucursal.objects.get(nombre='Almacen Central')
		except :
			pass
		if b_factura:
			try:
				r_factura=Factura.objects.get(folio=b_factura)
				agregados=TiempoAire.objects.filter(factura=r_factura)
			except:
				r_facturas=ListaFacturas(b_factura)


		form= addTiempoAireForm(initial={'factura': r_factura})
		if request.method == "POST":
			
			form = addTiempoAireForm(request.POST or None)
			a=None
			if form.is_valid():
				try:
					with transaction.atomic():
						factura = form.cleaned_data['factura']
						saldo   = form.cleaned_data['saldo']
						precioFac = form.cleaned_data['precioFac']

						a = TiempoAire()
						a.factura = factura
						a.saldo = saldo
						a.precioFac = precioFac
						a.save()
						agregados=TiempoAire.objects.filter(factura=a.factura)
						b_factura=factura.folio
						almacenItems(4,saldo,sucursal,None)
						form=addTiempoAireForm(initial={'factura': factura})
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		ctx = { 'b_factura':b_factura , 'agregados':agregados, 'nivel':nivel, 'informacion':info , 'r_factura':r_factura ,  'r_facturas':r_facturas ,  'form':form }
		return render_to_response('compras/addRecargasFactura.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#yet probado
@login_required(login_url='/')
def compras_almacen_reporte_view(request):
	nivel=Permiso(request.user,[0,1,5,6])
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

				#form = addFacturaForm(initial={'conFactura': b_factura.conFactura, 'documento': b_factura.documento, 'folio': b_factura.folio, 'proveedor': b_factura.proveedor, 'fxFactura': b_factura.fxFactura, 'formaPago': b_factura.formaPago, 'subTotal': b_factura.subTotal, 'descuento': b_factura.descuento, 'iva': b_factura.iva, 'montoTotal': b_factura.montoTotal, 'tipoFactura': b_factura.  'observacion': b_factura.observacion})
			except :
				b_facturas=ListaFacturas(b_folio)
		else:
			b_facturas=Factura.objects.all().distinct()

		ctx = {'nivel':nivel,'b_folio':b_folio , 'b_factura':b_factura, 'b_facturas':b_facturas, 'b_equipos':b_equipos, 'b_express':b_express, 'b_accesorios':b_accesorios, 'fichas':fichas, 'b_recargas':b_recargas}
		return render_to_response('compras/almacenReporte.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#yet
@login_required(login_url='/')
def compras_movimientos_transferencias_equipos_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		b_movimiento=request.GET.get('movimiento','')
		r_movi=None
		r_movis=None
		sucursal=None
		items=None
		info=''
		agregados=''
		_usuario=Usuario.objects.get(user=request.user)
		_empleado=_usuario.empleado
		vSucural=VendedorSucursal.objects.get(empleado=_empleado)
		_sucursal=vSucural.sucursal
		formMov=None

		if 'gmovimiento' in request.POST:
			formMov=MovimientoForm(request.POST)
			if formMov.is_valid():
				#if True:
				try:
					with transaction.atomic():
					#if True:
						transferencia=Movimiento()
						tmov=TipoMovimiento()
						try:
							tmov=TipoMovimiento.objects.get(nombre='Transferencia')
						except :
							tmov.nombre='Transferencia'
							tmov.save()
						transferencia.folio 			= folioxSucursal(formMov.cleaned_data['sucursalDestino'])
						transferencia.tipoMovimiento 	= tmov
						transferencia.sucursalOrigen 	= _sucursal
						transferencia.sucursalDestino   = formMov.cleaned_data['sucursalDestino']
						transferencia.usuarioOrigen 	= request.user
						transferencia.fx_movimiento = datetime.now()
						transferencia.save()

						b_movimiento=transferencia.folio
						r_movi=transferencia
						formMov=None
				#else:
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		elif 'addmovimiento' in request.POST:
			
			today = datetime.now() #fecha actual
			d = today.strftime("%d-%m-%Y") # fecha con formato
			numero=len(Movimiento.objects.all())
			formMov=MovimientoForm(initial={'folio':'%s-%s'%(numero+1,d)})
			sucurs=Sucursal.objects.exclude(id=_sucursal.id)
			sucursales=[]
			for su in sucurs:
				sucursales.append([su.id, '%s'%(su)])
			formMov.fields['sucursalDestino'].choices = sucursales


		elif 'gmovitem' in request.POST:
			formMovItem=ListaEquipoForm(request.POST)
			if formMovItem.is_valid():
				mov=formMovItem.cleaned_data['movimiento']
				b_movimiento=mov.folio
				r_movi=mov
				if True:
					x=0
					while x<10:
						b_item=request.POST.get('item%s'%(x),'')
						if b_item:
							try:
								item=Equipo.objects.get(imei=b_item,estatus__estatus="Existente")
								if ListaEquipo.objects.filter(movimiento=mov,equipo=item).exists():
									info='%s%s Ya Fue Agregado --- '%(info,item.imei)
								else:
									if item.sucursal != mov.sucursalOrigen:
										info='No puede seleccionar productos de otras Sucursales'
										info='%s%s No se pudo agregar, Esta registrado en otra sucursal: %s --- '%(info,item.imei, item.sucursal)
									else:
										if item.icc:
											try:
												with transaction.atomic():
													movItem=ListaEquipo()
													movItem.movimiento=mov
													movItem.equipo=item
													movItem.save()
													almacenItems(0,item,mov.sucursalDestino,mov.sucursalOrigen)
													agregados='%s%s .'%(agregados,item.imei)
													try:
														exp=Expres.objects.get(icc=item.icc)
														movEx=ListaExpres()
														movEx.movimiento=mov
														movEx.expres=exp
														movEx.save()
														almacenItems(1,exp,mov.sucursalDestino,mov.sucursalOrigen)
													except :
														pass
											except :
												info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."
										else:
											info='%s%s No se pudo agregar, No tiene ICC registrado--- '%(info,item.imei)

							except :
								info='%s%s No se pudo agregar --- '%(info,b_item)
						x+=1
				else:
					info='No puede seleccionar Transferencia de otras Sucursales'
					b_movimiento=None
					r_movi=None

		if b_movimiento and r_movi==None:
			try:
				r_movi=Movimiento.objects.get(folio=b_movimiento,tipoMovimiento__nombre='Transferencia',confirmacion=False)
			except :
				qset=(Q(folio__icontains=b_movimiento)|
				Q(fx_movimiento__icontains=b_movimiento)|
				Q(sucursalDestino__nombre__icontains=b_movimiento))
				r_movis=Movimiento.objects.filter(qset,tipoMovimiento__nombre='Transferencia',confirmacion=False).distinct()

		mov=Movimiento.objects.filter(tipoMovimiento__nombre='Transferencia',fx_movimiento__icontains=datetime.now().date(), confirmacion=False).order_by('-fx_movimiento') #fx recien a vieja del día de hoy
		movim=[]
		for m in mov:
			movim.append([m.id, '%s'%(m)])
		formMovItem=ListaEquipoForm()
		formMovItem.fields['movimiento'].choices = movim
		if r_movi:
			items=ListaEquipo.objects.filter(movimiento=r_movi).order_by('equipo__imei')
			formMovItem.fields['movimiento'].initial = r_movi

		ctx={'nivel':nivel, 'info':info, 'agregados':agregados , 'items':items,'formMovItem':formMovItem,'formMov':formMov,'b_movimiento':b_movimiento, 'r_movis':r_movis}

		return render_to_response('compras/movimientoTranEqu.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_movimientos_transferencias_accesorios_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		b_movimiento=request.GET.get('movimiento','')
		r_movi=None
		r_movis=None
		sucursal=None
		info=''
		agregados=''
		items=None
		_usuario=Usuario.objects.get(user=request.user)
		_empleado=_usuario.empleado
		vSucural=VendedorSucursal.objects.get(empleado=_empleado)
		_sucursal=vSucural.sucursal

		formMov=None

		if 'gmovimiento' in request.POST:
			formMov=MovimientoForm(request.POST)
			if formMov.is_valid():
				try:
					with transaction.atomic():
						transferencia=Movimiento()
						tmov=TipoMovimiento()
						try:
							tmov=TipoMovimiento.objects.get(nombre='Transferencia')
						except :
							tmov.nombre='Transferencia'
							tmov.save()
						transferencia.folio 			= folioxSucursal(formMov.cleaned_data['sucursalDestino'])
						transferencia.tipoMovimiento 	= tmov
						transferencia.sucursalOrigen 	= _sucursal
						transferencia.sucursalDestino   = formMov.cleaned_data['sucursalDestino']
						transferencia.usuarioOrigen 	= request.user
						transferencia.save()
						b_movimiento=transferencia.folio
						r_movi=transferencia
						formMov=None
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		elif 'addmovimiento' in request.POST:
			
			today = datetime.now() #fecha actual
			d = today.strftime("%d-%m-%Y") # fecha con formato
			numero=len(Movimiento.objects.all())
			formMov=MovimientoForm(initial={'folio':'%s-%s'%(numero+1,d)})
			sucurs=Sucursal.objects.exclude(id=_sucursal.id)
			sucursales=[]
			for su in sucurs:
				sucursales.append([su.id, '%s'%(su)])
			formMov.fields['sucursalDestino'].choices = sucursales


		elif 'gmovitem' in request.POST:
			formMovItem=ListaAccesorioForm(request.POST)
			if formMovItem.is_valid():
				try:
					with transaction.atomic():
						mov=formMovItem.cleaned_data['movimiento']
						b_movimiento=mov.folio
						r_movi=mov
						if True:
							x=0
							while x<10:
								b_item=request.POST.get('item%s'%(x),'')
								if b_item:
									try:
										item=Accesorio.objects.get(codigoBarras=b_item, estatusAccesorio__estatus="Existente")
										if ListaAccesorio.objects.filter(movimiento=mov,accesorio=item).exists():
											info='%s%s Ya Fue Agregado --- '%(info,item.codigoBarras)
										else:
											if item.sucursal != mov.sucursalOrigen:
												info='No puede seleccionar productos de otras Sucursales'
												info='%s%s No se pudo agregar, Esta registrado en otra sucursal: %s --- '%(info,item.codigoBarras, item.sucursal)
											else:
												movItem=ListaAccesorio()
												movItem.movimiento=mov
												movItem.accesorio=item
												movItem.save()
												almacenItems(2,item,mov.sucursalDestino,mov.sucursalOrigen)
												agregados='%s%s .'%(agregados,item.codigoBarras)
									except :
										info='%s%s No se pudo agregar --- '%(info,b_item)
								x+=1
						else:
							info='No puede seleccionar Transferencia de otras Sucursales'
							b_movimiento=None
							r_movi=None
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."


		if b_movimiento and r_movi==None:
			try:
				r_movi=Movimiento.objects.get(folio=b_movimiento,tipoMovimiento__nombre='Transferencia',confirmacion=False)
			except :
				qset=(Q(folio__icontains=b_movimiento)|
				Q(fx_movimiento__icontains=b_movimiento)|
				Q(sucursalDestino__nombre__icontains=b_movimiento))
				r_movis=Movimiento.objects.filter(qset,tipoMovimiento__nombre='Transferencia',confirmacion=False).distinct()

		mov=Movimiento.objects.filter(tipoMovimiento__nombre='Transferencia',fx_movimiento__icontains=datetime.now().date(),confirmacion=False).order_by('-fx_movimiento') #fx recien a vieja del día de hoy
		movim=[]
		for m in mov:
			movim.append([m.id, '%s'%(m)])
		formMovItem=ListaAccesorioForm()
		formMovItem.fields['movimiento'].choices = movim
			
		if r_movi:
			items=ListaAccesorio.objects.filter(movimiento=r_movi)
			formMovItem.fields['movimiento'].initial = r_movi

		ctx={'nivel':nivel, 'info':info, 'agregados':agregados , 'items':items, 'formMovItem':formMovItem,'formMov':formMov,'b_movimiento':b_movimiento, 'r_movis':r_movis}

		return render_to_response('compras/movimientoTranAcce.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_movimientos_transferencias_express_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		b_movimiento=request.GET.get('movimiento','')
		r_movi=None
		r_movis=None
		sucursal=None
		info=''
		agregados=''
		items=None
		_usuario=Usuario.objects.get(user=request.user)
		_empleado=_usuario.empleado
		vSucural=VendedorSucursal.objects.get(empleado=_empleado)
		_sucursal=vSucural.sucursal
		
		formMov=None

		if 'gmovimiento' in request.POST:
			formMov=MovimientoForm(request.POST)
			if formMov.is_valid():
				try:
					with transaction.atomic():
						transferencia=Movimiento()
						tmov=TipoMovimiento()
						try:
							tmov=TipoMovimiento.objects.get(nombre='Transferencia')
						except :
							tmov.nombre='Transferencia'
							tmov.save()
						transferencia.folio 			= folioxSucursal(formMov.cleaned_data['sucursalDestino'])
						transferencia.tipoMovimiento 	= tmov
						transferencia.sucursalOrigen 	= _sucursal
						transferencia.sucursalDestino   = formMov.cleaned_data['sucursalDestino']
						transferencia.usuarioOrigen 	= request.user
						transferencia.save()
						b_movimiento=transferencia.folio
						r_movi=transferencia
						formMov=None
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		elif 'addmovimiento' in request.POST:
			
			today = datetime.now() #fecha actual
			d = today.strftime("%d-%m-%Y") # fecha con formato
			numero=len(Movimiento.objects.all())
			formMov=MovimientoForm(initial={'folio':'%s-%s'%(numero+1,d)})
			sucurs=Sucursal.objects.exclude(id=_sucursal.id)
			sucursales=[]
			for su in sucurs:
				sucursales.append([su.id, '%s'%(su)])
			formMov.fields['sucursalDestino'].choices = sucursales

		elif 'gmovitem' in request.POST:
			formMovItem=ListaExpresForm(request.POST)
			if formMovItem.is_valid():
				try:
					with transaction.atomic():
						mov=formMovItem.cleaned_data['movimiento']
						b_movimiento=mov.folio
						r_movi=mov
						if True:
							x=0
							while x<10:
								b_item=request.POST.get('item%s'%(x),'')
								if b_item:
									try:
										item=Expres.objects.get(icc=b_item, estatus__estatus="Existente")
										if ListaExpres.objects.filter(movimiento=mov,expres=item).exists():
											info='%s%s Ya Fue Agregado %s--- '%(info,item.icc, item.tipoIcc)
										else:
											if item.sucursal != mov.sucursalOrigen:
												info='No puede seleccionar productos de otras Sucursales'
												info='%s%s No se pudo agregar, Esta registrado en otra sucursal: %s --- '%(info,item.icc, item.sucursal)
											elif item.detallesExpres.tipoIcc.tipoIcc == "Kit":
												info='No puede transferir express del <tipo Equipo> por que Pertenece a un equipo'
												info='%s%s No se pudo agregar, Esta registrado en otra sucursal: %s --- '%(info,item.icc, item.sucursal)
											else:
												movItem=ListaExpres()
												movItem.movimiento=mov
												movItem.expres=item
												movItem.save()
												almacenItems(1,item,mov.sucursalDestino,mov.sucursalOrigen)
												agregados='%s%s .'%(agregados,item.icc)
									except :
										info='%s%s No se pudo agregar --- '%(info,b_item)
								x+=1
						else:
							info='No puede seleccionar Transferencia de otras Sucursales'
							b_movimiento=None
							r_movi=None
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		if b_movimiento and r_movi==None:
			try:
				r_movi=Movimiento.objects.get(folio=b_movimiento,tipoMovimiento__nombre='Transferencia',confirmacion=False)
			except :
				qset=(Q(folio__icontains=b_movimiento)|
				Q(fx_movimiento__icontains=b_movimiento)|
				Q(sucursalDestino__nombre__icontains=b_movimiento))
				r_movis=Movimiento.objects.filter(qset,tipoMovimiento__nombre='Transferencia',confirmacion=False).distinct()
		mov=Movimiento.objects.filter(tipoMovimiento__nombre='Transferencia',fx_movimiento__icontains=datetime.now().date(),confirmacion=False).order_by('-fx_movimiento') #fx recien a vieja del día de hoy
		movim=[]
		for m in mov:
			movim.append([m.id, '%s'%(m)])
		formMovItem=ListaExpresForm()
		formMovItem.fields['movimiento'].choices = movim
						
		if r_movi:
			items=ListaExpres.objects.filter(movimiento=r_movi)
			formMovItem.fields['movimiento'].initial = r_movi
		ctx={'nivel':nivel, 'info':info, 'agregados':agregados, 'items':items, 'formMovItem':formMovItem,'formMov':formMov,'b_movimiento':b_movimiento, 'r_movis':r_movis}
		return render_to_response('compras/movimientoTranExp.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_movimientos_transferencias_fichas_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		b_movimiento=request.GET.get('movimiento','')
		r_movi=None
		r_movis=None
		sucursal=None
		info=''
		agregados=''
		items=''
		_usuario=Usuario.objects.get(user=request.user)
		_empleado=_usuario.empleado
		vSucural=VendedorSucursal.objects.get(empleado=_empleado)
		_sucursal=vSucural.sucursal
		
		formMov=None

		if 'gmovimiento' in request.POST:
			formMov=MovimientoForm(request.POST)
			if formMov.is_valid():
				try:
					with transaction.atomic():
						transferencia=Movimiento()
						tmov=TipoMovimiento()
						try:
							tmov=TipoMovimiento.objects.get(nombre='Transferencia')
						except :
							tmov.nombre='Transferencia'
							tmov.save()
						transferencia.folio 			= folioxSucursal(formMov.cleaned_data['sucursalDestino'])
						transferencia.tipoMovimiento 	= tmov
						transferencia.sucursalOrigen 	= _sucursal
						transferencia.sucursalDestino   = formMov.cleaned_data['sucursalDestino']
						transferencia.usuarioOrigen 	= request.user
						transferencia.save()
						b_movimiento=transferencia.folio
						r_movi=transferencia
						formMov=None
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		elif 'addmovimiento' in request.POST:
			
			today = datetime.now() #fecha actual
			d = today.strftime("%d-%m-%Y") # fecha con formato
			numero=len(Movimiento.objects.all())
			formMov=MovimientoForm(initial={'folio':'%s-%s'%(numero+1,d)})
			sucurs=Sucursal.objects.exclude(id=_sucursal.id)
			sucursales=[]
			for su in sucurs:
				sucursales.append([su.id, '%s'%(su)])
			formMov.fields['sucursalDestino'].choices = sucursales

		elif 'gmovitem' in request.POST:
			formMovItem=ListaFichasForm(request.POST)
			if formMovItem.is_valid():
				try:
					with transaction.atomic():
						mov=formMovItem.cleaned_data['movimiento']
						b_movimiento=mov.folio
						r_movi=mov
						if True:
							b_item1=0
							b_item2=0
							try:
								b_item1=int(request.POST.get('item1'))
								b_item2=int(request.POST.get('item2'))
								x=b_item1
								while x<=b_item2:
									try:
										item=Ficha.objects.get(folio=x, estatusFicha__estatus="Existente")
										if ListaFichas.objects.filter(movimiento=mov,ficha=item).exists():
											info='%s%s Ya Fue Agregado --- '%(info,item.folio)
										else:
											if item.sucursal != mov.sucursalOrigen:
												info='No puede seleccionar productos de otras Sucursales'
												info='%s%s No se pudo agregar, Esta registrado en otra sucursal: %s --- '%(info,item.folio, item.sucursal)
											else:
												movItem=ListaFichas()
												movItem.movimiento=mov
												movItem.ficha=item
												movItem.save()
												almacenItems(3,item,mov.sucursalDestino,mov.sucursalOrigen)
												agregados='%s%s .'%(agregados,item.folio)
									except :
										info='%s%s No se pudo agregar --- '%(info,x)
									x+=1
							except :
								info='Error en el Formato de los Folios'
						else:
							info='No puede seleccionar Transferencia de otras Sucursales'
							b_movimiento=None
							r_movi=None
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		if b_movimiento and r_movi==None:
			try:
				r_movi=Movimiento.objects.get(folio=b_movimiento,tipoMovimiento__nombre='Transferencia',confirmacion=False)
			except :
				qset=(Q(folio__icontains=b_movimiento)|
				Q(fx_movimiento__icontains=b_movimiento)|
				Q(sucursalDestino__nombre__icontains=b_movimiento))
				r_movis=Movimiento.objects.filter(qset,tipoMovimiento__nombre='Transferencia',confirmacion=False).distinct()
		mov=Movimiento.objects.filter(sucursalOrigen=_sucursal,tipoMovimiento__nombre='Transferencia',fx_movimiento__icontains=datetime.now().date(),confirmacion=False).order_by('-fx_movimiento')
		movim=[]
		for m in mov:
			movim.append([m.id, '%s'%(m)])
		formMovItem=ListaFichasForm()
		formMovItem.fields['movimiento'].choices = movim
						

		if r_movi:
			formMovItem.fields['movimiento'].initial = r_movi
			it=ListaFichas.objects.filter(movimiento=r_movi)
			if it:
				items='Total de Fichas $100: %s,  $200: %s, $300: %s, $500: %s'%(len(it.filter(ficha__nominacion__nominacion=100)),len(it.filter(ficha__nominacion__nominacion=200)),len(it.filter(ficha__nominacion__nominacion=300)),len(it.filter(ficha__nominacion__nominacion=500)))


		ctx={'nivel':nivel, 'info':info, 'agregados':agregados ,'items':items,'formMovItem':formMovItem,'formMov':formMov,'b_movimiento':b_movimiento, 'r_movis':r_movis}

		return render_to_response('compras/movimientoTranFicha.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_movimientos_transferencias_recargas_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		b_movimiento=request.GET.get('movimiento','')
		r_movi=None
		r_movis=None
		sucursal=None
		info=''
		agregados=''
		_usuario=Usuario.objects.get(user=request.user)
		_empleado=_usuario.empleado
		vSucural=VendedorSucursal.objects.get(empleado=_empleado)
		_sucursal=vSucural.sucursal

		saldoActual=0
		try:
			saldoSucursal=SaldoSucursal.objects.get(sucursal=_sucursal)
			saldoActual=saldoSucursal.saldo
		except:
			pass

		formMov=None

		if 'gmovimiento' in request.POST:
			formMov=MovimientoForm(request.POST)
			if formMov.is_valid():
				try:
					with transaction.atomic():
						transferencia=Movimiento()
						tmov=TipoMovimiento()
						try:
							tmov=TipoMovimiento.objects.get(nombre='Transferencia')
						except :
							tmov.nombre='Transferencia'
							tmov.save()
						transferencia.folio 			= folioxSucursal(formMov.cleaned_data['sucursalDestino'])
						transferencia.tipoMovimiento 	= tmov
						transferencia.sucursalOrigen 	= _sucursal
						transferencia.sucursalDestino   = formMov.cleaned_data['sucursalDestino']
						transferencia.usuarioOrigen 	= request.user
						transferencia.save()
						b_movimiento=transferencia.folio
						r_movi=transferencia
						formMov=None
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		elif 'addmovimiento' in request.POST:
			
			today = datetime.now() #fecha actual
			d = today.strftime("%d-%m-%Y") # fecha con formato
			numero=len(Movimiento.objects.all())
			formMov=MovimientoForm(initial={'folio':'%s-%s'%(numero+1,d)})
			sucurs=Sucursal.objects.exclude(id=_sucursal.id)
			sucursales=[]
			for su in sucurs:
				sucursales.append([su.id, '%s'%(su)])
			formMov.fields['sucursalDestino'].choices = sucursales


		elif 'gmovitem' in request.POST:
			formMovItem=TransferenciaSaldoForm(request.POST)
			if formMovItem.is_valid():
				try:
					with transaction.atomic():
						monto=formMovItem.cleaned_data['monto']
						mov=formMovItem.cleaned_data['movimiento']
						b_movimiento=mov.folio
						r_movi=mov
						if monto>saldoActual:
							info='No puede Mandar mas que el Saldo Actual'
						else:
							if mov.sucursalOrigen != _sucursal:
								info='No puede seleccionar Transferencia de otras Sucursales'
								b_movimiento=None
								r_movi=None
							else:
								formMovItem.save()
								almacenItems(4,monto,mov.sucursalDestino,mov.sucursalOrigen)
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		if b_movimiento and r_movi==None:
			try:
				r_movi=Movimiento.objects.get(folio=b_movimiento,tipoMovimiento__nombre='Transferencia',confirmacion=False)
			except :
				qset=(Q(folio__icontains=b_movimiento)|
				Q(fx_movimiento__icontains=b_movimiento)|
				Q(sucursalDestino__nombre__icontains=b_movimiento))
				r_movis=Movimiento.objects.filter(qset,tipoMovimiento__nombre='Transferencia',confirmacion=False).distinct()
		mov=Movimiento.objects.filter(sucursalOrigen=_sucursal,tipoMovimiento__nombre='Transferencia',fx_movimiento__icontains=datetime.now().date(),confirmacion=False).order_by('-fx_movimiento')
		movim=[]
		for m in mov:
			movim.append([m.id, '%s'%(m)])
		formMovItem=TransferenciaSaldoForm()
		formMovItem.fields['movimiento'].choices = movim
		items=None
		if r_movi:
			items=TransferenciaSaldo.objects.filter(movimiento=r_movi)
			formMovItem.fields['movimiento'].initial = r_movi

		ctx={'nivel':nivel, 'info':info, 'saldoActual':saldoActual,'items':items,'formMovItem':formMovItem,'formMov':formMov,'b_movimiento':b_movimiento, 'r_movis':r_movis}

		return render_to_response('compras/movimientoTranSaldo.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet cr
@login_required(login_url='/')
def compras_movimientos_transferencias_consultar_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		b_movimiento=request.GET.get('movimiento','')
		r_movi=None
		r_movis=None
		equipos=None
		express=None
		accesorios=None
		fichas=None
		transSaldo=None
		info=''
		_usuario=Usuario.objects.get(user=request.user)
		_empleado=_usuario.empleado
		vSucural=VendedorSucursal.objects.get(empleado=_empleado)
		_sucursal=vSucural.sucursal

		empleado2=None

		if b_movimiento:
			try:
				r_movi=Movimiento.objects.get(folio=b_movimiento,tipoMovimiento__nombre='Transferencia')
				transSaldo=TransferenciaSaldo.objects.filter(movimiento=r_movi)
				equipos=ListaEquipo.objects.filter(movimiento=r_movi).order_by('equipo__imei')
				accesorios=ListaAccesorio.objects.filter(movimiento=r_movi).order_by('accesorio__codigoBarras')
				express=ListaExpres.objects.filter(movimiento=r_movi).order_by('expres__icc')
				fichas=SerieListasFichas(ListaFichas.objects.filter(movimiento=r_movi).order_by('ficha__folio'))
				try:
					empleado2=Usuario.objects.get(user=r_movi.usuarioOrigen).empleado
				except :
					pass
			except :
				qset=(Q(folio__icontains=b_movimiento)|
				Q(fx_movimiento__icontains=b_movimiento)|
				Q(sucursalDestino__nombre__icontains=b_movimiento))
				r_movis=Movimiento.objects.filter(qset,tipoMovimiento__nombre='Transferencia').distinct().order_by('-fx_movimiento')

		if request.method == "POST":
			exportar = request.POST.get('excel','')
			expMov =  request.POST.get('expMov','')
			if exportar == 'Exportar':
				r_movi=Movimiento.objects.get(folio=expMov,tipoMovimiento__nombre='Transferencia')
				transSaldo=TransferenciaSaldo.objects.filter(movimiento=r_movi)
				equipos=ListaEquipo.objects.filter(movimiento=r_movi).order_by('equipo__imei')
				accesorios=ListaAccesorio.objects.filter(movimiento=r_movi).order_by('accesorio__codigoBarras')
				express=ListaExpres.objects.filter(movimiento=r_movi).order_by('expres__icc')
				fichas=SerieListasFichas(ListaFichas.objects.filter(movimiento=r_movi).order_by('ficha__folio'))

				query = "Transferencias del dia "+str(datetime.now().date())+" a Sucursal "+r_movi.sucursalDestino.nombre.title()

				empleado2=Usuario.objects.get(user=r_movi.usuarioOrigen).empleado
				entrega = empleado2.nombre+' '+empleado2.aPaterno+' '+empleado2.aMaterno
				elmo = []
				elmo.append(r_movi.folio)
				#elmo.append(str(r_movi.fx_movimiento))
				elmo.append(r_movi.sucursalDestino.nombre.title())
				elmo.append("Realizó")
				elmo.append(entrega)
				l1 = []
				l2 = []
				l3 = []
				l4 = []
				l5 = []
				for x in equipos:
					#equipo, imei, icc, nocell ,accesorios
					item = x.equipo.detallesEquipo.marca.marca.title()+' '+x.equipo.detallesEquipo.modelo.title()+' '+x.equipo.detallesEquipo.color.title()
					l1.append([item,str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.equipo.accesorioEqu.title()])
				for x in express:
					#icc, nocell
					l2.append([str(x.expres.icc),x.expres.noCell])
				for x in accesorios:
					item = x.accesorio.detallesAccesorio.seccion.seccion+' '+x.accesorio.detallesAccesorio.marca.marca+' '+x.accesorio.detallesAccesorio.descripcion+' '
					l3.append([str(x.accesorio.codigoBarras),item])
				#Fichas ya no es una listaFichas, es un arreglo basado en el metodo de SerieListaFichas
				#por lo cual, ya que el metodo muestra los totales el procedimiento de abajo es para encontrar
				#el ultimo y el penultimo renglon, que son los que tienen los totales. por eso los elif 
				z=1
				for x in fichas:
					fich=[]
					for y in x:
						fich.append(y)
					if len(fichas)-1==z:
						l4.append([fich[0],''])
					elif len(fichas)==z:
						l4.append(['%s, %s, %s, %s'%(fich[0],fich[1],fich[2],fich[3]),''])
					else:
						l4.append([fich[3],'%s - %s'%(fich[1],fich[2])])
					z+=1
				

				for x in transSaldo:
					l5.append([x.monto])
				folio = expMov
				try:
					return exportMovimiento(folio,query,elmo,l1,l2,l3,l4,l5)
				except :
					info = "No se genero su Archivo."

		ctx={'nivel':nivel, 'info':info, 'empleado2':empleado2, 'equipos':equipos, 'accesorios':accesorios , 'express':express , 'fichas':fichas ,'transSaldo':transSaldo,'b_movimiento':b_movimiento, 'r_movis':r_movis, 'r_movi':r_movi }

		return render_to_response('compras/movimientoTranConsultar.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#yet
@login_required(login_url='/')
def compras_movimientos_devoluciones_equipos_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		b_movimiento=request.GET.get('movimiento','')
		r_movi=None
		r_movis=None
		sucursal=None
		items=None
		info=''
		agregados=''
		_usuario=Usuario.objects.get(user=request.user)
		_empleado=_usuario.empleado
		vSucural=VendedorSucursal.objects.get(empleado=_empleado)
		_sucursal=vSucural.sucursal

		formMov=None

		if 'gmovimiento' in request.POST:
			formMov=MovimientoDForm(request.POST)
			if formMov.is_valid():
				try:
					with transaction.atomic():
						Devolucion=Movimiento()
						tmov=TipoMovimiento()
						try:
							tmov=TipoMovimiento.objects.get(nombre='Devolucion')
						except :
							tmov.nombre='Devolucion'
							tmov.save()
						Devolucion.folio 			= folioxSucursal(_sucursal)
						Devolucion.tipoMovimiento 	= tmov
						Devolucion.sucursalOrigen 	= formMov.cleaned_data['sucursalOrigen']
						Devolucion.sucursalDestino   = _sucursal
						Devolucion.usuarioOrigen 	= request.user
						Devolucion.save()
						b_movimiento=Devolucion.folio
						r_movi=Devolucion
						formMov=None
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		elif 'addmovimiento' in request.POST:
			
			today = datetime.now() #fecha actual
			d = today.strftime("%d-%m-%Y") # fecha con formato
			numero=len(Movimiento.objects.all())
			formMov=MovimientoDForm(initial={'folio':'%s-%s'%(numero+1,d)})
			sucurs=Sucursal.objects.exclude(id=_sucursal.id)


		elif 'gmovitem' in request.POST:
			formMovItem=ListaEquipoForm(request.POST)
			if formMovItem.is_valid():
				try:
					with transaction.atomic():
						mov=formMovItem.cleaned_data['movimiento']
						b_movimiento=mov.folio
						r_movi=mov
						if True:
							x=0
							while x<10:
								b_item=request.POST.get('item%s'%(x),'')
								if b_item:
									try:
										item=Equipo.objects.get(imei=b_item,estatus__estatus="Existente")
										if ListaEquipo.objects.filter(movimiento=mov,equipo=item).exists():
											info='%s%s Ya Fue Agregado --- '%(info,item.imei)
										else:
											if item.sucursal != mov.sucursalOrigen:
												info='No puede seleccionar productos de otras Sucursales'
												info='%s%s No se pudo agregar, Esta registrado en otra sucursal: %s --- '%(info,item.imei, item.sucursal)
											else:
												if item.icc:
													movItem=ListaEquipo()
													movItem.movimiento=mov
													movItem.equipo=item
													movItem.save()
													almacenItems(0,item,mov.sucursalDestino,mov.sucursalOrigen)
													agregados='%s%s .'%(agregados,item.imei)
												else:
													info='%s%s No se pudo agregar, No tienen ICC Registrado'%(info,item.imei)

									except :
										info='%s%s No se pudo agregar --- '%(info,b_item)
								x+=1
						else:
							info='No puede seleccionar Transferencia de otras Sucursales'
							b_movimiento=None
							r_movi=None
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		if b_movimiento and r_movi==None:
			try:
				r_movi=Movimiento.objects.get(folio=b_movimiento,tipoMovimiento__nombre='Devolucion',confirmacion=False)
			except :
				qset=(Q(folio__icontains=b_movimiento)|
				Q(fx_movimiento__icontains=b_movimiento)|
				Q(sucursalDestino__nombre__icontains=b_movimiento))
				r_movis=Movimiento.objects.filter(qset,tipoMovimiento__nombre='Devolucion',confirmacion=False).distinct()
		mov=Movimiento.objects.filter(tipoMovimiento__nombre='Devolucion',fx_movimiento__icontains=datetime.now().date(),confirmacion=False).order_by('-fx_movimiento')
		movim=[]
		for m in mov:
			movim.append([m.id, '%s'%(m)])
		formMovItem=ListaEquipoForm()
		formMovItem.fields['movimiento'].choices = movim
		if r_movi:
			items=ListaEquipo.objects.filter(movimiento=r_movi).order_by('equipo__imei')
			formMovItem.fields['movimiento'].initial = r_movi


		ctx={'nivel':nivel, 'info':info, 'agregados':agregados , 'items':items,'formMovItem':formMovItem,'formMov':formMov,'b_movimiento':b_movimiento, 'r_movis':r_movis}

		return render_to_response('compras/movimientoDevEqu.html', ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_movimientos_devoluciones_accesorios_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		b_movimiento=request.GET.get('movimiento','')
		r_movi=None
		r_movis=None
		sucursal=None
		info=''
		agregados=''
		items=None
		_usuario=Usuario.objects.get(user=request.user)
		_empleado=_usuario.empleado
		vSucural=VendedorSucursal.objects.get(empleado=_empleado)
		_sucursal=vSucural.sucursal
		formMov=None

		if 'gmovimiento' in request.POST:
			formMov=MovimientoDForm(request.POST)
			if formMov.is_valid():
				try:
					with transaction.atomic():
						Devolucion=Movimiento()
						tmov=TipoMovimiento()
						try:
							tmov=TipoMovimiento.objects.get(nombre='Devolucion')
						except :
							tmov.nombre='Devolucion'
							tmov.save()
						Devolucion.folio 			= folioxSucursal(_sucursal)
						Devolucion.tipoMovimiento 	= tmov
						Devolucion.sucursalOrigen 	= formMov.cleaned_data['sucursalOrigen']
						Devolucion.sucursalDestino   = _sucursal
						Devolucion.usuarioOrigen 	= request.user
						Devolucion.save()
						b_movimiento=Devolucion.folio
						r_movi=Devolucion
						formMov=None
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		elif 'addmovimiento' in request.POST:
			
			today = datetime.now() #fecha actual
			d = today.strftime("%d-%m-%Y") # fecha con formato
			numero=len(Movimiento.objects.all())
			formMov=MovimientoDForm(initial={'folio':'%s-%s'%(numero+1,d)})
			sucurs=Sucursal.objects.exclude(id=_sucursal.id)

		elif 'gmovitem' in request.POST:
			formMovItem=ListaAccesorioForm(request.POST)
			if formMovItem.is_valid():
				try:
					with transaction.atomic():
						mov=formMovItem.cleaned_data['movimiento']
						b_movimiento=mov.folio
						r_movi=mov
						if True:
							x=0
							while x<10:
								b_item=request.POST.get('item%s'%(x),'')
								if b_item:
									try:
										item=Accesorio.objects.get(codigoBarras=b_item, estatusAccesorio__estatus="Existente")
										if ListaAccesorio.objects.filter(movimiento=mov,accesorio=item).exists():
											info='%s%s Ya Fue Agregado --- '%(info,item.codigoBarras)
										else:
											if item.sucursal != mov.sucursalOrigen:
												info='No puede seleccionar productos de otras Sucursales'
												info='%s%s No se pudo agregar, Esta registrado en otra sucursal: %s --- '%(info,item.codigoBarras, item.sucursal)
											else:
												movItem=ListaAccesorio()
												movItem.movimiento=mov
												movItem.accesorio=item
												movItem.save()
												almacenItems(2,item,mov.sucursalDestino,mov.sucursalOrigen)
												agregados='%s%s .'%(agregados,item.codigoBarras)
									except :
										info='%s%s No se pudo agregar --- '%(info,b_item)
								x+=1
						else:
							info='No puede seleccionar Transferencia de otras Sucursales'
							b_movimiento=None
							r_movi=None
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		if b_movimiento and r_movi==None:
			try:
				r_movi=Movimiento.objects.get(folio=b_movimiento,tipoMovimiento__nombre='Devolucion',confirmacion=False)
			except :
				qset=(Q(folio__icontains=b_movimiento)|
				Q(fx_movimiento__icontains=b_movimiento)|
				Q(sucursalDestino__nombre__icontains=b_movimiento))
				r_movis=Movimiento.objects.filter(qset,tipoMovimiento__nombre='Devolucion',confirmacion=False).distinct()
		mov=Movimiento.objects.filter(tipoMovimiento__nombre='Devolucion',fx_movimiento__icontains=datetime.now().date(),confirmacion=False).order_by('-fx_movimiento')
		movim=[]
		for m in mov:
			movim.append([m.id, '%s'%(m)])
		formMovItem=ListaAccesorioForm()
		formMovItem.fields['movimiento'].choices = movim
			
		if r_movi:
			items=ListaAccesorio.objects.filter(movimiento=r_movi)
			formMovItem.fields['movimiento'].initial = r_movi

		ctx={'nivel':nivel, 'info':info, 'agregados':agregados , 'items':items,'formMovItem':formMovItem,'formMov':formMov,'b_movimiento':b_movimiento, 'r_movis':r_movis}

		return render_to_response('compras/movimientoDevAcce.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_movimientos_devoluciones_express_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		b_movimiento=request.GET.get('movimiento','')
		r_movi=None
		r_movis=None
		sucursal=None
		info=''
		agregados=''
		items=None
		_usuario=Usuario.objects.get(user=request.user)
		_empleado=_usuario.empleado
		vSucural=VendedorSucursal.objects.get(empleado=_empleado)
		_sucursal=vSucural.sucursal
		formMov=None

		if 'gmovimiento' in request.POST:
			formMov=MovimientoDForm(request.POST)
			if formMov.is_valid():
				try:
					with transaction.atomic():
						Devolucion=Movimiento()
						tmov=TipoMovimiento()
						try:
							tmov=TipoMovimiento.objects.get(nombre='Devolucion')
						except :
							tmov.nombre='Devolucion'
							tmov.save()
						Devolucion.folio 			= folioxSucursal(_sucursal)
						Devolucion.tipoMovimiento 	= tmov
						Devolucion.sucursalOrigen 	= formMov.cleaned_data['sucursalOrigen']
						Devolucion.sucursalDestino   = _sucursal
						Devolucion.usuarioOrigen 	= request.user
						Devolucion.save()
						b_movimiento=Devolucion.folio
						r_movi=Devolucion
						formMov=None
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		elif 'addmovimiento' in request.POST:
			
			today = datetime.now() #fecha actual
			d = today.strftime("%d-%m-%Y") # fecha con formato
			numero=len(Movimiento.objects.all())
			formMov=MovimientoDForm(initial={'folio':'%s-%s'%(numero+1,d)})
			sucurs=Sucursal.objects.exclude(id=_sucursal.id)


		elif 'gmovitem' in request.POST:
			formMovItem=ListaExpresForm(request.POST)
			if formMovItem.is_valid():
				try:
					with transaction.atomic():
						mov=formMovItem.cleaned_data['movimiento']
						b_movimiento=mov.folio
						r_movi=mov
						if True:
							x=0
							while x<10:
								b_item=request.POST.get('item%s'%(x),'')
								if b_item:
									try:
										item=Expres.objects.get(icc=b_item, estatus__estatus="Existente")
										if ListaExpres.objects.filter(movimiento=mov,expres=item).exists():
											info='%s%s Ya Fue Agregado --- '%(info,item.icc)
										else:
											if item.sucursal != mov.sucursalOrigen:
												info='No puede seleccionar productos de otras Sucursales'
												info='%s%s No se pudo agregar, Esta registrado en otra sucursal: %s --- '%(info,item.icc, item.sucursal)
											else:
												movItem=ListaExpres()
												movItem.movimiento=mov
												movItem.expres=item
												movItem.save()
												almacenItems(1,item,mov.sucursalDestino,mov.sucursalOrigen)
												agregados='%s%s .'%(agregados,item.icc)
									except :
										info='%s%s No se pudo agregar --- '%(info,b_item)
								x+=1
						else:
							info='No puede seleccionar Transferencia de otras Sucursales'
							b_movimiento=None
							r_movi=None
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		if b_movimiento and r_movi==None:
			try:
				r_movi=Movimiento.objects.get(folio=b_movimiento,tipoMovimiento__nombre='Devolucion',confirmacion=False)
			except :
				qset=(Q(folio__icontains=b_movimiento)|
				Q(fx_movimiento__icontains=b_movimiento)|
				Q(sucursalDestino__nombre__icontains=b_movimiento))
				r_movis=Movimiento.objects.filter(qset,tipoMovimiento__nombre='Devolucion',confirmacion=False).distinct()
		mov=Movimiento.objects.filter(tipoMovimiento__nombre='Devolucion',fx_movimiento__icontains=datetime.now().date(),confirmacion=False).order_by('-fx_movimiento')
		movim=[]
		for m in mov:
			movim.append([m.id, '%s'%(m)])
		formMovItem=ListaExpresForm()
		formMovItem.fields['movimiento'].choices = movim
						
		if r_movi:
			items=ListaExpres.objects.filter(movimiento=r_movi)
			formMovItem.fields['movimiento'].initial = r_movi

		ctx={'nivel':nivel, 'info':info, 'agregados':agregados , 'items':items,'formMovItem':formMovItem,'formMov':formMov,'b_movimiento':b_movimiento, 'r_movis':r_movis}

		return render_to_response('compras/movimientoDevExp.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_movimientos_devoluciones_fichas_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		b_movimiento=request.GET.get('movimiento','')
		r_movi=None
		r_movis=None
		sucursal=None
		info=''
		agregados=''
		items=''
		_usuario=Usuario.objects.get(user=request.user)
		_empleado=_usuario.empleado
		vSucural=VendedorSucursal.objects.get(empleado=_empleado)
		_sucursal=vSucural.sucursal


		formMov=None

		if 'gmovimiento' in request.POST:
			formMov=MovimientoDForm(request.POST)
			if formMov.is_valid():
				try:
					with transaction.atomic():
						Devolucion=Movimiento()
						tmov=TipoMovimiento()
						try:
							tmov=TipoMovimiento.objects.get(nombre='Devolucion')
						except :
							tmov.nombre='Devolucion'
							tmov.save()
						Devolucion.folio 			= folioxSucursal(_sucursal)
						Devolucion.tipoMovimiento 	= tmov
						Devolucion.sucursalOrigen 	= formMov.cleaned_data['sucursalOrigen']
						Devolucion.sucursalDestino   = _sucursal
						Devolucion.usuarioOrigen 	= request.user
						Devolucion.save()
						b_movimiento=Devolucion.folio
						r_movi=Devolucion
						formMov=None
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		elif 'addmovimiento' in request.POST:
			
			today = datetime.now() #fecha actual
			d = today.strftime("%d-%m-%Y") # fecha con formato
			numero=len(Movimiento.objects.all())
			formMov=MovimientoDForm(initial={'folio':'%s-%s'%(numero+1,d)})
			sucurs=Sucursal.objects.exclude(id=_sucursal.id)

		elif 'gmovitem' in request.POST:
			formMovItem=ListaFichasForm(request.POST)
			if formMovItem.is_valid():
				try:
					with transaction.atomic():
						mov=formMovItem.cleaned_data['movimiento']
						b_movimiento=mov.folio
						r_movi=mov
						if True:
							b_item1=0
							b_item2=0
							try:
								b_item1=int(request.POST.get('item1'))
								b_item2=int(request.POST.get('item2'))
								x=b_item1
								while x<=b_item2:
									try:
										item=Ficha.objects.get(folio=x, estatusFicha__estatus="Existente")
										if ListaFichas.objects.filter(movimiento=mov,ficha=item).exists():
											info='%s%s Ya Fue Agregado --- '%(info,item.folio)
										else:
											if item.sucursal != mov.sucursalOrigen:
												info='No puede seleccionar productos de otras Sucursales'
												info='%s%s No se pudo agregar, Esta registrado en otra sucursal: %s --- '%(info,item.folio, item.sucursal)
											else:
												movItem=ListaFichas()
												movItem.movimiento=mov
												movItem.ficha=item
												movItem.save()
												almacenItems(3,item,mov.sucursalDestino,mov.sucursalOrigen)
												agregados='%s%s .'%(agregados,item.folio)
									except :
										info='%s%s No se pudo agregar --- '%(info,x)
									x+=1
							except :
								info='Error en el Formato de los Folios'
						else:
							info='No puede seleccionar Transferencia de otras Sucursales'
							b_movimiento=None
							r_movi=None
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		if b_movimiento and r_movi==None:
			try:
				r_movi=Movimiento.objects.get(folio=b_movimiento,tipoMovimiento__nombre='Devolucion',confirmacion=False)
			except :
				qset=(Q(folio__icontains=b_movimiento)|
				Q(fx_movimiento__icontains=b_movimiento)|
				Q(sucursalDestino__nombre__icontains=b_movimiento))
				r_movis=Movimiento.objects.filter(qset,tipoMovimiento__nombre='Devolucion',confirmacion=False).distinct()
		mov=Movimiento.objects.filter(tipoMovimiento__nombre='Devolucion',fx_movimiento__icontains=datetime.now().date(),confirmacion=False).order_by('-fx_movimiento')
		movim=[]
		for m in mov:
			movim.append([m.id, '%s'%(m)])
		formMovItem=ListaFichasForm()
		formMovItem.fields['movimiento'].choices = movim
						

		if r_movi:
			formMovItem.fields['movimiento'].initial = r_movi
			it=ListaFichas.objects.filter(movimiento=r_movi)
			if it:
				items='Total de Fichas $100: %s,  $200: %s, $300: %s, $500: %s'%(len(it.filter(ficha__nominacion__nominacion=100)),len(it.filter(ficha__nominacion__nominacion=200)),len(it.filter(ficha__nominacion__nominacion=300)),len(it.filter(ficha__nominacion__nominacion=500)))


		ctx={'nivel':nivel, 'info':info, 'agregados':agregados , 'items':items,'formMovItem':formMovItem,'formMov':formMov,'b_movimiento':b_movimiento, 'r_movis':r_movis}

		return render_to_response('compras/movimientoDevFicha.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_movimientos_devoluciones_recargas_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:

		#******bloque para visualizar los saldos
		pagina=request.GET.get('pagina','')
		items=None
		items=SaldoSucursal.objects.all()
		paginator = Paginator(items, 50)
		itemsp=None
		try:
			itemsp = paginator.page(pagina)
		except PageNotAnInteger:
			itemsp = paginator.page(1)
		except EmptyPage:
			itemsp = paginator.page(paginator.num_pages)
		saldos=itemsp
		#*************

		b_movimiento=request.GET.get('movimiento','')
		r_movi=None
		r_movis=None
		sucursal=None
		info=''
		agregados=''
		items=''
		_usuario=Usuario.objects.get(user=request.user)
		_empleado=_usuario.empleado
		vSucural=VendedorSucursal.objects.get(empleado=_empleado)
		_sucursal=vSucural.sucursal

		formMov=None

		if 'gmovimiento' in request.POST:
			formMov=MovimientoDForm(request.POST)
			if formMov.is_valid():
				if True:
					if True:
				#try:
					#with transaction.atomic():
						Devolucion=Movimiento()
						tmov=TipoMovimiento()
						try:
							tmov=TipoMovimiento.objects.get(nombre='Devolucion')
						except :
							tmov.nombre='Devolucion'
							tmov.save()
						Devolucion.folio 			= folioxSucursal(_sucursal)
						Devolucion.tipoMovimiento 	= tmov
						Devolucion.sucursalOrigen 	= formMov.cleaned_data['sucursalOrigen']
						Devolucion.sucursalDestino   = _sucursal
						Devolucion.usuarioOrigen 	= request.user
						Devolucion.save()
						b_movimiento=Devolucion.folio
						r_movi=Devolucion
						formMov=None
				'''except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."'''

		elif 'addmovimiento' in request.POST:
			
			today = datetime.now() #fecha actual
			d = today.strftime("%d-%m-%Y") # fecha con formato
			numero=len(Movimiento.objects.all())
			formMov=MovimientoDForm(initial={'folio':'%s-%s'%(numero+1,d)})
			sucurs=Sucursal.objects.exclude(id=_sucursal.id)


		elif 'gmovitem' in request.POST:
			formMovItem=TransferenciaSaldoForm(request.POST)
			if formMovItem.is_valid():
				try:
					with transaction.atomic():
				#if True:
				#	if True:
						monto=formMovItem.cleaned_data['monto']
						mov=formMovItem.cleaned_data['movimiento']
						b_movimiento=mov.folio
						r_movi=mov
						saldoActual=0
						try:
							saldoSucursal=SaldoSucursal.objects.get(sucursal=r_movi.sucursalOrigen)
							saldoActual=saldoSucursal.saldo
						except:
							pass
						if monto>saldoActual:
							info='Error al tratar de mandar %s, No puede mandar mas de %s de la  %s'%(monto, saldoActual, r_movi.sucursalOrigen)
						else:
							'''if mov.sucursalOrigen != _sucursal:
								info='No puede seleccionar Devolucion de otras Sucursales'
								b_movimiento=None
								r_movi=None
							else:'''
							formMovItem.save()
							almacenItems(4,monto,mov.sucursalDestino,mov.sucursalOrigen)
							info='Devolucion de Saldo registrado correctamente'
				#'''
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."#'''

		if b_movimiento and r_movi==None:
			try:
				r_movi=Movimiento.objects.get(folio=b_movimiento,tipoMovimiento__nombre='Devolucion',confirmacion=False)
			except :
				qset=(Q(folio__icontains=b_movimiento)|
				Q(fx_movimiento__icontains=b_movimiento)|
				Q(sucursalDestino__nombre__icontains=b_movimiento))
				r_movis=Movimiento.objects.filter(qset,tipoMovimiento__nombre='Devolucion',confirmacion=False).distinct()
		mov=Movimiento.objects.filter(tipoMovimiento__nombre='Devolucion',fx_movimiento__icontains=datetime.now().date(),confirmacion=False).order_by('-fx_movimiento')
		movim=[]
		for m in mov:
			movim.append([m.id, '%s'%(m)])
		formMovItem=TransferenciaSaldoForm()
		formMovItem.fields['movimiento'].choices = movim

		if r_movi:
			items=TransferenciaSaldo.objects.filter(movimiento=r_movi)
			formMovItem.fields['movimiento'].initial = r_movi

		ctx={'nivel':nivel,'saldos':saldos, 'info':info,'items':items,'formMovItem':formMovItem,'formMov':formMov,'b_movimiento':b_movimiento, 'r_movis':r_movis}

		return render_to_response('compras/movimientoDevSaldo.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet cr
@login_required(login_url='/')
def compras_movimientos_devoluciones_consultar_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		b_movimiento=request.GET.get('movimiento','')
		r_movi=None
		r_movis=None
		equipos=None
		express=None
		accesorios=None
		fichas=None
		transSaldo=None
		info=''
		_usuario=Usuario.objects.get(user=request.user)
		_empleado=_usuario.empleado
		vSucural=VendedorSucursal.objects.get(empleado=_empleado)
		_sucursal=vSucural.sucursal

		empleado2=None

		if b_movimiento:
			try:
				r_movi=Movimiento.objects.get(folio=b_movimiento,tipoMovimiento__nombre='Devolucion')
				transSaldo=TransferenciaSaldo.objects.filter(movimiento=r_movi)
				equipos=ListaEquipo.objects.filter(movimiento=r_movi).order_by('equipo__imei')
				accesorios=ListaAccesorio.objects.filter(movimiento=r_movi).order_by('accesorio__codigoBarras')
				express=ListaExpres.objects.filter(movimiento=r_movi).order_by('expres__icc')
				fichas=SerieListasFichas(ListaFichas.objects.filter(movimiento=r_movi).order_by('ficha__folio'))
				try:
					empleado2=Usuario.objects.get(user=r_movi.usuarioOrigen).empleado
				except :
					pass
			except :
				qset=(Q(folio__icontains=b_movimiento)|
				Q(fx_movimiento__icontains=b_movimiento)|
				Q(sucursalDestino__nombre__icontains=b_movimiento))
				r_movis=Movimiento.objects.filter(qset,tipoMovimiento__nombre='Devolucion').distinct().order_by('-fx_movimiento')

		if request.method == "POST":
			exportar = request.POST.get('excel','')
			expMov =  request.POST.get('expMov','')
			if exportar == 'Exportar':
				r_movi=Movimiento.objects.get(folio=expMov,tipoMovimiento__nombre='Devolucion')
				transSaldo=TransferenciaSaldo.objects.filter(movimiento=r_movi)
				equipos=ListaEquipo.objects.filter(movimiento=r_movi).order_by('equipo__imei')
				accesorios=ListaAccesorio.objects.filter(movimiento=r_movi).order_by('accesorio__codigoBarras')
				express=ListaExpres.objects.filter(movimiento=r_movi).order_by('expres__icc')
				fichas=SerieListasFichas(ListaFichas.objects.filter(movimiento=r_movi).order_by('ficha__folio'))
				query = "Devolucion del dia "+str(datetime.now().date())+" de Sucursal "+r_movi.sucursalOrigen.nombre.title()

				empleado2=Usuario.objects.get(user=r_movi.usuarioOrigen).empleado
				entrega = empleado2.nombre+' '+empleado2.aPaterno+' '+empleado2.aMaterno
				elmo = []
				elmo.append(r_movi.folio)
				#elmo.append(str(r_movi.fx_movimiento))
				elmo.append(r_movi.sucursalDestino.nombre.title())
				elmo.append("Realizó")
				elmo.append(entrega)
				l1 = []
				l2 = []
				l3 = []
				l4 = []
				l5 = []
				for x in equipos:
					#equipo, imei, icc, nocell ,accesorios
					item = x.equipo.detallesEquipo.marca.marca.title()+' '+x.equipo.detallesEquipo.modelo.title()+' '+x.equipo.detallesEquipo.color.title()
					l1.append([item,str(x.equipo.imei),str(x.equipo.icc),x.equipo.noCell,x.equipo.accesorioEqu.title()])
				for x in express:
					#icc, nocell
					l2.append([str(x.expres.icc),x.expres.noCell])
				for x in accesorios:
					item = x.accesorio.detallesAccesorio.seccion.seccion+' '+x.accesorio.detallesAccesorio.marca.marca+' '+x.accesorio.detallesAccesorio.descripcion+' '
					l3.append([str(x.accesorio.codigoBarras),item])
				
				#Fichas ya no es una listaFichas, es un arreglo basado en el metodo de SerieListaFichas
				#por lo cual, ya que el metodo muestra los totales el procedimiento de abajo es para encontrar
				#el ultimo y el penultimo renglon, que son los que tienen los totales. por eso los elif 
				z=1
				for x in fichas:
					fich=[]
					for y in x:
						fich.append(y)
					if len(fichas)-1==z:
						l4.append([fich[0],''])
					elif len(fichas)==z:
						l4.append(['%s, %s, %s, %s'%(fich[0],fich[1],fich[2],fich[3]),''])
					else:
						l4.append([fich[3],'%s - %s'%(fich[1],fich[2])])
					z+=1

				for x in transSaldo:
					l5.append([x.monto])
				folio = expMov
				try:
					return exportMovimiento(folio,query,elmo,l1,l2,l3,l4,l5)
				except :
					info = "No se genero su Archivo."


		ctx={'nivel':nivel, 'info':info, 'empleado2':empleado2, 'equipos':equipos, 'accesorios':accesorios , 'express':express , 'fichas':fichas ,'transSaldo':transSaldo,'b_movimiento':b_movimiento, 'r_movis':r_movis, 'r_movi':r_movi }

		return render_to_response('compras/movimientoDevConsultar.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#yet
@login_required(login_url='/')
def compras_movimientos_asignar_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		error=''
		asignados=''
		_usuario=Usuario.objects.get(user=request.user)
		_empleado=_usuario.empleado
		vSucural=VendedorSucursal.objects.get(empleado=_empleado)
		_sucursal=vSucural.sucursal
		if 'asignar' in request.POST:
			x=0
			try:
				while x<10:
					_imei=request.POST.get('imei%s'%(x),'')
					_icc=request.POST.get('icc%s'%(x),'')
					if _imei and _icc:
						equipo=None
						expres=None
						try:
							equipo=Equipo.objects.get(imei=_imei)
						except :
							error='Equipo no Registrado imei:%s , %s'%(_imei, error)
						try:
							expres=Expres.objects.get(icc=_icc)
						except :
							error='Expres no Registrada icc:%s , %s'%(_icc, error)
						if equipo and expres:
							if equipo.icc:
								error='El Equipo imei:%s ya tiene una Expres asignada icc:%s , %s'%(_imei, equipo.icc, error)
							#comprovaciones del Equipo
							else:
								if equipo.sucursal==_sucursal:
									if equipo.estatus.estatus=='Existente':
										#comprovaciones de la Express
										if expres.sucursal==_sucursal:
											if expres.estatus.estatus=='Existente':
												if expres.detallesExpres.descripcion!='Equipo':
													#comprovada
													equipo.icc=expres.icc
													equipo.save()
													try:
														detExp=DetallesExpres.objects.get(descripcion='Equipo')
													except :
														detExp=DetallesExpres()
														detExp.descripcion='Equipo'
														try:
															ticc=TipoIcc.objects.get(tipoIcc='Kit')
														except :
															ticc=TipoIcc()
															ticc.tipoIcc='Kit'
															ticc.save()
														detExp.tipoIcc=ticc
														try:
															tgarn=TiempoGarantia.objects.get(dias=0)
														except :
															tgarn.TiempoGarantia()
															tgarn.dias=0
															tgarn.save()
														detExp.tiempoGarantia=tgarn
														detExp.precioMayoreo=0
														detExp.precioMenudeo=0
														detExp.save()
													expres.detallesExpres=detExp
													expres.save()
													asignados='Asignacion Realizada del Expres: %s  con el Equipo: %s    -|-|- %s'%(equipo,expres, asignados)
												else:
													error='La Expres no es Tipo Correcto icc:%s -- tipo:%s , %s'%(_icc, expres.detallesExpres.descripcion, error)
											else:
												error='La Expres no Se encuentra Existente icc:%s , %s'%(_icc, error)
										else:
											error='La Expres no Pertenese a la Sucursal icc:%s , %s'%(_icc, error)
									else:
										error='El Equipo no Se encuentra Existente imei:%s , %s'%(_imei, error)
								else:
									error='El Equipo no Pertenese a la Sucursal imei:%s , %s'%(_imei, error)
					else:
						if _imei or _icc:
							error='Datos Obligatorios, imei:%s -- icc:%s, %s'%(_imei,_icc, error)
					x+=1
			except :
				error = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

		ctx= {'nivel':nivel, 'error':error, 'asignados':asignados}
		
		return render_to_response('compras/movimientoAsignacion.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def compras_movimientos_confirmar_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		info =""
		query  = request.GET.get('q','')
		pag1=request.GET.get('pagina','')
		msgs = Movimiento.objects.filter(tipoMovimiento__nombre='Transferencia').order_by('-fx_movimiento')

		if query:
			msgs = Movimiento.objects.filter(folio__icontains=query,tipoMovimiento__nombre='Transferencia').order_by('-fx_movimiento')
		
		paginator1 = Paginator(msgs, 25)
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
					transEq = ListaEquipo.objects.filter(movimiento__id=s).order_by('confirmacion').order_by('equipo')
					transEx = ListaExpres.objects.filter(movimiento__id=s).order_by('confirmacion').order_by('expres')
					transAc = ListaAccesorio.objects.filter(movimiento__id=s).order_by('confirmacion').order_by('accesorio')
					transFic = ListaFichas.objects.filter(movimiento__id=s).order_by('confirmacion').order_by('ficha')
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__id=s)

					ctx={'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('compras/confirmacionProductos.html',ctx,context_instance=RequestContext(request))
			
			if request.GET.get('aceptEq'):
				s = request.GET.get('aceptEq','')
				grrr = request.GET.get('mChoice','')
				m = request.GET.get('transfGral','')
				if s:
					try:
						with transaction.atomic():
							mov = Movimiento.objects.get(folio=m)
							upd = ListaEquipo.objects.get(id=s)
							upd.confirmacion = True
							upd.save()

							item = Equipo.objects.get(id=upd.equipo.id)
							sd = Sucursal.objects.get(nombre='Almacen Central')
							if grrr == 'robado':
								item.estatus = Estatus.objects.get(estatus='Robado')
								item.save()
								#confirmarItems(0,item,None,item.sucursal)
							else:
								item.sucursal=sd
								item.estatus = Estatus.objects.get(estatus='Existente')
								item.save()
								alm=AlmacenEquipo()
								alm.sucursal=sd
								alm.equipo=item
								alm.estado=True
								alm.save()
								#confirmarItems(0,item,sd,item.sucursal)
					except :
						info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

					transEq = ListaEquipo.objects.filter(movimiento__folio=m).order_by('confirmacion').order_by('equipo')
					transEx = ListaExpres.objects.filter(movimiento__folio=m).order_by('confirmacion').order_by('expres')
					transAc = ListaAccesorio.objects.filter(movimiento__folio=m).order_by('confirmacion').order_by('accesorio')
					transFic = ListaFichas.objects.filter(movimiento__folio=m).order_by('confirmacion').order_by('ficha')
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__folio=m)

					ctx={'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('compras/confirmacionProductos.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('aceptEx'):
				s = request.GET.get('aceptEx','')
				grrr = request.GET.get('mChoice','')
				m = request.GET.get('transfGral','')
				if s:
					try:
						with transaction.atomic():
							mov = Movimiento.objects.get(folio=m)
							upd = ListaExpres.objects.get(id=s)
							upd.confirmacion = True
							upd.save()

							item = Expres.objects.get(id=upd.expres.id)
							sd = Sucursal.objects.get(nombre='Almacen Central')
							
							if grrr == 'robado':
								item.estatus = Estatus.objects.get(estatus='Robado')
								item.save()
								#confirmarItems(0,item,None,item.sucursal)
							else:
								item.sucursal=sd
								item.estatus = Estatus.objects.get(estatus='Existente')
								item.save()
								alm=AlmacenExpres()
								alm.sucursal=sd
								alm.expres=item
								alm.estado=True
								alm.save()
					except :
						info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."


					transEq = ListaEquipo.objects.filter(movimiento__folio=m).order_by('confirmacion').order_by('equipo')
					transEx = ListaExpres.objects.filter(movimiento__folio=m).order_by('confirmacion').order_by('expres')
					transAc = ListaAccesorio.objects.filter(movimiento__folio=m).order_by('confirmacion').order_by('accesorio')
					transFic = ListaFichas.objects.filter(movimiento__folio=m).order_by('confirmacion').order_by('ficha')
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__folio=m)

					ctx={'mostrar':True,'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('compras/confirmacionProductos.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('aceptAc'):
				s = request.GET.get('aceptAc','')
				grrr = request.GET.get('mChoice','')
				m = request.GET.get('transfGral','')
				if s:
					try:
						with transaction.atomic():
							mov = Movimiento.objects.get(folio=m)
							upd = ListaAccesorio.objects.get(id=s)
							upd.confirmacion = True
							upd.save()

							item = Accesorio.objects.get(id=upd.accesorio.id)
							sd = Sucursal.objects.get(nombre='Almacen Central')
							
							if grrr == 'robado':
								item.estatus = EstatusAccesorio.objects.get(estatus='Robado')
								item.save()
								#confirmarItems(0,item,None,item.sucursal)
							else:
								item.sucursal=sd
								item.estatus = EstatusAccesorio.objects.get(estatus='Existente')
								item.save()
								alm=AlmacenAccesorio()
								alm.sucursal=sd
								alm.accesorio=item
								alm.estado=True
								alm.save()
								#confirmarItems(0,item,sd,item.sucursal)
					except :
						info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."


					transEq = ListaEquipo.objects.filter(movimiento__folio=m).order_by('confirmacion').order_by('equipo')
					transEx = ListaExpres.objects.filter(movimiento__folio=m).order_by('confirmacion').order_by('expres')
					transAc = ListaAccesorio.objects.filter(movimiento__folio=m).order_by('confirmacion').order_by('accesorio')
					transFic = ListaFichas.objects.filter(movimiento__folio=m).order_by('confirmacion').order_by('ficha')
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__folio=m)

					ctx={'mostrar':True,'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('compras/confirmacionProductos.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('aceptFic'):
				s = request.GET.get('aceptFic','')
				grrr = request.GET.get('mChoice','')
				m = request.GET.get('transfGral','')
				if s:
					try:
						with transaction.atomic():
							mov = Movimiento.objects.get(folio=m)
							upd = ListaFichas.objects.get(id=s)
							upd.confirmacion = True
							upd.save()

							item = Ficha.objects.get(id=upd.ficha.id)
							sd = Sucursal.objects.get(nombre='Almacen Central')
							if grrr == 'robado':
								item.estatus = EstatusFicha.objects.get(estatus='Robado')
								item.save()
								#confirmarItems(0,item,None,item.sucursal)
							else:
								item.sucursal=sd
								item.estatusFicha = EstatusFicha.objects.get(estatus='Existente')
								item.save()
								alm=AlmacenFicha()
								alm.sucursal=sd
								alm.ficha=item
								alm.estado=True
								alm.save()
								#confirmarItems(0,item,sd,item.sucursal)
					except :
						info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."


					transEq = ListaEquipo.objects.filter(movimiento__folio=m).order_by('confirmacion').order_by('equipo')
					transEx = ListaExpres.objects.filter(movimiento__folio=m).order_by('confirmacion').order_by('expres')
					transAc = ListaAccesorio.objects.filter(movimiento__folio=m).order_by('confirmacion').order_by('accesorio')
					transFic = ListaFichas.objects.filter(movimiento__folio=m).order_by('confirmacion').order_by('ficha')
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__folio=m)

					ctx={'mostrar':True,'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('compras/confirmacionProductos.html',ctx,context_instance=RequestContext(request))

		ctx={'transferencias':pMovs,'query':query,'nivel':nivel}
		return render_to_response('compras/transferencias.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')
		
#listo - #yet
@login_required(login_url='/')
def compras_garantias_solicitudes_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
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

		paginator = Paginator(garantia, 25)
		pgar=None
		try:
			pgar = paginator.page(pagina)
		except PageNotAnInteger:
			pgar = paginator.page(1)
		except EmptyPage:
			pgar = paginator.page(paginator.num_pages)

		ctx={'nivel':nivel, 'garantias':pgar, 'query':query}
		return render_to_response('compras/mySolicitudGarantias.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#listo - #yet
@login_required(login_url='/')
def compras_garantias_consultar_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		
		formC = updGarantia()
		info =""
		mostrar = False
		buscar = True
		mostrarf = False
		query = ''
		results = []
		today = datetime.now() #fecha actual
		dateFormat = today.strftime("%d-%m-%Y") # fecha con formato

		if request.method == "GET":

			if request.GET.get('q'):
				if request.GET.get('q'):
					query = request.GET.get('q', '')
				if query:
					qset=(Q(sucursal__nombre__icontains=query) |Q(papeleta__folioPapeleta__icontains=query) | Q(papeleta__nombre__icontains=query) | Q(equipo__imei__icontains=query) | Q(equipo__icc__icontains=query))
					results = Garantia.objects.filter(qset).order_by('sucursal').order_by('fxSucursal').distinct()
					if results:
						info = ""
				else:
					results = []

				ctx = {'buscar':buscar,'mostrarf':mostrarf,"results": results,"query": query, 'info':info, 'nivel':nivel}
				return render_to_response('compras/mySeguimientoGarantias.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('upd'):
				query = request.GET.get('upd', '')
				if query:
					g = Garantia.objects.get(id = query)
					ptm = str( g.equipo.detallesEquipo.marca.marca + ' ' + g.equipo.detallesEquipo.modelo + ' ' + str(g.equipo.imei))
					if g.fxAlmacen == None:
						formC = updGarantia({'key':g.id,'papeleta':g.papeleta.folioPapeleta,'equipo':ptm,'fxAlmacen':today,'falla': g.falla, 'observacion':g.observacion })
					else:
						formC = updGarantia({'key':g.id,'papeleta':g.papeleta.folioPapeleta,'equipo':ptm,'fxAlmacen':g.fxAlmacen,'fxCAC':g.fxCAC ,'falla': g.falla, 'observacion':g.observacion })
						formC.fields['fxAlmacen']= forms.DateField()#attrs={'readonly':True}
						formC.fields['fxAlmacen'].widget.attrs={'readonly':True}
					mostrar = True
					buscar = False
					mostrarf = True

				else:
					info = "Resultados"

			ctx = {'buscar':buscar,'mostrarf':mostrarf,'mostrar':mostrar,'formC':formC ,'info':info, 'nivel':nivel}
			return render_to_response('compras/mySeguimientoGarantias.html',ctx,context_instance=RequestContext(request))

		if request.method == "POST":
			
			formC = updGarantia(request.POST or None)
			
			if formC.is_valid():
				try:
					with transaction.atomic():
						key = formC.cleaned_data['key']
						falla 		= formC.cleaned_data['falla']
						fxAlmacen 	= formC.cleaned_data['fxAlmacen']
						fxCAC 		= formC.cleaned_data['fxCAC']
						observacion = formC.cleaned_data['observacion']
						estado 		= formC.cleaned_data['estado']
						

						ham = Garantia.objects.get(id = key)
						ham.falla = falla
						ham.llegoAlmacen = True
						ham.fxAlmacen 	= fxAlmacen
						if fxCAC:
							ham.fxCAC 		= fxCAC
						ham.observacion = observacion
						ham.estado 		= EstadoGarantia.objects.get(id = estado)
						ham.fxRevision	= today
						ham.save()
						

						info = "Garantia. El Registro se ha actualizado con exito: " + ham.papeleta.folioPapeleta
						boton = False
						buscar = True
						mostrarf = False
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."

				ctx = {'buscar':buscar,'mostrarf':mostrarf, 'info':info, 'nivel':nivel}
				return render_to_response('compras/mySeguimientoGarantias.html',ctx,context_instance=RequestContext(request))

			else:
				info = "Verifique sus datos, actualizacion no realizada"
				formC = updGarantia(request.POST)
				mostrarf = True
				buscar = False

			
			ctx = {'buscar':buscar,'mostrarf':mostrarf, 'mostrar':mostrar, 'formC':formC, 'info':info, 'nivel':nivel}
			return render_to_response('compras/mySeguimientoGarantias.html',ctx,context_instance=RequestContext(request))
		
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_existencias_equipos_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		pagina=request.GET.get('pagina','')
		b_item=request.GET.get('item','')
		equipos=None
		nEquipos=0
		if b_item:
			qset=(Q(equipo__imei__icontains=b_item)|
			Q(equipo__icc__icontains=b_item)|
			Q(equipo__factura__folio__icontains=b_item)|
			Q(equipo__detallesEquipo__modelo__icontains=b_item)|
			Q(equipo__detallesEquipo__marca__marca__icontains=b_item)|
			Q(equipo__detallesEquipo__color__icontains=b_item)|
			Q(equipo__sucursal__nombre__icontains=b_item)|
			Q(equipo__noCell__icontains=b_item))
			equipos=AlmacenEquipo.objects.filter(qset,estado=True).order_by('equipo__imei')
		else:
			equipos=AlmacenEquipo.objects.filter(estado=True)
		paginator = Paginator(equipos, 50)
		nEquipos=len(equipos)
		equiposp=None
		try:
			equiposp = paginator.page(pagina)
		except PageNotAnInteger:
			equiposp = paginator.page(1)
		except EmptyPage:
			equiposp = paginator.page(paginator.num_pages)

		ctx={'nivel':nivel, 'equipos':equiposp, 'b_item':b_item,  'nEquipos':nEquipos}

		return render_to_response('compras/existenciasEquipo.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_existencias_accesorios_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		pagina=request.GET.get('pagina','')
		b_item=request.GET.get('item','')
		items=None
		nItems=0
		if b_item:
			qset=(Q(accesorio__codigoBarras__icontains=b_item)|
			Q(accesorio__factura__folio__icontains=b_item)|
			Q(accesorio__detallesAccesorio__marca__marca__icontains=b_item)|
			Q(accesorio__detallesAccesorio__seccion__seccion__icontains=b_item)|
			Q(accesorio__sucursal__nombre__icontains=b_item)|
			Q(accesorio__detallesAccesorio__descripcion__icontains=b_item))
			items=AlmacenAccesorio.objects.filter(qset,estado=True).order_by('accesorio__codigoBarras')
		else:
			items=AlmacenAccesorio.objects.filter(estado=True)
		paginator = Paginator(items, 50)
		nItems=len(items)
		itemsp=None
		try:
			itemsp = paginator.page(pagina)
		except PageNotAnInteger:
			itemsp = paginator.page(1)
		except EmptyPage:
			itemsp = paginator.page(paginator.num_pages)

		ctx={'nivel':nivel, 'items':itemsp, 'b_item':b_item,  'nItems':nItems}

		return render_to_response('compras/existenciasAccesorio.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_existencias_express_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		pagina=request.GET.get('pagina','')
		b_item=request.GET.get('item','')
		items=None
		nItems=0
		if b_item:
			qset=(Q(expres__icc__icontains=b_item)|
			Q(expres__factura__folio__icontains=b_item)|
			Q(expres__noCell__icontains=b_item)|
			Q(expres__detallesExpres__descripcion__icontains=b_item)|
			Q(expres__sucursal__nombre__icontains=b_item)|
			Q(expres__detallesExpres__tipoIcc__tipoIcc__icontains=b_item))
			items=AlmacenExpres.objects.filter(qset,estado=True).order_by('expres__icc')
		else:
			items=AlmacenExpres.objects.filter(estado=True)
		paginator = Paginator(items, 50)
		nItems=len(items)
		itemsp=None
		try:
			itemsp = paginator.page(pagina)
		except PageNotAnInteger:
			itemsp = paginator.page(1)
		except EmptyPage:
			itemsp = paginator.page(paginator.num_pages)

		ctx={'nivel':nivel, 'items':itemsp, 'b_item':b_item,  'nItems':nItems}

		return render_to_response('compras/existenciasExpres.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_existencias_fichas_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		pagina=request.GET.get('pagina','')
		b_item=request.GET.get('item','')
		items=None
		n100=0
		n200=0
		n500=0
		n300=0
		nItems=0

		if b_item:
			qset=(Q(ficha__folio__icontains=b_item)|
			Q(ficha__factura__folio__icontains=b_item)|
			Q(ficha__sucursal__nombre__icontains=b_item)|
			Q(ficha__nominacion__nominacion__icontains=b_item))
			items=AlmacenFicha.objects.filter(qset,estado=True).order_by('ficha__nominacion__nominacion','ficha__folio')
		else:
			items=AlmacenFicha.objects.filter(estado=True)

		n100=len(items.filter(estado=True,ficha__nominacion__nominacion=100))
		n200=len(items.filter(estado=True,ficha__nominacion__nominacion=200))
		n500=len(items.filter(estado=True,ficha__nominacion__nominacion=500))
		n300=len(items.filter(estado=True,ficha__nominacion__nominacion=300))

		paginator = Paginator(items, 50)
		nItems=len(items)
		itemsp=None
		try:
			itemsp = paginator.page(pagina)
		except PageNotAnInteger:
			itemsp = paginator.page(1)
		except EmptyPage:
			itemsp = paginator.page(paginator.num_pages)

		ctx={'nivel':nivel,'n100':n100,'n200':n200,'n500':n500,'n300':n300, 'items':itemsp, 'b_item':b_item,  'nItems':nItems}

		return render_to_response('compras/existenciasFichas.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_existencias_recargas_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		pagina=request.GET.get('pagina','')
		items=None

		items=SaldoSucursal.objects.all()

		paginator = Paginator(items, 50)
		itemsp=None
		try:
			itemsp = paginator.page(pagina)
		except PageNotAnInteger:
			itemsp = paginator.page(1)
		except EmptyPage:
			itemsp = paginator.page(paginator.num_pages)

		ctx={'nivel':nivel, 'items':itemsp}

		return render_to_response('compras/existenciasSaldos.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_existencias_almacen_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
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
				Q(equipo__detallesEquipo__color__icontains=query) |
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
				nineros.append([x.nombre.title(),nEq,nEx,nAc,nFi])
				#-------------------0------------1----2---3---4--

		
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
		return render_to_response('compras/existenciasTodo.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#nope
@login_required(login_url='/')
def compras_existencias_sucursal_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		return render_to_response('compras/index.html', {'nivel':nivel},context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_faltantes_equipos_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:

		b_sucursal=request.GET.get('sucursal','')
		r_sucu=None
		r_sucus=None
		stocks=None
		faltantes = []
		if b_sucursal:
			pass
		else:
			_usuario=Usuario.objects.get(user=request.user)
			_empleado=_usuario.empleado
			vSucural=VendedorSucursal.objects.get(empleado=_empleado)
			_sucursal=vSucural.sucursal
			b_sucursal=_sucursal.nombre

		if b_sucursal:
			try:
				r_sucu=Sucursal.objects.get(nombre=b_sucursal)
				stocks=StockEquipo.objects.filter(sucursal=r_sucu)
			except :
				qset=(Q(tipoSucursal__tipo__icontains=b_sucursal)|
				Q(nombre__icontains=b_sucursal)|
				Q(encargado__nombre__icontains=b_sucursal)|
				Q(noCelOfi__icontains=b_sucursal)|
				Q(direccion__icontains=b_sucursal))
				r_sucus=Sucursal.objects.filter(qset).distinct()


		if stocks:
			for stock in stocks:
				if stock.stockMin and stock.stockMax:
					faltante=''
					existentes=len(Equipo.objects.filter(sucursal=r_sucu, detallesEquipo=stock.detalle, estatus__estatus='Existente'))
					if stock.stockMin>existentes:
						faltantes.append([stock.detalle,existentes,stock.stockMin,(stock.stockMin-existentes)])

		ctx={'nivel':nivel,'r_sucus':r_sucus, 'b_sucursal':b_sucursal,'faltantes':faltantes}


		return render_to_response('compras/FaltantesEquipo.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_faltantes_accesorios_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:

		b_sucursal=request.GET.get('sucursal','')
		r_sucu=None
		r_sucus=None
		stocks=None
		faltantes = []
		if b_sucursal:
			pass
		else:
			_usuario=Usuario.objects.get(user=request.user)
			_empleado=_usuario.empleado
			vSucural=VendedorSucursal.objects.get(empleado=_empleado)
			_sucursal=vSucural.sucursal
			b_sucursal=_sucursal.nombre
		if b_sucursal:
			try:
				r_sucu=Sucursal.objects.get(nombre=b_sucursal)
				stocks=StockAccesorio.objects.filter(sucursal=r_sucu)
			except :
				qset=(Q(tipoSucursal__tipo__icontains=b_sucursal)|
				Q(nombre__icontains=b_sucursal)|
				Q(encargado__nombre__icontains=b_sucursal)|
				Q(noCelOfi__icontains=b_sucursal)|
				Q(direccion__icontains=b_sucursal))
				r_sucus=Sucursal.objects.filter(qset).distinct()

		if stocks:
			for stock in stocks:
				if stock.stockMin and stock.stockMax:
					faltante=''
					existentes=len(Accesorio.objects.filter(sucursal=r_sucu, detallesAccesorio=stock.detalle, estatusAccesorio__estatus='Existente'))
					if stock.stockMin>existentes:
						faltantes.append([stock.detalle,existentes,stock.stockMin,(stock.stockMin-existentes)])

		ctx={'nivel':nivel,'r_sucus':r_sucus, 'b_sucursal':b_sucursal,'faltantes':faltantes}
		return render_to_response('compras/FaltantesAccesorios.html',ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_faltantes_express_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:

		b_sucursal=request.GET.get('sucursal','')
		r_sucu=None
		r_sucus=None
		stock=None
		faltantes = []
		if b_sucursal:
			pass
		else:
			_usuario=Usuario.objects.get(user=request.user)
			_empleado=_usuario.empleado
			vSucural=VendedorSucursal.objects.get(empleado=_empleado)
			_sucursal=vSucural.sucursal
			b_sucursal=_sucursal.nombre
		if b_sucursal:
			try:
				r_sucu=Sucursal.objects.get(nombre=b_sucursal)
				try:
					stock=StockExpres.objects.get(sucursal=r_sucu)
				except :
					pass
				
			except :
				qset=(Q(tipoSucursal__tipo__icontains=b_sucursal)|
				Q(nombre__icontains=b_sucursal)|
				Q(encargado__nombre__icontains=b_sucursal)|
				Q(noCelOfi__icontains=b_sucursal)|
				Q(direccion__icontains=b_sucursal))
				r_sucus=Sucursal.objects.filter(qset).distinct()

		if stock:
			if stock.stockMin and stock.stockMax:
				faltante=''
				existentes=len(Expres.objects.filter(sucursal=r_sucu, estatus__estatus='Existente'))
				if stock.stockMin>existentes:
					faltantes.append([existentes,stock.stockMin,(stock.stockMin-existentes)])

		ctx={'nivel':nivel,'r_sucus':r_sucus, 'b_sucursal':b_sucursal,'faltantes':faltantes}
		return render_to_response('compras/FaltantesExpres.html',ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_faltantes_fichas_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:

		b_sucursal=request.GET.get('sucursal','')
		r_sucu=None
		r_sucus=None
		stocks=None
		faltantes = []
		if b_sucursal:
			pass
		else:
			_usuario=Usuario.objects.get(user=request.user)
			_empleado=_usuario.empleado
			vSucural=VendedorSucursal.objects.get(empleado=_empleado)
			_sucursal=vSucural.sucursal
			b_sucursal=_sucursal.nombre
		if b_sucursal:
			try:
				r_sucu=Sucursal.objects.get(nombre=b_sucursal)
				stocks=StockFicha.objects.filter(sucursal=r_sucu)
			except :
				qset=(Q(tipoSucursal__tipo__icontains=b_sucursal)|
				Q(nombre__icontains=b_sucursal)|
				Q(encargado__nombre__icontains=b_sucursal)|
				Q(noCelOfi__icontains=b_sucursal)|
				Q(direccion__icontains=b_sucursal))
				r_sucus=Sucursal.objects.filter(qset).distinct()

		if stocks:
			for stock in stocks:
				if stock.stockMin and stock.stockMax:
					faltante=''
					existentes=len(Ficha.objects.filter(sucursal=r_sucu, nominacion=stock.nominacion, estatusFicha__estatus='Existente'))
					if stock.stockMin>existentes:
						faltantes.append([stock.nominacion,existentes,stock.stockMin,(stock.stockMin-existentes)])

		ctx={'nivel':nivel,'r_sucus':r_sucus, 'b_sucursal':b_sucursal,'faltantes':faltantes}
		return render_to_response('compras/FaltantesFichas.html',ctx ,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_faltantes_recargas_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:

		b_sucursal=request.GET.get('sucursal','')
		r_sucu=None
		r_sucus=None
		stock=None
		faltantes = []
		if b_sucursal:
			pass
		else:
			_usuario=Usuario.objects.get(user=request.user)
			_empleado=_usuario.empleado
			vSucural=VendedorSucursal.objects.get(empleado=_empleado)
			_sucursal=vSucural.sucursal
			b_sucursal=_sucursal.nombre
		if b_sucursal:
			try:
				r_sucu=Sucursal.objects.get(nombre=b_sucursal)
				try:
					stock=SaldoStock.objects.get(sucursal=r_sucu)
				except :
					pass
				
			except :
				qset=(Q(tipoSucursal__tipo__icontains=b_sucursal)|
				Q(nombre__icontains=b_sucursal)|
				Q(encargado__nombre__icontains=b_sucursal)|
				Q(noCelOfi__icontains=b_sucursal)|
				Q(direccion__icontains=b_sucursal))
				r_sucus=Sucursal.objects.filter(qset).distinct()

		if stock:
			if stock.minimo and stock.maximo:
				faltante=''
				existentes=0
				try:
					suc=SaldoSucursal.objects.get(sucursal=r_sucu)
					existentes=suc.saldo
				except :
					pass
				if stock.minimo>existentes:
					#faltante='Requiere: %s, Existencias, %s'%( stock.minimo,existentes)
					faltantes.append([stock.minimo,existentes])


		ctx={'nivel':nivel,'r_sucus':r_sucus, 'b_sucursal':b_sucursal,'faltantes':faltantes}

		return render_to_response('compras/FaltantesSaldo.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#yet
@login_required(login_url='/')
def compras_faltantes_consultar_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:

		b_sucursal=request.GET.get('sucursal','')
		r_sucu=None
		r_sucus=None
		stocks1=None
		stocks2=None
		stock3=None
		stocks4=None
		stock5=None
		sucu=False
		faltantes1 = []
		faltantes2 = []
		faltantes3 = []
		faltantes4 = []
		faltantes5 = []
		if b_sucursal:
			pass
		else:
			_usuario=Usuario.objects.get(user=request.user)
			_empleado=_usuario.empleado
			vSucural=VendedorSucursal.objects.get(empleado=_empleado)
			_sucursal=vSucural.sucursal
			b_sucursal=_sucursal.nombre

		if b_sucursal:
			try:
				r_sucu=Sucursal.objects.get(nombre=b_sucursal)
				sucu=True
				stocks1=StockEquipo.objects.filter(sucursal=r_sucu)
				stocks2=StockAccesorio.objects.filter(sucursal=r_sucu)
				try:
					stock3=StockExpres.objects.get(sucursal=r_sucu)
				except :
					pass
				stocks4=StockFicha.objects.filter(sucursal=r_sucu)
				try:
					stock5=SaldoStock.objects.get(sucursal=r_sucu)
				except :
					pass
			except :
				qset=(Q(tipoSucursal__tipo__icontains=b_sucursal)|
				Q(nombre__icontains=b_sucursal)|
				Q(encargado__nombre__icontains=b_sucursal)|
				Q(noCelOfi__icontains=b_sucursal)|
				Q(direccion__icontains=b_sucursal))
				r_sucus=Sucursal.objects.filter(qset).distinct()
				sucu=False


		if stocks1:
			for stock in stocks1:
				if stock.stockMin and stock.stockMax:
					faltante=''
					existentes=len(Equipo.objects.filter(sucursal=r_sucu, detallesEquipo=stock.detalle, estatus__estatus='Existente'))
					if stock.stockMin>existentes:
						#faltante='Modelo: %s, Requiere: %s, Existencias, %s, Faltantes: %s'%(stock.detalle, stock.stockMin,existentes, (stock.stockMin-existentes))
						faltantes1.append([stock.detalle,existentes,stock.stockMin,(stock.stockMin-existentes)]) # eq 

		if stocks2:
			for stock in stocks2:
				if stock.stockMin and stock.stockMax:
					faltante=''
					existentes=len(Accesorio.objects.filter(sucursal=r_sucu, detallesAccesorio=stock.detalle, estatusAccesorio__estatus='Existente'))
					if stock.stockMin>existentes:
						#faltante='Modelo: %s, Requiere: %s, Existencias, %s, Faltantes: %s'%(stock.detalle, stock.stockMin,existentes, (stock.stockMin-existentes))
						faltantes2.append([stock.detalle,existentes,stock.stockMin,(stock.stockMin-existentes)]) # acc 


		if stock3:
			if stock3.stockMin and stock3.stockMax:
				faltante=''
				existentes=len(Expres.objects.filter(sucursal=r_sucu, estatus__estatus='Existente'))
				if stock3.stockMin>existentes:
					#faltante='Requiere: %s, Existencias, %s, Faltantes: %s'%( stock3.stockMin,existentes, (stock3.stockMin-existentes))
					faltantes3.append([existentes,stock3.stockMin,(stock3.stockMin-existentes)])

		if stocks4:
			for stock in stocks4:
				if stock.stockMin and stock.stockMax:
					faltante=''
					existentes=len(Ficha.objects.filter(sucursal=r_sucu, nominacion=stock.nominacion, estatusFicha__estatus='Existente'))
					if stock.stockMin>existentes:
						#faltante='Nominacion: %s, Requiere: %s, Existencias, %s, Faltantes: %s'%(stock.nominacion, stock.stockMin,existentes, (stock.stockMin-existentes))
						faltantes4.append([stock.nominacion,existentes,stock.stockMin,(stock.stockMin-existentes)]) #fichas 

		if stock5:
			if stock5.minimo and stock5.maximo:
				faltante=''
				existentes=0
				try:
					suc=SaldoSucursal.objects.get(sucursal=r_sucu)
					existentes=suc.saldo
				except :
					pass
				if stock5.minimo>existentes:
					#faltante='Requiere: %s, Existencias, %s'%( stock5.minimo,existentes)
					faltantes5.append([stock5.minimo,existentes]) # recarga


		ctx={'nivel':nivel,'r_sucus':r_sucus, 'b_sucursal':b_sucursal, 'sucu':sucu,'faltantes1':faltantes1,'faltantes2':faltantes2,'faltantes3':faltantes3,'faltantes4':faltantes4,'faltantes5':faltantes5}

		return render_to_response('compras/FaltantesSucursal.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo - #yet 1 ticket probado
@login_required(login_url='/')
def compras_ventas_mayoreo_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	
	if nivel != -1:

		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		
		form = AddVentaCaja()
		form2 = AddVentaRecarga()
		form3 = AsignarMayorista()
		
		resultAdd = ""
		queryEq  = ""
		queryExp = ""
		queryAcc = ""
		queryFic = ""
		queryRec = ""
		informeFichas = []
		show = True
		info=""
		vta = nuevoFolio('M',request.user,None)
		form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas(vta)})
		eqVendido = None
		expVendido = None
		ficVendido = None
		accVendido = None
		recVendido = None
		try:
			eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
			expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
			ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
			accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
			recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
		
		if request.method == "GET":
			m=None
			vta = request.GET.get('vtaGral','')
			if request.GET.get('addEq'):
				queryEq = request.GET.get('qEq','')
				try:
					with transaction.atomic():
						resultAdd = addEquipoVta1(queryEq,request.GET.get('mcPrecio'),mysucursal, vta,request.user)
						updVta(vta,mysucursal,request.user)
				except :
					resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				
				form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas(vta)})
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
				show=True
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,
				'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,
				'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myVentasAdd.html',ctx,context_instance=RequestContext(request))
				
			if request.GET.get('addExp'):
				queryExp = request.GET.get('qExp','')
				try:
					with transaction.atomic():
						resultAdd = addExpresVta1(queryExp,request.GET.get('mcPrecio') ,mysucursal, vta,request.user)
						updVta(vta,mysucursal,request.user)
				except :
					resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				
				form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas(vta)})

				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
				show=True
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,
				'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,
				'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myVentasAdd.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addAcc'):
				queryAcc = request.GET.get('qAcc','')
				try:
					with transaction.atomic():
						resultAdd = addAccVta1(queryAcc,request.GET.get('mcPrecio'),mysucursal, vta,request.user)
						updVta(vta,mysucursal,request.user)
				except :
					resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				
				form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas(vta)})
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
				show=True
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,
				'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,
				'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myVentasAdd.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addFic'):
				queryFic = request.GET.get('qFic','')
				queryFic2 = request.GET.get('qFic2','')
				cliente = request.GET.get('cliente')
				try:
					with transaction.atomic():
						resultAdd = addFichaVta1(queryFic,queryFic2,None,mysucursal, vta, request.user,cliente)					
						updVta(vta,mysucursal,request.user)
				except :
					resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				
				form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas(vta)})
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
				show=True
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,
				'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,
				'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myVentasAdd.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addRec'):
				folio = request.GET.get('folio')
				rfolio = request.GET.get('rfolio')
				montos = request.GET.get('montos')
				observaciones = request.GET.get('observaciones')
				cliente = request.GET.get('cliente')

				if folio or rfolio and vta:
					try:
						with transaction.atomic():
							resultAdd = addRecarga1(rfolio,folio,montos, observaciones,None ,mysucursal, vta,request.user, cliente)				
					except :
						resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				else:
					resultAdd = "Ingrese un Folio o Genere uno."
				
				updVta(vta,mysucursal,request.user)
				form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas(vta)})
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
				show=True
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,
				'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,
				'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myVentasAdd.html',ctx,context_instance=RequestContext(request))

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
					return render_to_response('compras/ticket.html',ctx,context_instance=RequestContext(request))
		
		if 'cobrar' in request.POST:
			form = AddVentaCaja(request.POST)
			form3 = AsignarMayorista(request.POST)
			if form.is_valid() and form3.is_valid():
				ifolioVenta = form.cleaned_data['folioVenta']
				efectivo 	= form.cleaned_data['efectivo']
				total 		= form.cleaned_data['total']

				cliente = form3.cleaned_data['cliente']

				if efectivo >= total and total > 0:
					try:
						with transaction.atomic():
							vtaGral =  Venta.objects.get(folioVenta=ifolioVenta)
							vtaGral.total 		= total
							vtaGral.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
							vtaGral.mayoreo  	= True
							vtaGral.aceptada  	= True
							vtaGral.estado 		= EstadoVenta.objects.get(estado='Pagada')
							vtaGral.save()
							
							#asginar venta a mayorista
							a =VentaMayoreo()
							a.folioVenta 		= vtaGral
							a.clienteMayoreo 	= Mayorista.objects.get(id=cliente)
							a.descuentoAplicado = 0
							a.save()

							form2 = AddVentaRecarga()
							form3 = AsignarMayorista()

							vta= nuevoFolio('M',request.user,None)
							form = AddVentaCaja({'folioVenta':vta,'total':0})
							show= False
							info=" Venta "+vtaGral.estado.estado+" - " + vtaGral.folioVenta +" Cambio: $ "+str(efectivo - total)+" - Cliente: " + a.clienteMayoreo.cliente.razonSocial
							mfolioVenta = vtaGral.folioVenta
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
					
					ctx = { 'folioVenta':mfolioVenta,'show':show,'url':'/compras/ventas/mayoreo/' ,'vtaGenerada':vta,'cliente':form3,'recForm':form2,'vtaForm':form,'nivel':nivel,'info':info}
					return render_to_response('compras/myVentasAdd.html',ctx,context_instance=RequestContext(request))
				else:
					show = True
					info = "El pago debe ser mayor o igual al monto total a pagar. Debe ingresar por lo menos un producto a la venta"
					form = AddVentaCaja(request.POST)
					form3 = AsignarMayorista(request.POST)
					ctx = {'show':show ,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
					return render_to_response('compras/myVentasAdd.html',ctx,context_instance=RequestContext(request))
			else:
				form = AddVentaCaja(request.POST)
				info = "Ingrese $monto del cliente a pagar. Debe ingresar al menos un producto a la venta"
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myVentasAdd.html',ctx,context_instance=RequestContext(request))

		if 'cancelar' in request.POST:
			form = AddVentaCaja(request.POST)
			if form.is_valid() :
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
							vtaGral.mayoreo  	= True
							vtaGral.estado 		= EstadoVenta.objects.get(estado='Cancelada')
							vtaGral.save()
							
							results = cancelaProductos(vtaGral.id) # Poner productos en cancelacion

							info="Venta Cancelada: "+ vtaGral.folioVenta +"- En espera de autorizacion."+results
							form = AddVentaCaja()
							form2 = AddVentaRecarga()
							form3 = AsignarMayorista()
							vta= nuevoFolio('M',request.user,None) #mayoreo
							form = AddVentaCaja({'folioVenta':vta,'total':0})
							show=False
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
					
					ctx = {'show':show,'vtaGenerada':vta,'cliente':form3,'recForm':form2,'vtaForm':form,'nivel':nivel,'info':info}
					return render_to_response('compras/myVentasAdd.html',ctx,context_instance=RequestContext(request))
				else:
					form = AddVentaCaja(request.POST)
					info = "Debe ingresar al menos un producto a la venta."
					ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
					return render_to_response('compras/myVentasAdd.html',ctx,context_instance=RequestContext(request))	
			else:
				form = AddVentaCaja(request.POST)
				info = "Ingrese el monto que pago el cliente, si en dado caso se cancelo, ponga un 0. Debe ingresar por lo menos un producto a la venta."
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myVentasAdd.html',ctx,context_instance=RequestContext(request))
		
		vta = nuevoFolio('M',request.user,None)
		form = AddVentaCaja({'folioVenta':vta,'total':0})
		ctx = {'show':show,'vtaGenerada':vta,'cliente':form3,'recForm':form2,'vtaForm':form,'nivel':nivel,'info':info}
		return render_to_response('compras/myVentasAdd.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#listo - #yet 1 ticket probado
@login_required(login_url='/')
def compras_ventas_credito_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:

		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		
		form = AddVentaCredito()
		form2 = AddVentaRecarga()
		form3 = AsignarACredito()
		
		resultAdd = ""
		queryEq  = ""
		queryExp = ""
		queryAcc = ""
		queryFic = ""
		queryRec = ""
		informeFichas = []
		show = True
		info=""
		vta = nuevoFolio('CR',request.user,None)
		form = AddVentaCredito({'folioVenta':vta,'total':sumaVtas(vta)})
		eqVendido = None
		expVendido = None
		ficVendido = None
		accVendido = None
		recVendido = None
		try:
			eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
			expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
			ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
			accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
			recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
		
		if request.method == "GET":
			m=None
			if request.GET.get('addEq'):
				queryEq = request.GET.get('qEq','')
				vta = request.GET.get('vtaGral','')
				try:
					with transaction.atomic():
						resultAdd = addEquipoVta1(queryEq,request.GET.get('mcPrecio'),mysucursal, vta,request.user)
						updVta(vta,mysucursal,request.user)
				except :
					resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				
				form = AddVentaCredito({'folioVenta':vta,'total':sumaVtas(vta)})

				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
				show=True
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myAddVtaCredito.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addExp'):
				queryExp = request.GET.get('qExp','')
				vta = request.GET.get('vtaGral','')
				try:
					with transaction.atomic():
						resultAdd = addExpresVta1(queryExp,request.GET.get('mcPrecio') ,mysucursal, vta,request.user)
						updVta(vta,mysucursal,request.user)
				except :
					resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				
				form = AddVentaCredito({'folioVenta':vta,'total':sumaVtas(vta)})
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
				show=True
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myAddVtaCredito.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addAcc'):
				queryAcc = request.GET.get('qAcc','')
				vta = request.GET.get('vtaGral','')

				try:
					with transaction.atomic():
						resultAdd = addAccVta1(queryAcc,request.GET.get('mcPrecio'),mysucursal, vta,request.user)
						updVta(vta,mysucursal,request.user)
				except :
					resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				
				form = AddVentaCredito({'folioVenta':vta,'total':sumaVtas(vta)})

				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
				show=True
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myAddVtaCredito.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addFic'):
				queryFic = request.GET.get('qFic','')
				queryFic2 = request.GET.get('qFic2','')
				vta = request.GET.get('vtaGral','')

				try:
					with transaction.atomic():
						resultAdd = addFichaVta1(queryFic,queryFic2,request.GET.get('dto',''),mysucursal, vta, request.user,None)
						updVta(vta,mysucursal,request.user)
				except :
					resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				
				form = AddVentaCredito({'folioVenta':vta,'total':sumaVtas(vta)})
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
				show=True
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myAddVtaCredito.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addRec'):
				vta = request.GET.get('vtaGral','')
				folio = request.GET.get('folio')
				rfolio = request.GET.get('rfolio')
				montos = request.GET.get('montos')
				observaciones = request.GET.get('observaciones')

				if folio or rfolio and vta:
					try:
						with transaction.atomic():
							resultAdd = addRecarga1(rfolio,folio,montos, observaciones,request.GET.get('dto','') ,mysucursal, vta,request.user, None)
					except :
						resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				
				else:
					resultAdd = "Ingrese un Folio o Genere uno."
					
				updVta(vta,mysucursal,request.user)
				form = AddVentaCredito({'folioVenta':vta,'total':sumaVtas(vta)})
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
				show=True
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myAddVtaCredito.html',ctx,context_instance=RequestContext(request))

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
					return render_to_response('compras/ticket.html',ctx,context_instance=RequestContext(request))

		if 'cobrar' in request.POST:
			form = AddVentaCredito(request.POST)
			form3 = AsignarACredito(request.POST)
			if form.is_valid() and form3.is_valid():
				ifolioVenta = form.cleaned_data['folioVenta']
				anticipo 	= form.cleaned_data['anticipo']
				total 		= form.cleaned_data['total']
				plazo 		= form.cleaned_data['plazo']
				observacion = form.cleaned_data['observacion']

				cliente = form3.cleaned_data['cliente']
				mfolioVenta = None
				limite = Subdistribuidor.objects.get(id=cliente).limCredito
				if anticipo > 0 and total > 0:
					if anticipo >= total:
						try:
							with transaction.atomic():
								vtaGral =  Venta.objects.get(folioVenta=ifolioVenta)
								vtaGral.total 		= total
								vtaGral.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
								vtaGral.credito  	= True
								vtaGral.aceptada  	= True
								vtaGral.estado 		= EstadoVenta.objects.get(estado='Pagada')
								vtaGral.save()

								a = Credito()
								a.folioc 	= nuevoFolio('CR',request.user,None)
								a.subdist 	= Subdistribuidor.objects.get(id=cliente)
								a.venta 	= vtaGral
								a.totalvta 	= vtaGral.total
								a.plazo 	= 0
								a.edo 		= EstadoCredito.objects.get(estado='Pagado')
								a.observacion = observacion
								a.save()

								b = HistorialSubdistribuidor()
								b.credito = a
								b.abono 	= total
								b.save()

								info=" Venta "+vtaGral.estado.estado+" - " + vtaGral.folioVenta +" Cambio: $ "+str(anticipo - total)+" - Cliente: " + a.subdist.cliente.razonSocial+' Credito: '+a.folioc
								mfolioVenta = vtaGral.folioVenta
								form = AddVentaCredito()
								form2 = AddVentaRecarga()
								form3 = AsignarACredito()
								vta= nuevoFolio('CR',request.user,None) #mayoreo
								form = AddVentaCredito({'folioVenta':vta,'total':0})
						except :
							info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
						ctx = {'folioVenta':mfolioVenta ,'vtaGenerada':vta,'cliente':form3,'recForm':form2,'vtaForm':form,'nivel':nivel,'info':info}
						return render_to_response('compras/myAddVtaCredito.html',ctx,context_instance=RequestContext(request))
					else:
						agregar = False
						try:
							qset = (Q(edo__estado__icontains='Adeudo') | Q(edo__estado__icontains='Cobrar'))
							otorgado = Credito.objects.filter(qset,subdist__id=cliente).distinct()
							sumar = 0
							
							for x in otorgado:
								sumar = sumar + x.totalvta
							puede = limite - sumar
							
							if puede == 0 and total > puede:
								agregar = False
							elif total <= puede:
								agregar = True
							
							if agregar == True:
								try:
									with transaction.atomic():
										vtaGral =  Venta.objects.get(folioVenta=ifolioVenta)
										vtaGral.total 		= total
										vtaGral.tipoPago 	= TipoPago.objects.get(tipo='Credito')
										vtaGral.credito  	= True
										vtaGral.aceptada  	= True
										vtaGral.estado 		= EstadoVenta.objects.get(estado='Proceso')
										vtaGral.save()

										a = Credito()
										a.folioc 	= nuevoFolio('CR',request.user,None)
										a.subdist 	= Subdistribuidor.objects.get(id=cliente)
										a.venta 	= vtaGral
										a.totalvta 	= vtaGral.total
										a.plazo 	= plazo
										a.edo 		= EstadoCredito.objects.get(estado='Adeudo')
										a.observacion = observacion
										a.save()

										b = HistorialSubdistribuidor()
										b.credito = a
										b.abono = anticipo
										b.save()

										d = Anticipo()
										d.folioVenta = vtaGral
										d.tipoAnticipo = 'Anticipo de Credito'
										d.monto = anticipo
										d.save()

										info=" Venta "+vtaGral.estado.estado+" - " + vtaGral.folioVenta +" Resta: $ "+str(total - anticipo)+" - Cliente: " + a.subdist.cliente.razonSocial+' Credito: '+a.folioc
										mfolioVenta = vtaGral.folioVenta
										form2 = AddVentaRecarga()
										form3 = AsignarACredito()
										vta= nuevoFolio('M',request.user,None)
										form = AddVentaCredito({'folioVenta':vta,'total':0})
										show= False
								except :
									info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
								
								ctx = { 'folioVenta':mfolioVenta,'vtaGenerada':vta,'cliente':form3,'recForm':form2,'vtaForm':form,'nivel':nivel,'info':info}
								return render_to_response('compras/myAddVtaCredito.html',ctx,context_instance=RequestContext(request))
							else:
								try:
									with transaction.atomic():
										vtaGral =  Venta.objects.get(folioVenta=ifolioVenta)
										vtaGral.total 		= total
										vtaGral.tipoPago 	= TipoPago.objects.get(tipo='Credito')
										vtaGral.aceptada 	= False
										vtaGral.credito  	= True
										vtaGral.estado 		= EstadoVenta.objects.get(estado='Cancelada')
										vtaGral.save()
										
										info="Venta Cancelada: "+ vtaGral.folioVenta+ "- En espera de autorizacion. No se genero el credito. Credito limitado al total de la venta."
										form = AddVentaCredito()
										form2 = AddVentaRecarga()
										form3 = AsignarACredito()
										vta= nuevoFolio('CR',request.user,None) #mayoreo
										form = AddVentaCredito({'folioVenta':vta,'total':0})
								except :
									info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'

								ctx = {'vtaGenerada':vta,'cliente':form3,'recForm':form2,'vtaForm':form,'nivel':nivel,'info':info}
								return render_to_response('compras/myAddVtaCredito.html',ctx,context_instance=RequestContext(request))
						
						except Credito.DoesNotExist:
							if total <= limite:
								try:
									with transaction.atomic():
										vtaGral =  Venta.objects.get(folioVenta=ifolioVenta)
										vtaGral.total 		= total
										vtaGral.tipoPago 	= TipoPago.objects.get(tipo='Credito')
										vtaGral.credito  	= True
										vtaGral.aceptada  	= True
										vtaGral.estado 		= EstadoVenta.objects.get(estado='Proceso')
										vtaGral.save()

										a = Credito()
										a.folioc 	= nuevoFolio('CR',request.user,None)
										a.subdist 	= Subdistribuidor.objects.get(id=cliente)
										a.venta 	= vtaGral
										a.totalvta 	= vtaGral.total
										a.plazo 	= plazo
										a.edo 		= EstadoCredito.objects.get(estado='Adeudo')
										a.observacion = observacion
										a.save()

										b = HistorialSubdistribuidor()
										b.credito = a
										b.abono = anticipo
										b.save()

										d = Anticipo()
										d.folioVenta = vtaGral
										d.tipoAnticipo = 'Anticipo de Credito'
										d.monto = anticipo
										d.save()

										info=" Venta "+vtaGral.estado.estado+" - " + vtaGral.folioVenta +" Resta: $ "+str(total - anticipo)+" - Cliente: " + a.subdist.cliente.razonSocial+' Credito: '+a.folioc
										mfolioVenta = vtaGral.folioVenta
										form2 = AddVentaRecarga()
										form3 = AsignarACredito()
										vta= nuevoFolio('M',request.user,None)
										form = AddVentaCredito({'folioVenta':vta,'total':0})
										show= False
								except :
									info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
								
								ctx = { 'folioVenta':mfolioVenta,'vtaGenerada':vta,'cliente':form3,'recForm':form2,'vtaForm':form,'nivel':nivel,'info':info}
								return render_to_response('compras/myAddVtaCredito.html',ctx,context_instance=RequestContext(request))
							else:
								try:
									with transaction.atomic():
										vtaGral =  Venta.objects.get(folioVenta=ifolioVenta)
										vtaGral.total 		= total
										vtaGral.tipoPago 	= TipoPago.objects.get(tipo='Credito')
										vtaGral.aceptada 	= False
										vtaGral.credito  	= True
										vtaGral.estado 		= EstadoVenta.objects.get(estado='Cancelada')
										vtaGral.save()
										
										info="Venta Cancelada: "+ vtaGral.folioVenta + " - En espera de autorizacion. No se genero el credito, la venta es mayor al limite de credito autorizado."
										form = AddVentaCredito()
										form2 = AddVentaRecarga()
										form3 = AsignarACredito()
										vta= nuevoFolio('CR',request.user,None) #mayoreo
										form = AddVentaCredito({'folioVenta':vta,'total':0})
								except :
									info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
								
								ctx = {'vtaGenerada':vta,'cliente':form3,'recForm':form2,'vtaForm':form,'nivel':nivel,'info':info}
								return render_to_response('compras/myAddVtaCredito.html',ctx,context_instance=RequestContext(request))
					
				else:
					show = True
					info = "El anticipo debe ser mayor que 0. Debe ingresar por lo menos un producto a la venta"
					form = AddVentaCredito(request.POST)
					form3 = AsignarACredito(request.POST)
					ctx = {'show':show ,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
					return render_to_response('compras/myAddVtaCredito.html',ctx,context_instance=RequestContext(request))
			else:
				form = AddVentaCredito(request.POST)
				info = "Ingrese $anticipo del cliente a pagar. Debe ingresar al menos un producto a la venta"
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myAddVtaCredito.html',ctx,context_instance=RequestContext(request))

		if 'cancelar' in request.POST:
			form = AddVentaCredito(request.POST)
			form3 = AsignarACredito(request.POST)
			if form.is_valid():
				ifolioVenta = form.cleaned_data['folioVenta']
				anticipo 	= form.cleaned_data['anticipo']
				total 		= form.cleaned_data['total']
				plazo 		= form.cleaned_data['plazo']
				observacion = form.cleaned_data['observacion']

				if total > 0:
					try:
						with transaction.atomic():
							vtaGral =  Venta.objects.get(folioVenta=ifolioVenta)
							vtaGral.total 		= total
							vtaGral.tipoPago 	= TipoPago.objects.get(tipo='Credito')
							vtaGral.aceptada 	= False
							vtaGral.credito  	= True
							vtaGral.estado 		= EstadoVenta.objects.get(estado='Cancelada')
							vtaGral.save()

							results = cancelaProductos(vtaGral.id) # Poner productos en cancelacion
							
							info="Venta Cancelada: "+ vtaGral.folioVenta  + "- En espera de autorizacion. No se genero el credito "+results
							form = AddVentaCredito()
							form2 = AddVentaRecarga()
							form3 = AsignarACredito()
							vta= nuevoFolio('CR',request.user,None) #mayoreo
							form = AddVentaCredito({'folioVenta':vta,'total':0})
							show=False
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
					
					ctx = {'show':show,'vtaGenerada':vta,'cliente':form3,'recForm':form2,'vtaForm':form,'nivel':nivel,'info':info}
					return render_to_response('compras/myAddVtaCredito.html',ctx,context_instance=RequestContext(request))
				else:
					form = AddVentaCredito(request.POST)
					info = "Debe ingresar al menos un producto a la venta."
					ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
					return render_to_response('compras/myAddVtaCredito.html',ctx,context_instance=RequestContext(request))
			else:
				form = AddVentaCredito(request.POST)
				info = "Ingrese el monto que pago el cliente, si en dado caso se cancelo, ponga un 0. Debe ingresar por lo menos un producto a la venta."
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'cliente':form3,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myAddVtaCredito.html',ctx,context_instance=RequestContext(request))
		
		vta = nuevoFolio('CR',request.user,None)
		form = AddVentaCredito({'folioVenta':vta,'total':0})
		ctx = {'vtaGenerada':vta,'cliente':form3,'recForm':form2,'vtaForm':form,'nivel':nivel,'info':info}
		return render_to_response('compras/myAddVtaCredito.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#listo - #yet 1 ticket probado
@login_required(login_url='/')
def compras_ventas_contado_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:

		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		
		form = AddVentaCaja()
		form2 = AddVentaRecarga()		
		
		resultAdd = ""
		queryEq  = ""
		queryExp = ""
		queryAcc = ""
		queryFic = ""
		queryRec = ""
		informeFichas = []
		show = True
		info=""
		vta = nuevoFolio('E',request.user,None)
		form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas(vta)})
		eqVendido = None
		expVendido = None
		ficVendido = None
		accVendido = None
		recVendido = None
		try:
			eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
			expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
			ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
			accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
			recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
		
		if request.method == "GET":
			m=None
			if request.GET.get('addEq'):
				queryEq = request.GET.get('qEq','')
				vta = request.GET.get('vtaGral','')

				try:
					with transaction.atomic():
						resultAdd = addEquipoVta1(queryEq,request.GET.get('mcPrecio')  ,mysucursal, vta, request.user)
						updVta(vta,mysucursal,request.user)
				except :
					resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				
				form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas(vta)})
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
				show=True
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myVtaContado.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addExp'):
				queryExp = request.GET.get('qExp','')
				vta = request.GET.get('vtaGral','')
				try:
					with transaction.atomic():
						resultAdd = addExpresVta1(queryExp,request.GET.get('mcPrecio') ,mysucursal, vta, request.user)
						updVta(vta,mysucursal,request.user)
				except :
					resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				

				form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas(vta)})
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
				show=True
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myVtaContado.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addAcc'):
				queryAcc = request.GET.get('qAcc','')
				vta = request.GET.get('vtaGral','')
				try:
					with transaction.atomic():
						resultAdd = addAccVta1(queryAcc, request.GET.get('mcPrecio'),mysucursal, vta, request.user)
						updVta(vta,mysucursal,request.user)
				except :
					resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				
				form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas(vta)})

				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
				show=True
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myVtaContado.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addFic'):
				queryFic = request.GET.get('qFic','')
				queryFic2 = request.GET.get('qFic2','')
				vta = request.GET.get('vtaGral','')
				descuentoFichas = request.GET.get('dto','')
				try:
					with transaction.atomic():
						resultAdd = addFichaVta1(queryFic,queryFic2,descuentoFichas ,mysucursal, vta, request.user,None)
						updVta(vta,mysucursal,request.user)
				except :
					resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				
				form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas(vta)})
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
				show=True
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myVtaContado.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addRec'):
				vta = request.GET.get('vtaGral','')
				folio = request.GET.get('folio')
				rfolio = request.GET.get('rfolio')
				montos = request.GET.get('montos')
				observaciones = request.GET.get('observaciones')
				descuentoRecargas = request.GET.get('dto','')

				if folio or rfolio and vta:
					try:
						with transaction.atomic():
							resultAdd = addRecarga1(rfolio,folio,montos, observaciones,request.GET.get('dto','') ,mysucursal, vta,request.user, None)
					except :
						resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				
				else:
					resultAdd = "Ingrese un Folio o Genere uno."

				updVta(vta,mysucursal,request.user)
				form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas(vta)})
				
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
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
				show=True
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myVtaContado.html',ctx,context_instance=RequestContext(request))
			
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
					return render_to_response('compras/ticket.html',ctx,context_instance=RequestContext(request))

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
							

							form2 = AddVentaRecarga()
							vta= nuevoFolio('E',request.user,None)
							form = AddVentaCaja({'folioVenta':vta,'total':0})
							show= False
							info=" Venta "+vtaGral.estado.estado+" - " + vtaGral.folioVenta +" Cambio: $ "+str(efectivo - total)
							mfolioVenta = vtaGral.folioVenta
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
					
					ctx = {'folioVenta':mfolioVenta, 'show':show,'vtaGenerada':vta,'recForm':form2,'vtaForm':form,'nivel':nivel,'info':info}
					return render_to_response('compras/myVtaContado.html',ctx,context_instance=RequestContext(request))
				else:
					show = True
					info = "El pago debe ser mayor o igual al monto total a pagar. Debe ingresar por lo menos un producto a la venta"
					form = AddVentaCaja(request.POST)
					ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
					return render_to_response('compras/myVtaContado.html',ctx,context_instance=RequestContext(request))
			else:
				form = AddVentaCaja(request.POST)
				info = "Ingrese $monto del cliente a pagar. Debe ingresar al menos un producto a la venta"
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myVtaContado.html',ctx,context_instance=RequestContext(request))

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
							form = AddVentaCaja()
							form2 = AddVentaRecarga()
							vta= nuevoFolio('E',request.user,None) #mayoreo
							form = AddVentaCaja({'folioVenta':vta,'total':0})
							show=False
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
					
					ctx = {'show':show,'vtaGenerada':vta,'recForm':form2,'vtaForm':form,'nivel':nivel,'info':info}
					return render_to_response('compras/myVtaContado.html',ctx,context_instance=RequestContext(request))
				else:
					form = AddVentaCaja(request.POST)
					info = "Debe ingresar al menos un producto a la venta."
					ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
					return render_to_response('compras/myVtaContado.html',ctx,context_instance=RequestContext(request))
			else:
				form = AddVentaCaja(request.POST)
				info = "Ingrese el monto que pago el cliente, si en dado caso se cancelo, ponga un 0. Debe ingresar por lo menos un producto a la venta."
				ctx = {'show':show,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'info':info}
				return render_to_response('compras/myVtaContado.html',ctx,context_instance=RequestContext(request))
		
		vta = nuevoFolio('E',request.user,None)
		form = AddVentaCaja({'folioVenta':vta,'total':0})
		ctx = {'show':show,'vtaGenerada':vta,'recForm':form2,'vtaForm':form,'nivel':nivel,'info':info}
		return render_to_response('compras/myVtaContado.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo - #yet
@login_required(login_url='/')
def compras_ventas_caja_vtas_dia_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
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
		
		manana = datetime.today() + timedelta(days=2) # mañana 
		hoy = datetime.today() - timedelta(days=2)
		#filtrar los cortes de la sucursal  de hoy y mañana
		Cortes = CorteVenta.objects.filter(sucursal=mysucursal,fxCorte__range=[hoy,manana])
		vtasCorte = VentasCorte.objects.all()
		eqVendido = None
		expVendido = None
		ficVendido = None
		accVendido = None
		recVendido = None
		menosAnticipo =  None
		try:
			eqVendido = VentaEquipo.objects.all()
			expVendido = VentaExpres.objects.all()
			ficVendido = VentaFichas.objects.all()
			accVendido = VentaAccesorio.objects.all()
			recVendido = VentaRecarga.objects.all()
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
					return render_to_response('compras/myVerificacionUser.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('cancelaciones'):
				query = request.GET.get('cancelaciones','')
				if query:
					vtaCanceladas = Venta.objects.filter(sucursal=mysucursal,aceptada=False,activa=True)
					ctx = {'anticipo':menosAnticipo,'accVendido':accVendido,'vtaCanceladas':vtaCanceladas,'recVendido':recVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'nivel':nivel}
					return render_to_response('compras/myCancelacionVtas.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('print'):
				corte = request.GET.get('print','')
				if corte:
					mivi = None
					try:
						Cortes = CorteVenta.objects.get(folioCorteVta=corte)
						ok = suc_Permisos(nivel,request.user,Cortes.sucursal)
						if ok:
							mivi = listarCorte(corte)
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('compras/ticketCorte.html',ctx,context_instance=RequestContext(request))

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
				return render_to_response('compras/myAddArqueo.html',ctx,context_instance=RequestContext(request))
			else:
				info="Ingrese "
				arqForm = addArqueoCaja(request.POST)
				ctx = {'arqForm':arqForm,'info':info,'nivel':nivel}
				return render_to_response('compras/myAddArqueo.html',ctx,context_instance=RequestContext(request))

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
								return render_to_response('compras/myAddArqueo.html',ctx,context_instance=RequestContext(request))
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
			return render_to_response('compras/myVerificacionUser.html',ctx,context_instance=RequestContext(request))
		
		ctx = {'vtasCorte':vtasCorte,'Cortes':Cortes,'anticipo':menosAnticipo,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'nivel':nivel}
		return render_to_response('compras/myCorteVentas.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#listo - #yet
@login_required(login_url='/')
def compras_ventas_caja_cerrar_corte_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
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
					return render_to_response('compras/myCerrarCorte.html',ctx,context_instance=RequestContext(request))
			

			if request.GET.get('hoy'):
				t = request.GET.get('hoy','')
				if t:
					corte = generarCorte(mysucursal,None, request.user)
					info = 'El corte de venta se ha generado correctamente. Folio: '+ corte
					show= False
					cerrar = False
					ctx = {'cerrar':cerrar,'show':show,'info':info,'nivel':nivel}
					return render_to_response('compras/myCerrarCorte.html',ctx,context_instance=RequestContext(request))
		
		if 'cerrar' in request.POST:
			form = updCorteVenta(request.POST or None)
			if form.is_valid():
				''' # habilitar si se necesita en compras
				if pendientes_papeletas(mysucursal.id) == True:
					info = "No puede cerrar Corte, tiene que terminar de llenar las papeletas pendientes, gracias."
					ctx = {'cerrar':cerrar,'show':show,'info':info,'nivel':nivel}
					return render_to_response('compras/myCerrarCorte.html',ctx,context_instance=RequestContext(request))
				else:
					pass
				#'''
				try:
					with transaction.atomic():
						folioCorteVta 	= form.cleaned_data['folioCorteVta']
						observacion 	= form.cleaned_data['observacion']

						upd = CorteVenta.objects.get(folioCorteVta=folioCorteVta)
						upd.observacion = observacion
						upd.cierraCorte = request.user
						upd.cerrado 	= True
						upd.save()

						a = RecargasVendidoCorte() #historial de saldo vendido
						a.sucursal = mysucursal
						a.corte = upd
						a.totalVentas = vtasRecargaCorte(folioCorteVta)
						a.saldoFinal 	= SaldoSucursal.objects.get(sucursal=mysucursal).saldo
						a.save()

						show =  False
						cerrar = True
						info = 'El corte de venta se ha cerrado correctamente. Folio: '+ upd.folioCorteVta
				except :
					info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."
				ctx = {'cerrar':cerrar,'show':show,'info':info,'nivel':nivel}
				return render_to_response('compras/myCerrarCorte.html',ctx,context_instance=RequestContext(request))
			
			else:
				info = "Verifique sus datos."
				form= updCorteVenta(request.POST)
				show = True
				cerrar = True
				ctx = {'cerrar':cerrar,'cerrarForm':form,'show':show,'info':info,'nivel':nivel}
				return render_to_response('compras/myCerrarCorte.html',ctx,context_instance=RequestContext(request))

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
							nivel=Permiso(request.user,[0,1,5,6,7])
							if nivel != -1:
								q = request.POST.get('thisCorte','')
								ctx = {'thisCorte':q ,'cerrarForm':form,'show':show,'info':info,'nivel':nivel}
								return render_to_response('compras/myCerrarCorte.html',ctx,context_instance=RequestContext(request))
							else:
								info ="El usuario no tiene Permiso para realizar esta operacion"
						except Usuario.DoesNotExist:
								pass
					else:
						info = "Usuario no Activo"
				else:
					info = "Usuario o contraseña Incorrecto"
			else:
				info = "Lo sentimos, los datos ingresados no corresponden al personal autorizado, intente nuevamente."
			
			verificarForm =  AuthenticationForm(request.POST)
			ctx = {'thisCorte':grrr,'verificarForm':verificarForm,'info':info,'nivel':nivel}
			return render_to_response('compras/myVerificacionUser.html',ctx,context_instance=RequestContext(request))

		ctx = {'thisCorte':grrr,'verificarForm':verificarForm,'info':info,'nivel':nivel}
		return render_to_response('compras/myVerificacionUser.html',ctx,context_instance=RequestContext(request))

		#ctx = {'cerrarForm':form,'show':show,'info':info,'nivel':nivel}
		#return render_to_response('compras/myCerrarCorte.html',ctx,context_instance=RequestContext(request))
		
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo - #yet
@login_required(login_url='/')
def compras_ventas_gastos_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
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
						info = "Lo Sentimos, hubo un problema al guardar la informacion. Infomacion no registrada."
				else:
					
					info = "No se puede registrar el gasto, el corte contiene un total menor al gasto. Corte: "+corteActivo
				form = addGastosSucursal()
				ctx = {'corte':corteActivo,'form':form,'info':info,'nivel':nivel}
				return render_to_response('compras/myAddGastos.html',ctx,context_instance=RequestContext(request))
			
			else:
				info = "Ingrese Datos al formulario"
				form= addGastosSucursal(request.POST)
		
		ctx = {'corte':corteActivo,'form':form,'info':info,'nivel':nivel}
		return render_to_response('compras/myAddGastos.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#nope
@login_required(login_url='/')
def compras_reportes_trensferencias_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		return render_to_response('compras/index.html', {'nivel':nivel},context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#nope
@login_required(login_url='/')
def compras_reportes_devoluciones_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		return render_to_response('compras/index.html', {'nivel':nivel},context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

		
#nope
@login_required(login_url='/')
def compras_reportes_exist_almacen_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
	if nivel != -1:
		return render_to_response('compras/index.html', {'nivel':nivel},context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


@login_required(login_url='/')
def compras_listas_equipos_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
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
		return render_to_response('compras/listaPreciosEquipos.html', ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

@login_required(login_url='/')
def compras_listas_accesorios_view(request):
	nivel=Permiso(request.user,[0,1,5,6,7])
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
		return render_to_response('compras/listaPreciosAccesorios.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')