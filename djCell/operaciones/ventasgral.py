# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models import Q
from decimal import Decimal
from djCell.apps.productos.models import TiempoGarantia,Estatus,Marca,Gama,DetallesEquipo,Equipo,TipoIcc,DetallesExpres,Expres, Secciones,MarcaAccesorio,DetallesAccesorio,EstatusAccesorio,Accesorio, NominacionFicha,EstatusFicha,Ficha,  TiempoAire
from djCell.apps.almacen.models import AlmacenEquipo, AlmacenExpres, AlmacenAccesorio, AlmacenFicha
from djCell.apps.sucursales.models import EstadoSucursal, TipoSucursal, Sucursal, VendedorSucursal
from djCell.apps.ventas.models import EstadoVenta, Venta,VentaEquipo,VentaExpres,VentaAccesorio,VentaFichas,VentaRecarga,VentaPlan,Renta, Cancelaciones, VentaMayoreo,TipoPago, Anticipo
from djCell.apps.corteVta.models import GastosSucursal, CorteVenta, DiferenciasCorte, VentasCorte,RecargasVendidoCorte
from djCell.apps.credito.models import Credito
from djCell.apps.recargas.models import Monto,Recarga,SaldoSucursal, HistorialSaldo, SaldoStock
from djCell.apps.clientes.models import ClienteFacturacion, ClienteServicio, Mayorista
from djCell.apps.papeletas.models import TipoProducto, Papeleta
from djCell.apps.activaciones.models import *
from djCell.apps.servicios.models import *
from djCell.apps.comisiones.models import *
from datetime import datetime, timedelta, date
import time


#------------------ ventas
def vta_almacenItems(tipo,item,sd,so):
	if tipo==0:
		try:
			aux=AlmacenEquipo.objects.get(estado=True,equipo=item,sucursal=so)
			aux.estado=False
			aux.save()
		except :
			pass
		if sd:
			alEq=AlmacenEquipo()
			alEq.sucursal=sd
			alEq.equipo=item
			alEq.estado=True
			alEq.save()

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

	elif tipo==1:
		try:
			aux=AlmacenExpres.objects.get(estado=True,expres=item,sucursal=so)
			aux.estado=False
			aux.save()
		except :
			pass
		if sd:
			alEq=AlmacenExpres()
			alEq.sucursal=sd
			alEq.expres=item
			alEq.estado=True
			alEq.save()
			
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

	elif tipo==2:
		try:
			aux=AlmacenAccesorio.objects.get(estado=True,accesorio=item,sucursal=so)
			aux.estado=False
			aux.save()
		except :
			pass
		if sd:
			alEq=AlmacenAccesorio()
			alEq.sucursal=sd
			alEq.accesorio=item
			alEq.estado=True
			alEq.save()

			estatus=None
			try:
				estatus=EstatusAccesorio.objects.get(estatus="Existente")
			except :
				estatus=EstatusAccesorio()
				estatus.estatus="Existente"
				estatus.save()
				
			item.estatusAccesorio=estatus
			item.sucursal=sd
			item.save()

	elif tipo==3:
		try:
			aux=AlmacenFicha.objects.get(estado=True,ficha=item,sucursal=so)
			aux.estado=False
			aux.save()
		except :
			pass
		if sd:
			alEq=AlmacenFicha()
			alEq.sucursal=sd
			alEq.ficha=item
			alEq.estado=True
			alEq.save()

			estatus=None
			try:
				estatus=EstatusFicha.objects.get(estatus="Existente")
			except :
				estatus=EstatusFicha()
				estatus.estatus="Existente"
				estatus.save()
				
			item.estatusFicha=estatus
			item.sucursal=sd
			item.save()

	elif tipo==4:
		saldo=item
		saldoAnte=0
		try:
			aux=SaldoSucursal.objects.get(sucursal=so)
			aux.saldo="%.2f" % round(aux.saldo-item,2)
			aux.save()
		except :
			pass
		if sd:
			try:
				sucursal=SaldoSucursal.objects.get(sucursal=sd)
				saldoAnte=sucursal.saldo
				sucursal.saldo="%.2f" % round(sucursal.saldo+item,2)
				sucursal.save()
			except :
				sucursal=SaldoSucursal()
				sucursal.sucursal=sd
				sucursal.saldo=item
				sucursal.save()
			historial=HistorialSaldo()
			historial.sucursal=sd
			historial.saldoInicial = saldoAnte
			historial.abono 	= saldo
			historial.save()

def nuevoFolio(tipo,myuser,folio):
	generarFolio = None
	today = datetime.now() #fecha actual
	dateFormat = today.strftime("%Y-%m-%d") # fecha con formato

	nuevo = False
	while nuevo == False:
		pfff = str(time.time())
		omo = ""
		for x in xrange(7,10):
			omo = omo + pfff[x]
		dateFormat2 = today.strftime("%Y.%m.%d")
		generarFolio = 'VA-'+ str(tipo) + str(dateFormat2) + '-' + omo
		try:
			v = Venta.objects.get(folioVenta=generarFolio)
			nuevo = False
		except Venta.DoesNotExist:
			nuevo = True
	#'''
	return generarFolio

