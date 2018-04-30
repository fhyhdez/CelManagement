# -*- coding: utf-8 -*-

from djCell.apps.almacen.models import *
from djCell.apps.auditoria.models import *
from djCell.apps.ventas.models import *
from djCell.apps.productos.models import *
from djCell.apps.contabilidad.models import *
from djCell.interface.contabilidad.forms import *

from decimal import Decimal

from datetime import datetime, timedelta
import re
from django.db import transaction
from django.http import HttpResponseRedirect
from djCell.interface.contabilidad.forms import * 

#Modulos de operaciones
from djCell.operaciones import op_pagina, r_conta, repor, r_factu, r_ventas, comunes


def nuevaGuardar(fInventario, user):
	mensaje=False

	if fInventario.is_valid():
		sucursal = fInventario.cleaned_data['sucursal']
		if Inventario.objects.filter(sucursal=sucursal, terminada=False).exists():
			mensaje = 'Ya Existe una auditoria en curso para esta Sucursal %s'%(sucursal)
		else:
			try:
				with transaction.atomic():
					inv=Inventario()
					inv.folio 	= comunes.Folio(Inventario.objects.count(), 'AUD-')
					inv.sucursal 	= fInventario.cleaned_data['sucursal']
					inv.determina 	= user
					inv.observaciones 	= fInventario.cleaned_data['observaciones']
					inv.save()
			except :
				inv=None
				mensaje='Error interno, la operacion de se realizo para asegurar la integridad de los datos'

			if inv:
				#**********listas*********
				sucursal=inv.sucursal
				equipos=AlmacenEquipo.objects.filter(estado=True, sucursal=sucursal)
				for item in equipos:
					il=InvEquipo()
					il.inventario 	= inv
					il.equipo 		= item.equipo
					il.save()
				#
				accesorios=AlmacenAccesorio.objects.filter(estado=True, sucursal=sucursal)
				for item in accesorios:
					il=InvAccesorio()
					il.inventario 	= inv
					il.accesorio 	= item.accesorio
					il.save()
				#
				expres=AlmacenExpres.objects.filter(estado=True, sucursal=sucursal)
				for item in expres:
					il=InvExpres()
					il.inventario 	= inv
					il.expres 		= item.expres
					il.save()
				#
				fichas=AlmacenFicha.objects.filter(estado=True, sucursal=sucursal)
				for item in fichas:
					il=InvFicha()
					il.inventario 	= inv
					il.ficha 		= item.ficha
					il.save()
				#*************************

	return mensaje

def asignarAuditor(formAudi):
	mensaje=None
	if formAudi.is_valid():
		auditor = formAudi.cleaned_data['auditor']
		inventario = formAudi.cleaned_data['inventario']
		if InventarioAuditores.objects.filter(auditor=auditor, inventario=inventario).exists():
			mensaje='El empleado %s ya esta asignado a esta Auditoria'%(auditor)
		else:
			try:
				with transaction.atomic():
					asignacion=InventarioAuditores()
					asignacion.auditor    = auditor
					asignacion.inventario = inventario
					asignacion.save()
			except:
				mensaje='Error en la transaccion, No se realizo la asignacion.'
	else:
		mensaje='Seleccione un Empleado para asignarlo'
	return mensaje

def cancelarAuditoria(inventario, usuario):
	mensaje=None
	try:
		with transaction.atomic():
			inventario.terminada=True
			inventario.cerrado=True
			obser=inventario.observaciones
			obser=u'%s, La auditoria fue cancelada por el usuario : %s, el dia %s'%(
				obser, usuario, datetime.now())
			inventario.observaciones=obser
			inventario.save()
	except :
		mensaje='Error en la transaccion, la auditoria no fue cancelada'

	return mensaje

def cerrarAuditoria(inventario, request):
	mensaje =''
	sansion=request.POST.get('sansion','')
	observaciones=request.POST.get('observaciones','')
	desSancion=request.POST.get('sancionDes','')
	diferencia=Decimal(inventario.difEquipo)+Decimal(inventario.difExpres)+Decimal(inventario.difFicha)
	diferencia+=Decimal(inventario.difAccesorio)+Decimal(inventario.difOtros)+Decimal(inventario.difStreet)
	diferencia+=Decimal(sansion)

	empleados=VendedorSucursal.objects.filter(sucursal=inventario.sucursal, empleado__estadoEmpleado=True)
	empleadosSancionado=[]
	try:
		with transaction.atomic():
			inventario.sancion=sansion
			inventario.descSancion=desSancion

			for empleado in empleados:
				if request.POST.get('em-%s'%(empleado.empleado.id),''):
					empleadosSancionado.append(empleado.empleado)
			nEmpl=len(empleadosSancionado)
			mensaje='Total del Diferencial fue de %s, dividido entre %s empleado(s)'%(diferencia, nEmpl )
			sancionEmpleado=diferencia/nEmpl

			for empleado in empleadosSancionado:
				try:
					with transaction.atomic():
						nuevaC=CuentaEmpleado()
						nuevaC.folio 		= comunes.Folio(len(CuentaEmpleado.objects.all()),'CE')
						nuevaC.empleado 	= empleado
						nuevaC.tipoCuenta 	= TipoCuenta.objects.filter(tipo__icontains='Diferencia de inventario')[0]
						nuevaC.monto 		= Decimal(sancionEmpleado)
						nuevaC.observacion = 'Diferencial se Auditoria %s, determinado por el usuario: %s'%(
							inventario, request.user)
						nuevaC.adeudo  = Decimal(sancionEmpleado)
						nuevaC.save()
						mensaje='%s, Cuenta %s agregada al empleado %s'%(mensaje, nuevaC, empleado)
				except :
					mensaje='%s, Error al agregar cuenta al empleado %s'%(mensaje, empleado)

			obser=inventario.observaciones
			obser=u'%s, %s, La auditoria fue Cerrada por el usuario : %s, el dia %s, %s'%(
				obser, observaciones, request.user, datetime.now(), mensaje)
			inventario.observaciones=obser
			inventario.cerrado=True
			inventario.fxFinal=datetime.now()
			inventario.save()

	except :
		mensaje='Verifique los datos de Sancion Extra'
	return mensaje

