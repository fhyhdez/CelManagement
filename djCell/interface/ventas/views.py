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
from django.utils.timesince import timesince
from decimal import Decimal
from django import forms
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
from djCell.apps.amonestaciones.models import TipoAmonestacion, Amonestacion
from djCell.apps.auditoria.models import ArqueoCaja
from djCell.apps.catalogos.models import Estado, Ciudad, Colonia, CP, Zona
from djCell.apps.clientes.models import ClienteFacturacion, ClienteServicio, Mayorista
from djCell.apps.comisiones.models import Comision
from djCell.apps.contabilidad.models import Nomina, TipoCuenta, CuentaEmpleado, HistorialEmpleado, Metas, Caja, Gastos,LineaCredito, HistLCredito, Cuenta
from djCell.apps.corteVta.models import TipoGastoSucursal, GastosSucursal, CorteVenta, DiferenciasCorte, VentasCorte, RecargasVendidoCorte
from djCell.apps.credito.models import EstadoSubdistribuidor, EstadoCredito, Subdistribuidor, Credito, HistorialSubdistribuidor
from djCell.apps.facturacion.models import *
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
from djCell.apps.sucursales.models import VendedorSucursal


#right here
from djCell.interface.ventas.forms import * 
from djCell.operaciones.comunes import *
from djCell.operaciones.ventasgral  import *
from djCell.operaciones.sucursales import *


#listo
@login_required(login_url='/')
def index_view(request):
	nivel=Permiso(request.user,[0,1,12,11])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		return render_to_response('ventas/index.html', {'nivel':nivel,'vendedor':xhsdfg},context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo
@login_required(login_url="/")
def resultado_operacion_vtas_view(request):
	nivel=Permiso(request.user,[0,1,11,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		return render_to_response('ventas/transaccion.html',{'nivel':nivel,'vendedor':xhsdfg},context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo
@login_required(login_url='/')
def ventas_papeleta_nueva_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		_usuario = Usuario.objects.get(user=request.user)
		myempleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=myempleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		p =request.GET.get('producto','')
		info = ""
		tipo = None
		form = addPapeleta()
		eq =None
		ex = None
		if p:
			try:
				eq =  Equipo.objects.get(imei=p)
			except Equipo.DoesNotExist:
				eq = None
			try:
				ex =  Expres.objects.get(icc=p)
			except Expres.DoesNotExist:
				ex = None

		if eq:
			tipo = "Equipo"
			form = addPapeleta({'telAsig':eq.noCell,'esnImei':eq.imei,'dat':'ACCELL'})
			form.fields['tipoProducto'] = forms.ChoiceField(required=True,choices=[(c.id, c.tipo ) for c in TipoProducto.objects.exclude(tipo='Express')])
			form.fields['tipoProducto'].label='Tipo de Activacion'
		if ex:
			tipo = "Express"
			form = addPapeleta({'telAsig':ex.noCell,'esnImei':ex.icc,'dat':'ACCELL'})
			form.fields['tipoProducto'] = forms.ChoiceField(required=True,choices=[(c.id, c.tipo ) for c in TipoProducto.objects.filter(tipo='Express')])
			form.fields['tipoProducto'].label='Tipo de Activacion'
	
		
		if request.method == "POST":
			form = addPapeleta(request.POST or None)
			if form.is_valid():
				try:
					l = Papeleta.objects.get(folioPapeleta__icontains=form.cleaned_data['folioPapeleta'])
					info = "El Folio de Papeleta ya esta en uso. Ingrese uno nuevo."
					if form.data.get('tipo') == 'Equipo':
						tipo= 'Equipo'
						form = addPapeleta(request.POST)
						form.fields['tipoProducto'] = forms.ChoiceField(required=True,choices=[(c.id, c.tipo ) for c in TipoProducto.objects.exclude(tipo='Express')])
						form.fields['tipoProducto'].label='Tipo de Activacion'
					else:
						tipo = 'Express'
						form = addPapeleta(request.POST)
						form.fields['tipoProducto'] = forms.ChoiceField(required=True,choices=[(c.id, c.tipo ) for c in TipoProducto.objects.filter(tipo='Express')])
						form.fields['tipoProducto'].label='Tipo de Activacion'
					
					ctx = {'nivel':nivel,'vendedor':xhsdfg,'form':form,'tipo':tipo,'info':info}
					return render_to_response('ventas/addPapeleta.html',ctx,context_instance=RequestContext(request))
			
				except Papeleta.DoesNotExist:
					folioPapeleta = form.cleaned_data['folioPapeleta']
					nombre 	= form.cleaned_data['nombre']
					calle 	= form.cleaned_data['calle']
					colonia 	= form.cleaned_data['colonia']
					cp 			= form.cleaned_data['cp']
					ciudad  	= form.cleaned_data['ciudad']
					estado 		= form.cleaned_data['estado']
					telPart = form.cleaned_data['telPart']
					telAsig = form.cleaned_data['telAsig']
					esnImei = form.cleaned_data['esnImei']
					dat 	= form.cleaned_data['dat']
					tipoProducto = form.cleaned_data['tipoProducto']

					tgarantia = 0
					if form.data.get('tipo') == 'Equipo':
						eq =  Equipo.objects.get(imei=esnImei)
						tgarantia = eq.detallesEquipo.tiempoGarantia.dias
					else:
						ex =  Expres.objects.get(icc=esnImei)
						tgarantia = ex.detallesExpres.tiempoGarantia.dias
					
					z1 = agregarCiudades(colonia,ciudad,estado,cp)
					try:
						with transaction.atomic():
							a = Papeleta()
							a.folioPapeleta = folioPapeleta
							a.sucursal = mysucursal
							a.empleado = myempleado
							a.nombre 	= (nombre).title()
							a.calle 	= (calle).title()
							a.colonia = Colonia.objects.get(id=z1[0])
							a.codP 	= CP.objects.get(id=z1[2])
							a.ciudad 	= Ciudad.objects.get(id=z1[1])
							a.estado 	= Estado.objects.get(id=estado)
							a.telPart = telPart
							a.telAsig = telAsig
							a.esnImei = esnImei
							a.dat 	= dat
							a.tipoProducto = TipoProducto.objects.get(id=tipoProducto)
							a.tgarantia = tgarantia 
							a.save()
							info = "Se ha Guardado la papeleta con folio : "+ a.folioPapeleta
					except :
						info='Lo sentimos, la información enviada no se almaceno por problemas de integridad de datos'
						#sukiiya #transaction.commit()#'''
					ctx = {'nivel':nivel,'vendedor':xhsdfg,'cerrar':True,'info':info}
					return render_to_response('ventas/addPapeleta.html',ctx,context_instance=RequestContext(request))
					
			else:
				info = "Los datos no se han Guardado correctamente. Verifique su informacion."
				if form.data.get('tipo') == 'Equipo':
					tipo= 'Equipo'
					form = addPapeleta(request.POST)
					form.fields['tipoProducto'] = forms.ChoiceField(required=True,choices=[(c.id, c.tipo ) for c in TipoProducto.objects.exclude(tipo='Express')])
					form.fields['tipoProducto'].label='Tipo de Activacion'
				else:
					tipo = 'Express'
					form = addPapeleta(request.POST)
					form.fields['tipoProducto'] = forms.ChoiceField(required=True,choices=[(c.id, c.tipo ) for c in TipoProducto.objects.filter(tipo='Express')])
					form.fields['tipoProducto'].label='Tipo de Activacion'
				ctx = {'nivel':nivel,'vendedor':xhsdfg,'form':form,'tipo':tipo,'info':info}
				return render_to_response('ventas/addPapeleta.html',ctx,context_instance=RequestContext(request))
	

		ctx = {'nivel':nivel,'vendedor':xhsdfg,'form':form,'tipo':tipo,'info':info}
		return render_to_response('ventas/addPapeleta.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo
@login_required(login_url='/')
def ventas_facturacion_productos_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		_usuario = Usuario.objects.get(user=request.user)
		myempleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=myempleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		vta =request.GET.get('venta','')
		info = ""
		form = addFactVenta()
		
		eqVendido = None
		expVendido = None
		ficVendido = None
		accVendido = None
		
		if vta:
			try:
				v = Venta.objects.get(folioVenta=vta, facturada = False)
				ok = suc_permisos(nivel,request.user,v.sucursal)
				if ok:
					form = addFactVenta({'key':v.id})
				else:
					form = None
					info = "Oops! Al parecer no tiene permitido ver esta informacion"
			except :
				form = None
				info = "Detectamos que la venta ya esta facturada o no existe. Verifique con un administrador."
			
			ctx = {'form':form,'info':info,'vta':vta ,'nivel':nivel}					
			return render_to_response('ventas/addFacturacion.html',ctx,context_instance=RequestContext(request))

		if request.method == "GET":
			if request.GET.get('aceptEq'):
				s = request.GET.get('aceptEq','')
				m = request.GET.get('factGral','')
				vta = Venta.objects.get(folioVenta=request.GET.get('vtaGral',''))
				f = None
				if s:
					try:
						with transaction.atomic():
							mov = Facturacion.objects.get(id=m)
							upd = Equipo.objects.get(id=s)
							upd.productoFacturado = True
							upd.save()

							try:
								x = FacturaEquipo.objects.get(equipo=upd)
							except :
								x = FacturaEquipo()
								x.factura = mov
								x.equipo  = upd
								x.save()

							mov.totalvta = mov.totalvta + VentaEquipo.objects.get(equipo=upd).precVenta
							mov.save()

							f = mov
							info = " Equipo Facturado "+str(upd.imei)
					except :
						info='Error en los datos enviados. Verifique con un administrador.'
					
					try:
						eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta.folioVenta, equipo__productoFacturado = False)
						expVendido = VentaExpres.objects.filter(venta__folioVenta=vta.folioVenta, expres__productoFacturado = False)
						ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta.folioVenta, ficha__productoFacturado = False)
						accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta.folioVenta, accesorio__productoFacturado = False)
					except VentaEquipo.DoesNotExist:
						eqVendido = None
					except VentaExpres.DoesNotExist:
						expVendido = None
					except VentaFichas.DoesNotExist:
						ficVendido = None
					except VentaAccesorio.DoesNotExist:
						accVendido = None
					paso2 = True
					mostrar = True
					ctx = {'nivel':nivel,'paso2':paso2,'mostrar':mostrar,'vta':vta,'fact':f,
							'eqVendido':eqVendido,'expVendido':expVendido,'ficVendido':ficVendido,'accVendido':accVendido,
							'vendedor':xhsdfg,'info':info}
					return render_to_response('ventas/addFacturacion.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('aceptEx'):
				s = request.GET.get('aceptEx','')
				m = request.GET.get('factGral','')
				vta = Venta.objects.get(folioVenta=request.GET.get('vtaGral',''))
				f=None
				if s:
					try:
						with transaction.atomic():
							mov = Facturacion.objects.get(id=m)
							upd = Expres.objects.get(id=s)
							upd.productoFacturado = True
							upd.save()

							try:
								x = FacturaExpres.objects.get(expres=upd)
							except :
								x = FacturaExpres()
								x.factura = mov
								x.expres  = upd
								x.save()

							mov.totalvta = mov.totalvta + VentaExpres.objects.get(expres=upd).precVenta
							mov.save()
							f = mov
							info = " Expres Facturado "+str(upd.icc)
					except :
						info='Error en los datos enviados. Verifique con un administrador.'
					
					try:
						eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta.folioVenta, equipo__productoFacturado = False)
						expVendido = VentaExpres.objects.filter(venta__folioVenta=vta.folioVenta, expres__productoFacturado = False)
						ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta.folioVenta, ficha__productoFacturado = False)
						accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta.folioVenta, accesorio__productoFacturado = False)
					except VentaEquipo.DoesNotExist:
						eqVendido = None
					except VentaExpres.DoesNotExist:
						expVendido = None
					except VentaFichas.DoesNotExist:
						ficVendido = None
					except VentaAccesorio.DoesNotExist:
						accVendido = None
					paso2 = True
					mostrar = True
					ctx = {'nivel':nivel,'paso2':paso2,'mostrar':mostrar,'vta':vta,'fact':f,
							'eqVendido':eqVendido,'expVendido':expVendido,'ficVendido':ficVendido,'accVendido':accVendido,
							'vendedor':xhsdfg,'info':info}
					return render_to_response('ventas/addFacturacion.html',ctx,context_instance=RequestContext(request))
			
			if request.GET.get('aceptAc'):
				s = request.GET.get('aceptAc','')
				m = request.GET.get('factGral','')
				vta = Venta.objects.get(folioVenta=request.GET.get('vtaGral',''))
				f=None
				if s:
					try:
						with transaction.atomic():
							mov = Facturacion.objects.get(id=m)
							upd = Accesorio.objects.get(id=s)
							upd.productoFacturado = True
							upd.save()
							try:
								x = FacturaAccesorio.objects.get(accesorio=upd)
							except :
								x = FacturaAccesorio()
								x.factura = mov
								x.accesorio  = upd
								x.save()

							mov.totalvta = mov.totalvta + VentaAccesorio.objects.get(accesorio=upd).precVenta
							mov.save()

							f = mov
							info = " Accesorio Facturado "+str(upd.codigoBarras)
					except :
						info='Error en los datos enviados. Verifique con un administrador.'
					
					try:
						eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta.folioVenta, equipo__productoFacturado = False)
						expVendido = VentaExpres.objects.filter(venta__folioVenta=vta.folioVenta, expres__productoFacturado = False)
						ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta.folioVenta, ficha__productoFacturado = False)
						accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta.folioVenta, accesorio__productoFacturado = False)
					except VentaEquipo.DoesNotExist:
						eqVendido = None
					except VentaExpres.DoesNotExist:
						expVendido = None
					except VentaFichas.DoesNotExist:
						ficVendido = None
					except VentaAccesorio.DoesNotExist:
						accVendido = None
					paso2 = True
					mostrar = True
					ctx = {'nivel':nivel,'paso2':paso2,'mostrar':mostrar,'vta':vta,'fact':f,
							'eqVendido':eqVendido,'expVendido':expVendido,'ficVendido':ficVendido,'accVendido':accVendido,
							'vendedor':xhsdfg,'info':info}
					return render_to_response('ventas/addFacturacion.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('aceptFic'):
				s = request.GET.get('aceptFic','')
				m = request.GET.get('factGral','')
				vta = Venta.objects.get(folioVenta=request.GET.get('vtaGral',''))
				f=None
				if s:
					try:
						with transaction.atomic():
							mov = Facturacion.objects.get(id=m)
							upd = Ficha.objects.get(id=s)
							upd.productoFacturado = True
							upd.save()
							try:
								x = FacturaFichas.objects.get(ficha=upd)
							except :
								x = FacturaFichas()
								x.factura = mov
								x.ficha  = upd
								x.save()

							mov.totalvta = mov.totalvta + VentaFichas.objects.get(ficha=upd).precVenta
							mov.save()

							f = mov
							info = " Ficha facturada "+str(upd.folio)
					except :
						info='Error en los datos enviados. Verifique con un administrador.'
					
					try:
						eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta.folioVenta, equipo__productoFacturado = False)
						expVendido = VentaExpres.objects.filter(venta__folioVenta=vta.folioVenta, expres__productoFacturado = False)
						ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta.folioVenta, ficha__productoFacturado = False)
						accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta.folioVenta, accesorio__productoFacturado = False)
					except VentaEquipo.DoesNotExist:
						eqVendido = None
					except VentaExpres.DoesNotExist:
						expVendido = None
					except VentaFichas.DoesNotExist:
						ficVendido = None
					except VentaAccesorio.DoesNotExist:
						accVendido = None
					paso2 = True
					mostrar = True
					ctx = {'nivel':nivel,'paso2':paso2,'mostrar':mostrar,'vta':vta,'fact':f,
							'eqVendido':eqVendido,'expVendido':expVendido,'ficVendido':ficVendido,'accVendido':accVendido,
							'vendedor':xhsdfg,'info':info}
					return render_to_response('ventas/addFacturacion.html',ctx,context_instance=RequestContext(request))

			
		if 'paso1' in request.POST:
			form = addFactVenta(request.POST or None)
			if form.is_valid():
				errores = False
				v = None
				f=None
				vta = None
				clienterfc = None
				nuevo = False
				key 	= form.cleaned_data['key'] 
				rfc 	= (form.cleaned_data['rfc']).upper()
				folio 	= form.cleaned_data['folio']
				
				try:
					v = Venta.objects.get(id=key)
					clienterfc = ClienteFacturacion.objects.get(rfc=(rfc).upper())
					vta = v.folioVenta
				except Venta.DoesNotExist:
					errores = True
					info = "La venta no existe, verifique con un Administrador"
				except ClienteFacturacion.DoesNotExist:
					nuevo = True
					info= "Cliente Facturacion nuevo"

				if nuevo:
					txt=str(rfc).upper()
					re1='[A-Z]{3,4}-[0-9]{2}[0-1][0-9][0-3][0-9]-[A-Z0-9]?[A-Z0-9]?[0-9A-Z]?'
					rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
					m = rg.search(txt)
					if m:
						try:
							with transaction.atomic():
								a = ClienteFacturacion()
								a.rfc 			= (txt).upper()
								a.razonSocial 	= ("Por actualizar").title()
								a.direccion 	= ("Por actualizar").title()
								a.colonia 		= Colonia.objects.get(id=1)
								a.ciudad 		= Ciudad.objects.get(id=1)
								a.cp 			= CP.objects.get(id=1)
								a.estado 		= Estado.objects.get(estado__icontains='PUEBLA')
								a.save()
								clienterfc = a
						except :
							form = addFactVenta(request.POST or None)
							errores = True
							info = "El Cliente nuevo se tendra que registrar en contabilidad. Consulte a un administrador."
					else:
						form = addFactVenta(request.POST or None)
						errores = True
						info = "El RFC no es correcto, Cliente nuevo."

				if errores:
					ctx = {'nivel':nivel,'vta':v,'vendedor':xhsdfg,'info':info}
					return render_to_response('ventas/addFacturacion.html',ctx,context_instance=RequestContext(request))
				else:
					try:
						with transaction.atomic():
							f =  Facturacion()
							f.clienteFacturacion = clienterfc
							f.venta = Venta.objects.get(id=key)
							f.folioFiscal = folio
							f.totalvta = 0
							f.estado = EstadoFacturacion.objects.get(estado='Sin Revisar')
							f.save()

							try:
								eqVendido = VentaEquipo.objects.filter(venta__folioVenta=v.folioVenta, equipo__productoFacturado = False)
								expVendido = VentaExpres.objects.filter(venta__folioVenta=v.folioVenta, expres__productoFacturado = False)
								ficVendido = VentaFichas.objects.filter(venta__folioVenta=v.folioVenta, ficha__productoFacturado = False)
								accVendido = VentaAccesorio.objects.filter(venta__folioVenta=v.folioVenta, accesorio__productoFacturado = False)
							except VentaEquipo.DoesNotExist:
								eqVendido = None
							except VentaExpres.DoesNotExist:
								expVendido = None
							except VentaFichas.DoesNotExist:
								ficVendido = None
							except VentaAccesorio.DoesNotExist:
								accVendido = None
							info = "Productos a Factura " + f.folioFiscal+" Venta "+str(v.folioVenta)

							ctx = {'nivel':nivel,'paso2':True,'mostrar':True,'vta':v,'fact':f,
							'eqVendido':eqVendido,'expVendido':expVendido,'ficVendido':ficVendido,'accVendido':accVendido,
							'vendedor':xhsdfg,'info':info}
							return render_to_response('ventas/addFacturacion.html',ctx,context_instance=RequestContext(request))

					except :
						info = "Hubo errores en la transaccion, favor de verificar con contabilidad"
						ctx = {'nivel':nivel,'paso2':True,'mostrar':True,'vta':v,'fact':f,
							'eqVendido':eqVendido,'expVendido':expVendido,'ficVendido':ficVendido,'accVendido':accVendido,
							'vendedor':xhsdfg,'info':info}
						return render_to_response('ventas/addFacturacion.html',ctx,context_instance=RequestContext(request))
					
			else:
				form = addFactVenta(request.POST or None)
				info = "Verifique sus datos"
				ctx = {'nivel':nivel,'form':form,'vendedor':xhsdfg,'info':info}
				return render_to_response('ventas/addFacturacion.html',ctx,context_instance=RequestContext(request))

		if 'cerrarFactura' in request.POST:
			try:
				with transaction.atomic():
					factura = Facturacion.objects.get(id=request.POST.get('factGral'))
					vta = Venta.objects.get(folioVenta=request.POST.get('vtaGral'))

					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta.folioVenta, equipo__productoFacturado = False)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta.folioVenta, expres__productoFacturado = False)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta.folioVenta, ficha__productoFacturado = False)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta.folioVenta, accesorio__productoFacturado = False)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta.folioVenta, recarga__productoFacturado = False).count()

					total = 0
					for x in eqVendido:
						total = total + x.precVenta
						upd = Equipo.objects.get(id=x.equipo.id)
						upd.productoFacturado = True
						upd.save()

						x = FacturaEquipo()
						x.factura = factura
						x.equipo  = upd
						x.save()

					for x in expVendido:
						total = total + x.precVenta
						upd = Expres.objects.get(id=x.expres.id)
						upd.productoFacturado = True
						upd.save()

						x = FacturaExpres()
						x.factura = factura
						x.expres  = upd
						x.save()
						

					for x in ficVendido:
						total = total + x.precVenta
						upd = Ficha.objects.get(id=x.ficha.id)
						upd.productoFacturado = True
						upd.save()

						x = FacturaFichas()
						x.factura = factura
						x.ficha  = upd
						x.save()
						

					for x in accVendido:
						total = total + x.precVenta
						upd = Accesorio.objects.get(id=x.accesorio.id)
						upd.productoFacturado = True
						upd.save()

						x = FacturaAccesorio()
						x.factura = factura
						x.accesorio  = upd
						x.save()
						

					factura.totalvta = total
					factura.save()
					
					if recVendido==0:
						vta.facturada = True
						vta.save()
						info =  "Se ha marcado toda la venta como facturada ("+factura.folioFiscal+") incluyendo sus productos, total: $"+str(factura.totalvta)+"Venta ("+vta.folioVenta+")"
					else:
						info =  "Se ha marcado Parte de la venta como facturada ("+factura.folioFiscal+") total: $"+str(factura.totalVta)+" incluye recargas, será revisado por contabilidad. Venta ("+vta.folioVenta+")"
					
					ctx = {'nivel':nivel,'vendedor':xhsdfg,'paso2':True,'mostrar':False,'vta':vta,'fact':factura,'info':info}
					return render_to_response('ventas/addFacturacion.html',ctx,context_instance=RequestContext(request))
			
			except :
				info = "Hubo problemas al actualizar la información"
				ctx = {'nivel':nivel,'vendedor':xhsdfg,'cerrar':True,'info':info}
				return render_to_response('ventas/addFacturacion.html',ctx,context_instance=RequestContext(request))

		ctx = {'nivel':nivel,'vendedor':xhsdfg,'form':form,'info':info}
		return render_to_response('ventas/addFacturacion.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')