def nuevoFolio2(tipo): #folio de venta generado
	generarFolio = None
	today = datetime.now() #fecha actual
	dateFormat = today.strftime("%Y-%m-%d") # fecha con formato

	nuevo = False
	while nuevo == False:
		pfff = str(time.time())
		omo = ""
		for x in xrange(7,10):
			omo = omo + pfff[x]
		dateFormat2 = today.strftime("%Y.%m.%d")
		generarFolio = 'V-'+ str(tipo) + str(dateFormat2) + '-' + omo
		try:
			v = Venta.objects.get(folioVenta=generarFolio)
			nuevo = False
		except Venta.DoesNotExist:
			nuevo = True
	#'''
	return generarFolio


def sumaVtas(folio):
	try:
		m = Venta.objects.get(folioVenta=folio)
		plus = 0
		if m:
			eq = VentaEquipo.objects.filter(venta__folioVenta=folio)
			for x in eq:
				plus = plus + x.precVenta

			ex = VentaExpres.objects.filter(venta__folioVenta=folio)
			for x in ex:
				plus = plus + x.precVenta

			fi = VentaFichas.objects.filter(venta__folioVenta=folio)
			for x in fi:
				plus = plus + x.precVenta

			acc = VentaAccesorio.objects.filter(venta__folioVenta=folio)
			for x in acc:
				plus = plus + x.precVenta

			rec = VentaRecarga.objects.filter(venta__folioVenta=folio)
			for x in rec:
				plus = plus + x.precVenta
	
	except Venta.DoesNotExist:
		plus = 0
	return plus

def sumaVtas2(folio):
	try:
		m = Venta.objects.get(folioVenta=folio)
		plus = 0
		if m:
			eq = VentaEquipo.objects.filter(venta__folioVenta=folio)
			for x in eq:
				plus = plus + x.precVenta

			ex = VentaExpres.objects.filter(venta__folioVenta=folio)
			for x in ex:
				plus = plus + x.precVenta

			fi = VentaFichas.objects.filter(venta__folioVenta=folio)
			for x in fi:
				plus = plus + x.precVenta

			acc = VentaAccesorio.objects.filter(venta__folioVenta=folio)
			for x in acc:
				plus = plus + x.precVenta

			rec = VentaRecarga.objects.filter(venta__folioVenta=folio)
			for x in rec:
				plus = plus + x.precVenta

			plan = VentaPlan.objects.filter(venta__folioVenta=folio)
			for x in plan:
				plus = plus + x.precVenta

			ren = Renta.objects.filter(venta__folioVenta=folio)
			for x in ren:
				plus = plus + x.abono
	
	except Venta.DoesNotExist:
		plus = 0
	return plus


def updVta(folio, mysucursal,myuser):
	try:
		vtaGral = Venta.objects.get(folioVenta=folio)
		vtaGral.total = sumaVtas(folio) 
		vtaGral.save()

	except Venta.DoesNotExist:
		vtaGral =  Venta()
		vtaGral.folioVenta 	= folio
		vtaGral.sucursal 	= mysucursal
		vtaGral.usuario 	= myuser
		vtaGral.total 		= 0
		vtaGral.aceptada 	= False
		vtaGral.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
		vtaGral.estado 		= EstadoVenta.objects.get(estado='Proceso')
		vtaGral.save()

def updVtaMayoreo(folio, mysucursal,myuser):
	try:
		vtaGral = Venta.objects.get(folioVenta=folio)
		vtaGral.total = sumaVtas(folio) 
		vtaGral.save()

	except Venta.DoesNotExist:
		vtaGral =  Venta()
		vtaGral.folioVenta 	= folio
		vtaGral.sucursal 	= mysucursal
		vtaGral.usuario 	= myuser
		vtaGral.total 		= 0
		vtaGral.aceptada 	= False
		vtaGral.mayoreo 	= True
		vtaGral.tipoPago 	= TipoPago.objects.get(tipo='Efectivo')
		vtaGral.estado 		= EstadoVenta.objects.get(estado='Proceso')
		vtaGral.save()

def listarTicket(vta):
	v = []
	eq = []
	ex = []
	ac = []
	fi = []
	rc = []
	pl = []
	vr = []
	an = []
	cd = []
	vm = []
	try:
		v = Venta.objects.get(folioVenta=vta)
		eq = VentaEquipo.objects.filter(venta=v)
		ex = VentaExpres.objects.filter(venta=v)
		ac = VentaAccesorio.objects.filter(venta=v)
		fi = VentaFichas.objects.filter(venta=v)
		rc = VentaRecarga.objects.filter(venta=v)
		pl = VentaPlan.objects.filter(venta=v)
		vr = Renta.objects.filter(venta=v)
		an = Anticipo.objects.filter(folioVenta=v)
		try:
			cd = Credito.objects.filter(venta=v)
		except :
			cd = []
		try:
			vm = VentaMayoreo.objects.filter(folioVenta=v)[:1]
		except :
			vm = []
	except :
		pass
	mivi = []
	mivi.append([v,eq,ex,ac,fi,rc,pl,vr,an,cd,vm])
	#            0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
	return mivi
				
