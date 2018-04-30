# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from djCell.apps.activaciones.models import TipoActivacion, ActivacionEquipo, ActivacionExpress, ActivacionPlan
from djCell.apps.almacen.models import AlmacenEquipo, AlmacenExpres, AlmacenAccesorio, AlmacenFicha
from djCell.apps.apartados.models import EstadoApartado, Apartado, HistorialApartado
from djCell.apps.amonestaciones.models import TipoAmonestacion, Amonestacion
from djCell.apps.auditoria.models import ArqueoCaja
from djCell.apps.catalogos.models import Estado, Ciudad, Colonia, CP, Zona
from djCell.apps.clientes.models import ClienteFacturacion, ClienteServicio, Mayorista
from djCell.apps.comisiones.models import Comision
from djCell.apps.contabilidad.models import Nomina, TipoCuenta, CuentaEmpleado, HistorialEmpleado, Metas, Caja, Gastos,LineaCredito, HistLCredito, Cuenta, EstadoPoliza
from djCell.apps.corteVta.models import TipoGastoSucursal, GastosSucursal, CorteVenta, DiferenciasCorte
from djCell.apps.credito.models import EstadoSubdistribuidor, EstadoCredito, Subdistribuidor, Credito, HistorialSubdistribuidor
from djCell.apps.facturacion.models import Facturacion, EstadoFacturacion
from djCell.apps.garantiasuc.models import EstadoGarantia, Garantia
from djCell.apps.mensajes.models import EstadoMensaje, SolicitudNuevoProducto 
from djCell.apps.movimientos.models import TipoMovimiento, Movimiento, ListaEquipo, ListaExpres, ListaAccesorio, ListaFichas, TransferenciaSaldo
from djCell.apps.papeletas.models import TipoProducto, Papeleta
from djCell.apps.personal.models import Area, Puesto, Empleado, Permiso, Usuario
from djCell.apps.planes.models import EstadoSolicitud, Solicitud, TipoRelacion, Banco, Plan, DetallePlan, ServiciosPlan
from djCell.apps.portabilidades.models import EstadoPortabilidad, Portabilidad,FlexeoEquipo
from djCell.apps.productos.models import TiempoGarantia,Estatus,Marca,Gama,DetallesEquipo,Equipo,TipoIcc,DetallesExpres,Expres,Secciones,MarcaAccesorio,DetallesAccesorio,EstatusAccesorio,Accesorio, NominacionFicha,EstatusFicha,Ficha,  TiempoAire, HistorialPreciosEquipos,HistorialPreciosAccesorios
from djCell.apps.proveedor.models import Proveedor, FormaPago, Factura
from djCell.apps.recargas.models import Monto,Recarga,SaldoSucursal, HistorialSaldo, SaldoStock
from djCell.apps.servicios.models import TipoReparacion, EstadoReparacion,Reparacion, EquipoReparacion, HistorialClienteReparacion
from djCell.apps.stocks.models import StockEquipo, StockExpres, StockAccesorio, StockFicha
from djCell.apps.sucursales.models import EstadoSucursal, TipoSucursal, Sucursal, VendedorSucursal
from djCell.apps.ventas.models import EstadoVenta, Venta,VentaEquipo,VentaExpres,VentaAccesorio,VentaFichas,VentaRecarga,VentaPlan,Renta, Cancelaciones, VentaMayoreo,TipoPago, Anticipo



def index_view(request):
	return render_to_response('datos/index.html', {'nivel':'ninguno'},context_instance=RequestContext(request))

