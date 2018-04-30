# -*- coding: utf-8 -*-
from djCell.apps.personal.models import Empleado, Usuario
from djCell.apps.sucursales.models import Sucursal, VendedorSucursal
from djCell.apps.planes.models import *
from djCell.apps.clientes.models import *
from djCell.apps.mensajes.models import EstadoMensaje, SolicitudNuevoProducto 
from django.db.models import Q
import re
from datetime import datetime, timedelta
import time
from decimal import Decimal


def cveSucursal(user):
	_usuario = Usuario.objects.get(user=user)
	myempleado 			= _usuario.empleado
	vendedorSucursal 	= VendedorSucursal.objects.get(empleado=myempleado)
	mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)

	return mysucursal.id

def cveEmpleado(user):
	_usuario = Usuario.objects.get(user=user)
	myempleado 			= _usuario.empleado
	vendedorSucursal 	= VendedorSucursal.objects.get(empleado=myempleado)

	return myempleado.id

def inuSucursal(user):
	myusuario = Usuario.objects.get(user=user)
	myempleado 			= myusuario.empleado
	vendedorSucursal 	= VendedorSucursal.objects.get(empleado=myempleado)
	mysucursal = Sucursal.objects.get(id= vendedorSucursal.sucursal.id)
	vendedor = []
	vendedor.append(myusuario.user.username)
	vendedor.append(mysucursal.nombre)

	return vendedor

def suc_permisos(nivel,user,sucursal): #troll 
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

def nuevoBanco(banco):
	n = None
	try:
		n = Banco.objects.get(banco=banco.title())
	except Banco.DoesNotExist:
		try:
			n = Banco()
			n.banco = banco.title()
			n.save()
		except :
			
			info='Lo sentimos, la información enviada no se almaceno/actualizo correctamente, por problemas de integridad de datos'
		
			#sukii #transaction.commit()#'''
	return n



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