#------------------------ ventas Mayoreo
def addEquipoVta1(prod,mcPrecio ,mysucursal, vta, user):
	resultAdd = ""
	m = None
	try:
		m = Equipo.objects.get(imei=prod,sucursal=mysucursal)
		gogeta = VentaEquipo.objects.get(equipo=m,folioVenta__aceptada=True)
		if gogeta:
			m = None
	except :
		resultAdd ="Venta: "+vta+" (-) El equipo no se encuentra disponible o pertenece a otra sucursal."
	if m and vta:
		v = m # producto a la vta |evitar hacer doble busqueda
		if v.estatus.estatus=='En mal estado' or v.estatus.estatus=='Activado' or v.estatus.estatus=='Existente' and v.icc != None:
			try:
				with transaction.atomic():
					updVta(vta,mysucursal,user)
					#agregar a la venta general
					nv = VentaEquipo()
					nv.venta = Venta.objects.get(folioVenta=vta)
					if mcPrecio == 'Publico':
						nv.precVenta = v.detallesEquipo.precioMenudeo
					else:
						nv.precVenta = v.detallesEquipo.precioMayoreo
					nv.equipo = v
					nv.save()
								
					#upd producto state
					upd = Equipo.objects.get(imei=nv.equipo.imei)
					upd.estatus = Estatus.objects.get(estatus='Vendido')
					upd.save()
				
					#dar de baja de su almacen
					vta_almacenItems(0,upd,None,mysucursal)
					resultAdd ="Venta: "+vta+" (+) Equipo: "+nv.equipo.detallesEquipo.marca.marca+" "+nv.equipo.detallesEquipo.modelo+" $"+ str(nv.precVenta)
					
			except :
				resultAdd ="Error en Venta: "+vta+" (-) producto: "+v+" NO SE PUDO AGREGAR "+v.estatus.estatus
		else:
			resultAdd ="Venta: "+vta+" (-) El equipo no cuenta con express asignada. Equipo: "+v.estatus.estatus
	else:
		resultAdd = "El equipo pertenece a otra sucursal o ya se encuentra vendido. Avisar a administracion si el producto lo tiene en existencia. "
	return resultAdd	

def addExpresVta1(prod, mcPrecio,mysucursal, vta, user):
	resultAdd = ""
	m=None
	try:
		m = Expres.objects.get(icc=prod,sucursal=mysucursal)
		gogeta = VentaExpres.objects.get(expres=m,folioVenta__aceptada=True)
		if gogeta:
			m = None
	except :
		resultAdd ="Venta: "+vta+" (-) La express no se encuentra disponible o pertenece a otra sucursal."
	if m and vta:
		v = m # producto a la vta
		#if m.estatus.estatus!='Vendido':
		if (v.estatus.estatus=='En mal estado' or v.estatus.estatus=='Activado' or v.estatus.estatus=='Existente') and v.detallesExpres.descripcion!='Equipo':
			try:
				with transaction.atomic():
					updVta(vta,mysucursal,user)
					#agregar a la venta general 
					nv = VentaExpres()
					nv.venta = Venta.objects.get(folioVenta=vta)
					if mcPrecio == 'Publico':
						nv.precVenta = v.detallesExpres.precioMenudeo
					else:
						nv.precVenta = v.detallesExpres.precioMayoreo
					nv.expres = v
					nv.save()
								
					#upd producto state
					upd = Expres.objects.get(icc=nv.expres.icc)
					upd.estatus = Estatus.objects.get(estatus='Vendido')
					upd.save()
					
					#dar de baja de su almacen
					vta_almacenItems(1,upd,None,mysucursal)

					#actualizacmos formulario de venta
					resultAdd ="Venta: "+vta+" (+) Express: "+str(nv.expres.icc)+" $"+ str(nv.precVenta)
			except :
				resultAdd ="Error en Venta: "+vta+" (-) producto: "+v+" NO SE PUDO AGREGAR "+v.estatus.estatus
		else:
			resultAdd ="Venta: "+vta+" (-) La express no se encuentra disponible o pertenece a otra sucursal. "+v.estatus.estatus+" No puede ser tipo Equipo. Tipo: "+v.detallesExpres.descripcion
	else:
		resultAdd = "El producto pertenece a otra sucursal o ya se encuentra vendido. Avisar a administracion si el producto lo tiene en existencia. "+v.estatus.estatus

	return resultAdd

def addAccVta1(prod, mcPrecio,mysucursal, vta, user):
	resultAdd = ""
	m = None
	try:
		m = Accesorio.objects.get(codigoBarras=prod,sucursal=mysucursal)
		gogeta = VentaAccesorio.objects.get(accesorio=m,folioVenta__aceptada=True)
		if gogeta:
			m = None
	except :
		resultAdd ="Venta: "+vta+" El accesorio no se encuentra o pertenece a otra sucursal"

	if m and vta:
		v = m 
		if v.estatusAccesorio.estatus != 'Vendido':
			try:
				with transaction.atomic():
					updVta(vta,mysucursal,user)
					#agregar a la venta general
					nv = VentaAccesorio()
					nv.venta = Venta.objects.get(folioVenta=vta)
					if mcPrecio == 'Publico':
						nv.precVenta = v.detallesAccesorio.precioMenudeo
					else:
						nv.precVenta = v.detallesAccesorio.precioMayoreo
					nv.accesorio = v
					nv.save()
								
					#upd producto state
					upd = Accesorio.objects.get(codigoBarras=nv.accesorio.codigoBarras)
					upd.estatusAccesorio = EstatusAccesorio.objects.get(estatus__icontains='Vendido')#vendido
					upd.save()
					
					#dar de baja de su almacen
					vta_almacenItems(2,upd,None,mysucursal)

					#actualizacmos formulario de venta
					resultAdd ="Venta: "+vta+" (+) Accesorio: "+nv.accesorio.detallesAccesorio.marca.marca+" "+nv.accesorio.detallesAccesorio.descripcion+" $"+ str(nv.precVenta)
			except :
				resultAdd =" Error en Venta: "+vta+" (-) producto: "+v+" NO SE PUDO AGREGAR"	
		else:
			resultAdd ="Venta: "+vta+" El accesorio no se encuentra o pertenece a otra sucursal"
	else:
		resultAdd = "El producto pertenece a otra sucursal o ya se encuentra vendido. Avisar a administracion si el producto lo tiene en existencia. "

	return resultAdd