def datos_iniciales_view(request):
	info = ""
	if request.method == "POST":
		if not request.user.is_anonymous():
			
			#tipo de activaciones
			tact = ['Kit','Tip','Pag. G.','Otros','Express','Virgen','Plan']
			no = len(tact)
			for x in xrange(0,no):
				t = TipoActivacion()
				t.tipo = tact[x]
				t.save()
				

			#tipo amonestaciones
			tamon = ['Administrativa','Mal Servicio al cliente','Sucursal en mal estado','Equipos sin precio','Equipos sin ficha electronica','Comportamiento inapropiado','Otros']
			no = len(tamon)
			for x in xrange(0,no):
				t = TipoAmonestacion()
				t.tipo = tamon[x]
				t.save()
				

			#tipo de cuentas - contabilidad
			tctas = ['Diferencia de inventario','Financiamiento de Equipo','Prestamo Personal','Diferencia de Corte','Sancion','Diferencia en Arqueo' ]
			no = len(tctas)
			for x in xrange(0,no):
				t = TipoCuenta()
				t.tipo = tctas[x]
				t.save()
				
			#tipo gasto sucursal
			tgs = ['Comida','Papeleria','Articulos de Limpieza','Pasajes','Nomina','Pago de dia Domingo','Otros (especificar en observaciones)']
			no = len(tgs)
			for x in xrange(0,no):
				t = TipoGastoSucursal()
				t.tipo = tgs[x]
				t.save()
			
			#tipo de movimientos- movimientos prod
			tmov = ['Transferencia','Devolucion','A Bodega']
			no = len(tmov)
			for x in xrange(0,no):
				t = TipoMovimiento()
				t.tipo = tmov[x]
				t.save()
			
			#tipo products
			tprod = ['Kit','Express','Paq. G.']
			no = len(tprod)
			for x in xrange(0,no):
				t = TipoProducto()
				t.tipo = tprod[x]
				t.save()
			
			#tipo de relaciones- planes
			trel = ['Familiar','Amigo','Conocido','Vecino']
			no = len(trel)
			for x in xrange(0,no):
				t = TipoRelacion()
				t.tipo = trel[x]
				t.save()
			
			#tipo icc
			tic = ['Kit','Virgen','Expres','Paq. G.','Portabilidad']
			no = len(tic)
			for x in xrange(0,no):
				t = TipoIcc()
				t.tipoIcc = tic[x]
				t.save()

			
			#tiempos de garantia
			a = [0,3,6,12]
			no = len(a)
			for x in xrange(0,no):
				brrr = TiempoGarantia()
				brrr.dias = a[x]
				brrr.save()
			

			#detalles de express
			detExp = None
			detExp=DetallesExpres()
			detExp.descripcion='Equipo'
			detExp.tipoIcc= TipoIcc.objects.get(tipoIcc='Kit')
			detExp.tiempoGarantia= TiempoGarantia.objects.get(dias = 0)
			detExp.precioMenudeo = 0
			detExp.precioMayoreo = 0
			detExp.save()
			
			detExp=DetallesExpres()
			detExp.descripcion='Expres'
			detExp.tipoIcc= TipoIcc.objects.get(tipoIcc='Expres')
			detExp.tiempoGarantia= TiempoGarantia.objects.get(dias = 0)
			detExp.precioMenudeo = 150
			detExp.precioMayoreo = 150
			detExp.save()
			
			detExp=DetallesExpres()
			detExp.descripcion='Virgen'
			detExp.tipoIcc= TipoIcc.objects.get(tipoIcc='Virgen')
			detExp.tiempoGarantia= TiempoGarantia.objects.get(dias = 0)
			detExp.precioMenudeo = 100
			detExp.precioMayoreo = 100
			detExp.save()

			detExp=DetallesExpres()
			detExp.descripcion='Paq. G'
			detExp.tipoIcc= TipoIcc.objects.get(tipoIcc='Paq. G.')
			detExp.tiempoGarantia= TiempoGarantia.objects.get(dias = 0)
			detExp.precioMenudeo = 0
			detExp.precioMayoreo = 0
			detExp.save()

			detExp=DetallesExpres()
			detExp.descripcion='Portabilidad'
			detExp.tipoIcc= TipoIcc.objects.get(tipoIcc='Portabilidad')
			detExp.tiempoGarantia= TiempoGarantia.objects.get(dias = 0)
			detExp.precioMenudeo = 0
			detExp.precioMayoreo = 0
			detExp.save()
			
			#formas de pago - prov
			fp = ['Efectivo','Cheque','Credito','Transferencia']
			no = len(fp)
			for x in xrange(0,no):
				t = FormaPago()
				t.forma = fp[x]
				t.save()
			
			#tipo de facturas - proveedor - se borra
			
			#tipo de reparaciones- servicios
			trs = ['Flexeos','Reparacion Fisica','Carga de Software']
			no = len(trs)
			for x in xrange(0,no):
				t = TipoReparacion()
				t.tipo = trs[x]
				t.save()
			
			#tipo de sucursales
			tsuc = ['Servicios','Bodega','Almacen','Sucursal','Evento']
			no = len(tsuc)
			for x in xrange(0,no):
				t = TipoSucursal()
				t.tipo = tsuc[x]
				t.save()
			

			#tipo de pago
			tpv = ['Liquidacion de Servicio','Liquidacion de Apartado','Credito','Financiamiento','Tarjeta de credito','Efectivo']
			no = len(tpv)
			for x in xrange(0,no):
				t = TipoPago()
				t.tipo = tpv[x]
				t.save()
			

			#estados
			sts = ['AGUASCALIENTES','BAJA CALIFORNIA','BAJA CALIFORNIA SUR','CAMPECHE','CHIAPAS','CHIHUAHUA','COAHUILA','COLIMA','DISTRITO FEDERAL','DURANGO','ESTADO DE MEXICO','GUANAJUATO','GUERRERO','HIDALGO','JALISCO','MICHOACAN','MORELOS','NAYARIT','NUEVO LEON','OAXACA','PUEBLA','QUERETARO','QUINTANA ROO','SAN LUIS POTOSI','SINALOA','SONORA','TABASCO','TAMAULIPAS','TLAXCALA','VERACRUZ','YUCATAN','ZACATECAS']
			no = len(sts)
			for x in xrange(0,no):
				n = Estado()
				n.estado = sts[x]
				n.save()
			


			#estado de apartados
			sa = ['Liquidado','Abonos','Apartado','Auto-Cancelado','Cambiado por fichas']
			no = len(sa)
			for x in xrange(0,no):
				t = EstadoApartado()
				t.estado = sa[x]
				t.save()
			

			#estado de poliza
			sa = ['Confirmado','Cancelado']
			no = len(sa)
			for x in xrange(0,no):
				t = EstadoPoliza()
				t.estado = sa[x]
				t.save()
			

			#estado de creditos- credit
			sc = ['Pagado','Adeudo','Cobrar']
			no = len(sc)
			for x in xrange(0,no):
				t = EstadoCredito()
				t.estado = sc[x]
				t.save()
			

			#estado subdistribuidores - credito
			ss = ['Buen Pagador','Moratorio','Nuevo']
			no = len(ss)
			for x in xrange(0,no):
				t = EstadoSubdistribuidor()
				t.estado = ss[x]
				t.save()
			

			#estado facturaciones
			sf = ['Revisada en SAT','Sin Revisar','Cancelada']
			no = len(sf)
			for x in xrange(0,no):
				t = EstadoFacturacion()
				t.estado = sf[x]
				t.save()
			

			#estado de garantia
			sg = ['En Sucursal - Sin enviar','Enviado a Almacen','En revision - Almacen','Enviado a CAC','Listo - Por enviar a Suc.','Enviado a Sucursal','Por entregar a Cliente - Sucursal','Entregado','Cancelado','Aun en Mantenimiento']
			no = len(sg)
			for x in xrange(0,no):
				t = EstadoGarantia()
				t.estado = sg[x]
				t.save()
			

			#estado mensajes- mensajes
			sm = ['Revisado','Sin Revisar','Eliminado']
			no = len(sm)
			for x in xrange(0,no):
				t = EstadoMensaje()
				t.estado = sm[x]
				t.save()
			

			#estado solicitudes
			splan = ['En Sucursal - Sin Enviar','Enviado a Planes T.','En Tramite','Aceptado','No Aceptado','Cancelado','Activado - Sin Entregar','Enviado a Sucursal','Enviado a Cliente','Entregado']
			no = len(splan)
			for x in xrange(0,no):
				t = EstadoSolicitud()
				t.estado = splan[x]
				t.save()
			

			#estado portablidaddes
			sporta = ['En Sucursal - Sin enviar','Enviado a Mesa de Control','En Tramite - Mesa de Control','Activado por Entregar','Enviado a Sucursal','Por entregar a Cliente - Sucursal','Entregado','Cancelado']
			no = len(sporta)
			for x in xrange(0,no):
				t = EstadoPortabilidad()
				t.estado = sporta[x]
				t.save()
			
			
			#estado reparaciones
			srep = ['En Sucursal - Sin enviar','En revision - Serv. Tecnico','Listo - Por enviar/Serv.Tecnico','Enviado a Serv.Tecnico','Entregado a Cliente','Cancelado por el Cliente','Aun en Mantenimiento']
			no = len(srep)
			comi = 0
			for x in xrange(0,no):
				'''if srep[x] == 'Entregado a Cliente':
					comi = 10
				#'''
				t = EstadoReparacion()
				t.estado = srep[x]
				t.comisionReparacion = comi
				t.save()
			

			#estado de sucursales
			stsuc = ['Activa','Baja','Inactiva']
			no = len(stsuc)
			for x in xrange(0,no):
				t = EstadoSucursal()
				t.estado = stsuc[x]
				t.save()
			

			#estado de ventas
			edov = ['Pagada','Cancelada','Proceso','Autorizada']
			no = len(edov)
			for x in xrange(0,no):
				t = EstadoVenta()
				t.estado = edov[x]
				t.save()
			
			
			#estatus accesorios y estatus fichas
			sta = ['Existente','Vendido','En mal Estado','Sin Confirmar','Robado','Faltante - Auditado','Cancelado x Autorizar']
			no = len(sta)
			for x in xrange(0,no):
				t = EstatusAccesorio()
				t.estatus = sta[x]
				t.save()
				
				p = EstatusFicha()
				p.estatus = sta[x]
				p.save()
			

			#estatus expres  y Equipo
			see = ['Existente','Vendido','Liquidado' ,'Activado','Sin Confirmar','Robado','En mal estado','Faltante - Auditado','Cancelado x Autorizar']
			no = len(see)
			for x in xrange(0,no):
				t = Estatus()
				t.estatus = see[x]
				t.save()
			

			#zonas
			z = ['Tehuacan','Tlacotepec','Ajalpan']
			no = len(z)
			for x in xrange(0,no):
				n = Zona()
				n.zona = z[x]
				n.save()
			
			
			#gamma
			g = Gama()
			g.gama = 'Alta'
			g.comision = 20
			g.save()
			
			g = Gama()
			g.gama = 'Media'
			g.comision = 15
			g.save()
			
			g = Gama()
			g.gama = 'Baja'
			g.comision = 10
			g.save()

			#Marca Accesorio
			ma = ['Mobo','Moss']
			no = len(ma)
			for x in xrange(0,no):
				t = MarcaAccesorio()
				t.marca = ma[x]
				t.save()

			#Marcas
			marce = ['ALCATEL','NOKIA','LG','SAMSUNG','SONY','MOTOROLA','LANIX','HUAWUEI','ZONDA']
			no = len(marce)
			for x in xrange(0,no):
				t = Marca()
				t.marca = marce[x]
				t.save()

			#nominacion fichas
			nf = [100,200,300,500]
			no = len(nf)
			for x in xrange(0,no):
				t = NominacionFicha()
				t.nominacion = nf[x]
				t.save()

			#secciones
			secc = ['REFACCIONES','EQUIPOS OBSOLETOS', 'CARGADOR DE CASA','MANOS LIBRES GENERICOS','PLUG IN','CARGADOR DE CASA ORIGINAL','PROTECTOR DE PANTALLA','PROTECTOR DE SILICON','FUNDAS','COLGANTES','MEMORIA','MULTICARGADOR','ANTENA YAQUI AZUL']
			no = len(secc)
			for x in xrange(0,no):
				t = Secciones()
				t.seccion = secc[x]
				t.save()

			#montos
			mo = [20,30,50,100,150,200,300,500,1000,1500,2000,2500,3000,3500,4000,4500,5000]
			no = len(mo)
			for x in xrange(0,no):
				t = Monto()
				t.monto  = mo[x]
				t.save()

			#areas
			areas = ['Administracion General','Contabilidad','Compras','Ventas','Activaciones','Planes Tarifarios','Servicios','Django','Otros']
			no = len(areas)
			for x in xrange(0,no):
				t = Area()
				t.area = areas[x]
				t.save()

			#puestos
			ps = ['Administrador General','Gerente','Jefe de Distribudion','Analista de Contabilidad','Auditores','Activador Kit','Tecnico','Encargado','Vendedor','Analista de Planes','Almacenista','Adsys']
			no = len(ps)
			for x in xrange(0,no):
				t = Puesto()
				t.puesto = ps[x]
				t.save()

			

			#permisos
			n = Permiso()
			n.descripcion = 'Administrador General'
			n.nivel = 1
			n.save()
			
			n = Permiso()
			n.descripcion = 'Contador General'
			n.nivel = 2
			n.save()
			
			n = Permiso()
			n.descripcion = 'Contador Analista'
			n.nivel = 3
			n.save()
				
			n = Permiso()
			n.descripcion = 'Contador Auditor'
			n.nivel = 4
			n.save()
			
			n = Permiso()
			n.descripcion = 'Compras Gerencia'
			n.nivel = 5
			n.save()
			
			n = Permiso()
			n.descripcion = 'Jefe de Distribudion - Compras'
			n.nivel = 6
			n.save()
			
			n = Permiso()
			n.descripcion = 'Almacenista - Compras'
			n.nivel = 7
			n.save()
			
			n = Permiso()
			n.descripcion = 'Activaciones Kit'
			n.nivel = 8
			n.save()
				
			n = Permiso()
			n.descripcion = 'Planes Tarifarios'
			n.nivel = 9
			n.save()
			
			n = Permiso()
			n.descripcion = 'Tecnico General'
			n.nivel = 10
			n.save()
			
			n = Permiso()
			n.descripcion = 'Gerencia Ventas'
			n.nivel = 11
			n.save()
			
			n = Permiso()
			n.descripcion = 'Vendedores'
			n.nivel = 12
			n.save()
			
			n = Permiso()
			n.descripcion = 'Django'
			n.nivel = 0
			n.save()
			
			nwt =Ciudad()
			nwt.ciudad = 'Tehuacan'
			nwt.estado = Estado.objects.get(estado__icontains='PUEBLA')
			nwt.save()
			
			nwc = Colonia()
			nwc.colonia = 'Centro'
			nwc.ciudad = nwt
			nwc.save()
			
			ncp = CP()
			ncp.colonia = nwc
			ncp.cp = '75700'
			ncp.save()

			#proveedor
			
			p = Proveedor()
			p.rfc= 'ABCD130101KJU'
			p.nombre = 'EJEMPLO S.A. DE C.V.'
			p.direccion = 'CONOCIDA S.N.'
			p.tel = '2380000000'
			p.save()
			
			#''' comentar si no se quiere agregar empleados usuarios
			#try:
			#empleado - global
			nem = Empleado()
			nem.nombre 	= 'Fatima'
			nem.aPaterno 	= 'Hernandez'
			nem.aMaterno 	= 'Hernandez'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'HEHF870604MPLRRT08'
			nem.puesto  = Puesto.objects.get(puesto='Adsys')
			nem.area = Area.objects.get(area='Django')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()
				
			#usuario - global
			myusr = Usuario()
			myusr.user = request.user
			myusr.empleado = Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 0)
			myusr.save()

			#sucursales - almacen - global -accesos
			nsuc = Sucursal()
			nsuc.tipoSucursal = TipoSucursal.objects.get(tipo__icontains='Almacen')
			nsuc.nombre 	 = 'Almacen Central'
			nsuc.encargado 	 = Empleado.objects.get(id =1) #nem
			nsuc.noCelOfi 	 = 'sin asignar'
			nsuc.direccion 	 = 'Conocido'
			nsuc.colonia 	 = Colonia.objects.get(colonia='Centro')#nwc#nwc
			nsuc.cp 		 = CP.objects.get(cp='75700')#ncp
			nsuc.ciudad 	 = Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nsuc.zona    	 = Zona.objects.get(zona='Tehuacan')
			nsuc.estado  	 = EstadoSucursal.objects.get(estado='Activa')
			nsuc.save()
			
			#vendedor sucursal - global
			vs =VendedorSucursal()
			vs.empleado = Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(id=1)
			vs.save()
		
			#------------- usuarios de prueba
			lNewUser = User()
			lNewUser.username = 'admingral'
			lNewUser.set_password('xftgy1')
			lNewUser.save()
		
			nem = Empleado()
			nem.nombre 	= 'Aoi'
			nem.aPaterno 	= 'Hernandez'
			nem.aMaterno 	= 'Hernandez'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'HEHF870604MPLRRT09'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Administrador General')
			nem.area = Area.objects.get(area='Administracion General')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()
						
			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 1)
			myusr.save()

			#vendedor sucursal - global
			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(nem)
			vs.sucursal = Sucursal.objects.get(id=1)
			vs.save()
	
			lNewUser = User()
			lNewUser.username = 'conta01'
			lNewUser.set_password('cguvh2')
			lNewUser.save()
		
			#"""
			nem = Empleado()
			nem.nombre 	= 'ADRIANA'
			nem.aPaterno 	= 'LOPEZ'
			nem.aMaterno 	= 'CABANZO'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'LOCA580806MPYUHT98'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Gerente')
			nem.area = Area.objects.get(area__icontains='Contabilidad')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()
		
			#usuario - empleado
			myusr = Usuario()
			myusr.user =  User.objects.get(username='conta01') #lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 2)
			myusr.save()
	
			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(id=1)
			vs.save()
	
			lNewUser = User()
			lNewUser.username = 'conta02'
			lNewUser.set_password('bjink3')
			lNewUser.save()
		
			nem = Empleado()
			nem.nombre 	= 'GLORIA'
			nem.aPaterno 	= 'ANDRADE'
			nem.aMaterno 	= 'SERRANO'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'ANSG780913MPHGFD76'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Analista de Contabilidad')
			nem.area = Area.objects.get(area__icontains='Contabilidad')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()
	
			
			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 3)
			myusr.save()
	
			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(id=1)
			vs.save()
	
			lNewUser = User()
			lNewUser.username = 'auditor'
			lNewUser.set_password('nkoml4')
			lNewUser.save()

			nem = Empleado()
			nem.nombre 	= 'MARIO'
			nem.aPaterno 	= 'SALAZAR'
			nem.aMaterno 	= 'GOMEZ'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'SAGM691909HVIUJI37'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Auditores')
			nem.area = Area.objects.get(area__icontains='Contabilidad')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()
	
			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 4)
			myusr.save()

			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(id=1)
			vs.save()

			lNewUser = User()
			lNewUser.username = 'compras01'
			lNewUser.set_password('zsexd5')
			lNewUser.save()
	
			nem = Empleado()
			nem.nombre 	= 'ANA MARIA'
			nem.aPaterno 	= 'GONZALEZ'
			nem.aMaterno 	= 'SALAS'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'GOMA551123MOSGDB23'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Gerente')
			nem.area = Area.objects.get(area__icontains='Compras')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()
	
			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 5)
			myusr.save()
	
			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(id=1)
			vs.save()
	
			lNewUser = User()
			lNewUser.username = 'compras02'
			lNewUser.set_password('cgybj6')
			lNewUser.save()

			nem = Empleado()
			nem.nombre 	= 'FERNANDO'
			nem.aPaterno 	= 'SOTERO'
			nem.aMaterno 	= 'MARTINEZ'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'SOMF791214HOASDC45'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Jefe de Distribudion')
			nem.area = Area.objects.get(area__icontains='Compras')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()

			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 6)
			myusr.save()

			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(id=1)
			vs.save()

			lNewUser = User()
			lNewUser.username = 'almacenista'
			lNewUser.set_password('mjunh7')
			lNewUser.save()

			nem = Empleado()
			nem.nombre 	= 'AARON'
			nem.aPaterno 	= 'TRUJILLO'
			nem.aMaterno 	= 'SANCHEZ'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'TRSA880121HZNCBD85'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Almacenista')
			nem.area = Area.objects.get(area__icontains='Compras')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()

				
			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 7)
			myusr.save()

			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(id=1)
			vs.save()

			lNewUser = User()
			lNewUser.username = 'activador'
			lNewUser.set_password('nhybg8')
			lNewUser.save()
			
			nem = Empleado()
			nem.nombre 	= 'SANDRA'
			nem.aPaterno 	= 'SANCHEZ'
			nem.aMaterno 	= 'OJEDA'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'SAOS900210MOHJUY28'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Activador Kit')
			nem.area = Area.objects.get(area__icontains='Activaciones')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()
			
			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 8)
			myusr.save()
			

			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(id=1)
			vs.save()
			

			lNewUser = User()
			lNewUser.username = 'planes01'
			lNewUser.set_password('bhygb9')
			lNewUser.save()
			
			nem = Empleado()
			nem.nombre 	= 'BEATRIZ'
			nem.aPaterno 	= 'RAMIREZ'
			nem.aMaterno 	= 'RAMIREZ'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'RARB580325MGFDSE76'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Gerente')
			nem.area = Area.objects.get(area__icontains='Planes Tarifarios')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()
				
			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 9)
			myusr.save()

			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(id=1)
			vs.save()

			lNewUser = User()
			lNewUser.username = 'planes02'
			lNewUser.set_password('bgtvf10')
			lNewUser.save()

			nem = Empleado()
			nem.nombre 	= 'SOFIA'
			nem.aPaterno 	= 'SUAREZ'
			nem.aMaterno 	= 'MARCIAL'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'SUMS790328MAWSQD99'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Analista de Planes')
			nem.area = Area.objects.get(area__icontains='Planes Tarifarios')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()
				
			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 9)
			myusr.save()
			
			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(id=1)
			vs.save()

			lNewUser = User()
			lNewUser.username = 'tecnico'
			lNewUser.set_password('cdexs11')
			lNewUser.save()

			nem = Empleado()
			nem.nombre 	= 'ALBERTO'
			nem.aPaterno 	= 'ARIAS'
			nem.aMaterno 	= 'DURAN'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'ARDA800417HMNVHJ87'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Tecnico')
			nem.area = Area.objects.get(area__icontains='Servicios')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()
				
			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 10)
			myusr.save()

			vs =VendedorSucursal()
			vs.empleado = myusr.empleado #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(id=1)
			vs.save()

			lNewUser = User()
			lNewUser.username = 'gerente-vtas'
			lNewUser.set_password('xwwza12')
			lNewUser.save()

			nem = Empleado()
			nem.nombre 	= 'LUIS'
			nem.aPaterno 	= 'BARRIO'
			nem.aMaterno 	= 'MONTES'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'BAML810529HYTGHR01'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Gerente')
			nem.area = Area.objects.get(area__icontains='Ventas')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()


			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 11)
			
			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(id=1)
			vs.save()

			nem1 = Empleado()
			nem1.nombre 	= 'RAQUEL'
			nem1.aPaterno 	= 'MENDOZA'
			nem1.aMaterno 	= 'SANCHEZ'
			nem1.direccion 	= 'Conocido S.N.'
			nem1.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem1.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem1.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem1.telefono 	= 'Sin asignar'
			nem1.fxNacimiento 	= '2013-02-11'
			nem1.curp 	= 'MESR781122MASDEW49'
			nem1.puesto  = Puesto.objects.get(puesto__icontains='Encargado')
			nem1.area = Area.objects.get(area__icontains='Ventas')
			nem1.salarioxDia 	= 0
			nem1.estadoEmpleado 	= True
			nem1.save()
				
				
			#otra sucursal
			nsuc1 = Sucursal()
			nsuc1.tipoSucursal = TipoSucursal.objects.get(tipo__icontains='Sucursal')
			nsuc1.nombre 	 = '1 Oriente'
			nsuc1.encargado  = Empleado.objects.get(curp ='MESR781122MASDEW49') #nem
			nsuc1.noCelOfi 	 = 'sin asignar'
			nsuc1.direccion 	 = 'Conocido'
			nsuc1.colonia 	 = Colonia.objects.get(colonia='Centro')#nwc#nwc
			nsuc1.cp 		 = CP.objects.get(cp='75700')#ncp
			nsuc1.ciudad 	 = Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nsuc1.zona    	 = Zona.objects.get(zona='Tehuacan')
			nsuc1.estado  	 = EstadoSucursal.objects.get(estado='Activa')
			nsuc1.save()

			lNewUser = User()
			lNewUser.username = 'vendedor01'
			lNewUser.set_password('lokij13')
			lNewUser.save()

			nem = Empleado()
			nem.nombre 	= 'ALEJANDRO'
			nem.aPaterno 	= 'CORTINEZ'
			nem.aMaterno 	= 'FLORES'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'COFA760730HHJUDH02'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Encargado')
			nem.area = Area.objects.get(area__icontains='Ventas')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()
				
			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 12)
			myusr.save()

			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(nombre__icontains='1 Oriente')
			vs.save()

			lNewUser = User()
			lNewUser.username = 'vendedor02'
			lNewUser.set_password('mjunh14')
			lNewUser.save()

			nem = Empleado()
			nem.nombre 	= 'ALISON'
			nem.aPaterno 	= 'CARBAJAL'
			nem.aMaterno 	= 'SANCHEZ'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'CASA771007MDUIRH09'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Encargado')
			nem.area = Area.objects.get(area__icontains='Ventas')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()
				
			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 12)
			myusr.save()

			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(nombre__icontains='1 Oriente')
			vs.save()

			lNewUser = User()
			lNewUser.username = 'vendedor03'
			lNewUser.set_password('nhybg15')
			lNewUser.save()

				
			#usuario - empleado ..........
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = Empleado.objects.get(curp = 'MESR781122MASDEW49')
			myusr.permiso = Permiso.objects.get(nivel = 12)
			myusr.save()

			vs =VendedorSucursal()
			vs.empleado = Empleado.objects.get(curp = 'MESR781122MASDEW49')
			vs.sucursal = Sucursal.objects.get(nombre__icontains='1 Oriente')
			vs.save()

			lNewUser = User()
			lNewUser.username = 'vendedor04'
			lNewUser.set_password('tgbfv16')
			lNewUser.save()

			nem = Empleado()
			nem.nombre 	= 'MELISA'
			nem.aPaterno 	= 'TOBON'
			nem.aMaterno 	= 'LUNA'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'TOLM821009MHLADO01'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Vendedor')
			nem.area = Area.objects.get(area__icontains='Ventas')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()
				
			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 12)
			myusr.save()

			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(nombre__icontains='1 Oriente')
			vs.save()

			lNewUser = User()
			lNewUser.username = 'vendedor05'
			lNewUser.set_password('rfvdc17')
			lNewUser.save()

			nem = Empleado()
			nem.nombre 	= 'ROSARIO'
			nem.aPaterno 	= 'PINEDA'
			nem.aMaterno 	= 'ESQUIVEZ'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'PIER840211MPIEZS02'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Vendedor')
			nem.area = Area.objects.get(area__icontains='Ventas')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()
				
			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 12)
			myusr.save()

			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(nombre__icontains='1 Oriente')
			vs.save()

			lNewUser = User()
			lNewUser.username = 'vendedor06'
			lNewUser.set_password('edcws18')
			lNewUser.save()

			nem = Empleado()
			nem.nombre 	= 'MAURO'
			nem.aPaterno 	= 'CORDOBA'
			nem.aMaterno 	= 'PIÑEDA'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'COPM890419HCDOCH01'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Vendedor')
			nem.area = Area.objects.get(area__icontains='Ventas')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()
				
			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 12)
			myusr.save()

			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(nombre__icontains='1 Oriente')
			vs.save()

			lNewUser = User()
			lNewUser.username = 'vendedor07'
			lNewUser.set_password('wsxqa19')
			lNewUser.save()

			nem = Empleado()
			nem.nombre 	= 'TERESA'
			nem.aPaterno 	= 'AGUILAR'
			nem.aMaterno 	= 'SUAREZ'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'AGST901118MOSGAR15'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Vendedor')
			nem.area = Area.objects.get(area__icontains='Ventas')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()
				
			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 12)
			myusr.save()

			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(nombre__icontains='1 Oriente')
			vs.save()

			lNewUser = User()
			lNewUser.username = 'vendedor08'
			lNewUser.set_password('qazws20')
			lNewUser.save()

			nem = Empleado()
			nem.nombre 	= 'GUILLERMINA'
			nem.aPaterno 	= 'FLORES'
			nem.aMaterno 	= 'AGUIRRE'
			nem.direccion 	= 'Conocido S.N.'
			nem.colonia 	= Colonia.objects.get(colonia='Centro')#nwc
			nem.ciudad  	= Ciudad.objects.get(ciudad='Tehuacan') #nwt
			nem.estado   	= Estado.objects.get(estado__icontains='PUEBLA')
			nem.telefono 	= 'Sin asignar'
			nem.fxNacimiento 	= '2013-02-11'
			nem.curp 	= 'FLAG910712MBJSUD02'
			nem.puesto  = Puesto.objects.get(puesto__icontains='Vendedor')
			nem.area = Area.objects.get(area__icontains='Ventas')
			nem.salarioxDia 	= 0
			nem.estadoEmpleado 	= True
			nem.save()
				
			#usuario - empleado
			myusr = Usuario()
			myusr.user = lNewUser
			myusr.empleado = nem #Empleado.objects.get(id = 1)#nem
			myusr.permiso = Permiso.objects.get(nivel = 12)
			myusr.save()

			vs =VendedorSucursal()
			vs.empleado = nem #Empleado.objects.get(id=1)
			vs.sucursal = Sucursal.objects.get(nombre__icontains='1 Oriente')
			vs.save()
			#except :
			#	pass
		
			#'''
			info = info + "Se genero correctamente"
		else:
			info = 'No se ha logueado'

		

	ctx = {'info':info}
	return render_to_response('datos/agregar.html', ctx ,context_instance=RequestContext(request))