def terminarAuditoria(inventario, usuario):
	mensaje=None
	if True:
		if True:
	#try:
		#with transaction.atomic():
			inventario.terminada=True
			obser=inventario.observaciones
			obser=u'%s, La auditoria fue Terminada por el usuario : %s, el dia %s'%(obser, usuario, datetime.now())
			inventario.observaciones=obser
			inventario.fxFinal=datetime.now()

			listas=InvEquipo.objects.filter(inventario=inventario, revisado=False)
			faltantes=0
			for item in listas:
				if VentaEquipo.objects.filter(equipo=item.equipo).exists():
					item.existe = True
					item.revisado = True
					item.fxRevision = datetime.now()
					item.observacion = 'Vendido mientras se auditaba'
					item.save()
				else:
					item.existe = False
					item.revisado = True
					item.fxRevision = datetime.now()
					item.save()
					faltantes=faltantes+item.equipo.detallesEquipo.precioMenudeo
					#baja Estatus,EstatusAccesorio,EstatusFicha
					eqAlm=AlmacenEquipo.objects.get(estado=True, equipo=item.equipo)
					eqAlm.estado=False
					eqAlm.save()
					estatus=Estatus.objects.get(estatus='Faltante - Auditado')
					item.equipo.estatus=estatus
					item.equipo.save()

			inventario.difEquipo="%.2f" % round(faltantes,2)

			listas=InvExpres.objects.filter(inventario=inventario, revisado=False)
			faltantes=0
			for item in listas:
				if VentaExpres.objects.filter(expres=item.expres).exists():
					item.existe = False
					item.revisado = True
					item.fxRevision = datetime.now()
					item.observacion = 'Vendido mientras se auditaba'
					item.save()
				else:
					item.existe = False
					item.revisado = True
					item.fxRevision = datetime.now()
					item.save()
					faltantes=faltantes+item.expres.detallesExpres.precioMenudeo
					#baja Estatus,EstatusAccesorio,EstatusFicha
					eqAlm=AlmacenExpres.objects.get(estado=True, expres=item.expres)
					eqAlm.estado=False
					eqAlm.save()
					estatus=Estatus.objects.get(estatus='Faltante - Auditado')
					item.expres.estatus=estatus
					item.expres.save()
			inventario.difExpres="%.2f" % round(faltantes,2)

			listas=InvAccesorio.objects.filter(inventario=inventario, revisado=False)
			faltantes=0
			for item in listas:
				if VentaAccesorio.objects.filter(accesorio=item.accesorio).exists():
					item.existe = False
					item.revisado = True
					item.fxRevision = datetime.now()
					item.observacion = 'Vendido mientras se auditaba'
					item.save()
				else:
					item.existe = False
					item.revisado = True
					item.fxRevision = datetime.now()
					item.save()
					faltantes=faltantes+item.accesorio.detallesAccesorio.precioMenudeo
					#baja Estatus,EstatusAccesorio,EstatusFicha
					eqAlm=AlmacenAccesorio.objects.get(estado=True, accesorio=item.accesorio)
					eqAlm.estado=False
					eqAlm.save()
					estatus=EstatusAccesorio.objects.get(estatus='Faltante - Auditado')
					item.accesorio.estatusAccesorio=estatus
					item.accesorio.save()
			inventario.difAccesorio="%.2f" % round(faltantes,2)

			listas=InvFicha.objects.filter(inventario=inventario, revisado=False)
			faltantes=0
			for item in listas:
				if VentaFichas.objects.filter(ficha=item.ficha).exists():
					item.existe = False
					item.revisado = True
					item.fxRevision = datetime.now()
					item.observacion = 'Vendido mientras se auditaba'
					item.save()
				else:
					item.existe = False
					item.revisado = True
					item.fxRevision = datetime.now()
					item.save()
					faltantes=faltantes+item.ficha.nominacion.nominacion
					#baja Estatus,EstatusAccesorio,EstatusFicha
					eqAlm=AlmacenFicha.objects.get(estado=True, ficha=item.ficha)
					eqAlm.estado=False
					eqAlm.save()
					estatus=EstatusFicha.objects.get(estatus='Faltante - Auditado')
					item.ficha.estatus=estatus
					item.ficha.save()
			inventario.difFicha="%.2f" % round(faltantes,2)

			inventario.fxFinal=datetime.now()
			inventario.save()

	'''except :
		mensaje='Error en la transaccion, la auditoria no fue Terminada'''

	return mensaje


def seleccionAuditor(audi_id, empleado):
	mensaje=''
	inventarios=InventarioAuditores.objects.filter(auditor=empleado, inventario__terminada=False)
	try:
		with transaction.atomic():
			for inven in inventarios:
				if '%s'%(inven.inventario.id) == '%s'%(audi_id):
					inven.turno=True
				else:
					inven.turno=False
				inven.save()

	except :
		mensaje='Error en la transaccion, no se asigno ninguna auditoria'
	return mensaje