def addFichaVta1(queryFic,queryFic2,descuento1 ,mysucursal, vta, user,cliente):
	resultAdd = ""
	m = None
	descuento = 0	
	try:
		m = Ficha.objects.get(folio = queryFic,sucursal=mysucursal)
		if descuento1 == None:
			descuento = Mayorista.objects.get(id=cliente).descuentoFichas
		else:
			descuento = Decimal(descuento1)
	except :
		resultAdd = "La Ficha no esta disponible o el cliente no aplico. "
	if m and queryFic2 and vta:
		updVta(vta,mysucursal,user)
		fin = queryFic
		inicio = queryFic2 
		dif = Decimal(inicio) - Decimal(fin)
		nominacion = Ficha.objects.get(folio = queryFic,sucursal=mysucursal).nominacion.nominacion
					
		no = dif +  1
		stot = (nominacion * no) * (descuento/ 100)
		tot = ((nominacion * no) - stot)/no
		resultAdd ="Venta: "+vta+ " Fichas Agregadas "
		i = 0
		j = 0
		for x in xrange(0,no):
			try:
				v = Ficha.objects.get(folio = Decimal(fin) + i,sucursal=mysucursal)
				if v.estatusFicha.estatus != 'Vendido' :
					#agregar a la venta general e inicializar de nuevo el 
					nv = VentaFichas()
					nv.venta = Venta.objects.get(folioVenta=vta)
					nv.precVenta = tot
					nv.ficha = v
					nv.save()
								
					#upd producto state
					upd = Ficha.objects.get(folio=nv.ficha.folio)
					upd.estatusFicha = EstatusFicha.objects.get(estatus__icontains='Vendido')
					upd.save()
					
					#dar de baja de su almacen
					vta_almacenItems(3,upd,None,mysucursal)
					resultAdd = resultAdd +" (+) "+str(nv.ficha.folio)+" . $"+str(nv.precVenta)
					j = j +  1
				else:
					resultAdd = resultAdd +" Vendido (-) "+str(Decimal(fin) + i) +" . "
				i = i + 1
			except :
				resultAdd = resultAdd +" Ficha no disponible (-) "+str(Decimal(fin) + i) +" . "

		resultAdd = resultAdd +' Total: '+str(j)
		
	elif m and vta:
		updVta(vta,mysucursal,user)
		nominacion = Ficha.objects.get(folio = queryFic,sucursal=mysucursal).nominacion.nominacion
		stot = nominacion * (descuento/ 100)
		tot = (nominacion - stot)
					
		v = Ficha.objects.get(folio = queryFic,sucursal=mysucursal)
		if v.estatusFicha.estatus != 'Vendido' :
			try:
				with transaction.atomic():
					#agregar a la venta general e inicializar de nuevo el 
					nv = VentaFichas()
					nv.venta = Venta.objects.get(folioVenta=vta)
					nv.precVenta = tot
					nv.ficha = v
					nv.save()
					
					#upd producto state
					upd = Ficha.objects.get(folio=nv.ficha.folio)
					upd.estatusFicha = EstatusFicha.objects.get(estatus__icontains='Vendido')
					upd.save()
					
					#dar de baja de su almacen
					vta_almacenItems(3,upd,None,mysucursal)
					resultAdd="Venta: "+vta+" (+) "+str(nv.ficha.folio)+" . $"+str(nv.precVenta)
			except :
				resultAdd="Error en Venta: "+vta+" (-) "+queryFic+" . No se agrego."
		else:
			resultAdd="Venta: "+vta+" (-) "+queryFic+" . No se encuentra disponible o no pertenece a la Sucursal"
	
	return resultAdd

