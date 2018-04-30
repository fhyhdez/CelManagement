# -*- coding: utf-8 -*-

#metodos comunes y de utilidad para muchas aplicaciones
from djCell.apps.personal.models import *
from djCell.apps.catalogos.models import Ciudad,CP,Colonia, Estado

from datetime import datetime

def empleado(user):
	try:
		usuario=Usuario.objects.get(user=user)
	except:
		usuario=None
	if usuario:
		return usuario.empleado
	else:
		return None

def Permiso(usuario,permisos):
	logUsuario=Usuario.objects.get(user=usuario)
	logNivel=logUsuario.permiso.nivel
	permiso=-1
	for x in permisos:
		if logNivel==x:
			permiso=logNivel
	return permiso

def Folio(numero,txt):
	today = datetime.now() #fecha actual
	d = today.strftime("%d%m%Y") # fecha con formato
	if txt:
		return '%s%s%s'%(txt,numero+1,d)
	else:
		return '%s%s'%(numero+1,d)

def Folio4(numero,txt):
	numero=numero+1
	if numero<10:
		numero = '000%s'%(numero)
	elif numero < 100:
		numero = '00%s'%(numero)
	elif numero<1000:
		numero = '0%s'%(numero)
	return '%s%s'%(txt,numero)

def FechaSTR(fecha):
	if fecha:
		hora=fecha.strftime("%H:%M")
		if hora == '00:00':
			return fecha.strftime("%Y - %m - %d")
		else:
			return fecha.strftime("%Y - %m - %d %H:%M")
	else:
		return ''
def FechaMes(fecha):
	if fecha:
		return fecha.strftime("%Y - %m")
	else:
		return ''

def agregarCiudades(colonia,ciudad,estado,cp):
	c1 = None
	c2 = None
	c3 = None
	giveCatalogo = []
	try:
		if ciudad:
			c1 = Ciudad.objects.get(ciudad=ciudad.title())
	except :
		try:
			c1 = Ciudad()
			c1.estado = Estado.objects.get(id=estado)
			c1.ciudad = (ciudad).title()
			c1.save()
		except :
			pass

	try:
		if colonia:
			c2 = Colonia.objects.get(colonia=colonia.title())
	except :
		try:
			c2 = Colonia()
			c2.ciudad = Ciudad.objects.get(id=c1.id)
			c2.colonia = (colonia).title()
			c2.save()
		except :
			pass
	try:
		if cp:
			c3 = CP.objects.get(cp=cp)				
	except :
		try:
			c3 = CP()
			c3.colonia = Colonia.objects.get(id=c2.id)
			c3.cp = str(cp)
			c3.save()
		except :
			pass

	giveCatalogo.append(c2.id)#colonia
	giveCatalogo.append(c1.id)#ciudad
	if cp:
		giveCatalogo.append(c3.id)#cp

	return giveCatalogo