#listo
@login_required(login_url='/')
def ventas_ventas_menudeo_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		
		form = AddVentaCaja()
		form2 = AddVentaRecarga()
		form3 = AddVentaPlan()
		form4 = AddRenta()
		papeleta = ""
		resultAdd = ""
		queryEq  = ""
		queryExp = ""
		queryAcc = ""
		queryFic = ""
		queryRec = ""
		informeFichas = []
		show = True
		info=""
		vta = nuevoFolio2(str(mysucursal.id)+'S')
		form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas2(vta)})
		eqVendido = None
		expVendido = None
		ficVendido = None
		accVendido = None
		recVendido = None
		planVendido = None
		rentaVendido = None
		anticipo = None
		producto = None

		try:
			eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
			expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
			ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
			accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
			recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
			planVendido = VentaPlan.objects.filter(venta__folioVenta=vta)
			rentaVendido = Renta.objects.filter(venta__folioVenta=vta)
			anticipo = Anticipo.objects.filter(folioVenta__folioVenta=vta)
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
		except VentaPlan.DoesNotExist:
			planVendido = None
		except Renta.DoesNotExist:
			rentaVendido = None
		except Anticipo.DoesNotExist:
			anticipo = None
		nv = None
		v = None
		if request.method == "GET":
			m=None
			if request.GET.get('addEq'):
				queryEq = request.GET.get('qEq','')
				vta = request.GET.get('vtaGral','')
				try:
					with transaction.atomic():
						resultAdd = addEquipoVta1(queryEq,'Publico',mysucursal, vta,request.user)
						updVta(vta,mysucursal,request.user)
						
				except :
					resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."

				form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas2(vta)})
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
					planVendido = VentaPlan.objects.filter(venta__folioVenta=vta)
					rentaVendido = Renta.objects.filter(venta__folioVenta=vta)
					anticipo = Anticipo.objects.filter(folioVenta__folioVenta=vta)
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
				except VentaPlan.DoesNotExist:
					planVendido = None
				except Renta.DoesNotExist:
					rentaVendido = None
				except Anticipo.DoesNotExist:
					anticipo = None
				show=True
				ctx = {'producto':producto,'show':show,'planForm':form3,'rentaForm':form4,'planVendido':planVendido,'rentaVendido':rentaVendido,'anticipo':anticipo,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
				return render_to_response('ventas/VtaMenudeo.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addExp'):
				queryExp = request.GET.get('qExp','')
				vta = request.GET.get('vtaGral','')
				try:
					with transaction.atomic():
						resultAdd = addExpresVta1(queryExp,'Publico' ,mysucursal, vta,request.user)
						updVta(vta,mysucursal,request.user)
				except :
					resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				
				form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas2(vta)})
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
					planVendido = VentaPlan.objects.filter(venta__folioVenta=vta)
					rentaVendido = Renta.objects.filter(venta__folioVenta=vta)
					anticipo = Anticipo.objects.filter(folioVenta__folioVenta=vta)
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
				except VentaPlan.DoesNotExist:
					planVendido = None
				except Renta.DoesNotExist:
					rentaVendido = None
				except Anticipo.DoesNotExist:
					anticipo = None
				show=True
				ctx = {'producto':producto,'show':show,'planForm':form3,'rentaForm':form4,'planVendido':planVendido,'rentaVendido':rentaVendido,'anticipo':anticipo,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
				return render_to_response('ventas/VtaMenudeo.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addAcc'):
				queryAcc = request.GET.get('qAcc','')
				vta = request.GET.get('vtaGral','')

				try:
					with transaction.atomic():
						resultAdd = addAccVta1(queryAcc,'Publico',mysucursal, vta,request.user)
						updVta(vta,mysucursal,request.user)
				except :
					resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				
				form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas2(vta)})
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
					planVendido = VentaPlan.objects.filter(venta__folioVenta=vta)
					rentaVendido = Renta.objects.filter(venta__folioVenta=vta)
					anticipo = Anticipo.objects.filter(folioVenta__folioVenta=vta)
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
				except VentaPlan.DoesNotExist:
					planVendido = None
				except Renta.DoesNotExist:
					rentaVendido = None
				except Anticipo.DoesNotExist:
					anticipo = None
				show=True
				ctx = {'show':show,'planForm':form3,'rentaForm':form4,'planVendido':planVendido,'rentaVendido':rentaVendido,'anticipo':anticipo,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
				return render_to_response('ventas/VtaMenudeo.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addFic'):
				queryFic = request.GET.get('qFic','')
				vta = request.GET.get('vtaGral','')
				try:
					with transaction.atomic():
						resultAdd = addFichaVta1(queryFic,None,0,mysucursal, vta, request.user,None)
						updVta(vta,mysucursal,request.user)
				except :
					resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."

				
				form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas2(vta)})
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
					planVendido = VentaPlan.objects.filter(venta__folioVenta=vta)
					rentaVendido = Renta.objects.filter(venta__folioVenta=vta)
					anticipo = Anticipo.objects.filter(folioVenta__folioVenta=vta)
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
				except VentaPlan.DoesNotExist:
					planVendido = None
				except Renta.DoesNotExist:
					rentaVendido = None
				except Anticipo.DoesNotExist:
					anticipo = None
				show=True
				ctx = {'show':show,'planForm':form3,'rentaForm':form4,'planVendido':planVendido,'rentaVendido':rentaVendido,'anticipo':anticipo,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
				return render_to_response('ventas/VtaMenudeo.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addRec'):
				vta = request.GET.get('vtaGral','')
				folio = request.GET.get('folio')
				rfolio = request.GET.get('rfolio')
				montos = request.GET.get('montos')
				observaciones = request.GET.get('observaciones')

				if folio or rfolio and vta:
					try:
						with transaction.atomic():
							resultAdd = addRecarga1(rfolio,folio,montos, observaciones,0,mysucursal, vta,request.user, None)
					except :
						resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				else:
					resultAdd = "Ingrese un Folio o Genere uno."

				updVta(vta,mysucursal,request.user)
				form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas2(vta)})
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
					planVendido = VentaPlan.objects.filter(venta__folioVenta=vta)
					rentaVendido = Renta.objects.filter(venta__folioVenta=vta)
					anticipo = Anticipo.objects.filter(folioVenta__folioVenta=vta)
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
				except VentaPlan.DoesNotExist:
					planVendido = None
				except Renta.DoesNotExist:
					rentaVendido = None
				except Anticipo.DoesNotExist:
					anticipo = None
				show=True
				ctx = {'show':show,'planForm':form3,'rentaForm':form4,'planVendido':planVendido,'rentaVendido':rentaVendido,'anticipo':anticipo,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
				return render_to_response('ventas/VtaMenudeo.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addPlan'):
				vta = request.GET.get('vtaGral','')
				plan = request.GET.get('plan','')
				precVenta = request.GET.get('precVenta','')
				observacion = request.GET.get('observacion','')

				if precVenta and plan and vta:
					updVta(vta,mysucursal,request.user)
					try:
						with transaction.atomic():
							nv = VentaPlan()
							nv.venta 		= Venta.objects.get(folioVenta=vta)
							nv.precVenta 	= precVenta
							nv.plan 		= Plan.objects.get(id=plan)
							if observacion:
								nv.observacion = observacion
							nv.save()

							resultAdd = "Se Registro Deposito de Plan (+) $"+str(nv.precVenta) +" Observaciones: "+nv.observacion					

							updVta(vta,mysucursal,request.user)
							form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas2(vta)})
					except :
						info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
						#sukiiya #transaction.commit()#'''
				else:
					resultAdd ="Elija un plan / ingrese el monto a depositar"
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
					planVendido = VentaPlan.objects.filter(venta__folioVenta=vta)
					rentaVendido = Renta.objects.filter(venta__folioVenta=vta)
					anticipo = Anticipo.objects.filter(folioVenta__folioVenta=vta)
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
				except VentaPlan.DoesNotExist:
					planVendido = None
				except Renta.DoesNotExist:
					rentaVendido = None
				except Anticipo.DoesNotExist:
					anticipo = None
				show=True
				ctx = {'show':show,'planForm':form3,'rentaForm':form4,'planVendido':planVendido,'rentaVendido':rentaVendido,'anticipo':anticipo,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
				return render_to_response('ventas/VtaMenudeo.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addRentas'):
				vta = request.GET.get('vtaGral','')
				numeroReferencia = request.GET.get('numeroReferencia','')
				abono 		= request.GET.get('abono','')
				observacion = request.GET.get('observacion','')

				if numeroReferencia and abono and vta:
					updVta(vta,mysucursal,request.user)
					try:
						with transaction.atomic():
							nv = Renta()
							nv.venta 		= Venta.objects.get(folioVenta=vta)
							nv.numeroReferencia = numeroReferencia
							nv.abono 		= abono
							nv.sucursal 	= mysucursal
							nv.usuario 	= request.user
							if observacion:
								nv.observacion = observacion
							nv.save()

							resultAdd = "Se Registro Deposito de Renta (+) $"+str(nv.abono) +" Observaciones: "+nv.observacion					
							
							updVta(vta,mysucursal,request.user)

							form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas2(vta)})
					except :
						info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
						#sukiiya #transaction.commit()#'''

				else:
					resultAdd ="Ingrese el monto a depositar y el numero de referencia."
				try:
					eqVendido = VentaEquipo.objects.filter(venta__folioVenta=vta)
					expVendido = VentaExpres.objects.filter(venta__folioVenta=vta)
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
					accVendido = VentaAccesorio.objects.filter(venta__folioVenta=vta)
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
					planVendido = VentaPlan.objects.filter(venta__folioVenta=vta)
					rentaVendido = Renta.objects.filter(venta__folioVenta=vta)
					anticipo = Anticipo.objects.filter(folioVenta__folioVenta=vta)
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
				except VentaPlan.DoesNotExist:
					planVendido = None
				except Renta.DoesNotExist:
					rentaVendido = None
				except Anticipo.DoesNotExist:
					anticipo = None
				show=True
				ctx = {'show':show,'planForm':form3,'rentaForm':form4,'planVendido':planVendido,'rentaVendido':rentaVendido,'anticipo':anticipo,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
				return render_to_response('ventas/VtaMenudeo.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('print'):
				vta = request.GET.get('print','')
				if vta:
					mivi = None
					try:
						v = Venta.objects.get(folioVenta=vta)
						ok = suc_permisos(nivel,request.user,v.sucursal)
						if ok:
							mivi = listarTicket(vta)
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}					
					return render_to_response('ventas/ticket.html',ctx,context_instance=RequestContext(request))

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
							vtaGral.aceptada 	= True
							vtaGral.estado 		= EstadoVenta.objects.get(estado='Pagada')
							vtaGral.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
					
					form2 = AddVentaRecarga()
					form3 = AddVentaPlan()
					form4 = AddRenta()
					vta= nuevoFolio2(str(mysucursal.id)+'S')
					form = AddVentaCaja({'folioVenta':vta,'total':0})
					show= False
					info=" Venta "+vtaGral.estado.estado+" - " + vtaGral.folioVenta +" Cambio: $ "+str(efectivo - total)
					mfolioVenta = vtaGral.folioVenta #ticket ya

					
					ctx = {'folioVenta':mfolioVenta, 'show':show,'vtaGenerada':vta,'planForm':form3,'rentaForm':form4,'recForm':form2,'vtaForm':form,'nivel':nivel,'vendedor':xhsdfg,'info':info}
					return render_to_response('ventas/VtaMenudeo.html',ctx,context_instance=RequestContext(request))
				else:
					show = True
					info = "El pago debe ser mayor o igual al monto total a pagar. Debe ingresar por lo menos un producto a la venta"
					form = AddVentaCaja(request.POST)
					ctx = {'show':show,'planForm':form3,'rentaForm':form4,'planVendido':planVendido,'rentaVendido':rentaVendido,'anticipo':anticipo,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
				return render_to_response('ventas/VtaMenudeo.html',ctx,context_instance=RequestContext(request))
			else:
				form = AddVentaCaja(request.POST)
				info = "Ingrese $monto del cliente a pagar. Debe ingresar al menos un producto a la venta"
				ctx = {'show':show,'planForm':form3,'rentaForm':form4,'planVendido':planVendido,'rentaVendido':rentaVendido,'anticipo':anticipo,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
				return render_to_response('ventas/VtaMenudeo.html',ctx,context_instance=RequestContext(request))

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
						info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
						#sukiiya #transaction.commit()#'''
					form = AddVentaCaja()
					form2 = AddVentaRecarga()
					form3 = AddVentaPlan()
					form4 = AddRenta()
					vta= nuevoFolio2(str(mysucursal.id)+'S')
					form = AddVentaCaja({'folioVenta':vta,'total':0})
					show=False
					ctx = {'show':show,'vtaGenerada':vta,'planForm':form3,'rentaForm':form4,'recForm':form2,'vtaForm':form,'nivel':nivel,'vendedor':xhsdfg,'info':info}
					return render_to_response('ventas/VtaMenudeo.html',ctx,context_instance=RequestContext(request))
				else:
					form = AddVentaCaja(request.POST)
					info = "Debe ingresar al menos un producto a la venta."
					ctx = {'show':show,'planForm':form3,'rentaForm':form4,'planVendido':planVendido,'rentaVendido':rentaVendido,'anticipo':anticipo,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
					return render_to_response('ventas/VtaMenudeo.html',ctx,context_instance=RequestContext(request))
			else:
				form = AddVentaCaja(request.POST)
				info = "Ingrese el monto que pago el cliente, si en dado caso se cancelo, ponga un 0. Debe ingresar por lo menos un producto a la venta."
				ctx = {'show':show,'planForm':form3,'rentaForm':form4,'planVendido':planVendido,'rentaVendido':rentaVendido,'anticipo':anticipo,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
				return render_to_response('ventas/VtaMenudeo.html',ctx,context_instance=RequestContext(request))
		
		vta = nuevoFolio2(str(mysucursal.id)+'S')
		form = AddVentaCaja({'folioVenta':vta,'total':0})
		ctx = {'show':show,'planForm':form3,'rentaForm':form4,'planVendido':planVendido,'rentaVendido':rentaVendido,'anticipo':anticipo,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'recForm':form2,'vtaForm':form ,'resultAdd':resultAdd,'queryEq':queryEq,'queryExp':queryExp,'queryAcc':queryAcc,'queryFic':queryFic,'queryRec':queryRec,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
		return render_to_response('ventas/VtaMenudeo.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_ventas_mayoreo_tae_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		
		form = AddVentaCaja()
		form2 = AddVentaRecarga()
		form3 = AsignarMayorista()
		
		resultAdd = ""
		info=""
		vta = nuevoFolio2(str(mysucursal.id)+'M')
		form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas2(vta)})
		recVendido = None
		try:
			recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
		except VentaRecarga.DoesNotExist:
			recVendido = None
		
		if request.method == "GET":
			m=None
			if request.GET.get('addRec'):
				vta = request.GET.get('vtaGral','')
				folio = request.GET.get('folio')
				rfolio = request.GET.get('rfolio')
				montos = request.GET.get('montos')
				observaciones = request.GET.get('observaciones')
				cliente = request.GET.get('cliente')

				if folio or rfolio and vta:
					try:
						with transaction.atomic():
							resultAdd = addRecarga1(rfolio,folio,montos, observaciones,None,mysucursal, vta,request.user, cliente)
							
					except :
						resultAdd = "Hubo problemas al agregar la venta. Avisar al Administrador."
				else:
					resultAdd ="Ingrese un Folio de recarga o seleccion generar uno."

				updVtaMayoreo(vta,mysucursal,request.user)
				form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas2(vta)})
				try:
					recVendido = VentaRecarga.objects.filter(venta__folioVenta=vta)
				except VentaRecarga.DoesNotExist:
					recVendido = None
				
				ctx = {'recVendido':recVendido,'cliente':form3,'recForm':form2,'vtaForm':form,'resultAdd':resultAdd,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
				return render_to_response('ventas/VtaMayoreoTAE.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('print'):
				vta = request.GET.get('print','')
				if vta:
					mivi = None
					try:
						v = Venta.objects.get(folioVenta=vta)
						ok = suc_permisos(nivel,request.user,v.sucursal)
						if ok:
							mivi = listarTicket(vta)
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('ventas/ticket.html',ctx,context_instance=RequestContext(request))

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
							vtaGral.mayoreo  	= True
							vtaGral.aceptada  	= True
							vtaGral.estado 		= EstadoVenta.objects.get(estado='Pagada')
							vtaGral.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
					
					form2 = AddVentaRecarga()
					form3 = AsignarMayorista()

					vta= nuevoFolio2(str(mysucursal.id)+'M')
					form = AddVentaCaja({'folioVenta':vta,'total':0})
					show= False
					info=" Venta "+vtaGral.estado.estado+" - " + vtaGral.folioVenta +" Cambio: $ "+str(efectivo - total)
					mfolioVenta = vtaGral.folioVenta #ticket ya

					ctx = {'folioVenta':mfolioVenta, 'cliente':form3,'recForm':form2,'vtaForm':form,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
					return render_to_response('ventas/VtaMayoreoTAE.html',ctx,context_instance=RequestContext(request))
				else:
					show = True
					info = "El pago debe ser mayor o igual al monto total a pagar. Debe ingresar por lo menos un producto a la venta"
					form = AddVentaCaja(request.POST)
					form3 = AsignarMayorista(request.POST)
					ctx = {'recVendido':recVendido,'cliente':form3,'recForm':form2,'vtaForm':form,'resultAdd':resultAdd,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
					return render_to_response('ventas/VtaMayoreoTAE.html',ctx,context_instance=RequestContext(request))
			else:
				form = AddVentaCaja(request.POST)
				info = "Ingrese $monto del cliente a pagar. Debe ingresar al menos un producto a la venta"
				ctx = {'recVendido':recVendido,'cliente':form3,'recForm':form2,'vtaForm':form,'resultAdd':resultAdd,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
				return render_to_response('ventas/VtaMayoreoTAE.html',ctx,context_instance=RequestContext(request))

		if 'cancelaVta' in request.POST:
			form = AddVentaCaja(request.POST)
			form3 = AsignarMayorista(request.POST)
			if form.is_valid():
				ifolioVenta 	= form.cleaned_data['folioVenta']
				efectivo 	= form.cleaned_data['efectivo']
				total 		= form.cleaned_data['total']
				vtaGral = None
				if total > 0 or efectivo == 0:
					try:
						with transaction.atomic():
							vtaGral =  Venta.objects.get(folioVenta=ifolioVenta)
							vtaGral.total 		= total
							vtaGral.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
							vtaGral.aceptada 	= False
							vtaGral.mayoreo  	= True
							vtaGral.estado 		= EstadoVenta.objects.get(estado='Cancelada')
							vtaGral.save()
							info="Venta Cancelada: "+ vtaGral.folioVenta +"- En espera de autorizacion."
					except :
						info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
						#sukii #transaction.commit()#'''
					form = AddVentaCaja()
					form2 = AddVentaRecarga()
					form3 = AsignarMayorista()
					vta= nuevoFolio2(str(mysucursal.id)+'M')
					form = AddVentaCaja({'folioVenta':vta,'total':0})
					
					ctx = {'cliente':form3,'recForm':form2,'vtaForm':form,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
					return render_to_response('ventas/VtaMayoreoTAE.html',ctx,context_instance=RequestContext(request))
				else:
					form = AddVentaCaja(request.POST)
					info = "Debe ingresar al menos un producto a la venta."
					ctx = {'recVendido':recVendido,'cliente':form3,'recForm':form2,'vtaForm':form,'resultAdd':resultAdd,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
					return render_to_response('ventas/VtaMayoreoTAE.html',ctx,context_instance=RequestContext(request))
			else:
				form = AddVentaCaja(request.POST)
				info = " Ingrese el monto que pago el cliente, si en dado caso se cancelo, ponga un 0. Debe ingresar por lo menos un producto a la venta."
				ctx = {'recVendido':recVendido,'cliente':form3,'recForm':form2,'vtaForm':form,'resultAdd':resultAdd,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
				return render_to_response('ventas/VtaMayoreoTAE.html',ctx,context_instance=RequestContext(request))
		
		
		ctx = {'cliente':form3,'recForm':form2,'vtaForm':form,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
		return render_to_response('ventas/VtaMayoreoTAE.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_ventas_mayoreo_fichas_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		
		form = AddVentaCaja()
		form3 = AsignarMayorista()
		
		resultAdd = ""
		queryFic = ""
		info=""
		vta = nuevoFolio2(str(mysucursal.id)+'M')
		form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas2(vta)})

		ficVendido = None
		try:
			ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
		except VentaFichas.DoesNotExist:
			ficVendido = None
		
		if request.method == "GET":
			m=None
			if request.GET.get('addFic'):
				queryFic = request.GET.get('qFic','')
				queryFic2 = request.GET.get('qFic2','')
				vta = request.GET.get('vtaGral','')
				cliente = request.GET.get('cliente')
				descuento = Mayorista.objects.get(id=cliente).descuentoFichas

				try:
					with transaction.atomic():
						resultAdd = addFichaVta1(queryFic,queryFic2,descuento,mysucursal, vta, request.user,None)	
						pf = VentaMayoreo() #historial de ventas de mayoristas
						pf.folioVenta 	= Venta.objects.get(folioVenta=vta)
						pf.clienteMayoreo 	= Mayorista.objects.get(id=cliente)
						pf.descuentoAplicado = descuento
						pf.save()
						updVta(vta,mysucursal,request.user)
						form = AddVentaCaja({'folioVenta':vta,'total':sumaVtas2(vta)})
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
					#sukiiya #transaction.commit()#'''
				try:
					ficVendido = VentaFichas.objects.filter(venta__folioVenta=vta)
				except VentaFichas.DoesNotExist:
					ficVendido = None
				
				ctx = {'ficVendido':ficVendido,'cliente':form3,'vtaForm':form ,'resultAdd':resultAdd,'queryFic':queryFic,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
				return render_to_response('ventas/VtaMayoreoFichas.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('print'):
				vta = request.GET.get('print','')
				if vta:
					mivi = None
					try:
						v = Venta.objects.get(folioVenta=vta)
						ok = suc_permisos(nivel,request.user,v.sucursal)
						if ok:
							mivi = listarTicket(vta)
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('ventas/ticket.html',ctx,context_instance=RequestContext(request))

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
							vtaGral.mayoreo  	= True
							vtaGral.aceptada  	= True
							vtaGral.estado 		= EstadoVenta.objects.get(estado='Pagada')
							vtaGral.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
						#sukii #transaction.commit()#'''

					form3 = AsignarMayorista()

					vta= nuevoFolio2(str(mysucursal.id)+'M')
					form = AddVentaCaja({'folioVenta':vta,'total':0})
					show= False
					info=" Venta "+vtaGral.estado.estado+" - " + vtaGral.folioVenta +" Cambio: $ "+str(efectivo - total)
					mfolioVenta = vtaGral.folioVenta #ticket ya
				
					ctx = {'folioVenta':mfolioVenta, 'cliente':form3,'vtaForm':form ,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
					return render_to_response('ventas/VtaMayoreoFichas.html',ctx,context_instance=RequestContext(request))
				else:
					show = True
					info = "El pago debe ser mayor o igual al monto total a pagar. Debe ingresar por lo menos un producto a la venta"
					form = AddVentaCaja(request.POST)
					form3 = AsignarMayorista(request.POST)
					ctx = {'ficVendido':ficVendido,'cliente':form3,'vtaForm':form ,'resultAdd':resultAdd,'queryFic':queryFic,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
					return render_to_response('ventas/VtaMayoreoFichas.html',ctx,context_instance=RequestContext(request))
			else:
				form = AddVentaCaja(request.POST)
				info = "Ingrese $monto del cliente a pagar. Debe ingresar al menos un producto a la venta"
				ctx = {'ficVendido':ficVendido,'cliente':form3,'vtaForm':form ,'resultAdd':resultAdd,'queryFic':queryFic,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
				return render_to_response('ventas/VtaMayoreoFichas.html',ctx,context_instance=RequestContext(request))

		if 'cancelar' in request.POST:
			form = AddVentaCaja(request.POST)
			if form.is_valid():
				ifolioVenta 	= form.cleaned_data['folioVenta']
				efectivo 	= form.cleaned_data['efectivo']
				total 		= form.cleaned_data['total']

				if total > 0 or efectivo == 0:
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
							info="Venta Cancelada: "+ vtaGral.folioVenta +"- En espera de autorizacion. "+results
					except :
						info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
					
					form = AddVentaCaja()
					form3 = AsignarMayorista()
					vta= nuevoFolio2(str(mysucursal.id)+'M')
					form = AddVentaCaja({'folioVenta':vta,'total':0})
					
					ctx = {'cliente':form3,'vtaForm':form ,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
					return render_to_response('ventas/VtaMayoreoFichas.html',ctx,context_instance=RequestContext(request))
				else:
					form = AddVentaCaja(request.POST)
					info = "Debe ingresar al menos un producto a la venta."
					ctx = {'ficVendido':ficVendido,'cliente':form3,'vtaForm':form ,'resultAdd':resultAdd,'queryFic':queryFic,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
					return render_to_response('ventas/VtaMayoreoFichas.html',ctx,context_instance=RequestContext(request))
			else:
				form = AddVentaCaja(request.POST)
				info = "Ingrese el monto que pago el cliente, si en dado caso se cancelo, ponga un 0. Debe ingresar por lo menos un producto a la venta."
				ctx = {'ficVendido':ficVendido,'cliente':form3,'vtaForm':form ,'resultAdd':resultAdd,'queryFic':queryFic,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
				return render_to_response('ventas/VtaMayoreoFichas.html',ctx,context_instance=RequestContext(request))
		
		
		ctx = {'ficVendido':ficVendido,'cliente':form3,'vtaForm':form ,'resultAdd':resultAdd,'queryFic':queryFic,'vtaGenerada':vta,'nivel':nivel,'vendedor':xhsdfg,'info':info}
		return render_to_response('ventas/VtaMayoreoFichas.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_ventas_apartados_clientes_nuevo_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		
		form = addClienteServicioForm()
		info = ""
		
		if request.method == "POST":
			form = addClienteServicioForm(request.POST or None)
			
			if form.is_valid():
				nombre 		= form.cleaned_data['nombre']
				direccion 	= form.cleaned_data['direccion']
				colonia 	= form.cleaned_data['colonia']
				ciudad  	= form.cleaned_data['ciudad']
				estado  	= form.cleaned_data['estado']
				
				z1 = agregarCiudades(colonia,ciudad,estado,None)
				try:
					with transaction.atomic():
						a = ClienteServicio()
						a.nombre 		= (nombre).title()
						a.direccion 	= (direccion).title()
						a.colonia = Colonia.objects.get(id=z1[0])
						a.ciudad = Ciudad.objects.get(id=z1[1])
						a.sucursal 	= mysucursal
						a.tipoCliente = 'Apartado'
						a.folio = nvofolioCliente()
						a.save()
						info ="Se ha Guardado con Exito. Folio Cliente: "+ a.folio
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				form = addClienteServicioForm()
				ctx = {'form':form,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/nuevoClienteApartado.html', ctx, context_instance=RequestContext(request))
				
			else:
				form = addClienteServicioForm(request.POST)
				info ="Verifique la informacion, no se han registrado los datos"

		ctx = {'form':form,'info':info,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/nuevoClienteApartado.html', ctx, context_instance=RequestContext(request))
		
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_ventas_apartados_clientes_catalogo_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)
		
		clientes = ClienteServicio.objects.all()
		query = ''
		results = []
		info =""
		mostrar= True
		if request.method == "GET":
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					qset = (Q(nombre__icontains=query) | Q(direccion__icontains=query) | Q(folio__icontains=query)  | 
						Q(colonia__colonia__icontains=query) | Q(ciudad__ciudad__icontains=query))
					results = ClienteServicio.objects.filter(qset,tipoCliente='Apartado',sucursal__id=suc).distinct()
					if results:
						info = "Resultados de la Sucursal"
						mostrar = False
				else:
					results = []
					mostrar = True
			
				ctx = {"results": results,"query": query, 'info':info, 'nivel':nivel,'vendedor':xhsdfg, 'clientes':clientes, 'mostrar':mostrar }
				return render_to_response('ventas/catalogoClienteApartados.html',ctx,context_instance=RequestContext(request))

			else:
				info = 'Por Favor, de un nombre o direccion a buscar'
				mostrar = True
		
		ctx = {"results": results,"query": query, 'info':info, 'nivel':nivel,'vendedor':xhsdfg,'clientes':clientes, 'mostrar':mostrar}
		return render_to_response('ventas/catalogoClienteApartados.html',ctx,context_instance=RequestContext(request))
		#"""
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_ventas_apartados_nuevo_apartado_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)
		#variables
		form 	= addApartado()
		buscar  = True
		query 	= ''
		mostrar = False
		boton   = False
		resultsCli 	= []
		info 		= ""
		#envia el apartado para el catalogo de clietnes
		newVta = None
		if request.method == "GET":
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					qset = (Q(nombre__icontains=query) | Q(direccion__icontains=query) | Q(folio__icontains=query)  | 
						Q(colonia__colonia__icontains=query) | Q(ciudad__ciudad__icontains=query))
					resultsCli = ClienteServicio.objects.filter(qset,tipoCliente='Apartado',sucursal__id=suc).distinct()
					if resultsCli:
						info = "Resultados Cliente-Servicio"
				else:
					resultsCli = []
			
				buscar = True
				ctx = {'buscar':buscar,"resultsCli": resultsCli,"query": query,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/addApartado.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('nvoA'):
				elCliente = request.GET.get('nvoA','')
				if elCliente:
					x = ClienteServicio.objects.get(id=elCliente)
					form= addApartado({'key': x.id,'cliente':x.nombre+' '+x.direccion})
					buscar = False
					mostrar = True
					boton = True

					ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,"resultsCli": resultsCli,"query": query,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/addApartado.html',ctx,context_instance=RequestContext(request))
	
			if request.GET.get('print'):
				vta = request.GET.get('print','')
				if vta:
					mivi = None
					try:
						v = Venta.objects.get(folioVenta=vta)
						ok = suc_permisos(nivel,request.user,v.sucursal)
						if ok:
							mivi = listarTicket(vta)
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('ventas/ticket.html',ctx,context_instance=RequestContext(request))

		if request.method == "POST":

			form = addApartado(request.POST)
			if form.is_valid():
				key 		= form.cleaned_data['key']
				equipo 		= form.cleaned_data['equipo']
				observacion = form.cleaned_data['observacion']
				anticipo 	= form.cleaned_data['anticipo']
				
				cliente = ClienteServicio.objects.get(id= key)
				dte = DetallesEquipo.objects.get(id=equipo)
				pa = dte.precioMenudeo # precio actual
				Cambio = 0
				Pagado = None
				if anticipo > 0 and anticipo >= pa:
					Pagado = True
					Cambio = anticipo - pa
				elif anticipo > 0 and anticipo < pa:
					Pagado = False

				else:
					form = addApartado(request.POST)
					buscar = False
					mostrar = True
					boton = True
					info ='Lo sentimos, El Anticipo debe ser mayor que cero.'	
					ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,"resultsCli": resultsCli,"query": query,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/addApartado.html',ctx,context_instance=RequestContext(request))
				if Pagado:
					form = addApartado(request.POST)
					buscar = False
					mostrar = True
					boton = True
					info ='Lo sentimos, En un primer apartado no puede haber liquidaciones.'	
					ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,"resultsCli": resultsCli,"query": query,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/addApartado.html',ctx,context_instance=RequestContext(request))

				try:	
					with transaction.atomic():
						newVta = Venta()
						newVta.folioVenta 	= nuevoFolio2(str(suc)+'A')
						newVta.sucursal 	= Sucursal.objects.get(id=suc)
						newVta.usuario 		= request.user
						if Pagado:
							newVta.total 	= pa
						else:
							newVta.total 	= anticipo
						newVta.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
						newVta.estado 		= EstadoVenta.objects.get(estado='Pagada')
						newVta.aceptada = True
						newVta.save()

						#generar anticipo
						a = Anticipo()
						a.folioVenta 	= newVta
						a.tipoAnticipo 	= 'Anticipo de Apartado'
						if Pagado:
							a.monto		= pa
						else:
							a.monto		= anticipo
						a.observacion  = 'Cliente No. '+ cliente.folio+' '+cliente.nombre
						a.save()
								
						#generar historial cliente -a abono
						b = Apartado()
						b.clienteApartado = cliente
						b.equipo 	= dte
						b.observacion 	= observacion+' Eq.Inicial '+ dte.marca.marca+' '+dte.modelo
						b.precioEquipo 	= pa
						if Pagado:
							b.pagado = True
							b.estado = EstadoApartado.objects.get(estado='Liquidado')
						else:
							b.estado = EstadoApartado.objects.get(estado='Apartado')
						b.save()
								
						c = HistorialApartado()
						c.apartado 	= b
						c.abono = anticipo
						if Pagado:
							c.tipo = 'Liquidacion'
						else:
							c.tipo = 'Anticipo'
						c.save()

						buscar = False
						mostrar = True
						boton =  False
						mfolioVenta = newVta.folioVenta #ticket ya
						info ="Se ha Guardado con Exito y Agregado la venta con folio: "+ newVta.folioVenta
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				ctx = {'folioVenta':mfolioVenta, 'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/addApartado.html',ctx,context_instance=RequestContext(request))
				

			else:
				form = addApartado(request.POST)
				buscar = False
				mostrar = True
				boton = True
				info ='Lo sentimos, la informacion contiene errores, verifique sus datos.'	
				ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,"resultsCli": resultsCli,"query": query,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/addApartado.html',ctx,context_instance=RequestContext(request))	
			
		ctx = {'buscar':buscar,"resultsCli": resultsCli,"query": query,'info':info,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/addApartado.html',ctx,context_instance=RequestContext(request))
		
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_ventas_apartados_abonos_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)
		#variables
		form 	= abonoApartado()
		buscar  = True
		query 	= ''
		apartados = False
		mostrar = False
		boton   = False
		resultsCli 	= []
		info 		= ""
		mfolioVenta = None
		if request.method == "GET":
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					qset = (Q(nombre__icontains=query) | Q(direccion__icontains=query) | Q(folio__icontains=query)  | 
						Q(colonia__colonia__icontains=query) | Q(ciudad__ciudad__icontains=query))
					resultsCli = ClienteServicio.objects.filter(qset,tipoCliente='Apartado',sucursal__id=suc).distinct()
					if resultsCli:
						info = "Resultados Cliente-Servicio"
				else:
					resultsCli = []
			
				buscar = True
				ctx = {'buscar':buscar,"resultsCli": resultsCli,"query": query,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/abonoClienteApartado.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('veA'):
				elCliente = request.GET.get('veA','')
				if elCliente:
					dequien = ClienteServicio.objects.get(id=elCliente)
					apartadosCli = Apartado.objects.filter(clienteApartado__id=elCliente)
					caducado = []
					for x in apartadosCli:
						fx1 = (x.fxApartado).date()
						fx2 = datetime.now().date() 
						diff = fx2 - fx1
						if diff > timedelta(days=32):
							caducado.append([x, diff.days, True])
							try:
								x.estado = EstadoApartado.objects.get(estado='Auto-Cancelado')
								x.observacion = "Cancelado por el sistema"
								x.save()
							except :
								pass
						else:
							caducado.append([x, diff.days , False])
					buscar = False
					apartados = True

					ctx = {'apartados':apartados, 'buscar':buscar,"apartadosCli": apartadosCli,"caducado":caducado ,"dequien": dequien,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/abonoClienteApartado.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('aboA'):
				elapa = request.GET.get('aboA','')
				if elapa:
					grrr = Apartado.objects.get(id=elapa)
					pe = grrr.equipo.precioMenudeo
					hist = HistorialApartado.objects.filter(apartado=grrr)
					suma = 0
					for x in hist:
						suma = suma + x.abono
					resta = pe - suma

					form= abonoApartado({
						'key':grrr.id,
						'cliente':grrr.clienteApartado.nombre+' '+grrr.clienteApartado.direccion,
						'equipo':grrr.equipo.marca.marca+' '+grrr.equipo.modelo+' '+grrr.equipo.color+' $'+str(grrr.equipo.precioMenudeo),
						'faltante': resta
						})
					
					buscar = False
					mostrar = True
					boton = True

					ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/abonoClienteApartado.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('print'):
				vta = request.GET.get('print','')
				if vta:
					mivi = None
					try:
						v = Venta.objects.get(folioVenta=vta)
						ok = suc_permisos(nivel,request.user,v.sucursal)
						if ok:
							mivi = listarTicket(vta)
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('ventas/ticket.html',ctx,context_instance=RequestContext(request))			
		
		if request.method == "POST":

			form = abonoApartado(request.POST)
			if form.is_valid():
				key 	 = form.cleaned_data['key']
				faltante = form.cleaned_data['faltante']
				abonar 	 = form.cleaned_data['abonar']

				b = Apartado.objects.get(id=key)
				fx1 = (b.fxApartado).date()
				fx2 = datetime.now().date() 
				diff = fx2 - fx1
				errores = False
				if diff > timedelta(days=32):
					try:
						b.estado = EstadoApartado.objects.get(estado='Auto-Cancelado')
						b.observacion = "Cancelado por el sistema"
						b.save()
						caducado = True
						info = "Lo sentimos, su apartado ha sido Auto-Cancelado por que ya paso el limite de espera."
					except :
						pass
				
				Cambio = 0
				Pagado = None
				if abonar > 0 and abonar >= faltante:
					form = abonoApartado(request.POST)
					info
					buscar = False
					mostrar = True
					boton = True
					info = "El apartado será liquidado, por lo que se le solicita que ingrese a la seccion de liquidaciones, Gracias."
					
					ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/abonoClienteApartado.html',ctx,context_instance=RequestContext(request))

				elif abonar > 0 and abonar < faltante:
					try:
						Pagado = False
						b.estado = EstadoApartado.objects.get(estado='Abonos')
						b.save()
					except :
						info=' Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				elif errores:
					form = abonoApartado(request.POST)
					buscar = False
					mostrar = True
					boton = False
					ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/abonoClienteApartado.html',ctx,context_instance=RequestContext(request))

				else:
					form = abonoApartado(request.POST)
					buscar = False
					mostrar = True
					boton = True
					info = 'Lo sentimos, El Abono debe ser mayor que cero.'	
					ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/abonoClienteApartado.html',ctx,context_instance=RequestContext(request))

				try:
					with transaction.atomic():
						newVta = Venta()
						newVta.folioVenta 	= nuevoFolio2(str(suc)+'A')
						newVta.sucursal 	= Sucursal.objects.get(id=suc)
						newVta.usuario 		= request.user
						if Pagado:
							newVta.total 	= faltante
						else:
							newVta.total 	= abonar
						newVta.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
						newVta.estado 		= EstadoVenta.objects.get(estado='Pagada')
						newVta.aceptada = True
						newVta.save()

						#generar anticipo
						a = Anticipo()
						a.folioVenta 	= newVta
						a.tipoAnticipo 	= 'Apartado Abono'
						if Pagado:
							a.monto		= faltante
						else:
							a.monto		= abonar
						a.observacion 	= 'Cliente No. '+b.clienteApartado.folio+' '+b.clienteApartado.nombre
						a.save()
								
						#generar historial cliente -a abono
						c = HistorialApartado()
						c.apartado 	= b
						c.abono = abonar
						if Pagado:
							c.tipo = 'Liquidacion'
						else:
							c.tipo = 'Abono'
						c.save()

						buscar = False
						mostrar = True
						boton =  False
						info ="Se ha Guardado con Exito y Agregado la venta con folio: "+ newVta.folioVenta
						mfolioVenta = newVta.folioVenta #ticket ya
				
				except :			
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				ctx = {'folioVenta':mfolioVenta, 'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/abonoClienteApartado.html',ctx,context_instance=RequestContext(request))

			else:
				info ='Lo sentimos, la informacion contiene errores, verifique sus datos.'	
				form = abonoApartado(request.POST)
				buscar = False
				mostrar = True
				boton = True
				
				ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/abonoClienteApartado.html',ctx,context_instance=RequestContext(request))
			
		ctx = {'buscar':buscar,"resultsCli": resultsCli,"query": query,'info':info,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/abonoClienteApartado.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo
@login_required(login_url='/')
def ventas_ventas_apartados_liquidacion_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)
		#
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		#variables
		form 	= liquidacionApartado()
		buscar  = True
		query 	= ''
		apartados = False
		mostrar = False
		boton   = False
		resultsCli 	= []
		info 		= ""
		mfolioVenta = None
		if request.method == "GET":
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					qset = (Q(nombre__icontains=query) | Q(direccion__icontains=query) | Q(folio__icontains=query)  | 
						Q(colonia__colonia__icontains=query) | Q(ciudad__ciudad__icontains=query))
					resultsCli = ClienteServicio.objects.filter(qset,tipoCliente='Apartado',sucursal__id=suc).distinct()
					if resultsCli:
						info = "Resultados Cliente-Servicio :"
				else:
					resultsCli = []
			
				buscar = True
				ctx = {'buscar':buscar,"resultsCli": resultsCli,"query": query,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/liquidacionApartado.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('veA'):
				elCliente = request.GET.get('veA','')
				if elCliente:
					dequien = ClienteServicio.objects.get(id=elCliente)
					apartadosCli = Apartado.objects.filter(clienteApartado__id=elCliente)
					caducado = []
					for x in apartadosCli:
						fx1 = (x.fxApartado).date()
						fx2 = datetime.now().date() 
						diff = fx2 - fx1
						if diff > timedelta(days=32):
							caducado.append([x, diff.days, True])
							try:
								x.estado = EstadoApartado.objects.get(estado='Auto-Cancelado')
								x.observacion = "Cancelado por el sistema"
								x.save()
							except :
								pass
						else:
							caducado.append([x, diff.days, False])

					buscar = False
					apartados = True

					ctx = {'apartados':apartados, 'buscar':buscar,"apartadosCli": apartadosCli,"caducado":caducado ,"dequien": dequien,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/liquidacionApartado.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('liquida'):
				elapa = request.GET.get('liquida','')
				if elapa:
					grrr = Apartado.objects.get(id=elapa)
					pe = grrr.equipo.precioMenudeo
					hist = HistorialApartado.objects.filter(apartado=grrr)
					suma = 0
					for x in hist:
						suma = suma + x.abono
					resta = pe - suma

					form= liquidacionApartado({
						'key':grrr.id,
						'key2':grrr.equipo.id,
						'cliente':grrr.clienteApartado.nombre+' '+grrr.clienteApartado.direccion,
						'equipo':grrr.equipo.marca.marca+' '+grrr.equipo.modelo+' '+grrr.equipo.color+' $'+str(grrr.equipo.precioMenudeo),
						'precio':pe,
						'historial':suma,
						'faltante': resta
						})
					
					
					buscar = False
					mostrar = True
					boton = True

					ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/liquidacionApartado.html',ctx,context_instance=RequestContext(request))
				else:
					info='puta madre'

			if request.GET.get('print'):
				vta = request.GET.get('print','')
				if vta:
					mivi = None
					try:
						v = Venta.objects.get(folioVenta=vta)
						ok = suc_permisos(nivel,request.user,v.sucursal)
						if ok:
							mivi = listarTicket(vta)
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('ventas/ticket.html',ctx,context_instance=RequestContext(request))			
		
		if request.method == "POST":

			form = liquidacionApartado(request.POST)
			if form.is_valid():
				key 	 = form.cleaned_data['key']
				key2 	 = form.cleaned_data['key2']
				imei 	 = form.cleaned_data['imei']
				faltante = form.cleaned_data['faltante']
				historial = form.cleaned_data['historial']
				abonar 	 = form.cleaned_data['abonar']

				b = Apartado.objects.get(id=key)
				fx1 = (b.fxApartado).date()
				fx2 = datetime.now().date() 
				diff = fx2 - fx1
				caducado = False
				if diff > timedelta(days=32):
					try:
						b.estado = EstadoApartado.objects.get(estado='Auto-Cancelado')
						b.observacion = "Cancelado por el sistema"
						b.save()
						caducado = True
						info = "Lo sentimos, su apartado ha sido Auto-Cancelado por que ya paso el limite de espera."
					except :
						pass
				
				mismo = False
				diferente = False
				cambiado = False
				errores = False
				faltante2 = 0				
				meq = None
				
				try:
					meq = Equipo.objects.get(imei=imei,sucursal=mysucursal)
					try:
						gogeta = VentaEquipo.objects.get(equipo=meq)
						if gogeta:
							meq = None
					except :
						pass					
					if meq.estatus.estatus=='En mal estado' or meq.estatus.estatus=='Activado' or meq.estatus.estatus=='Existente' and meq.icc != None:
						pass
					else:
						meq = None
				
				except :
					info ="(-) El equipo no se encuentra disponible o no cuenta con icc o pertenece a otra sucursal."
					form = liquidacionApartado(request.POST)
					buscar = False
					mostrar = True
					boton = True
					
					ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/liquidacionApartado.html',ctx,context_instance=RequestContext(request))
				
				if meq:
					total = abonar + historial
					eqA = DetallesEquipo.objects.get(id=key2)
					if eqA.id == meq.detallesEquipo.id:
						if abonar > 0 and abonar >= faltante:
							mismo = True
						else:
							info = "Lo sentimos no cubre el faltante del equipo, realice la operacion en la seccion de abonos. Gracias"
							errores = True
					elif meq.detallesEquipo.precioMenudeo >=eqA.precioMenudeo:
						faltante2 = meq.detallesEquipo.precioMenudeo - historial
						if abonar > 0 and total >=faltante2:
							diferente = True
						elif abonar > 0 and total < faltante2:
							cambiado = True
							diferente = True
					if total > meq.detallesEquipo.precioMenudeo:
						errores = True
						info = "Lo sentimos, para cambios de equipo diferentes al apartado, debe ser mayor a los abonos acumulados, no hay reembolsos. Verifique con un Administrador. gracias."
						
				else:
					errores = True
				if caducado:
					form = liquidacionApartado(request.POST)
					buscar = False
					mostrar = True
					boton = False
					
					ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/liquidacionApartado.html',ctx,context_instance=RequestContext(request))

				if errores:
					form = liquidacionApartado(request.POST)
					buscar = False
					mostrar = True
					boton = True
					
					ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/liquidacionApartado.html',ctx,context_instance=RequestContext(request))
				else:
					Pagado = False
					if mismo or diferente and cambiado == False:
						try:
							with transaction.atomic():
								Pagado = True
								if mismo:
									Cambio = abonar - faltante
								else:
									Cambio = abonar - faltante2
								b.pagado = True
								b.estado = EstadoApartado.objects.get(estado='Liquidado')
								b.save()

								newVta = Venta()
								newVta.folioVenta 	= nuevoFolio2(str(suc)+'A')
								newVta.sucursal 	= Sucursal.objects.get(id=suc)
								newVta.usuario 		= request.user
								if mismo:
									newVta.total 	= faltante
								else:
									newVta.total 	= faltante2
								newVta.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
								newVta.estado 		= EstadoVenta.objects.get(estado='Pagada')
								newVta.aceptada 	= True
								newVta.save()

								#generar anticipo
								a = Anticipo()
								a.folioVenta 	= newVta
								a.tipoAnticipo 	= 'Liquidacion Apartado'
								a.observacion = 'Cliente: No. '+b.clienteApartado.folio+' '+b.clienteApartado.nombre
								if mismo:
									a.monto		= faltante
								else:
									a.monto 	= faltante2
								a.save()

								#generar historial cliente -a abono
								c = HistorialApartado()
								c.apartado 	= b
								if mismo:
									c.abono = faltante
								else:
									c.abono = faltante2
								c.tipo = 'Liquidacion'
								c.save()

								#actualizar el apartado con el equipo que se liquido
								nv = Apartado.objects.get(id=c.apartado.id)
								nv.equipo = DetallesEquipo.objects.get(id=meq.detallesEquipo.id)
								nv.save()

								#actualizar equipo
								nv = VentaEquipo()
								nv.venta = newVta #Venta.objects.get(folioVenta=newVta.folioVenta)
								nv.precVenta = 0
								nv.equipo = meq
								nv.save()
											
								#upd producto state
								upd = Equipo.objects.get(imei=nv.equipo.imei)
								upd.estatus = Estatus.objects.get(estatus='Liquidado')
								upd.save()
							
								#dar de baja de su almacen
								vta_almacenItems(0,upd,None,mysucursal)

								buscar = False
								mostrar = True
								boton =  False
								info ="Se ha Guardado con Exito y Agregado la venta con folio: "+ newVta.folioVenta
								mfolioVenta = newVta.folioVenta
								
								ctx = {'folioVenta':mfolioVenta, 'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
								return render_to_response('ventas/liquidacionApartado.html',ctx,context_instance=RequestContext(request))
						except :
							info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
					else:
						try:
							with transaction.atomic():
								b.pagado = False
								b.estado = EstadoApartado.objects.get(estado='Abonos')
								b.save()

								newVta = Venta()
								newVta.folioVenta 	= nuevoFolio2(str(suc)+'A')
								newVta.sucursal 	= Sucursal.objects.get(id=suc)
								newVta.usuario 		= request.user
								newVta.total 		= abonar
								newVta.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
								newVta.estado 		= EstadoVenta.objects.get(estado='Pagada')
								newVta.aceptada 	= True
								newVta.save()

								#generar anticipo
								a = Anticipo()
								a.folioVenta 	= newVta
								a.tipoAnticipo 	= 'Apartado Cambio'
								a.observacion = 'Cliente: No. '+b.clienteApartado.folio+' '+b.clienteApartado.nombre
								a.monto		= abonar
								a.save()
										
								#generar historial cliente -a abono
								c = HistorialApartado()
								c.apartado 	= b
								c.abono = abonar
								c.tipo = 'Cambio de Equipo'
								c.save()

								#actualizar equipo en apartados
								nv = Apartado.objects.get(id=c.apartado.id)
								nv.equipo = DetallesEquipo.objects.get(id=meq.detallesEquipo.id)
								nv.save()
											

								buscar = False
								mostrar = True
								boton =  False
								info ="Se ha Guardado con Exito y Agregado la venta con folio: "+ newVta.folioVenta
								mfolioVenta = newVta.folioVenta
								
								ctx = {'folioVenta':mfolioVenta, 'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
								return render_to_response('ventas/liquidacionApartado.html',ctx,context_instance=RequestContext(request))
						except :
							info='(1798) Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
	
				ctx = {'folioVenta':mfolioVenta, 'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/liquidacionApartado.html',ctx,context_instance=RequestContext(request))

			else:
				info ='Lo sentimos, la informacion contiene errores, verifique sus datos.'	
				form = liquidacionApartado(request.POST)
				buscar = False
				mostrar = True
				boton = True
				
				ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/liquidacionApartado.html',ctx,context_instance=RequestContext(request))
			
		ctx = {'buscar':buscar,"resultsCli": resultsCli,"query": query,'info':info,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/liquidacionApartado.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo
@login_required(login_url='/')
def ventas_ventas_apartados_historial_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)
		#variables
		buscar  = True
		query 	= ''
		apartados = False
		mostrar = False
		resultsCli 	= []
		info 		= ""
		
		if request.method == "GET":
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					qset = (Q(nombre__icontains=query) | Q(direccion__icontains=query) | Q(folio__icontains=query)  | 
						Q(colonia__colonia__icontains=query) | Q(ciudad__ciudad__icontains=query))
					resultsCli = ClienteServicio.objects.filter(qset,tipoCliente='Apartado',sucursal__id=suc).distinct()
					if resultsCli:
						info = "Resultados Cliente-Servicio"
				else:
					resultsCli = []
			
				buscar = True
				ctx = {'buscar':buscar,"resultsCli": resultsCli,"query": query,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/historialApartado.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('veA'):
				elCliente = request.GET.get('veA','')
				if elCliente:
					dequien = ClienteServicio.objects.get(id=elCliente)
					apartadosCli = Apartado.objects.filter(clienteApartado__id=elCliente)
					caducado = []
					for x in apartadosCli:
						fx1 = (x.fxApartado).date()
						fx2 = datetime.now().date() 
						diff = fx2 - fx1
						if diff > timedelta(days=32):
							caducado.append([x, diff.days, True])
							try:
								x.estado = EstadoApartado.objects.get(estado='Auto-Cancelado')
								x.observacion = "Cancelado por el sistema"
								x.save()
							except :
								pass
						else:
							caducado.append([x, diff.days, False])
					buscar = False
					apartados = True

					ctx = {'apartados':apartados, 'buscar':buscar,"apartadosCli": apartadosCli,"caducado":caducado ,"dequien": dequien,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/historialApartado.html',ctx,context_instance=RequestContext(request))

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
					

					ctx = {'elapa':grrr,'historial':hist,'sumaHist':suma,'restaHist':resta,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/historialApartado.html',ctx,context_instance=RequestContext(request))
			
		
		ctx = {'buscar':buscar,"resultsCli": resultsCli,"query": query,'info':info,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/historialApartado.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo
@login_required(login_url='/')
def ventas_ventas_apartados_cancelacion_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)
		#
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		#variables
		form 	= cancelacionApartado()
		buscar  = True
		query 	= ''
		apartados = False
		mostrar = False
		boton   = False
		resultsCli 	= []
		info 		= ""
		mfolioVenta = None
		if request.method == "GET":
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					qset = (Q(nombre__icontains=query) | Q(direccion__icontains=query) | Q(folio__icontains=query)  | 
						Q(colonia__colonia__icontains=query) | Q(ciudad__ciudad__icontains=query))
					resultsCli = ClienteServicio.objects.filter(qset,tipoCliente='Apartado',sucursal__id=suc).distinct()
					if resultsCli:
						info = "Resultados Cliente-Servicio :"
				else:
					resultsCli = []
			
				buscar = True
				ctx = {'buscar':buscar,"resultsCli": resultsCli,"query": query,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/cancelacionApartado.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('veA'):
				elCliente = request.GET.get('veA','')
				if elCliente:
					dequien = ClienteServicio.objects.get(id=elCliente)
					apartadosCli = Apartado.objects.filter(clienteApartado__id=elCliente)
					caducado = []
					for x in apartadosCli:
						fx1 = (x.fxApartado).date()
						fx2 = datetime.now().date() 
						diff = fx2 - fx1
						if diff > timedelta(days=32):
							caducado.append([x, diff.days, True])
							try:
								x.estado = EstadoApartado.objects.get(estado='Auto-Cancelado')
								x.observacion = "Cancelado por el sistema"
								x.save()
							except :
								pass
						else:
							caducado.append([x, diff.days, False])

					buscar = False
					apartados = True

					ctx = {'apartados':apartados, 'buscar':buscar,"apartadosCli": apartadosCli,"caducado":caducado ,"dequien": dequien,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/cancelacionApartado.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('cancelapa'):
				elapa = request.GET.get('cancelapa','')
				if elapa:
					grrr = Apartado.objects.get(id=elapa)
					pe = grrr.equipo.precioMenudeo
					hist = HistorialApartado.objects.filter(apartado=grrr)
					suma = 0
					for x in hist:
						suma = suma + x.abono
					resta = pe - suma

					form= cancelacionApartado({
						'key':grrr.id,
						'key2':grrr.equipo.id,
						'cliente':grrr.clienteApartado.nombre+' '+grrr.clienteApartado.direccion,
						'equipo':grrr.equipo.marca.marca+' '+grrr.equipo.modelo+' '+grrr.equipo.color+' $'+str(grrr.equipo.precioMenudeo),
						'precio':pe,
						'historial':suma,
						'completar':0
						})
					
					buscar = False
					mostrar = True
					boton = True

					ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/cancelacionApartado.html',ctx,context_instance=RequestContext(request))
				else:
					info='puta madre'

			if request.GET.get('print'):
				vta = request.GET.get('print','')
				if vta:
					mivi = None
					try:
						v = Venta.objects.get(folioVenta=vta)
						ok = suc_permisos(nivel,request.user,v.sucursal)
						if ok:
							mivi = listarTicket(vta)
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('ventas/ticket.html',ctx,context_instance=RequestContext(request))			
		
		if request.method == "POST":

			form = cancelacionApartado(request.POST)
			if form.is_valid():
				key 	 = form.cleaned_data['key']
				key2 	 = form.cleaned_data['key2']
				historial = form.cleaned_data['historial']
				folio = form.cleaned_data['folio']
				completar = form.cleaned_data['completar']

				b = Apartado.objects.get(id=key)
				fx1 = (b.fxApartado).date()
				fx2 = datetime.now().date() 
				diff = fx2 - fx1
				caducado = False
				if diff > timedelta(days=32):
					try:
						b.estado = EstadoApartado.objects.get(estado='Auto-Cancelado')
						b.observacion = "Cancelado por el sistema"
						b.save()
						caducado = True
						info = "Lo sentimos, su apartado ha sido Auto-Cancelado por que ya paso el limite de espera."
					except :
						pass
					
				
				errores = False
				meq = None
				ficha = 0
				actualizo = False
				cancelar = False
				gen_ant = False
				on_faltante = 0
				Cambio = 0
				try:
					meq = Ficha.objects.get(folio=folio,sucursal=mysucursal)
					try:
						gogeta = VentaFichas.objects.get(ficha=meq)
						if gogeta:
							meq = None
					except :
						pass					
					if meq.estatusFicha.estatus != 'Vendido':
						pass
					else:
						meq = None
				except :
					info ="(-) La ficha no se encuentra disponible o pertenece a otra sucursal."
					form = cancelacionApartado(request.POST)
					buscar = False
					mostrar = True
					boton = True
					
					ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/cancelacionApartado.html',ctx,context_instance=RequestContext(request))
				
				if meq:
					ficha = meq.nominacion.nominacion
					diferencia = historial - ficha
					if diferencia >= 0:
						actualizo = True
						if diferencia == 0:
							cancelar = True
					else:
						dif_completa = diferencia + completar
						if completar > 0 and dif_completa >= 0:
							actualizo = True
							gen_ant = True
							on_faltante = diferencia
							cancelar = True
							if dif_completa >0:
								Cambio = dif_completa
						else:
							errores = True
							info = "Lo sentimos, no podemos cancelar porque no se completa para pagar la ficha de $"+str(meq.nominacion.nominacion)						
				else:
					errores = True
				if caducado:
					form = cancelacionApartado(request.POST)
					buscar = False
					mostrar = True
					boton = False
					
					ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/cancelacionApartado.html',ctx,context_instance=RequestContext(request))

				if errores:
					form = cancelacionApartado(request.POST)
					buscar = False
					mostrar = True
					boton = True
					
					ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/cancelacionApartado.html',ctx,context_instance=RequestContext(request))
				else:
					if actualizo:
						try:
							with transaction.atomic():
								newVta = Venta()
								newVta.folioVenta 	= nuevoFolio2(str(suc)+'A')
								newVta.sucursal 	= Sucursal.objects.get(id=suc)
								newVta.usuario 		= request.user
								if gen_ant:
									newVta.total 	= (on_faltante)*-1
								else:
									newVta.total 	= 0
								newVta.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
								newVta.estado 		= EstadoVenta.objects.get(estado='Pagada')
								newVta.aceptada 	= True
								newVta.save()

								#generar anticipo
								a = Anticipo()
								a.folioVenta 	= newVta
								a.tipoAnticipo 	= 'Cancelacion Apartado'
								a.observacion = 'Cliente: No. '+b.clienteApartado.folio+' '+b.clienteApartado.nombre
								if gen_ant:
									a.monto		= (on_faltante)*-1
								else:
									a.monto 	= 0
								a.save()

								#generar historial cliente -a abono
								c = HistorialApartado()
								c.apartado 	= b
								if cancelar:
									c.abono = -(historial)
								else:
									c.abono = -(ficha)
								c.tipo = '-Ficha $'+str(ficha)
								c.save()

								if cancelar:
									b.pagado = True
									b.estado = EstadoApartado.objects.get(estado='Cambiado por fichas')
									if gen_ant:
										b.observacion = "Se cancela por el cliente. Completo para la ficha "+str(meq)
									else:
										b.observacion = "Se cancela por el cliente. Adquiere ficha "+str(meq)
									b.save()

								#actualizar ficha
								nv = VentaFichas()
								nv.venta = Venta.objects.get(folioVenta=newVta.folioVenta)
								nv.precVenta = 0
								nv.ficha = meq
								nv.save()
											
								#upd producto state
								upd = Ficha.objects.get(folio=nv.ficha.folio)
								upd.estatus = EstatusFicha.objects.get(estatus='Vendido')
								upd.save()
							
								#dar de baja de su almacen
								vta_almacenItems(3,upd,None,mysucursal)
								#'''

								buscar = False
								mostrar = True
								boton =  False

								info = info + " Se ha Guardado con Exito y Agregado la venta con folio: " + newVta.folioVenta
								info = info + " Apartado con estatus : "+str(b.estado)
								if Cambio >0:
									info = info +" Cambio: $ "+str(Cambio)
								mfolioVenta = newVta.folioVenta
								
								ctx = {'folioVenta':mfolioVenta, 'boton':boton,'mostrar':mostrar,'buscar':buscar,
								'info':info,'nivel':nivel,'vendedor':xhsdfg}
								return render_to_response('ventas/cancelacionApartado.html',ctx,context_instance=RequestContext(request))
						except :
							info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'

				ctx = {'folioVenta':mfolioVenta, 'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/cancelacionApartado.html',ctx,context_instance=RequestContext(request))

			else:
				info ='Lo sentimos, la informacion contiene errores, verifique sus datos.'	
				form = cancelacionApartado(request.POST)
				buscar = False
				mostrar = True
				boton = True
				
				ctx = {'form':form,'boton':boton,'mostrar':mostrar,'buscar':buscar,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/cancelacionApartado.html',ctx,context_instance=RequestContext(request))
			
		ctx = {'buscar':buscar,"resultsCli": resultsCli,"query": query,'info':info,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/cancelacionApartado.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')



#listo
@login_required(login_url='/')
def ventas_ventas_pedidos_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)
		form =  nuevoProducto()
		info =""
		enviado = None
		if request.method == "POST":
			form =  nuevoProducto(request.POST or None)
			if form.is_valid():
				producto 	= form.cleaned_data['producto']
				try:
					with transaction.atomic():
						a = SolicitudNuevoProducto()
						a.folio 	= folioMensage(suc)
						a.nuevoProducto = producto
						a.sucursal 	= Sucursal.objects.get(id=suc)
						a.usuario 	= request.user
						a.estado 	= EstadoMensaje.objects.get(estado='Sin Revisar')
						a.save()
						
						info ="Se ha Guardado con Exito. Folio del mensaje: "+ a.folio
						form = nuevoProducto()
						enviado = SolicitudNuevoProducto.objects.filter(sucursal__id=suc)
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
			else:
				form =  nuevoProducto(request.POST or None)
				info = "Verifique la informacion, no se han registrado los datos"

		ctx = {'form':form,'enviado':enviado,'info':info,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/nuevoProducto.html', ctx, context_instance=RequestContext(request))
		
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_ventas_corte_dia_caja_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		
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
					ctx = {'verificarForm':verificarForm ,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/myVerificacionUser.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('cancelaciones'):
				query = request.GET.get('cancelaciones','')
				if query:
					vtaCanceladas = Venta.objects.filter(sucursal=mysucursal,aceptada=False,activa=True)
					ctx = {'rentaVendido':rentaVendido,'planVendido':planVendido,'anticipo':menosAnticipo,'accVendido':accVendido,'vtaCanceladas':vtaCanceladas,'recVendido':recVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'nivel':nivel}
					return render_to_response('ventas/cancelacionServ.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('print'):
				corte = request.GET.get('print','')
				if corte:
					mivi = None
					try:
						Cortes = CorteVenta.objects.get(folioCorteVta=corte)
						ok = suc_permisos(nivel,request.user,Cortes.sucursal)
						if ok:
							mivi = listarCorte(corte) #papitas call method
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('ventas/ticketCorte.html',ctx,context_instance=RequestContext(request))

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
				
				ctx = {'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/myAddArqueo.html',ctx,context_instance=RequestContext(request))
			else:
				info="Ingrese "
				arqForm = addArqueoCaja(request.POST)
				ctx = {'arqForm':arqForm,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/myAddArqueo.html',ctx,context_instance=RequestContext(request))

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
							nivel = Permiso(auditor.user,[1,2,3,4,12])
							if nivel != -1:
								#mandar formulario de arqueo
								caja = updCaja(mysucursal)
								arq = arqueoCaja(mysucursal)
								#llenamos datos iniciales
								arqForm = addArqueoCaja({'vendedor':request.user,'auditor':usuario,'totalCaja':caja })
								ctx = {'arqForm':arqForm, 'arq':arq,'info':info,'nivel':nivel,'vendedor':xhsdfg}
								return render_to_response('ventas/myAddArqueo.html',ctx,context_instance=RequestContext(request))			
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
			ctx = {'verificarForm':verificarForm,'info':info,'nivel':nivel,'vendedor':xhsdfg}
			return render_to_response('ventas/myVerificacionUser.html',ctx,context_instance=RequestContext(request))
		
		ctx = {'vtasCorte':vtasCorte,'Cortes':Cortes,'rentaVendido':rentaVendido,'planVendido':planVendido,'anticipo':menosAnticipo,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/myCorteVentas.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_ventas_corte_dia_gastos_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		
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
						info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
					
				else:
					
					info = "No se puede registrar el gasto, el corte contiene un total menor al gasto. Corte: "+corteActivo
				form = addGastosSucursal()
				ctx = {'corte':corteActivo,'form':form,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/myAddGastos.html',ctx,context_instance=RequestContext(request))
			
			else:
				info = "Ingrese Datos al formulario"
				form= addGastosSucursal(request.POST)
		
		ctx = {'corte':corteActivo,'form':form,'info':info,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/myAddGastos.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')



#listo
@login_required(login_url='/')
def ventas_ventas_corte_dia_cerrar_corte_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		
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
					ctx = {'cerrar':cerrar,'show':show,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/myCerrarCorte.html',ctx,context_instance=RequestContext(request))
			

			if request.GET.get('hoy'):
				t = request.GET.get('hoy','')
				if t:
					corte = generarCorte(mysucursal,None, request.user)
					info = 'El corte de venta se ha generado correctamente. Folio: '+ corte
					show= False
					cerrar = False
					ctx = {'cerrar':cerrar,'show':show,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/myCerrarCorte.html',ctx,context_instance=RequestContext(request))
		
		if 'cerrar' in request.POST:
			form = updCorteVenta(request.POST or None)
			if form.is_valid():
				folioCorteVta 	= form.cleaned_data['folioCorteVta']
				observacion 	= form.cleaned_data['observacion']

				if len(pendientes_papeletas(mysucursal.id)) > 0:
					info = "No puede cerrar Corte, tiene que terminar de llenar las papeletas pendientes, gracias."
					ctx = {'cerrar':cerrar,'show':show,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/myCerrarCorte.html',ctx,context_instance=RequestContext(request))
				else:
					pass
				try:
					with transaction.atomic():
						upd = CorteVenta.objects.get(folioCorteVta=folioCorteVta)
						upd.observacion = observacion
						upd.cierraCorte = request.user
						upd.cerrado 	= True
						upd.save()

						a = RecargasVendidoCorte() #historial de saldo vendido
						a.sucursal = mysucursal
						a.corte =  upd
						a.totalVentas = vtasRecargaCorte(folioCorteVta)
						a.saldoFinal 	= SaldoSucursal.objects.get(sucursal=mysucursal).saldo
						a.save()

						show =  False
						cerrar = True
						info = 'El corte de venta se ha cerrado correctamente. Folio: '+ upd.folioCorteVta
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				ctx = {'cerrar':cerrar,'show':show,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/myCerrarCorte.html',ctx,context_instance=RequestContext(request))
			
			else:
				info = "Verifique sus datos."
				form= updCorteVenta(request.POST)
				show = True
				cerrar = True
				ctx = {'cerrar':cerrar,'cerrarForm':form,'show':show,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/myCerrarCorte.html',ctx,context_instance=RequestContext(request))

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
							#-- django
							nivel=Permiso(request.user,[0,1,2,3,4,12])
							if nivel != -1:
								q = request.POST.get('thisCorte','')
								ctx = {'thisCorte':q ,'cerrarForm':form,'show':show,'info':info,'nivel':nivel,'vendedor':xhsdfg}
								return render_to_response('ventas/myCerrarCorte.html',ctx,context_instance=RequestContext(request))
							else:
								info ="El usuario no tiene permiso para realizar esta operacion"
						except Usuario.DoesNotExist:
								pass
					else:
						info = "Usuario no Activo"
				else:
					info = "Usuario o contraseña incorrectos"
			else:
				info = "Lo sentimos, los datos ingresados no corresponden al personal autorizado, intente nuevamente."
			
			verificarForm =  AuthenticationForm(request.POST)
			ctx = {'thisCorte':grrr,'verificarForm':verificarForm,'info':info,'nivel':nivel,'vendedor':xhsdfg}
			return render_to_response('ventas/myVerificacionUser.html',ctx,context_instance=RequestContext(request))

		ctx = {'thisCorte':grrr,'verificarForm':verificarForm,'info':info,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/myVerificacionUser.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_servicios_clientes_nuevo_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		form = addClienteServicioForm()
		info = ""
		clientes = ClienteServicio.objects.filter(sucursal__id= suc)
		
		if request.method == "POST":

			form = addClienteServicioForm(request.POST or None)
			
			if form.is_valid():
				
				nombre 		= form.cleaned_data['nombre']
				direccion 	= form.cleaned_data['direccion']
				colonia 	= form.cleaned_data['colonia']
				ciudad  	= form.cleaned_data['ciudad']
				estado  	= form.cleaned_data['estado']
				# #id de sucursal

				z1 = agregarCiudades(colonia,ciudad,estado,None)
				try:
					with transaction.atomic():
						a = ClienteServicio()
						a.nombre 		= (nombre).title()
						a.direccion 	= (direccion).title()
						a.colonia = Colonia.objects.get(id=z1[0])
						a.ciudad = Ciudad.objects.get(id=z1[1])
						a.sucursal 	= mysucursal
						a.tipoCliente = 'Servicio'
						a.folio = nvofolioCliente()
						a.save()

						info ="Se ha Guardado con Exito, Folio cliente: "+ a.folio
						form = addClienteServicioForm()
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				ctx = {'form':form,'clientes':clientes ,'info':info,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/nuevoClienteServicio.html', ctx, context_instance=RequestContext(request))

			else:
				form = addClienteServicioForm(request.POST)
				info ="Verifique la informacion, no se han registrado los datos"

		ctx = {'form':form,'clientes':clientes ,'info':info,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/nuevoClienteServicio.html', ctx, context_instance=RequestContext(request))
		
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_servicios_clientes_catalogo_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)
		clientes = ClienteServicio.objects.filter(sucursal__id=suc)
		query = ''
		results = []
		info =""
		mostrar= True
		if request.method == "GET":
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					qset = (Q(folio__icontains=query) | Q(nombre__icontains=query) | Q(direccion__icontains=query) )
					results = ClienteServicio.objects.filter(qset, sucursal__id=suc).distinct()
					if results:
						mostrar = False
				else:
					results = []
					info = "No se Encontraron Resultados."
					mostrar = True
			
				ctx = {"results": results,"query": query, 'info':info, 'nivel':nivel, 'clientes':clientes, 'mostrar':mostrar ,'vendedor':xhsdfg}
				return render_to_response('ventas/catalogoClienteServicios.html',ctx,context_instance=RequestContext(request))

			if  request.GET.get('updC'):
				query = request.GET.get('updC','')
				if query:
					cli = ClienteServicio.objects.get(id=query)
					form = addClienteServicioForm({'nombre':cli.nombre,'direccion':cli.direccion,'colonia':cli.colonia.colonia,
					'ciudad':cli.ciudad.ciudad,'estado':cli.ciudad.estado.id})
				
				ctx = {'form':form, 'info':info, 'nivel':nivel,'noCli':query ,'vendedor':xhsdfg}
				return render_to_response('ventas/updClienteServicios.html',ctx,context_instance=RequestContext(request))				

			else:
				info = 'Por Favor, de un nombre o direccion a buscar'
				mostrar = True
		
		if request.method == "POST":
			form = addClienteServicioForm(request.POST or None)
			if form.is_valid():
				key=request.POST.get('noCli','')
				
				nombre 	= form.cleaned_data['nombre']
				direccion 	= form.cleaned_data['direccion']
				colonia 	= form.cleaned_data['colonia']
				ciudad 	= form.cleaned_data['ciudad']
				estado 	= form.cleaned_data['estado']

				z1 = agregarCiudades(colonia,ciudad,estado,None)
				try:
					with transaction.atomic():
						a = ClienteServicio.objects.get(id=key)
						a.nombre 		= (nombre).title()
						a.direccion 	= (direccion).title()
						a.colonia = Colonia.objects.get(id=z1[0])
						a.ciudad = Ciudad.objects.get(id=z1[1])
						a.save()
						info ="Se ha actualizado con Exito. Folio Cliente: "+ a.folio
				except :
					form = addClienteServicioForm(request.POST or None)
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'				
					form = addClienteServicioForm()

				ctx = {'form':form, 'info':info, 'nivel':nivel, 'vendedor':xhsdfg}
				return render_to_response('ventas/updClienteServicios.html',ctx,context_instance=RequestContext(request))				

			else:
				form = addClienteServicioForm(request.POST or None)
				info='Favor de verificar la información, no se ha podido actualizar.'
				ctx = {'form':form, 'info':info, 'nivel':nivel, 'vendedor':xhsdfg}
				return render_to_response('ventas/updClienteServicios.html',ctx,context_instance=RequestContext(request))				

		ctx = {"results": results,"query": query, 'info':info, 'nivel':nivel,'clientes':clientes, 'mostrar':mostrar,'vendedor':xhsdfg}
		return render_to_response('ventas/catalogoClienteServicios.html',ctx,context_instance=RequestContext(request))
		
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_servicios_cat_reparaciones_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		query = ''
		results = []
		info =""
		mostrarForm = False
		catalogo= Reparacion.objects.filter(activo=True).order_by('tipo').order_by('descripcion')
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
					results = Reparacion.objects.filter(qset, activo=True).distinct()
					if results:
						info = "Resultados"
				else:
					results = []
			
				ctx = {"results": results,"query": query, 'reparaciones':reparaciones ,'info':info, 'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/catalogoReparaciones.html',ctx,context_instance=RequestContext(request))


		ctx = {"results": results,"query": query, 'reparaciones':reparaciones ,'info':info, 'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/catalogoReparaciones.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_servicios_nva_reparacion_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)
	
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
		a = None
		b = None
		c = None
		v = None
		dv = None
		query = ""
		results = ""
		buscar = True
		boton = True
		nvoCC = False
		yaCC = False
		info=""
		formCC = vtaReparacion()
		form = addClienteServicioForm()
		xVendedor = addVendedor()
		mfolioVenta = None
		v = None
		if request.method == "GET":
			
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					
					qset = (Q(nombre__icontains=query)|Q(direccion__icontains=query)|Q(colonia__colonia__icontains=query)|Q(sucursal__nombre__icontains=query)|Q(folio__icontains=query)|Q(fxIngreso__icontains=query) )
					results = ClienteServicio.objects.filter(qset,tipoCliente__icontains='Servicio',sucursal__id=mysucursal.id).distinct()

				else:
					info="El cliente no se encuentra o pertenece a otra sucursal"
					results = []

				buscar = True
				ctx = {'query':query,'results':results,'buscar':buscar,'nivel':nivel,'info':info,'vendedor':xhsdfg}
				return render_to_response('ventas/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))
				
			if request.GET.get('cliCCosto'):
				cliente = request.GET.get('cliCCosto','')
				if cliente:
					cli = ClienteServicio.objects.get(id=cliente)
					formCC = vtaReparacion({'key':cli.id,'cliente':cli.nombre })
					formCC.fields['reparacion'] = forms.ChoiceField(choices=[(c.id, c.tipoReparacion.tipo +' - '+c.descripcion+' $'+str(c.monto) ) for c in Reparacion.objects.filter(activo=True).order_by('descripcion')])
					
					buscar = False
					yaCC = True
					boton = True
					ctx = {'yaCC':yaCC,'formC':formCC,'xVendedor':xVendedor,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
					return render_to_response('ventas/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('nvoCCosto'):
				cliente = request.GET.get('nvoCCosto','')
				if cliente:
					formCC = vtaReparacion({'key':nvofolioCliente(),'cliente':'Nuevo'})
					formCC.fields['reparacion'] = forms.ChoiceField(choices=[(c.id, c.tipoReparacion.tipo +' - '+c.descripcion+' $'+str(c.monto) ) for c in Reparacion.objects.filter(activo=True).order_by('descripcion')])

					buscar = False
					nvoCC = True
					boton = True
					ctx = {'nvoCC':nvoCC,'form':form,'formC':formCC,'xVendedor':xVendedor,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
					return render_to_response('ventas/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('print'):
				vta = request.GET.get('print','')
				if vta:
					mivi = None
					try:
						v = Venta.objects.get(folioVenta=vta)
						ok = suc_permisos(nivel,request.user,v.sucursal)
						if ok:
							mivi = listarTicket(vta)
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('ventas/ticket.html',ctx,context_instance=RequestContext(request))

		if 'regNvoCC' in request.POST:
			formCC = vtaReparacion(request.POST)
			form = addClienteServicioForm(request.POST)
			xVendedor = addVendedor(request.POST)

			if form.is_valid() and formCC.is_valid() and xVendedor.is_valid():
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

				uempleado 	= xVendedor.cleaned_data['usuario']

				elusuario = None
				try:
					elusuario = Usuario.objects.get(user__username = uempleado,empleado__estadoEmpleado=True)
				except Usuario.DoesNotExist:
					info = "Lo sentimos, el nombre de usuario que registra la operacion no existe o no esta activo."
					formCC = vtaReparacion(request.POST)
					form = addClienteServicioForm(request.POST)
					formCC.fields['reparacion'] = forms.ChoiceField(choices=[(c.id, c.tipoReparacion.tipo +' - '+c.descripcion+' $'+str(c.monto) ) for c in Reparacion.objects.filter(activo=True).order_by('descripcion')])
					xVendedor = addVendedor(request.POST)
					buscar = False
					nvoCC = True
					boton = True

					ctx = {'nvoCC':nvoCC,'form':form,'xVendedor':xVendedor,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info, 'vendedor':xhsdfg}
					return render_to_response('ventas/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))
		
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
					formCC.fields['reparacion'] = forms.ChoiceField(choices=[(c.id, c.tipoReparacion.tipo +' - '+c.descripcion+' $'+str(c.monto) ) for c in Reparacion.objects.filter(activo=True).order_by('descripcion')])
					form = addClienteServicioForm(request.POST)
					buscar = False
					nvoCC = True
					boton = True

					ctx = {'nvoCC':nvoCC,'form':form,'xVendedor':xVendedor,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info, 'vendedor':xhsdfg}
					return render_to_response('ventas/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))

				z1 = agregarCiudades(colonia,ciudad,estado,None)
				try:
					with transaction.atomic():
						a = ClienteServicio()
						a.nombre 		= (nombre).title()
						a.direccion 	= (direccion).title()
						a.colonia 		= Colonia.objects.get(id=z1[0])
						a.ciudad 		= Ciudad.objects.get(id=z1[1])
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

						zzz = comisionesReparacion()
						zzz.usuario = elusuario.user
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
						v.aceptada = True
						v.save()

						dv = Anticipo()
						dv.folioVenta 	= v
						dv.tipoAnticipo = 'Servicio: '+c.reparacion.tipoReparacion.tipo
						dv.observacion 	= 'Cliente No. '+a.folio+' '+a.nombre
						dv.monto 		= pago
						dv.save()
						
						info="Se ha registrado la entrada de un equipo para flexeo Tecnico.Folio cliente: "+str(a.folio)+" Folio de Venta: "+ v.folioVenta+" Cambio: $"+str(Cambio)
						mfolioVenta = v.folioVenta #ticket ya
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'

				boton= False
				nvoCC = True
				ctx = {'folioVenta':mfolioVenta, 'nvoCC':nvoCC,'boton':boton,'nivel':nivel,'info':info}
				return render_to_response('ventas/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))
			else:
				info = "No se registro. Verifique sus datos."
				formCC = vtaReparacion(request.POST)
				formCC.fields['reparacion'] = forms.ChoiceField(choices=[(c.id, c.tipoReparacion.tipo +' - '+c.descripcion+' $'+str(c.monto) ) for c in Reparacion.objects.filter(activo=True).order_by('descripcion')])
					
				form = addClienteServicioForm(request.POST)
				buscar = False
				nvoCC = True
				boton = True
			ctx = {'nvoCC':nvoCC,'form':form,'formC':formCC,'xVendedor':xVendedor,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
			return render_to_response('ventas/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))

		if 'regCC' in request.POST:
			formCC = vtaReparacion(request.POST)
			xVendedor = addVendedor(request.POST)
			if formCC.is_valid() and xVendedor.is_valid():#cliente conocido, porta con costo

				key 	= formCC.cleaned_data['key']
				marcaModelo = formCC.cleaned_data['marcaModelo']
				imei 		= formCC.cleaned_data['imei']
				falla 		= formCC.cleaned_data['falla']
				observacion = formCC.cleaned_data['observacion']
				anticipo 	= formCC.cleaned_data['anticipo']
				reparacion 	= formCC.cleaned_data['reparacion']

				uempleado 	= xVendedor.cleaned_data['usuario']

				elusuario = None
				try:
					elusuario = Usuario.objects.get(user__username = uempleado,empleado__estadoEmpleado=True)
				except Usuario.DoesNotExist:
					info = "Lo sentimos, el nombre de usuario que registra la operacion no existe o no esta activo."
					form = addClienteServicioForm(request.POST)
					xVendedor = addVendedor(request.POST)
					formCC = vtaReparacion(request.POST)
					formCC.fields['reparacion'] = forms.ChoiceField(choices=[(c.id, c.tipoReparacion.tipo +' - '+c.descripcion+' $'+str(c.monto) ) for c in Reparacion.objects.filter(activo=True).order_by('descripcion')])
					
					buscar = False
					yaCC = True
					boton = True
					ctx = {'yaCC':yaCC,'form':form,'xVendedor':xVendedor,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info, 'vendedor':xhsdfg}
					return render_to_response('ventas/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))

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
					formCC.fields['reparacion'] = forms.ChoiceField(choices=[(c.id, c.tipoReparacion.tipo +' - '+c.descripcion+' $'+str(c.monto) ) for c in Reparacion.objects.filter(activo=True).order_by('descripcion')])
					xVendedor = addVendedor(request.POST)

					buscar = False
					yaCC = True
					boton = True
					ctx = {'yaCC':yaCC,'form':form,'xVendedor':xVendedor,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info, 'vendedor':xhsdfg}
					return render_to_response('ventas/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))
				try:
					with transaction.atomic():
						a = ClienteServicio.objects.get(id=key)

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

						zzz = comisionesReparacion()
						zzz.usuario = elusuario.user
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
						v.aceptada = True
						v.save()

						dv = Anticipo()
						dv.folioVenta 		= v
						dv.tipoAnticipo 	= 'Servicio: '+c.reparacion.tipoReparacion.tipo
						dv.monto 			= pago
						dv.observacion 	= 'Cliente No. '+a.folio+' '+a.nombre
						dv.save()

						info="Se ha registrado la entrada de un equipo para flexeo por portabilidad con costo. Folio de Venta: "+ v.folioVenta+" Cambio: $"+str(Cambio)+" Cliente: "+str(a.folio)
						mfolioVenta = v.folioVenta
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				buscar = False
				yaCC = True
				boton = False
				ctx = {'folioVenta':mfolioVenta, 'yaCC':yaCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info, 'vendedor':xhsdfg}
				return render_to_response('ventas/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))
				
			else:
				info = "No se registro. Verifique sus datos."
				formCC = vtaReparacion(request.POST)
				formCC.fields['reparacion'] = forms.ChoiceField(choices=[(c.id, c.tipoReparacion.tipo +' - '+c.descripcion+' $'+str(c.monto) ) for c in Reparacion.objects.filter(activo=True).order_by('descripcion')])
				xVendedor = addVendedor(request.POST)

				buscar = False
				yaCC = True
				boton = True
			ctx = {'yaCC':yaCC,'formC':formCC,'xVendedor':xVendedor,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info, 'vendedor':xhsdfg}
			return render_to_response('ventas/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))
		
		ctx = {'query':query,'results':results,'buscar':buscar,'nivel':nivel,'info':info, 'vendedor':xhsdfg}
		return render_to_response('ventas/vtaReparacionFisica.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_servicios_seguimiento_consultar_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)
		info =""
		buscar = True
		query = ''
		_usuario 	= Usuario.objects.get(user=request.user)
		_empleado 	= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		pagina = request.GET.get('pagina','')
		query  = request.GET.get('q','')
		reparaciones=None
		nReparaciones=0
		mfolioVenta = None
		if query:
			qset=(Q(cliente__nombre__icontains=query) |
			 Q(sucursal__nombre__icontains=query) | 
			 Q(cliente__folio__icontains=query))
			ccosto = EquipoReparacion.objects.filter(qset,sucursal__id=suc, cliente__tipoCliente__icontains='Servicio')
		else:
			ccosto = EquipoReparacion.objects.filter(sucursal__id=suc, cliente__tipoCliente__icontains='Servicio')

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
				show =  True

				ctx = {'reparaciones':reparacionesp,'show':show,'buscar':buscar,'info':info, 'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/seguimientoReparaciones.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('upd'):
				query = request.GET.get('upd', '')
				if query:
					ccosto = EquipoReparacion.objects.get(id = query)
					formC = updCostoPorta({'key':ccosto.id,'cliente':ccosto.cliente.nombre,
						'marcaModelo':ccosto.marcaModelo,'imei':ccosto.imei,'falla': ccosto.falla,
						'observacion':ccosto.observacion,'edoActual':ccosto.estado.estado })
					updDatos = True
					buscar = False

					ctx = {'buscar':buscar,'updDatos':updDatos,'formC':formC ,'info':info, 'nivel':nivel,'vendedor':xhsdfg }
					return render_to_response('ventas/seguimientoReparaciones.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('histRep'):
				query = request.GET.get('histRep', '')
				if query:
					clirep = EquipoReparacion.objects.get(id = query)
					repHist = HistorialClienteReparacion.objects.filter(equipoReparacion__id=clirep.id)

					sumaHist=0
					for x in repHist:
						sumaHist =  sumaHist + x.abono

					resta = clirep.reparacion.monto - sumaHist

					histCli = True

					ctx = {'clirep':clirep,'sumaHist':sumaHist,'restaHist':resta,'historial':repHist,'histCli':histCli ,'info':info, 'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/seguimientoReparaciones.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('aboRep'):
				query = request.GET.get('aboRep', '')
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
					buscar = False
					abonarCli = True
					ctx = {'buscar':buscar,'abonarCli':abonarCli,'formC':formC ,'info':info, 'nivel':nivel,'vendedor':xhsdfg }
					return render_to_response('ventas/seguimientoReparaciones.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('print'):
				vta = request.GET.get('print','')
				if vta:
					mivi = None
					try:
						v = Venta.objects.get(folioVenta=vta)
						ok = suc_permisos(nivel,request.user,v.sucursal)
						if ok:
							mivi = listarTicket(vta)
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('ventas/ticket.html',ctx,context_instance=RequestContext(request))
		
		if 'actualizar' in request.POST:
			
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
						buscar = True
						updDatos = True
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				ctx = {'buscar':buscar,'updDatos':updDatos, 'info':info, 'nivel':nivel,'vendedor':xhsdfg }
				return render_to_response('ventas/seguimientoReparaciones.html',ctx,context_instance=RequestContext(request))

			else:
				info = "Verifique sus datos, actualizacion no realizada"
				formC = updCostoPorta( request.POST)
				updDatos = True
				buscar = False
				ctx = {'buscar':buscar,'updDatos':updDatos,'formC':formC,'info':info, 'nivel':nivel,'vendedor':xhsdfg }
				return render_to_response('ventas/seguimientoReparaciones.html',ctx,context_instance=RequestContext(request))

		if 'abonarRep' in request.POST:
			
			formC = addAbonoReparacion(request.POST)
			today = datetime.now() #fecha actual
			dateFormat = today.strftime("%d-%m-%Y") # fecha con formato
			
			if formC.is_valid():
				key = formC.cleaned_data['key']
				abonar 	= formC.cleaned_data['abonar']
				faltante = formC.cleaned_data['faltante']
				b = None
				abonarCli = True
				errores = False
				try:
					b = EquipoReparacion.objects.get(id = key)
					Cambio = 0
					Pagado = None
					if abonar > 0 and abonar >= faltante:
						Pagado = True
						Cambio = abonar - faltante

					elif abonar > 0 and abonar < faltante:
						Pagado = False
						
					else:
						errores = True
						info ='Lo sentimos, El Abono debe ser mayor que cero.'
				except :
					errores = True
					info='(3078) Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				if errores:
					formC = addAbonoReparacion(request.POST)
					abonarCli = True
					ctx = {'formC':formC,'abonarCli':abonarCli ,'info':info,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/seguimientoReparaciones.html',ctx,context_instance=RequestContext(request))
				else:
					try:
						with transaction.atomic():
							if Pagado:
								b.pagado = True
							b.fxRevision = today
							b.save()

							v = Venta()
							v.folioVenta = nuevoFolio2(str(mysucursal.id)+'S')
							v.sucursal 	= mysucursal
							v.usuario 	= request.user
							if Pagado:
								v.total 	= faltante
							else:
								v.total 	= abonar
							v.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
							v.estado 	= EstadoVenta.objects.get(estado='Pagada')
							v.save()

							dv = Anticipo()
							dv.folioVenta 	= v
							dv.tipoAnticipo = 'Servicio'
							if Pagado:
								dv.monto 	= faltante
							else:
								dv.monto 	= abonar
							dv.observacion 	= 'Cliente No. '+b.cliente.folio+' '+b.cliente.nombre
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
							mfolioVenta = v.folioVenta
					except :
						info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'

				ctx = {'folioVenta':mfolioVenta, 'abonarCli':abonarCli, 'info':info, 'nivel':nivel,'vendedor':xhsdfg }
				return render_to_response('ventas/seguimientoReparaciones.html',ctx,context_instance=RequestContext(request))

			else:
				info = "Verifique sus datos, datos incorrectos."
				formC = addAbonoReparacion( request.POST or None)
				abonarCli = True

				ctx = {'abonarCli':abonarCli,'formC':formC, 'info':info, 'nivel':nivel,'vendedor':xhsdfg  }
				return render_to_response('ventas/seguimientoReparaciones.html',ctx,context_instance=RequestContext(request))

		ctx = {'show':True,'buscar':buscar,'reparaciones':reparacionesp,'info':info, 'nivel':nivel,'vendedor':xhsdfg }
		return render_to_response('ventas/seguimientoReparaciones.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_servicios_garantias_recepcion_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)

		info =""
		buscar = True
		show = True
		query = ''

		pagina = request.GET.get('pagina','')
		query  = request.GET.get('q','')
		papeletas=None
		if query:
			qset=(Q(folioPapeleta__icontains=query) |
			 Q(nombre__icontains=query) | Q(calle__icontains=query) | 
			 Q(colonia__colonia__icontains=query) | Q(codP__cp__icontains=query) | 
			 Q(ciudad__ciudad__icontains=query) | Q(estado__estado__icontains=query) | 
			 Q(telAsig__icontains=query) | Q(esnImei__icontains=query))
			gaara = Papeleta.objects.filter(qset,sucursal__id=suc).exclude(tipoProducto__tipo__icontains='Express').order_by('folioPapeleta').order_by('nombre').order_by('fxActivacion')
		else:
			gaara = Papeleta.objects.filter(sucursal__id=suc).exclude(tipoProducto__tipo__icontains='Express').order_by('folioPapeleta').order_by('nombre').order_by('fxActivacion')

		sigarantias = []
		fx2 = datetime.now().date() 
		for x in gaara:
			fx1 = (x.fxActivacion).date()
			diff = fx2 - fx1
			tg = x.tgarantia * 30.416667
			if diff.days <= tg:
				sigarantias.append(x.folioPapeleta)

		paginator = Paginator(gaara, 50)
		
		papeletas=None
		try:
			papeletas = paginator.page(pagina)
		except PageNotAnInteger:
			papeletas = paginator.page(1)
		except EmptyPage:
			papeletas = paginator.page(paginator.num_pages)


		if request.method == "GET":

			if request.GET.get('q'):
				buscar = True
				show =  True

				ctx = {'papeletas':papeletas,'sigarantias':sigarantias,'show':show,'buscar':buscar,'info':info, 'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/addGarantia.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('nvoG'):
				query = request.GET.get('nvoG', '')
				if query:
					x = Papeleta.objects.get(id = query)
					e = Equipo.objects.get(imei=x.esnImei)
					formC = addGarantia({'key':x.id,'key2':e.id,'cliente':x.nombre,
						'equipo':e.detallesEquipo.marca.marca+' '+e.detallesEquipo.modelo+' Imei:'+str(e.imei) })
					garantiaCli = True
					
					ctx = {'garantiaCli':garantiaCli,'formC':formC,'info':info, 'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/addGarantia.html',ctx,context_instance=RequestContext(request))

		if request.method == "POST":
			
			formC = addGarantia( request.POST)
			today = datetime.now() #fecha actual
			
			if formC.is_valid():
				key 		= formC.cleaned_data['key']
				key2 		= formC.cleaned_data['key2']
				falla 		= formC.cleaned_data['falla']
				observacion = formC.cleaned_data['observacion']
				try: 
					with transaction.atomic():
						a = Garantia()
						a.papeleta 	= Papeleta.objects.get(id=key)
						a.equipo 		= Equipo.objects.get(id=key2)
						a.falla 		= falla
						a.sucursal 	= Sucursal.objects.get(id=suc)
						if observacion:
							a.observacion = observacion
						a.estado 		= EstadoGarantia.objects.get(estado='En Sucursal - Sin enviar')
						a.fxRevision	= today
						a.save()

						info = "El Registro se ingreso con exito la papeleta, folio: " +a.papeleta.folioPapeleta 
						garantiaCli = True
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				ctx = {'garantiaCli':garantiaCli,'info':info, 'nivel':nivel,'vendedor':xhsdfg }
				return render_to_response('ventas/addGarantia.html',ctx,context_instance=RequestContext(request))

			else:
				info = "Verifique sus datos, no se registro correctamente. "
				formC = addGarantia( request.POST)
				garantiaCli = True
				ctx = {'garantiaCli':garantiaCli,'formC':formC,'info':info, 'nivel':nivel,'vendedor':xhsdfg }
				return render_to_response('ventas/addGarantia.html',ctx,context_instance=RequestContext(request))

		ctx = {'sigarantias':sigarantias,'papeletas':papeletas,'show':show,'buscar':buscar,'info':info, 'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/addGarantia.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_servicios_garantias_seguimiento_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)

		formC = updGarantiaS()
		info =""
		buscar = True
		show = True
		
		pagina = request.GET.get('pagina','')
		query  = request.GET.get('q','')
		gaara=None
		if query:
			qset=(Q(papeleta__folioPapeleta__icontains=query) |Q(equipo__detallesEquipo__modelo__icontains=query)|
				Q(equipo__detallesEquipo__marca__marca__icontains=query) |Q(estado__estado__icontains=query) |
				Q(falla__icontains=query) |Q(fxSucursal__icontains=query) |Q(observacion__icontains=query))
			gaara = Garantia.objects.filter(qset,sucursal__id=suc).order_by('papeleta').order_by('equipo').order_by('fxSucursal')
		else:
			gaara = Garantia.objects.filter(sucursal__id=suc).order_by('papeleta').order_by('equipo').order_by('fxSucursal')

		paginator = Paginator(gaara, 50)
		
		garantias=None
		try:
			garantias = paginator.page(pagina)
		except PageNotAnInteger:
			garantias = paginator.page(1)
		except EmptyPage:
			garantias = paginator.page(paginator.num_pages)

		if request.method == "GET":

			if request.GET.get('q'):
				if request.GET.get('q'):
					buscar = True
					show =  True
					ctx = {'buscar':buscar,'show':show,'garantias':garantias, 'info':info, 'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/mySeguimientoGarantias.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('upd'):
				query = request.GET.get('upd', '')
				if query:
					g = Garantia.objects.get(id = query)
					ptm = str( g.equipo.detallesEquipo.marca.marca + ' ' + g.equipo.detallesEquipo.modelo + ' ' + str(g.equipo.imei))
					formC = updGarantiaS({'key':g.id,'papeleta':g.papeleta.nombre,'equipo':ptm,'falla':g.falla,'actualmente':g.estado.estado})
					mostrarf = True
					ctx = {'mostrarf':mostrarf,'formC':formC,'info':info, 'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/mySeguimientoGarantias.html',ctx,context_instance=RequestContext(request))

		if request.method == "POST":
			
			formC = updGarantiaS(request.POST or None)
			
			if formC.is_valid():
				key = formC.cleaned_data['key']
				estado 		= formC.cleaned_data['estado']
				try:
					with transaction.atomic():
						ham = Garantia.objects.get(id = key)
						ham.estado 		= EstadoGarantia.objects.get(id = estado)
						ham.fxRevision	= datetime.now()
						ham.save()
						
						info = "Garantia. El Registro se ha actualizado con exito: " + ham.papeleta.folioPapeleta
						show = True
						buscar = True
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				ctx = {'buscar':buscar,'show':show,'garantias':garantias,'info':info, 'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/mySeguimientoGarantias.html',ctx,context_instance=RequestContext(request))

			else:
				info = "Verifique sus datos, actualizacion no realizada"
				formC = updGarantiaS(request.POST)
				mostrarf = True
				
				ctx = {'mostrarf':mostrarf, 'formC':formC, 'info':info, 'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/mySeguimientoGarantias.html',ctx,context_instance=RequestContext(request))
		
		ctx = {'buscar':buscar,'show':show,'garantias':garantias,'info':info, 'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/mySeguimientoGarantias.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')



#listo
@login_required(login_url='/')
def ventas_planes_tarifarios_nva_solicitud_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc =  cveSucursal(request.user)
		info = "" 
		form = addSolicitud({'fxSolicitud':datetime.now()})

		if request.method == "POST":
			form = addSolicitud(request.POST or None)
			if form.is_valid():
				elempleado = form.cleaned_data['vendedor']
				e= None
				try:
					e = Empleado.objects.get(curp__icontains=elempleado)	
				except Empleado.DoesNotExist:
					info = "La Curp de Empleado no coincide con la base de datos"
					form = addSolicitud(request.POST)
					ctx = {'form':form,'nivel':nivel,'info':info,'vendedor':xhsdfg}
					return render_to_response('ventas/addSolicitudPlan.html',ctx,context_instance=RequestContext(request))
				
				z1 = agregarCiudades(form.cleaned_data['coloniaP'],form.cleaned_data['ciudadP'],form.cleaned_data['countryP'],form.cleaned_data['cpP'])	
				z2 = agregarCiudades(form.cleaned_data['ecolonia'],form.cleaned_data['eciudad'],form.cleaned_data['ecountry'],form.cleaned_data['ecp'])
				
				try:
					with transaction.atomic():
						a = Solicitud()
						a.fxSolicitud = form.cleaned_data['fxSolicitud']
						a.canalVta 	= form.cleaned_data['canalVta']
						a.folioSisAct = form.cleaned_data['folioSisAct']
						a.lineaSolicitadas = form.cleaned_data['lineaSolicitadas']
						a.vendedor 	= e
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
						a.estado 		= EstadoSolicitud.objects.get(estado='En Sucursal - Sin Enviar')
						a.observacion = form.cleaned_data['observacion']
						a.folio = nvofolioSolicitud()
						a.save()
						info ="La Solicitud se ha Guardado correctamente. En espera por revision. "
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				ctx = {'nivel':nivel,'info':info,'vendedor':xhsdfg}
				return render_to_response('ventas/addSolicitudPlan.html',ctx,context_instance=RequestContext(request))
			else:
				info = "La informacion, contiene algunos errores, favor de verificar."
				form = addSolicitud(request.POST)
				ctx = {'form':form,'nivel':nivel,'info':info,'vendedor':xhsdfg}
				return render_to_response('ventas/addSolicitudPlan.html',ctx,context_instance=RequestContext(request))
				

		ctx = {'form':form,'nivel':nivel,'info':info,'vendedor':xhsdfg}
		return render_to_response('ventas/addSolicitudPlan.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_planes_tarifarios_seguimiento_todos_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)

		info =""
		pagina = request.GET.get('pagina','')
		query  = request.GET.get('q','')
		gaara=None
		if query:
			qset=(Q(folio__icontains=query) |Q(fxSolicitud__icontains=query) |Q(vendedor__curp__icontains=query) |
				Q(nombre__icontains=query) |Q(aPat__icontains=query) |Q(aMat__icontains=query) |Q(plan__plan__icontains=query) |
				Q(plan__costo__icontains=query) |Q(estado__estado__icontains=query) |Q(fxModificacion__icontains=query))

			gaara = Solicitud.objects.filter(qset,sucursal__id=suc).order_by('folio').order_by('fxSolicitud').order_by('nombre')
		else:
			gaara = Solicitud.objects.filter(sucursal__id=suc).order_by('folio').order_by('fxSolicitud').order_by('nombre')

		paginator = Paginator(gaara, 50)
		
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
				ctx = {'grrr':grrr,'info':info, 'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/solicitudCompleta.html',ctx,context_instance=RequestContext(request))
					

		ctx = {'solicitudes':solicitudes,'query':query,'info':info, 'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/seguimientoPlanes.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_planes_tarifarios_seguimiento_consultar_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)

		info =""
		pagina = request.GET.get('pagina','')
		query  = request.GET.get('q','')
		gaara=None
		if query:
			qset=(Q(folio__icontains=query) |Q(fxSolicitud__icontains=query) |Q(vendedor__curp__icontains=query) |
				Q(nombre__icontains=query) |Q(aPat__icontains=query) |Q(aMat__icontains=query) |Q(plan__plan__icontains=query) |
				Q(plan__costo__icontains=query) |Q(estado__estado__icontains=query) |Q(fxModificacion__icontains=query))

			gaara = Solicitud.objects.filter(qset,sucursal__id=suc).order_by('folio').order_by('fxSolicitud').order_by('nombre')
		else:
			gaara = Solicitud.objects.filter(sucursal__id=suc).order_by('folio').order_by('fxSolicitud').order_by('nombre')

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
					form = updSolicitudPlan({'fxSolicitud':x.fxSolicitud,'canalVta':x.canalVta,'folioSisAct':x.folioSisAct,'lineaSolicitadas':x.lineaSolicitadas,
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
				ctx = {'cosa':'Actualizacion de ' ,'form':form,'nivel':nivel,'info':info,'vendedor':xhsdfg}
				return render_to_response('ventas/addSolicitudPlan.html',ctx,context_instance=RequestContext(request))
		
		if request.method == "POST":
			form = updSolicitudPlan(request.POST or None)
			if form.is_valid():
				
				z1 = agregarCiudades(form.cleaned_data['coloniaP'],form.cleaned_data['ciudadP'],form.cleaned_data['countryP'],form.cleaned_data['cpP'])	
				z2 = agregarCiudades(form.cleaned_data['ecolonia'],form.cleaned_data['eciudad'],form.cleaned_data['ecountry'],form.cleaned_data['ecp'])
				
				try:
					with transaction.atomic():
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
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				ctx = {'nivel':nivel,'info':info,'vendedor':xhsdfg}
				return render_to_response('ventas/addSolicitudPlan.html',ctx,context_instance=RequestContext(request))
			else:
				info = "La informacion, contiene algunos errores, favor de verificar."
				form = updSolicitudPlan(request.POST)
				ctx = {'form':form,'nivel':nivel,'info':info,'vendedor':xhsdfg}
				return render_to_response('ventas/addSolicitudPlan.html',ctx,context_instance=RequestContext(request))
					

		ctx = {'solicitudes':solicitudes,'query':query,'info':info, 'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/seguimientoPlanes.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_planes_tarifarios_actualizacion_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)

		info =""
		pagina = request.GET.get('pagina','')
		query  = request.GET.get('q','')
		gaara=None
		if query:
			qset=(Q(folio__icontains=query) |Q(fxSolicitud__icontains=query) |Q(vendedor__curp__icontains=query) |
				Q(nombre__icontains=query) |Q(aPat__icontains=query) |Q(aMat__icontains=query) |Q(plan__plan__icontains=query) |
				Q(plan__costo__icontains=query) |Q(estado__estado__icontains=query) |Q(fxModificacion__icontains=query))

			gaara = Solicitud.objects.filter(qset,sucursal__id=suc).order_by('folio').order_by('fxSolicitud').order_by('nombre')
		else:
			gaara = Solicitud.objects.filter(sucursal__id=suc).order_by('folio').order_by('fxSolicitud').order_by('nombre')

		paginator = Paginator(gaara, 50)
		
		solicitudes=None
		try:
			solicitudes = paginator.page(pagina)
		except PageNotAnInteger:
			solicitudes = paginator.page(1)
		except EmptyPage:
			solicitudes = paginator.page(paginator.num_pages)
		
		if request.method == "GET":
			if request.GET.get('updRfc'):
				s = request.GET.get('updRfc','')
				if s:
					d = Solicitud.objects.get(id=s)
					formR = addRfc({
						'folio':d.folio,'nomRazon': d.nomRazon, 'sexo': d.sexo, 'rfc': d.rfc, 'nomRep':d.nomRep, 
						'profesion':d.profesion, 'ocupacion':d.ocupacion, 'cargo':d.cargo, 'direcc':d.direcc, 
						'telPart':d.telPart, 'telOfi':d.telOfi, 'refPersonal':d.refPersonal, 'telRefpers':d.telRefpers, 
						'tipoIdent':d.tipoIdent, 'noIdent':d.noIdent
						})
					formS = addServiciosPlan({'folio':d.folio})
				else:
					info="Oops! lo sentimos, alguien ha cambiado la Solicitud manualmente...regrese a la pagina principal."
				ctx = {'formR':formR,'formS':formS,'nivel':nivel,'info':info,'vendedor':xhsdfg}
				return render_to_response('ventas/servicioPlanTarifario.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('addServicio'):
				s = request.GET.get('addServicio','')
				if s:
					d = Solicitud.objects.get(id=s)
					formS = addServiciosPlan({'folio':d.folio})
				else:
					info="Oops! lo sentimos, alguien ha cambiado la Solicitud manualmente...regrese a la pagina principal."
				ctx = {'formS':formS,'nivel':nivel,'info':info,'vendedor':xhsdfg}
				return render_to_response('ventas/servicio2PlanTarifario.html',ctx,context_instance=RequestContext(request))
		
		if 'rfcS' in request.POST:
			formR = addRfc(request.POST)
			formS = addServiciosPlan(request.POST)

			if formR.is_valid() and formS.is_valid():

				re1='[A-Z]{3,4}-[0-9]{2}[0-1][0-9][0-3][0-9]-[A-Z0-9]?[A-Z0-9]?[0-9A-Z]?'

				txt=str(formR.cleaned_data['rfc']).upper()
				rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
				m = rg.search(txt)
				if m:
					pass
				else:
					info = "El formato de rfc, no es correcto."
					formR = addRfc(request.POST)
					formS = addServiciosPlan(request.POST)

					ctx = {'formR':formR,'formS':formS,'nivel':nivel,'info':info,'vendedor':xhsdfg}
					return render_to_response('ventas/servicioPlanTarifario.html',ctx,context_instance=RequestContext(request))
				try:
					with transaction.atomic():
						a = Solicitud.objects.get(folio=formR.cleaned_data['folio'])
						a.nomRazon 	=formR.cleaned_data['nomRazon'].title()
						a.sexo 		=formR.cleaned_data['sexo']
						a.rfc 		=formR.cleaned_data['rfc'].upper()
						a.nomRep 	=formR.cleaned_data['nomRep'].title()
						a.profesion =formR.cleaned_data['profesion'].title()
						a.ocupacion =formR.cleaned_data['ocupacion'].title()
						a.cargo 	=formR.cleaned_data['cargo'].title()
						a.direcc 	=formR.cleaned_data['direcc'].title()
						a.telPart 	=formR.cleaned_data['telPart']
						a.telOfi 	=formR.cleaned_data['telOfi']
						a.refPersonal 	= formR.cleaned_data['refPersonal'].title()
						a.telRefpers	=formR.cleaned_data['telRefpers']
						a.tipoIdent 	=formR.cleaned_data['tipoIdent'].title()
						a.noIdent 	=formR.cleaned_data['noIdent']
						a.save()

						b = ServiciosPlan()
						b.sucursal 	= Sucursal.objects.get(id=suc)
						b.solicitante = a
						b.servicioRequiere = formS.cleaned_data['servicioRequiere'].title()
						b.fxAtencion 	= datetime.now()
						b.save()
						info ="La Solicitud se ha Guardado correctamente. En espera por revision. "+a.folio
				except :
					info='(3821) Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				ctx = {'solicitudes':solicitudes,'query':query,'nivel':nivel,'info':info,'vendedor':xhsdfg}
				return render_to_response('ventas/actualizacionPlanes.html',ctx,context_instance=RequestContext(request))
			else:
				info = "La informacion, contiene algunos errores, favor de verificar."
				formR = addRfc(request.POST)
				formS = addServiciosPlan(request.POST)

				ctx = {'formR':formR,'formS':formS,'nivel':nivel,'info':info,'vendedor':xhsdfg}
				return render_to_response('ventas/servicioPlanTarifario.html',ctx,context_instance=RequestContext(request))
		
		if 'solS' in request.POST:
			formS = addServiciosPlan(request.POST)

			if formS.is_valid():
				try:
					with transaction.atomic():
						a = Solicitud.objects.get(folio=formS.cleaned_data['folio'])
						b = ServiciosPlan()
						b.sucursal 	= Sucursal.objects.get(id=suc)
						b.solicitante = a
						b.servicioRequiere = formS.cleaned_data['servicioRequiere'].title()
						b.fxAtencion 	= datetime.now()
						b.save()

						info ="La Solicitud en Servicio se ha Guardado correctamente. En espera por revision. "+a.folio
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				ctx = {'solicitudes':solicitudes,'query':query,'nivel':nivel,'info':info,'vendedor':xhsdfg}
				return render_to_response('ventas/actualizacionPlanes.html',ctx,context_instance=RequestContext(request))
			else:
				info = "La informacion, contiene algunos errores, favor de verificar."
				formS = addServiciosPlan(request.POST)

				ctx = {'formS':formS,'nivel':nivel,'info':info,'vendedor':xhsdfg}
				return render_to_response('ventas/servicio2PlanTarifario.html',ctx,context_instance=RequestContext(request))

		ctx = {'solicitudes':solicitudes,'query':query,'info':info, 'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/actualizacionPlanes.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_planes_tarifarios_catalogo_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		query=request.GET.get('q','')
		
		r_items=None
		info=''

		r_items=Plan.objects.filter(activo=True)

		if query:
			qset=(Q(plan__icontains=query)|
				Q(costo__icontains=query)|
				Q(equiposGratis__icontains=query))
			r_items=Plan.objects.filter(qset,activo=True).distinct()
		
		ctx={'nivel':nivel, 'query':query, 'r_items':r_items, 'info':info,'vendedor':xhsdfg}
		return render_to_response('ventas/listaPlanes.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_portabilidades_agregar_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)

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
		xVendedor = addVendedor()
		mfolioVenta = None
		if request.method == "GET":
			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					
					qset = (Q(nombre__icontains=query)|Q(direccion__icontains=query)|Q(colonia__colonia__icontains=query)|Q(sucursal__nombre__icontains=query)|Q(folio__icontains=query)|Q(fxIngreso__icontains=query) )
					results = ClienteServicio.objects.filter(qset,sucursal__id=mysucursal.id,tipoCliente__icontains='Portabilidad').distinct()

				else:
					results = []

				buscar = True
				ctx = {'query':query,'results':results,'buscar':buscar,'nivel':nivel,'info':info,'vendedor':xhsdfg }
				return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))
				
			if request.GET.get('cliCCosto'):
				cliente = request.GET.get('cliCCosto','')
				if cliente:
					cli = ClienteServicio.objects.get(id=cliente)
					formCC = vtaCostoPorta({'key':cli.id,'cliente':cli.nombre})

					buscar = False
					yaCC = True
					boton = True
					ctx = {'yaCC':yaCC,'formC':formCC,'xVendedor':xVendedor,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
					return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('cliSCosto'):
				cliente = request.GET.get('cliSCosto','')
				if cliente:
					cli = ClienteServicio.objects.get(id=cliente)
					formSC = vtaGratisFlexeo({'key':cli.id,'cliente':cli.nombre})

					buscar = False
					yaSC = True
					boton = True
					ctx = {'yaSC':yaSC,'formS':formSC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
					return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))
					
			if request.GET.get('nvoCCosto'):
				cliente = request.GET.get('nvoCCosto','')
				if cliente:
					formCC = vtaCostoPorta({'key':nvofolioCliente(),'cliente':'Nuevo'})

					buscar = False
					nvoCC = True
					boton = True
					ctx = {'nvoCC':nvoCC,'form':form,'xVendedor':xVendedor,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
					return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('nvoSCosto'):
				cliente = request.GET.get('nvoSCosto','')
				if cliente:					
					formSC = vtaGratisFlexeo({'key':nvofolioCliente(),'cliente':'Nuevo'})

					buscar = False
					nvoSC = True
					boton = True
					ctx = {'nvoSC':nvoSC,'form':form,'formS':formSC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
					return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('print'):
				vta = request.GET.get('print','')
				if vta:
					mivi = None
					try:
						v = Venta.objects.get(folioVenta=vta)
						ok = suc_permisos(nivel,request.user,v.sucursal)
						if ok:
							mivi = listarTicket(vta)
						else:
							info = "Oops! Al parecer no tiene permitido ver esta informacion"
					except :
						info = "Oops! Al parecer algo se ha movido!, intente recargar o consultar a un administrador."
					ctx = {'aio':mivi,'info':info, 'nivel':nivel}
					return render_to_response('ventas/ticket.html',ctx,context_instance=RequestContext(request))

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
				#
				key 		= formSC.cleaned_data['key']
				marcaModelo = formSC.cleaned_data['marcaModelo']
				noaportar 	= formSC.cleaned_data['noaportar']
				observaciones 	= formSC.cleaned_data['observaciones']

				z1 = agregarCiudades(colonia,ciudad,estado,None)
				try:
					with transaction.atomic():
						a = ClienteServicio()
						a.nombre 		= (nombre).title()
						a.direccion 	= (direccion).title()
						a.colonia = Colonia.objects.get(id=z1[0])
						a.ciudad = Ciudad.objects.get(id=z1[1])
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
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				boton= False
				nvoSC = True
				ctx = {'nvoSC':nvoSC,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
				return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

			else:
				formSC = vtaGratisFlexeo(request.POST)
				form = addClienteServicioForm(request.POST)
				buscar = False
				nvoSC = True
				boton = True
				info = "Revise su informacion"
			
			ctx = {'nvoSC':nvoSC,'form':form,'formS':formSC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
			return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

		if 'regNvoCC' in request.POST:
			formCC = vtaCostoPorta(request.POST)
			form = addClienteServicioForm(request.POST)
			xVendedor = addVendedor(request.POST)

			if form.is_valid() and formCC.is_valid() and xVendedor.is_valid():
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

				uempleado 	= xVendedor.cleaned_data['usuario']

				elusuario = None
				try:
					elusuario = Usuario.objects.get(user__username = uempleado,empleado__estadoEmpleado=True)
				except Usuario.DoesNotExist:
					info = "Lo sentimos, el nombre de usuario que registra la operacion no existe o no esta activo."
					formCC = vtaCostoPorta(request.POST)
					form = addClienteServicioForm(request.POST)
					xVendedor = addVendedor(request.POST)
					buscar = False
					nvoCC = True
					boton = True

					ctx = {'nvoCC':nvoCC,'xVendedor':xVendedor,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
					return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

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

					ctx = {'nvoCC':nvoCC,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
					return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))
				try:
					with transaction.atomic():
						z1 = agregarCiudades(colonia,ciudad,estado,None)
						a = ClienteServicio()
						a.nombre 		= (nombre).title()
						a.direccion 	= (direccion).title()
						a.colonia 		= Colonia.objects.get(id=z1[0])
						a.ciudad 		= Ciudad.objects.get(id=z1[1])
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

						zzz = comisionesReparacion()
						zzz.usuario = elusuario.user
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
						v.aceptada = True
						v.save()

						dv = Anticipo()
						dv.folioVenta 	= v
						dv.tipoAnticipo = 'Portabilidad con costo'
						dv.monto 		= pago
						dv.observacion 	= 'Cliente No. '+ a.folio+' '+a.nombre
						dv.save()
						
						info="Se ha registrado la entrada de un equipo para flexeo por portabilidad con costo.Folio cliente: "+str(a.folio)+" Folio de Venta: "+ v.folioVenta+" Cambio: $"+str(Cambio)
						mfolioVenta = v.folioVenta
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				boton= False
				nvoCC = True
				ctx = {'folioVenta':mfolioVenta, 'nvoCC':nvoCC,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
				return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))
			else:
				info = "No se registro. Verifique sus datos."
				formCC = vtaCostoPorta(request.POST)
				form = addClienteServicioForm(request.POST)
				xVendedor = addVendedor(request.POST)
				buscar = False
				nvoCC = True
				boton = True
			ctx = {'nvoCC':nvoCC,'form':form,'xVendedor':xVendedor,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
			return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

		if 'regSC' in request.POST:
			formSC = vtaGratisFlexeo(request.POST)

			if formSC.is_valid():#cliente conocido , porta gratis
				key 	= formSC.cleaned_data['key']
				marcaModelo = formSC.cleaned_data['marcaModelo']
				noaportar = formSC.cleaned_data['noaportar']
				observaciones 	= formSC.cleaned_data['observaciones']
				try:
					with transaction.atomic():
						a = ClienteServicio.objects.get(id=key)

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

				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				boton= False
				yaSC = True
				ctx = {'yaSC':yaSC,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
				return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

			else:
				formSC = vtaGratisFlexeo(request.POST)
				buscar = False
				yaSC = True
				boton = True
			ctx = {'yaSC':yaSC,'form':form,'formS':formSC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
			return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

		if 'regCC' in request.POST:
			formCC = vtaCostoPorta(request.POST)
			xVendedor = addVendedor(request.POST)
			if formCC.is_valid() and xVendedor.is_valid():#cliente conocido, porta con costo

				key 	= formCC.cleaned_data['key']
				noaportar 	= formCC.cleaned_data['noaportar']
				marcaModelo = formCC.cleaned_data['marcaModelo']
				imei 		= formCC.cleaned_data['imei']
				observacion = formCC.cleaned_data['observacion']
				anticipo 	= formCC.cleaned_data['anticipo']
				reparacion 	= formCC.cleaned_data['reparacion']

				uempleado 	= xVendedor.cleaned_data['usuario']

				elusuario = None
				try:
					elusuario = Usuario.objects.get(user__username = uempleado,empleado__estadoEmpleado=True)
				except Usuario.DoesNotExist:
					info = "Lo sentimos, el nombre de usuario que registra la operacion no existe o no esta activo."
					xVendedor = addVendedor(request.POST)
					formCC = vtaCostoPorta(request.POST)
					buscar = False
					yaCC = True
					boton = True
					ctx = {'yaCC':yaCC,'form':form,'xVendedor':xVendedor,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
					return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))

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
					xVendedor= addVendedor(request.POST)
					buscar = False
					yaCC = True
					boton = True
					ctx = {'yaCC':yaCC,'xVendedor':xVendedor,'form':form,'formC':formCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
					return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))
				try:
					with transaction.atomic():
						a = ClienteServicio.objects.get(id=key)

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
						v.aceptada = True
						v.save()

						dv = Anticipo()
						dv.folioVenta 	= v
						dv.tipoAnticipo = 'Portabilidad con costo'
						dv.monto 		= pago
						dv.observacion 	= 'Cliente No. '+a.folio+' '+a.nombre
						dv.save()

						info="Se ha registrado la entrada de un equipo para flexeo por portabilidad con costo. Folio de Venta: "+ v.folioVenta+" Cambio: $"+str(Cambio)
						mfolioVenta = v.folioVenta
				except :
					
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
					#sukii #transaction.commit()#'''
				
				buscar = False
				yaCC = True
				boton = False
				ctx = {'folioVenta':mfolioVenta, 'yaCC':yaCC,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
				return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))
				
			else:
				info = "No se registro. Verifique sus datos."
				formCC = vtaCostoPorta(request.POST)
				xVendedor = addVendedor(request.POST)
				buscar = False
				yaCC = True
				boton = True
			ctx = {'yaCC':yaCC,'formC':formCC,'xVendedor':xVendedor,'buscar':buscar,'boton':boton,'nivel':nivel,'info':info,'vendedor':xhsdfg}
			return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))	
		
		ctx = {'query':query,'results':results,'buscar':buscar,'nivel':nivel,'info':info,'vendedor':xhsdfg}
		return render_to_response('ventas/vtaFlexeoPorta.html',ctx,context_instance=RequestContext(request))	
		
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_portabilidades_seguimiento_view(request):
	nivel=Permiso(request.user,[0,1,12])
	
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)

		formC = updCostoPorta()
		formS = updGratisFlexeo()
		info =""
		mostrar = False
		buscar = True
		mostrarf = False
		query = ''
		results = []
		scosto = FlexeoEquipo.objects.filter(portabilidad__cliente__tipoCliente__icontains='Portabilidad sin costo', portabilidad__sucursal__id=suc)
		ccosto = EquipoReparacion.objects.filter(cliente__tipoCliente__icontains='Portabilidad con costo', sucursal__id=suc)

		if request.method == "GET":
			if request.GET.get('portas'):
				query = request.GET.get('portas','')
				if query:
					
					ctx = {'info':info, 'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/seguimientoPortabilidades.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('qPorta'):
				query = request.GET.get('qPorta','')
				if query:
					qset = (Q(cliente__nombre__icontains=query) |
					Q(sucursal__nombre__icontains=query) |
					Q(noaPortar__icontains=query) |
					Q(estado__estado__icontains=query) |
					Q(cliente__folio__icontains=query))
					results = Portabilidad.objects.filter(qset,sucursal__id=suc).distinct()
					eqFlexeo = FlexeoEquipo.objects.filter(portabilidad__cliente__tipoCliente__icontains='Portabilidad sin costo')
					eqReparacion = EquipoReparacion.objects.filter(cliente__tipoCliente__icontains='Portabilidad con costo')
					
					ctx = {'queryPorta':query,'eqFlexeo':eqFlexeo,'eqReparacion':eqReparacion,'results':results,'info':info, 'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/seguimientoPortabilidades.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('updPorta'):
				query = request.GET.get('updPorta','')
				if query:
					x = Portabilidad.objects.get(id = query)
					form = updPorta({'key':x.id,'cliente':x.cliente.nombre,'actualmente':x.estado.estado})

					ctx = {'info':info,'form':form,'mostrarPorta':True,'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/seguimientoPortabilidades.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('q'):
				query = request.GET.get('q', '')
				if query:
					qset = (Q(cliente__nombre__icontains=query) | Q(sucursal__nombre__icontains=query) | Q(cliente__folio__icontains=query))
					results = Portabilidad.objects.filter(qset,sucursal__id=suc).distinct()
					if results:
						info = "Resultados"

				else:
					results = []
				ctx = {'buscar':buscar,'mostrarf':mostrarf,"results": results,"query": query, 'scosto':scosto, 'ccosto':ccosto, 'info':info, 'nivel':nivel,'vendedor':xhsdfg }
				return render_to_response('ventas/seguimientoFlexeoPorta.html',ctx,context_instance=RequestContext(request))

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

			ctx = {'buscar':buscar,'mostrarf':mostrarf, 'mostrar':mostrar, 'formS':formS, 'formC':formC, 'info':info, 'nivel':nivel,'vendedor':xhsdfg}
			return render_to_response('ventas/seguimientoFlexeoPorta.html',ctx,context_instance=RequestContext(request))

		if 'updCFlexeo' in request.POST:
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
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				boton = False
				buscar = True
				mostrarf = False

				ctx = {'buscar':buscar,'mostrarf':mostrarf, 'boton':boton,'info':info, 'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/seguimientoFlexeoPorta.html',ctx,context_instance=RequestContext(request))

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
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				boton = False
				buscar = True
				mostrarf = False
				ctx = {'buscar':buscar,'mostrarf':mostrarf,'boton':boton,'info':info, 'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/seguimientoFlexeoPorta.html',ctx,context_instance=RequestContext(request))

			else:
				info = "Verifique sus datos, actualizacion no realizada"
				formC = updCostoPorta( request.POST or None)
				formS = updGratisFlexeo( request.POST or None)
				mostrarf = True
				buscar = False
				
				ctx = {'buscar':buscar,'mostrarf':mostrarf, 'boton':boton ,'mostrar':mostrar, 'formS':formS, 'formC':formC, 'info':info, 'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/seguimientoFlexeoPorta.html',ctx,context_instance=RequestContext(request))
		
		if 'edoPorta' in request.POST:
			form = updPorta(request.POST)
			if form.is_valid():
				key = form.cleaned_data['key']
				estado = form.cleaned_data['estado']
				try:
					with transaction.atomic():
						upd= Portabilidad.objects.get(id=key)
						upd.estado = EstadoPortabilidad.objects.get(id=estado)
						upd.save()
						info = "Se ha actualizado correctamente. Portabilidad de cliente: "+upd.cliente.folio
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				ctx = {'info':info,'form':form,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/seguimientoPortabilidades.html',ctx,context_instance=RequestContext(request))

			else:
				info = "Se Encontraron algunos errores, favor de verificar su informacion"
				form = updPorta(request.POST)
				mostrarf = True
				ctx = {'info':info,'mostrarPorta':mostrarf,'form':form,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/seguimientoPortabilidades.html',ctx,context_instance=RequestContext(request))


		ctx = {'buscar':buscar,'mostrarf':mostrarf, 'boton':boton ,'mostrar':mostrar, 'formS':formS, 'formC':formC, 'info':info, 'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/seguimientoFlexeoPorta.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_sucursal_transferencias_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)
		query  = request.GET.get('q','')
		pag1=request.GET.get('pagina','')
		msgs = Movimiento.objects.filter(sucursalDestino__id=suc,tipoMovimiento__nombre='Transferencia').order_by('-fx_movimiento')
		#mov = None
		if query:
			msgs = Movimiento.objects.filter(sucursalDestino__id=suc,folio__icontains=query,tipoMovimiento__nombre='Transferencia').order_by('-fx_movimiento').order_by('confirmacion')
		
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
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__id=s)#'''

					ctx={'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('ventas/confirmacionProductos.html',ctx,context_instance=RequestContext(request))
			
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
					return render_to_response('ventas/confirmacionProductos.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('aceptEq'):
				s = request.GET.get('aceptEq','')
				m = request.GET.get('transfGral','')
				if s:
					try:
						with transaction.atomic():
							mov = Movimiento.objects.get(folio=m)
							upd = ListaEquipo.objects.get(id=s)
							upd.confirmacion = True
							upd.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
					
					transEq = ListaEquipo.objects.filter(movimiento__folio=m)
					transEx = ListaExpres.objects.filter(movimiento__folio=m)
					transAc = ListaAccesorio.objects.filter(movimiento__folio=m)
					transFic = ListaFichas.objects.filter(movimiento__folio=m)
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__folio=m)

					ctx={'mostrar':True,'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('ventas/confirmacionProductos.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('aceptEx'):
				s = request.GET.get('aceptEx','')
				m = request.GET.get('transfGral','')
				if s:
					try:
						with transaction.atomic():
							mov = Movimiento.objects.get(folio=m)
							upd = ListaExpres.objects.get(id=s)
							upd.confirmacion = True
							upd.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
					
					transEq = ListaEquipo.objects.filter(movimiento__folio=m)
					transEx = ListaExpres.objects.filter(movimiento__folio=m)
					transAc = ListaAccesorio.objects.filter(movimiento__folio=m)
					transFic = ListaFichas.objects.filter(movimiento__folio=m)
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__folio=m)

					ctx={'mostrar':True,'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('ventas/confirmacionProductos.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('aceptAc'):
				s = request.GET.get('aceptAc','')
				m = request.GET.get('transfGral','')
				if s:
					try:
						with transaction.atomic():
							mov = Movimiento.objects.get(folio=m)
							upd = ListaAccesorio.objects.get(id=s)
							upd.confirmacion = True
							upd.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
					
					transEq = ListaEquipo.objects.filter(movimiento__folio=m)
					transEx = ListaExpres.objects.filter(movimiento__folio=m)
					transAc = ListaAccesorio.objects.filter(movimiento__folio=m)
					transFic = ListaFichas.objects.filter(movimiento__folio=m)
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__folio=m)

					ctx={'mostrar':True,'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('ventas/confirmacionProductos.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('aceptFic'):
				s = request.GET.get('aceptFic','')
				m = request.GET.get('transfGral','')
				if s:
					try:
						with transaction.atomic():
							mov = Movimiento.objects.get(folio=m)
							upd = ListaFichas.objects.get(id=s)
							upd.confirmacion = True
							upd.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
					
					transEq = ListaEquipo.objects.filter(movimiento__folio=m)
					transEx = ListaExpres.objects.filter(movimiento__folio=m)
					transAc = ListaAccesorio.objects.filter(movimiento__folio=m)
					transFic = ListaFichas.objects.filter(movimiento__folio=m)
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__folio=m)

					ctx={'mostrar':True,'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('ventas/confirmacionProductos.html',ctx,context_instance=RequestContext(request))

			if request.GET.get('aceptSaldo'):
				s = request.GET.get('aceptSaldo','')
				m = request.GET.get('transfGral','')
				if s:
					try:
						with transaction.atomic():
							mov = Movimiento.objects.get(folio=m)
							upd = TransferenciaSaldo.objects.get(id=s)
							upd.save()
					except :
						info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
					
					transEq = ListaEquipo.objects.filter(movimiento__folio=m)
					transEx = ListaExpres.objects.filter(movimiento__folio=m)
					transAc = ListaAccesorio.objects.filter(movimiento__folio=m)
					transFic = ListaFichas.objects.filter(movimiento__folio=m)
					transSaldo = TransferenciaSaldo.objects.filter(movimiento__folio=m)

					ctx={'mostrar':True,'mov':mov,'transEq':transEq,'transEx':transEx,'transAc':transAc,'transFic':transFic,'transSaldo':transSaldo,'query':query,'nivel':nivel}
					return render_to_response('ventas/confirmacionProductos.html',ctx,context_instance=RequestContext(request))

		if request.method == "POST":
			cerrar = request.POST.get('transfGral')
			try:
				with transaction.atomic():
					mov = Movimiento.objects.get(folio=cerrar)
					mov.usuarioDestino = request.user
					mov.confirmacion = True
					mov.save()
			except :
				info='(4756) Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
			
			transEq = ListaEquipo.objects.filter(movimiento__folio=mov.folio, confirmacion=False)
			transEx = ListaExpres.objects.filter(movimiento__folio=mov.folio, confirmacion=False)
			transAc = ListaAccesorio.objects.filter(movimiento__folio=mov.folio, confirmacion=False)
			transFic = ListaFichas.objects.filter(movimiento__folio=mov.folio, confirmacion=False)
			transSaldo = TransferenciaSaldo.objects.filter(movimiento__folio=mov.folio)
			mensaje = "Transferencia con Productos no Aceptados: "+mov.folio
			for x in transEq:
				try:
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
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
			for x in transEx:
				try:
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
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'				

			for x in transAc:
				try:
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
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				

			for x in transFic:
				try:
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
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
			for x in transSaldo:
				mensaje = mensaje + ' Saldo no Confirmado monto : $ '+str(x.monto)


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
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
			info = "La Transferencia se ha Guardado correctamente. Si no se aceptaron productos, se muestran a continuacion. "+mensaje

			ctx={'transferencias':pMovs,'query':query,'nivel':nivel}
			return render_to_response('ventas/transferencias.html',ctx,context_instance=RequestContext(request))

		ctx={'transferencias':pMovs,'query':query,'nivel':nivel}
		return render_to_response('ventas/transferencias.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_sucursal_devoluciones_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
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
			r_movi=Movimiento.objects.get(folio=b_movimiento,sucursalOrigen=_sucursal,tipoMovimiento__nombre='Devolucion')
			transSaldo=TransferenciaSaldo.objects.filter(movimiento=r_movi)
			equipos=ListaEquipo.objects.filter(movimiento=r_movi).order_by('equipo__imei')
			accesorios=ListaAccesorio.objects.filter(movimiento=r_movi).order_by('accesorio__codigoBarras')
			express=ListaExpres.objects.filter(movimiento=r_movi).order_by('expres__icc')
			fichas=ListaFichas.objects.filter(movimiento=r_movi).order_by('ficha__folio')
			try:
				empleado2=Usuario.objects.get(user=r_movi.usuarioOrigen).empleado
			except :
				pass
		
		qset=(Q(folio__icontains=b_movimiento)|
			Q(fx_movimiento__icontains=b_movimiento)|
			Q(sucursalDestino__nombre__icontains=b_movimiento))
		r_movis=Movimiento.objects.filter(qset,sucursalOrigen=_sucursal,tipoMovimiento__nombre='Devolucion').distinct().order_by('-fx_movimiento')


		ctx={'nivel':nivel, 'info':info, 'empleado2':empleado2, 'equipos':equipos, 'accesorios':accesorios , 
		'express':express , 'fichas':fichas ,'transSaldo':transSaldo,'b_movimiento':b_movimiento, 'r_movis':r_movis,
		 'r_movi':r_movi, 'vendedor':xhsdfg}

		return render_to_response('ventas/movimientoDevConsultar.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_sucursal_existencias_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)

		query  = request.GET.get('item','')
		pag1 = request.GET.get('pagEq','')
		pag2 = request.GET.get('pagEx','')
		pag3 = request.GET.get('pagC','')
		pag4 = request.GET.get('pagF','')
		
		almEquipo = AlmacenEquipo.objects.filter(estado=True,sucursal__id=suc).exclude(equipo__estatus__estatus='Vendido').order_by('equipo')
		almExpress = AlmacenExpres.objects.filter(estado=True,sucursal__id=suc).exclude(expres__estatus__estatus='Vendido').order_by('expres')
		almAccs = AlmacenAccesorio.objects.filter(estado=True,sucursal__id=suc).exclude(accesorio__estatusAccesorio__estatus='Vendido').order_by('accesorio')
		almFic = AlmacenFicha.objects.filter(estado=True,sucursal__id=suc).exclude(ficha__estatusFicha__estatus='Vendido').order_by('ficha')
		almSaldo = SaldoSucursal.objects.filter(sucursal__id=suc)
		if query:
			qsetE=(Q(equipo__detallesEquipo__marca__marca__icontains=query) |Q(equipo__detallesEquipo__modelo__icontains=query) |
				Q(equipo__imei__icontains=query) |Q(equipo__icc__icontains=query))
			qsetX=(Q(expres__icc__icontains=query))
			qsetA=(Q(accesorio__codigoBarras__icontains=query)| Q(accesorio__detallesAccesorio__marca__marca__icontains=query)|
				Q(accesorio__detallesAccesorio__seccion__seccion__icontains=query)| 
				Q(accesorio__detallesAccesorio__descripcion__icontains=query))
			qsetF=(Q(ficha__folio__icontains=query)|Q(ficha__nominacion__nominacion__icontains=query))

			almEquipo = AlmacenEquipo.objects.filter(qsetE,estado=True,sucursal__id=suc).exclude(equipo__estatus__estatus='Vendido').order_by('equipo')
			almExpress = AlmacenExpres.objects.filter(qsetX,estado=True,sucursal__id=suc).exclude(expres__estatus__estatus='Vendido').order_by('expres')
			almAccs = AlmacenAccesorio.objects.filter(qsetA,estado=True,sucursal__id=suc).exclude(accesorio__estatusAccesorio__estatus='Vendido').order_by('accesorio')
			almFic = AlmacenFicha.objects.filter(qsetF,estado=True,sucursal__id=suc).exclude(ficha__estatusFicha__estatus='Vendido').order_by('ficha')
		
		
		paginator1 = Paginator(almEquipo, 50)
		paginator2 = Paginator(almExpress, 50)
		paginator3 = Paginator(almAccs, 50)
		paginator4 = Paginator(almFic, 50)
		pEq = None
		pEx = None
		pAc = None
		pFi = None
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

		
		ctx={'almEquipos':pEq,'almExpress':pEx,'almAccs':pAc,'almFic':pFi,'almSaldo':almSaldo,'query':query,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/existenciasTodo.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_vendedores_comisiones_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		verificarForm =  AuthenticationForm()
		info=""
		if 'identificarse' in request.POST:
			verificarForm = AuthenticationForm(request.POST)
			if verificarForm.is_valid:
			
				usuario=request.POST['username']
				clave=request.POST['password']

				acceso=authenticate(username=usuario,password=clave)
				
				if acceso is not None:
					if acceso.is_active:
						try:
							elusuario = Usuario.objects.get(user__username=usuario)
							## tipo de empleados vendedores que reciben comision por ventas
							nivel = Permiso(elusuario.user,[1,12])
							if nivel != -1:
								empleado = Empleado.objects.get(id=cveEmpleado(elusuario.user))
								comisiones = updComision(empleado,elusuario.user)
								#comisiones = Comision.objects.filter(empleado=empleado)[:12]
								
								ctx = {'empleado':empleado,'comisiones':comisiones,'info':info,'nivel':nivel,'vendedor':xhsdfg}
								return render_to_response('ventas/comisionEmpleado.html',ctx,context_instance=RequestContext(request))			

						except Usuario.DoesNotExist:
							pass
					else:
						info = info + 'no activo'
				else:
					info = info + ' acceso None'
			else:
				info = info + "Lo sentimos, los datos ingresados no corresponden al personal autorizado, intente nuevamente."
			verificarForm =  AuthenticationForm(request.POST)
			ctx = {'verificarForm':verificarForm,'info':info,'nivel':nivel,'vendedor':xhsdfg}
			return render_to_response('ventas/myVerificacionUser.html',ctx,context_instance=RequestContext(request))
			
		ctx = {'verificarForm':verificarForm,'info':info,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/myVerificacionUser.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_vendedores_estado_cuenta_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		verificarForm =  AuthenticationForm()
		info=""
		if 'identificarse' in request.POST:
			verificarForm = AuthenticationForm(request.POST)
			if verificarForm.is_valid:
			
				usuario=request.POST['username']
				clave=request.POST['password']

				acceso=authenticate(username=usuario,password=clave)
				
				if acceso is not None:
					if acceso.is_active:
						try:
							elusuario = Usuario.objects.get(user__username=usuario)
							## tipo de empleado cualquier empleado que quiera saber su estado de cuenta
							nivel = Permiso(elusuario.user,[1,2,3,4,5,6,7,8,9,10,11,12])
							if nivel != -1:
								cuentas=[]
								empleado = Empleado.objects.get(id=cveEmpleado(elusuario.user))
								cuenta=CuentaEmpleado.objects.filter(empleado=empleado).order_by('fxCreacion')
								for cue in cuenta:
									historial=HistorialEmpleado.objects.filter(cuentaEmpleado=cue)
									cuentas.append([cue,historial])
								
								ctx = {'empleado':empleado,'cuentas':cuentas,'info':info,'nivel':nivel,'vendedor':xhsdfg}
								return render_to_response('ventas/edoCuenta.html',ctx,context_instance=RequestContext(request))			
							
						except Usuario.DoesNotExist:
							pass
					else:
						info = info + 'no activo'
				else:
					info = info + ' acceso None'
			else:
				info = info + "Lo sentimos, los datos ingresados no corresponden al personal autorizado, intente nuevamente."
			verificarForm =  AuthenticationForm(request.POST)
			ctx = {'verificarForm':verificarForm,'info':info,'nivel':nivel,'vendedor':xhsdfg}
			return render_to_response('ventas/myVerificacionUser.html',ctx,context_instance=RequestContext(request))
			
		ctx = {'verificarForm':verificarForm,'info':info,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/myVerificacionUser.html',ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_caja_al_dia_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
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
		
		eqVendido = None
		expVendido = None
		ficVendido = None
		accVendido = None
		recVendido = None
		planVendido = None
		rentaVendido = None
		anticipo = None

		try:
			eqVendido = VentaEquipo.objects.filter(venta=vtaRealizadas)
			expVendido = VentaExpres.objects.filter(venta=vtaRealizadas)
			ficVendido = VentaFichas.objects.filter(venta=vtaRealizadas)
			accVendido = VentaAccesorio.objects.filter(venta=vtaRealizadas)
			recVendido = VentaRecarga.objects.filter(venta=vtaRealizadas)
			planVendido = VentaPlan.objects.filter(venta=vtaRealizadas)
			rentaVendido = Renta.objects.filter(venta=vtaRealizadas)
			anticipo = Anticipo.objects.filter(folioVenta=vtaRealizadas)
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
		except VentaPlan.DoesNotExist:
			planVendido = None
		except Renta.DoesNotExist:
			rentaVendido = None
		except Anticipo.DoesNotExist:
			anticipo = None

		ctx = {'caja':caja,'cosa':'Realizadas','vtaRealizadas':vtaRealizadas,'planVendido':planVendido,'rentaVendido':rentaVendido,'anticipo':anticipo,'recVendido':recVendido,'accVendido':accVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'info':info,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/allCaja.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_listas_equipos_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
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
		

		ctx={'nivel':nivel, 'query':query, 'r_items':r_items, 'info':info,'vendedor':xhsdfg}
		return render_to_response('ventas/listaPreciosEquipos.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_listas_accesorios_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
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
		

		ctx={'nivel':nivel, 'query':query, 'r_items':r_items, 'info':info,'vendedor':xhsdfg}
		return render_to_response('ventas/listaPreciosAccesorios.html', ctx,context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo
@login_required(login_url='/')
def ventas_listas_planes_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		query=request.GET.get('q','')
		
		r_items=None
		info=''

		r_items=Plan.objects.filter(activo=True)

		if query:
			qset=(Q(plan__icontains=query)|
				Q(costo__icontains=query)|
				Q(equiposGratis__icontains=query))
			r_items=Plan.objects.filter(qset,activo=True).distinct()
		
		ctx={'nivel':nivel, 'query':query, 'r_items':r_items, 'info':info,'vendedor':xhsdfg}
		return render_to_response('ventas/listaPlanes.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo
@login_required(login_url='/')
def ventas_papeleta_reporte_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		suc = cveSucursal(request.user)

		papeleta = None
		spapeleta = []
		eq = None
		ex = None
		veq = None
		vex = None
		try:
			veq = VentaEquipo.objects.filter(venta__sucursal__id=suc, venta__aceptada=True)
			vex = VentaExpres.objects.filter(venta__sucursal__id=suc, venta__aceptada=True)	
			for x in veq:
				try:
					papeleta = Papeleta.objects.get(esnImei=x.equipo.imei)
				except Papeleta.DoesNotExist:
					spapeleta.append([(x.venta.fecha).date(),x.equipo.detallesEquipo.marca.marca+' '+x.equipo.detallesEquipo.modelo+' '+str(x.equipo.imei),str(x.equipo.imei) ])
			for x in vex:
				try:
					papeleta = Papeleta.objects.get(esnImei=x.expres.icc)
				except Papeleta.DoesNotExist:
					spapeleta.append([(x.venta.fecha).date(),str(x.expres.icc),str(x.expres.icc)])	

		except VentaExpres.DoesNotExist:
			vex = None
		except VentaEquipo.DoesNotExist:
			veq = None
			
		
			
		ctx={'nivel':nivel,'spapeleta':spapeleta,'vendedor':xhsdfg}
		return render_to_response('ventas/sinPapeleta.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_autorizaciones_cancelaciones_view(request):
	nivel=Permiso(request.user,[0,1,12])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		
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

		info =""
		
		vtaCanceladas = Venta.objects.filter(sucursal=mysucursal,aceptada=False)

		ctx = {'rentaVendido':rentaVendido,'planVendido':planVendido,'anticipo':menosAnticipo,
		'accVendido':accVendido,'vtaCanceladas':vtaCanceladas,'recVendido':recVendido,'ficVendido':ficVendido,'expVendido':expVendido,'eqVendido':eqVendido,'nivel':nivel}
		return render_to_response('ventas/cancelacionServ.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo
@login_required(login_url='/')
def ventas_reportes_view(request):
	nivel=Permiso(request.user,[0,1,11])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		form = reporteCompleto()
		info = ""
		query = ""
		resultsExp = []
		resultsEq  = []
		if request.method == "POST":
			form = reporteCompleto(request.POST or None)
			if form.is_valid():
				fxInicio 	= form.cleaned_data['fxInicio']
				fxFinal 	= form.cleaned_data['fxFinal']
				tipo = form.data.get('tipoActivacion')
				
				if fxFinal:
					resultsEq = ActivacionEquipo.objects.filter(fxActivacion__range=[fxInicio,fxFinal],tipoActivacion__tipo__icontains=tipo)
					resultsExp = ActivacionExpress.objects.filter(fxActivacion__range=[fxInicio,fxFinal],tipoActivacion__tipo__icontains=tipo)
					query = "Entre fechas : "+str(fxInicio)+" y "+str(fxFinal)+" Activacion : "+str(tipo)
				else:
					resultsEq = ActivacionEquipo.objects.filter(fxActivacion__icontains=fxInicio,tipoActivacion__tipo__icontains=tipo)
					resultsExp = ActivacionExpress.objects.filter(fxActivacion__icontains=fxInicio,tipoActivacion__tipo__icontains=tipo)
					query = "Fecha : "+str(fxInicio)+" Activacion : "+str(tipo)

				
				ctx = {'form':form,'query':query, 'info':info, 'resultsEq':resultsEq, 'resultsExp': resultsExp, 'tipo':tipo ,'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/gerente_reporteConsultar.html',ctx,context_instance=RequestContext(request))
			
			else:
				info = "Seleccione un rango de fechas o la fecha inicial"
				form= reporteCompleto(request.POST)
		
		ctx = {'form':form,'query':query, 'info':info, 'resultsEq':resultsEq, 'resultsExp': resultsExp,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/gerente_reporteConsultar.html',ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo rev
@login_required(login_url='/')
def ventas_eventos_agregar_view(request):
	nivel=Permiso(request.user,[0,1,11])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		form = addEvento()
		info = ""
		if request.method == "POST":
			form = addEvento(request.POST or None)
			if form.is_valid():
				nombre 		= form.cleaned_data['nombre']
				direccion 	= form.cleaned_data['direccion']
				colonia 	= form.cleaned_data['colonia'] #buscar
				ciudad  	= form.cleaned_data['ciudad'] #buscar
				estado 		= form.cleaned_data['estado'] #id de estado
				cp 			= form.cleaned_data['cp'] #buscar
				zona    	= form.cleaned_data['zona'] #id 
				zona2    	= form.cleaned_data['zona2'] #id 
				encargado 	= form.cleaned_data['encargado'] #id empleado
				noCelOfi 	= form.cleaned_data['noCelOfi']

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
					noRepite = Sucursal.objects.get(nombre=nombre.title())#sucursal repetida
					info = "Lo sentimos, el nombre de la sucursal o evento, ya existe. Intente con otro nombre."
					form= addEvento(request.POST)
					ctx = {'form':form, 'info':info, 'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/nuevoEvento.html', ctx,context_instance=RequestContext(request))
				except :
					pass
				try:
					nousuario = Usuario.objects.get(empleado=myempleado,permiso=12)
					ocupado = Sucursal.objects.get(encargado=myempleado) # el empleado ya tiene una sucursal asignada como encargado
					sucAnterior = VendedorSucursal.objects.get(empleado=myempleado)

					if ocupado:
						info = "El empleado que quiere asignar como encargado, ya pertenece a una sucursal como tal. Intente con otro."
						form= addEvento(request.POST)
						ctx = {'form':form, 'info':info, 'nivel':nivel,'vendedor':xhsdfg}
						return render_to_response('ventas/nuevoEvento.html', ctx,context_instance=RequestContext(request))
				except Usuario.DoesNotExist:
					info = "El empleado que quiere asignar como encargado, No tiene un usuario disponible para acceder al portal. Intente con otro o pida a un administrador agregar dicho empleado."
					form= addEvento(request.POST)
					ctx = {'form':form, 'info':info, 'nivel':nivel,'vendedor':xhsdfg}
					return render_to_response('ventas/nuevoEvento.html', ctx,context_instance=RequestContext(request))					
				except Sucursal.DoesNotExist:
					pass
				except VendedorSucursal.DoesNotExist:
					pass

				if sucAnterior:
					try:
						sucAnterior.delete() #lo borramos de la sucursal anterior, para asignarlo a la nueva.
					except :
						info='Lo sentimos, la información enviada no se almaceno/actualizo por problemas de integridad de datos'
				try:
					with transaction.atomic():
						a = Sucursal()
						a.tipoSucursal = TipoSucursal.objects.get(tipo='Evento')
						a.nombre 	= nombre.title()
						a.encargado = myempleado
						if noCelOfi:
							a.noCelOfi 	= noCelOfi
						a.direccion = direccion.title()
						a.colonia = Colonia.objects.get(id=z1[0])
						a.cp 	  = CP.objects.get(id=z1[2])
						a.ciudad  = Ciudad.objects.get(id=z1[1])
						a.zona    = lazona
						a.estado  = EstadoSucursal.objects.get(estado='Activa')
						a.save()

						b = VendedorSucursal()
						b.empleado = myempleado
						b.sucursal = a
						b.save()
						info ="Se agrego correctamente el Evento: "+a.nombre+" Encargado: "+myempleado.nombre
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
				form = addEvento()
				ctx = {'form':form, 'info':info, 'nivel':nivel,'vendedor':xhsdfg}
				return render_to_response('ventas/nuevoEvento.html', ctx,context_instance=RequestContext(request))	
			else:
				info = "No se registraron los datos, verifique sus datos."
				form= addEvento(request.POST)
		
		ctx = {'form':form, 'info':info, 'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/nuevoEvento.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo rev
@login_required(login_url='/')
def ventas_eventos_consultar_view(request):
	nivel=Permiso(request.user,[0,1,11])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
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
					try:
						upd = Sucursal.objects.get(id= s)
						upd.estado = EstadoSucursal.objects.get(estado='Inactiva')
						upd.save()
					except :
						
						info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
					
						#sukii #transaction.commit()#'''

			if request.GET.get('act'):
				s = request.GET.get('act','')
				if s:
					try:
						upd = Sucursal.objects.get(id= s)
						upd.estado = EstadoSucursal.objects.get(estado='Activa')
						upd.save()
					except :
						
						info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
					
						#sukii #transaction.commit()#'''

		ctx={'Sucursal':pSucursales,'query':query,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/reporteEventos.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo rev
@login_required(login_url='/')
def ventas_amonestaciones_agregar_view(request):
	nivel=Permiso(request.user,[0,1,11])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
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
						form = AmonestacionForm()
						info = "Se ha registrado la Amonestacion."
				except :
					info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
				
			else:
				info = "Por favor, Verifique su informacion"
				form= AmonestacionForm(request.POST)
		
		ctx = {'form':form,'info':info,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/amonestaciones.html',ctx,context_instance=RequestContext(request))
		#'''

	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo rev
@login_required(login_url='/')
def ventas_amonestaciones_consultar_view(request):
	nivel=Permiso(request.user,[0,1,11])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		query  = request.GET.get('q','')
		pag1=request.GET.get('pag','')
		
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


		ctx={'amonestaciones':pAm,'query':query,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/consultaAmonestaciones.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')

#listo rev
@login_required(login_url='/')
def ventas_sucursales_reporte_view(request):
	nivel=Permiso(request.user,[0,1,11])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		query  = request.GET.get('q','')
		pag1=request.GET.get('pag','')
		
		qset2=(Q(tipoSucursal__tipo__icontains='Evento') | Q(tipoSucursal__tipo__icontains='Sucursal'))#
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
					return render_to_response('ventas/reporteSucursalesActivas.html', ctx,context_instance=RequestContext(request))

							
		ctx={'Sucursal':pSucursales,'query':query,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/reporteSucursalesActivas.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo rev
@login_required(login_url='/')
def ventas_sucursales_vendedores_view(request):
	nivel=Permiso(request.user,[0,1,11])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		_usuario = Usuario.objects.get(user=request.user)
		_empleado 			= _usuario.empleado
		vendedorSucursal 	= VendedorSucursal.objects.get(empleado=_empleado)
		mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

		query  = request.GET.get('q','')
		pag1=request.GET.get('pag','')

		qset2=(Q(sucursal__tipoSucursal__tipo__icontains='Evento') | Q(sucursal__tipoSucursal__tipo__icontains='Sucursal'))# | Q(tipoSucursal__tipo__icontains='Sucursal')
		vd = VendedorSucursal.objects.filter(qset2).exclude(sucursal=mysucursal).order_by('sucursal').order_by('empleado')

		if query:
			qset=(Q(sucursal__nombre__icontains=query) |
			 Q(empleado__nombre__icontains=query) | 
			 Q(empleado__aPaterno__icontains=query) | 
			 Q(empleado__aMaterno__icontains=query) | 
			 Q(empleado__curp__icontains=query) | 
			 Q(sucursal__zona__zona__icontains=query))
			vd = VendedorSucursal.objects.filter(qset,qset2,empleado__estadoEmpleado=True).exclude(sucursal=mysucursal).order_by('sucursal').order_by('empleado')
		
		
		paginator1 = Paginator(vd, 50)

		pAm=None
		
		try:
			pAm = paginator1.page(pag1)
		except PageNotAnInteger:
			pAm= paginator1.page(1)
		except EmptyPage:
			pAm = paginator1.page(paginator1.num_pages)


		ctx={'empleado':pAm,'query':query,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/reporteVendedores.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo rev
@login_required(login_url='/')
def ventas_reportes_equipos_view(request):
	nivel=Permiso(request.user,[0,1,11])
	
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		today = datetime.now() #fecha actual
		dateFormat = today.strftime("%Y-%m-%d") # fecha con formato

		query  = request.GET.get('q','')
		pag1=request.GET.get('pag','')
		today = datetime.now()

		activacion = ActivacionEquipo.objects.filter(fxActivacion__icontains=dateFormat, equipo__estatus__estatus='Vendido')
	
		if query:
			qset=(Q(fxActivacion__icontains=query) |
			 Q(equipo__imei__icontains=query) | 
			 Q(equipo__icc__icontains=query) | 
			 Q(equipo__detallesEquipo__marca__marca__icontains=query) | 
			 Q(equipo__detallesEquipo__modelo__icontains=query) | 
			 Q(equipo__estatus__estatus='Vendido')|
			 Q(equipo__estatus__estatus='Liquidado')|
			 Q(tipoActivacion__tipo__icontains=query) |
			 Q(empleado__nombre__icontains=query) | 
			 Q(empleado__aPaterno__icontains=query) | 
			 Q(empleado__aMaterno__icontains=query) |  
			 Q(empleado__curp__icontains=query) | 
			 Q(sucursal__nombre__icontains=query))
			activacion = ActivacionEquipo.objects.filter(qset).order_by('equipo')
		
		
		paginator1 = Paginator(activacion, 50)

		pAm=None
		
		try:
			pAm = paginator1.page(pag1)
		except PageNotAnInteger:
			pAm= paginator1.page(1)
		except EmptyPage:
			pAm = paginator1.page(paginator1.num_pages)


		ctx={'activacion':pAm,'query':query,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/reporteEquipos.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')



#listo rev
@login_required(login_url='/')
def ventas_reportes_express_view(request):
	nivel=Permiso(request.user,[0,1,11])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		today = datetime.now() #fecha actual
		dateFormat = today.strftime("%Y-%m-%d") # fecha con formato

		query  = request.GET.get('q','')
		pag1=request.GET.get('pag','')
		today = datetime.now()

		activacion = ActivacionExpress.objects.filter(fxActivacion__icontains=dateFormat, express__estatus__estatus='Vendido')
	
		if query:
			qset=(Q(fxActivacion__icontains=query) |
			 Q(express__icc__icontains=query) | 
			 Q(tipoActivacion__tipo__icontains=query) |
			 Q(empleado__nombre__icontains=query) | 
			 Q(empleado__aPaterno__icontains=query) | 
			 Q(empleado__aMaterno__icontains=query) |  
			 Q(empleado__curp__icontains=query) | 
			 Q(sucursal__nombre__icontains=query))
			activacion = ActivacionExpress.objects.filter(qset,express__estatus__estatus='Vendido').order_by('express')
		
		
		paginator1 = Paginator(activacion, 50)

		pAm=None
		
		try:
			pAm = paginator1.page(pag1)
		except PageNotAnInteger:
			pAm= paginator1.page(1)
		except EmptyPage:
			pAm = paginator1.page(paginator1.num_pages)


		ctx={'activacion':pAm,'query':query,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/reporteExpress.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')


#listo rev
@login_required(login_url='/')
def ventas_reportes_planes_view(request):
	nivel=Permiso(request.user,[0,1,11])
	if nivel != -1:
		xhsdfg = inuSucursal(request.user)
		today = datetime.now() #fecha actual
		dateFormat = today.strftime("%Y-%m-%d") # fecha con formato

		query  = request.GET.get('q','')
		pag1=request.GET.get('pag','')
		today = datetime.now()

		activacion = ActivacionPlan.objects.filter(fxActivacion__icontains=dateFormat)
	
		if query:
			qset=(Q(fxActivacion__icontains=query) |
			 Q(plan__plan__icontains=query) |
			 Q(equipo__imei__icontains=query) | 
			 Q(equipo__icc__icontains=query) | 
			 Q(equipo__detallesEquipo__marca__marca__icontains=query) | 
			 Q(equipo__detallesEquipo__modelo__icontains=query) | 
			 Q(sucursal__nombre__icontains=query))
			activacion = ActivacionPlan.objects.filter(qset).order_by('equipo')
		
		
		paginator1 = Paginator(activacion, 50)

		pAm=None
		
		try:
			pAm = paginator1.page(pag1)
		except PageNotAnInteger:
			pAm= paginator1.page(1)
		except EmptyPage:
			pAm = paginator1.page(paginator1.num_pages)


		ctx={'activacion':pAm,'query':query,'nivel':nivel,'vendedor':xhsdfg}
		return render_to_response('ventas/reportePlanes.html', ctx,context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/NoTienePermiso')