def addRecarga1(rfolio,folio,montos, observaciones, descuento1,mysucursal, vta, user, cliente):
	#por politicas de la empresa el saldo mayoreo se descuenta de almacen
	descuento = 0
	saldo = 0
	if descuento1 == None:
		descuento = Mayorista.objects.get(id=cliente).descuentoRecargas
		saldo = SaldoSucursal.objects.get(sucursal__nombre='Almacen Central').saldo
	else:
		descuento = Decimal(descuento1)
		saldo = SaldoSucursal.objects.get(sucursal__nombre=mysucursal.nombre).saldo
	
	monto = Monto.objects.get(id=montos).monto
	if saldo >= monto:
		try:
			with transaction.atomic():
				if descuento1 == None:
					updVtaMayoreo(vta,mysucursal,user)
				else:
					updVta(vta,mysucursal,user)
				stot = monto * (descuento/ 100)
				tot = monto - stot
				v = Recarga()
				if rfolio:
					v.folio = 'G'+str(datetime.now().strftime("%d.%m.%Y.%X"))
				else:
					v.folio = folio
				v.montos = Monto.objects.get(id=montos)
				v.sucursal = Sucursal.objects.get(id=mysucursal.id) #sucursal donde se hizo 
				v.observaciones = observaciones
				v.save()
								
				nv = VentaRecarga()
				nv.venta = Venta.objects.get(folioVenta=vta)
				nv.precVenta = tot
				nv.recarga = v
				nv.save()

				if cliente:			
					pf = VentaMayoreo() #historial de ventas de mayoristas
					pf.folioVenta 	= Venta.objects.get(folioVenta=vta)
					pf.clienteMayoreo 	= Mayorista.objects.get(id=cliente)
					pf.descuentoAplicado = descuento
					pf.save()

					#upd producto state - saldo de sucursal
					upd = SaldoSucursal.objects.get(sucursal__nombre='Almacen Central')
					upd.saldo = upd.saldo - monto
					upd.save()
				else:
					#upd producto state - saldo de sucursal
					upd = SaldoSucursal.objects.get(sucursal__nombre=mysucursal.nombre)
					upd.saldo = upd.saldo - monto
					upd.save()		
				resultAdd = "Se Registro Recarga (+) $"+str(v.montos.monto) +" %desc. "+str(nv.precVenta)
		except :
			resultAdd = "Error en el Registro de Recarga (-)$"+str(monto)
	else:
		resultAdd ="La Sucursal no cuenta con saldo para aplicar a la venta"

	return resultAdd

#------------------------ ventas Credito


#-------------------- corte de caja
def generarCorte(sucursal, dia, myuser):
	generarFolio = None
	today = None
	folio = None
	#si dia es none es la fecha de hoy
	#sino agregar un dia a la fecha
	if dia:
		today = datetime.today() + timedelta(days=1) # mañana
	else:
		today = datetime.now()

	dateFormat = today.strftime("%Y-%m-%d") # fecha con formato
	
	i = 1
	nuevo = False
	crear = True
	while nuevo == False: #devolver folio nuevo o existente que no este cerrado
		generarFolio = 'A'+str(sucursal.id)+ str(dateFormat) +'-' + str(i)
		try:
			v = CorteVenta.objects.get(folioCorteVta=generarFolio)
			if v.cerrado:
				nuevo =  False # si esta cerrado generar uno nuevo
				crear = "No" # no crear ni actualizar
			else:
				nuevo = True # corte sin cerrar
				crear = "upd" # actualizar
				folio = v.folioCorteVta
		except CorteVenta.DoesNotExist:
			nuevo = True
			crear = "nuevo" # corte nuevo
		i = i + 1

	if crear == "nuevo":
		a = CorteVenta()
		a.folioCorteVta	= generarFolio
		a.sucursal 		= sucursal
		a.totalVta 		= 0
		a.totalGastos 	= 0
		a.total			= 0
		a.cierraCorte 	= myuser
		a.save()
		folio = a.folioCorteVta
	
	return folio

def fillCorte(folio, mysucursal):
	vtas = None
	try:
		qset = (Q(estado__estado='Pagada')|Q(estado__estado='Proceso'))
		vtas = Venta.objects.filter(qset,sucursal__nombre=mysucursal.nombre, aceptada=True) 
		# todas las ventas de  la sucursal que esten pagadas
		# en proceso porque las ventas a credito tambien cuentan
		for v in vtas:
			try:
				corte = VentasCorte.objects.get(venta = v) #filtrar, verificar si la venta ya pertence a un corte
				if corte: #la venta pertenece ya a un corte
					pass
				else:
					#agregar la venta al corte
					n = VentasCorte()
					n.corteVenta = CorteVenta.objects.get(folioCorteVta=folio)
					n.venta = v
					n.save()
			except VentasCorte.DoesNotExist:
				#agregar la venta al corte
				n = VentasCorte()
				n.corteVenta = CorteVenta.objects.get(folioCorteVta=folio)
				n.venta = v
				n.save()

	except Venta.DoesNotExist:
		vtas = None

def updCorte(folio):
	try:
		sumaVtas = 0
		sumaAnticipo = 0
		sumaGastos = 0
		total = 0
		vc = VentasCorte.objects.filter(corteVenta__folioCorteVta=folio)
		for x in vc:
			if x.venta.credito and x.venta.estado.estado == 'Proceso':
				try:
					an = Anticipo.objects.get(folioVenta=x.venta)
					sumaAnticipo = sumaAnticipo + an.monto
				except :
					pass
			else:
				sumaVtas = sumaVtas + x.venta.total
		
		g = GastosSucursal.objects.filter(corteVenta__folioCorteVta=folio)
		for x in g:
			sumaGastos =  sumaGastos + x.gasto

		total = sumaVtas + sumaAnticipo - sumaGastos

		upd = CorteVenta.objects.get(folioCorteVta=folio)
		upd.totalVta = sumaVtas + sumaAnticipo
		upd.totalGastos =  sumaGastos
		upd.total = total
		upd.save()

	except VentasCorte.DoesNotExist:
		pass
	except GastosSucursal.DoesNotExist:
		pass
	except CorteVenta.DoesNotExist:
		pass


def updCaja(mysucursal):
	total = 0
	try:
		caja = CorteVenta.objects.filter(sucursal=mysucursal,cerrado=False)
		for x in caja:
			total = total +  x.total

	except CorteVenta.DoesNotExist:
		pass

	return total

def arqueoCaja(mysucursal):
	caja = None
	try:
		caja = CorteVenta.objects.filter(sucursal=mysucursal,cerrado=False)
	except CorteVenta.DoesNotExist:
		pass

	return caja

def listarCorte(corte):
	#manda lo de corte
	#papitas method to do process
	Cortes = CorteVenta.objects.get(folioCorteVta=corte)
	vtasCorte = VentasCorte.objects.filter(corteVenta=Cortes)
	eq = []
	ex = []
	ac = []
	fi = []
	rc = []
	pl = []
	vr = []
	an = []
	noRec = []
	nofic = []
	gastos = GastosSucursal.objects.filter(corteVenta = Cortes)
	f100 = 0
	f200 = 0
	f300 = 0
	f500 = 0
	totSumaFichas = 0
	sumRecargas = 0 #precio de vta de recarga
	nRecSinDesc = 0 #num de recarga sin descuento
	nRecDesc = 0 #num de recarga con descuento
	saldoVendido = 0 #suma de montos de saldo de recarga vendidos
	for vc in vtasCorte:
		if vc.corteVenta.id == Cortes.id:
			item = VentaEquipo.objects.filter(venta__folioVenta =vc.venta.folioVenta)
			for m in item:
				eq.append(m)

			item = VentaExpres.objects.filter(venta__folioVenta=vc.venta.folioVenta)
			for m in item:
				ex.append(m)

			item = VentaAccesorio.objects.filter(venta__folioVenta=vc.venta.folioVenta)
			for m in item:
				ac.append(m)

			item = VentaPlan.objects.filter(venta__folioVenta=vc.venta.folioVenta)
			for m in item:
				pl.append(m)

			item = Renta.objects.filter(venta__folioVenta=vc.venta.folioVenta)
			for m in item:
				vr.append(m)

			item = Anticipo.objects.filter(folioVenta__folioVenta=vc.venta.folioVenta)
			for m in item:
				an.append(m)

			item = VentaFichas.objects.filter(venta__folioVenta =vc.venta.folioVenta)
			for omi in item:
				if omi.precVenta != omi.ficha.nominacion.nominacion:
					fi.append(omi)
				totSumaFichas = totSumaFichas + omi.precVenta
				if omi.ficha.nominacion.nominacion == 100:
					f100 = f100 + 1
				elif omi.ficha.nominacion.nominacion == 200:
					f200 = f200 + 1
				elif omi.ficha.nominacion.nominacion == 300:
					f300 = f300 + 1
				elif omi.ficha.nominacion.nominacion == 500:
					f500 = f500 + 1

			item = VentaRecarga.objects.filter(venta__folioVenta =vc.venta.folioVenta)
			for omi in item:
				if omi.precVenta == omi.recarga.montos.monto:
					nRecSinDesc = nRecSinDesc + 1
				else:
					nRecDesc = nRecDesc + 1
					rc.append(omi)
				sumRecargas = sumRecargas + omi.precVenta
				saldoVendido = saldoVendido + omi.recarga.montos.monto
			
	nofic.append(f100)
	nofic.append(f200)
	nofic.append(f300)
	nofic.append(f500)
	nofic.append(totSumaFichas)
	totNRecargas = nRecDesc + nRecSinDesc
	noRec.append(nRecDesc)
	noRec.append(nRecSinDesc)
	noRec.append(totNRecargas)
	noRec.append(sumRecargas)
	noRec.append(saldoVendido)
	mivi = []
	mivi.append([Cortes,eq,ex,ac,fi,rc,pl,vr,an,nofic,noRec,gastos])
	#                0, 1, 2, 3, 4, 5, 6, 7, 8  , 9,   10  , 11
	return mivi

def vtasRecargaCorte(folio):
	suma = 0
	vc = VentasCorte.objects.filter(corteVenta__folioCorteVta=folio)
	for x in vc:
		try:
			rec = VentaRecarga.objects.filter(venta=x.venta)
			for j in rec:
				suma = suma + j.precVenta

		except VentaRecarga.DoesNotExist:
			suma = 0

	return suma

def pendientes_papeletas(suc):
	spapeleta = []
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
	return spapeleta

#------------------------- ventas acumuladas - contabilidad y gerencia/administracion
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

#---------------------Cancelaciones

def fillCancelaciones():
	vc = Venta.objects.filter(aceptada=False)
	can = None
	for x in vc:
		try:
			can = Cancelaciones.objects.get(venta=x)
		except :
			try:
				can = Cancelaciones()
				can.venta = x
				can.save()
			except :
				pass 

def back_almacenItems(tipo,item,so):
	resultAdd = ""
	aux = None
	mal = ""
	if tipo==0:
		try:
			try:
				aux=AlmacenEquipo.objects.get(estado=False,equipo=item,sucursal=so)
			except :
				mal = "El Equipo, se encuentra activo en el almacen "+str(so.nombre)
			
			if mal:
				try:
					aux=AlmacenEquipo.objects.get(estado=True,equipo=item,sucursal=so)
				except :
					mal = "El Equipo, no se encuentra activo en el almacen "+str(so.nombre)

			if aux:
				aux.estado=True
				aux.save()
			
				item.estatus=Estatus.objects.get(estatus="Existente")
				item.save()

				resultAdd = " ~ "+str(item)+" -> "+str(item.estatus)+" ~ "
			else:
				resultAdd = " ||Error ~ "+str(item)+" <- "+str(item.estatus)+" Cambiar Manualmente con Sistemas ~ "+mal
		except :
			resultAdd = " ||Error ~ "+str(item)+" <- "+str(item.estatus)+" ~ " 
			
	elif tipo==1:
		try:
			try:
				aux=AlmacenExpres.objects.get(estado=False,expres=item,sucursal=so)
			except :
				mal = "El Expres, se encuentra activo en el almacen "+str(so.nombre)
			
			if mal:
				try:
					aux=AlmacenExpres.objects.get(estado=True,expres=item,sucursal=so)
				except :
					mal = "El Expres, no se encuentra activo en el almacen "+str(so.nombre)

			if aux:
				aux.estado=True
				aux.save()
				
				item.estatus=Estatus.objects.get(estatus="Existente")
				item.save()

				resultAdd = " ~ "+str(item)+" -> "+str(item.estatus)+" ~ "
			else:
				resultAdd = " ||Error ~ "+str(item)+" <- "+str(item.estatus)+" Cambiar Manualmente con Sistemas ~ "+mal
		except :
			resultAdd = " Error ~ "+str(item)+" <- "+str(item.estatus)+" ~ " 


	elif tipo==2:
		try:
			try:
				aux=AlmacenAccesorio.objects.get(estado=False,accesorio=item,sucursal=so)
			except :
				mal = "El Accesorio, se encuentra activo en el almacen "+str(so.nombre)
			
			if mal:
				try:
					aux=AlmacenAccesorio.objects.get(estado=True,accesorio=item,sucursal=so)
				except :
					mal = "El Accesorio, no se encuentra activo en el almacen "+str(so.nombre)

			if aux:
				aux.estado=True
				aux.save()
				
				item.estatusAccesorio=EstatusAccesorio.objects.get(estatus="Existente")
				item.save()
				resultAdd = " ~ "+str(item)+" -> "+str(item.estatusAccesorio)+" ~ "
			else:
				resultAdd = " ||Error ~ "+str(item)+" <- "+str(item.estatusAccesorio)+" Cambiar Manualmente con Sistemas ~ "+mal
		except :
			resultAdd = " Error ~ "+str(item)+" <- "+str(item.estatusAccesorio)+" ~ " 
			

	elif tipo==3:
		try:
			try:
				aux=AlmacenFicha.objects.get(estado=False,ficha=item,sucursal=so)
			except :
				mal = "La ficha, se encuentra activo en el almacen "+str(so.nombre)
			if mal:
				try:
					aux=AlmacenFicha.objects.get(estado=True,ficha=item,sucursal=so)
				except :
					mal = "La ficha, no se encuentra activo en el almacen "+str(so.nombre)
			
			if aux:
				aux.estado=True
				aux.save()

				item.estatusFicha=EstatusFicha.objects.get(estatus="Existente")
				item.save()
				resultAdd = " ~ "+str(item)+" -> "+str(item.estatusFicha)+" ~ "
			else:
				resultAdd = " ||Error ~ "+str(item)+" <- "+str(item.estatusFicha)+" Cambiar Manualmente con Sistemas ~ "+mal
		except :
			resultAdd = " Error ~ "+str(item)+" <- "+str(item.estatusFicha)+" ~ " 


	elif tipo==4:
		try:
			aux=SaldoSucursal.objects.get(sucursal=so)
			aux.saldo="%.2f" % round(aux.saldo+item,2)
			aux.save()
			resultAdd = " ~ "+str(aux)+" -> "+str(item)+" ~ "
		except :
			resultAdd = " Error ~ No se agrego "+str(item) +" ~ "

	return resultAdd

	
def reembolso(venta,monto):
	try:
		r = VentasCorte.objects.get(venta=venta)
		upd = CorteVenta.objects.get(folioCorteVta=r.corteVta.folioCorteVta)
		upd.total = upd.total - monto #reembolso
		upd.save()
	except :
		pass 

	
def liberarProductos(venta):
	v = Venta.objects.get(id=venta)
	suc = Sucursal.objects.get(id= v.sucursal.id)
	resultAdd = ""
	#equipos
	try:
		ev = VentaEquipo.objects.filter(venta=v)
		for x in ev:
			try:
				meh = back_almacenItems(0,x.equipo,suc)
				resultAdd = resultAdd +" Equipo "+meh
			except :
				pass
	except :
		pass 

	#express
	try:
		ev = VentaExpres.objects.filter(venta=v)
		for x in ev:
			try:
				meh = back_almacenItems(1,x.expres,suc)
				resultAdd = resultAdd +" Expres "+meh
			except :
				pass
	except :
		pass 

	#accesorios
	try:
		ev = VentaAccesorio.objects.filter(venta=v)
		for x in ev:
			try:
				meh = back_almacenItems(2,x.accesorio,suc)
				resultAdd = resultAdd +" Accesorio x "+meh
			except :
				pass
	except :
		pass

	#fichas
	try:
		ev = VentaFichas.objects.filter(venta=v)
		for x in ev:
			try:
				meh = back_almacenItems(3,x.ficha,suc)
				resultAdd = resultAdd +" Ficha "+meh
			except :
				pass
	except :
		pass 

	#saldo
	try:
		ev = VentaRecarga.objects.filter(venta=v)
		for x in ev:
			try:
				if v.mayoreo:
					suc = Sucursal.objects.get(nombre='Almacen Central')
					meh = back_almacenItems(4,x.recarga.montos.monto,suc)
					resultAdd = resultAdd +" Recarga "+meh
				else:
					meh = back_almacenItems(4,x.recarga.montos.monto,suc)
					resultAdd = resultAdd +" Recarga "+meh
			except :
				pass
	except :
		pass

	return resultAdd

def nvofolioCliente():
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
			v = ClienteServicio.objects.get(folio=generarFolio)
			nuevo = False
		except ClienteServicio.DoesNotExist:
			nuevo = True
	#'''
	return generarFolio

#------------
def updComision(empleado,user):
	today = datetime.now()
	dateFormat = today.strftime("%Y-%m") #mes actual
	kit = 0
	tip = 0
	plan = 0 
	serv = 0

	nkit = 0
	ntip = 0
	nplan = 0 
	nserv = 0
	marlon = []
	try:
		eq = VentaEquipo.objects.filter(venta__aceptada=True,venta__fecha__icontains=dateFormat)
		for x in eq:
			try:
				brr = ActivacionEquipo.objects.get(equipo__imei=x.equipo.imei,empleado__id=empleado.id)
				tipo = brr.tipoActivacion.tipo
				if tipo == 'Tip':
					tip = tip + x.equipo.detallesEquipo.gama.comision
					ntip = ntip + 1
				elif tipo == 'Kit':
					kit = kit +  x.equipo.detallesEquipo.gama.comision
					nkit = nkit + 1

			except ActivacionEquipo.DoesNotExist:
				pass
	except VentaEquipo.DoesNotExist:
		pass

	try:
		mmm = ActivacionPlan.objects.filter(ejecutivo=empleado,fxActivacion__icontains=dateFormat)
		for x in mmm:
			plan = plan + x.plan.comision
			nplan = nplan +1
	except ActivacionPlan.DoesNotExist:
		pass

	try:
		zzz = comisionesReparacion.objects.filter(usuario=user,reparacion__fxRevision__icontains=dateFormat,reparacion__pagado=True)
		for x in zzz:
			serv = serv + x.reparacion.estado.comisionReparacion
			nserv = nserv +1

	except comisionesReparacion.DoesNotExist:
		pass

	try:
		grrr = Comision.objects.get(empleado=empleado,mes__icontains=dateFormat,pagado=False)
		grrr.comEquipoKit = kit
		grrr.comEquipoTip = tip
		grrr.comPlanes    = plan
		grrr.comServicios = serv
		grrr.save()
		marlon.append([nkit,ntip,nplan,nserv,grrr])
	
	except :
		a = Comision()
		a.empleado  = empleado
		a.comEquipoKit = kit
		a.comEquipoTip = tip
		a.comPlanes    = plan
		a.comServicios = serv
		a.mes = datetime.now().date()
		a.pagado = False
		a.save()
		marlon.append([nkit,ntip,nplan,nserv,a])
	
	return marlon
	


#-----------
def cancelaProductos(venta):
	v = Venta.objects.get(id=venta)
	suc = Sucursal.objects.get(id= v.sucursal.id)
	resultAdd = "En Cancelaciones "
	#equipos
	try:
		ev = VentaEquipo.objects.filter(venta=v)
		for x in ev:
			try:
				x.equipo.estatus=Estatus.objects.get(estatus='Cancelado x Autorizar')
				x.equipo.save()
				resultAdd = resultAdd +" Equipo "+str(x.equipo)
			except :
				pass
	except :
		pass 

	#express
	try:
		ev = VentaExpres.objects.filter(venta=v)
		for x in ev:
			try:
				x.expres.estatus=Estatus.objects.get(estatus='Cancelado x Autorizar')
				x.expres.save()
				resultAdd = resultAdd +" Expres "+str(x.expres)
			except :
				pass
	except :
		pass 

	#accesorios
	try:
		ev = VentaAccesorio.objects.filter(venta=v)
		for x in ev:
			try:
				x.accesorio.estatusAccesorio=EstatusAccesorio.objects.get(estatus='Cancelado x Autorizar')
				x.accesorio.save()
				resultAdd = resultAdd +" Accesorio "+str(x.accesorio)
			except :
				pass
	except :
		pass

	#fichas
	try:
		ev = VentaFichas.objects.filter(venta=v)
		for x in ev:
			try:
				x.ficha.estatusFicha=EstatusFicha.objects.get(estatus='Cancelado x Autorizar')
				x.ficha.save()
				resultAdd = resultAdd +" Ficha "+str(x.ficha)
			except :
				pass
	except :
		pass 

	#saldo --- no es un producto fisico por lo que no aplica

	return resultAdd

