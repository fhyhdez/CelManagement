# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from djCell.apps.personal.models import Usuario

def permiso(usuario,permisos):
	logUsuario=Usuario.objects.get(user=usuario)
	logNivel=logUsuario.permiso.nivel
	permiso=-1
	for x in permisos:
		if logNivel==x:
			permiso=logNivel
	return permiso

def permiso(usuario):
	logUsuario=Usuario.objects.get(user=usuario)
	return logUsuario.permiso.nivel

def usuario_anonimo(request):
	return render_to_response('home/usuario_anonimo.html',{'informacion':'aun_no_declarado'},context_instance=RequestContext(request))

@login_required(login_url='/')
def sin_permiso(request):
	return render_to_response('home/sinpermiso.html',{'informacion':'sin_previlegios'},context_instance=RequestContext(request))

def index_view(request):
	
	if not request.user.is_anonymous():
		
		try:
			usuario=Usuario.objects.get(user=request.user)
			permiso=usuario.permiso.nivel
			if permiso==0:
				return HttpResponseRedirect('/admin')
			elif permiso==1:
				return HttpResponseRedirect('/administracion')
			elif permiso==2 or permiso==3 or permiso==4:
				return HttpResponseRedirect('/contabilidad')
			elif permiso==5 or permiso==6 or permiso==7:
				return HttpResponseRedirect('/compras')
			elif permiso==8:
				return HttpResponseRedirect('/activaciones')
			elif permiso==9:
				return HttpResponseRedirect('/planes')
			elif permiso==10:
				return HttpResponseRedirect('/servicios')
			elif permiso==11 or permiso==12:
				return HttpResponseRedirect('/ventas')
			else:
				return HttpResponseRedirect('/aunNoDeclarado')
		
		except Usuario.DoesNotExist:

			return render_to_response('home/nousuario.html', context_instance=RequestContext(request))
				
	if request.method=='POST':
		formulario=AuthenticationForm(request.POST)
		
		if formulario.is_valid:
			
			usuario=request.POST['username']
			clave=request.POST['password']
			
			acceso=authenticate(username=usuario,password=clave)
			
			if acceso is not None:
				if acceso.is_active:
					login(request,acceso)
					try:
						usuario=Usuario.objects.get(user=request.user)
						permiso=usuario.permiso.nivel
						if permiso==0:
							return HttpResponseRedirect('/admin')
						elif permiso==1:
							return HttpResponseRedirect('/administracion')
						elif permiso==2 or permiso==3 or permiso==4:
							return HttpResponseRedirect('/contabilidad')
						elif permiso==5 or permiso==6 or permiso==7:
							return HttpResponseRedirect('/compras')
						elif permiso==8:
							return HttpResponseRedirect('/activaciones')
						elif permiso==9:
							return HttpResponseRedirect('/planes')
						elif permiso==10:
							return HttpResponseRedirect('/servicios')
						elif permiso==11 or permiso==12:
							return HttpResponseRedirect('/ventas')
						else:
							return HttpResponseRedirect('/aunNoDeclarado')
					
					except Usuario.DoesNotExist:
						return render_to_response('home/nousuario.html', context_instance=RequestContext(request))
				else:
					return render_to_response('home/noactivo.html', context_instance=RequestContext(request))
			else:
				return render_to_response('home/nousuario.html', context_instance=RequestContext(request))
		else:
			return render_to_response('home/nousuario.html', context_instance=RequestContext(request))

	else:
		formulario=AuthenticationForm()

	return render_to_response('home/index.html',{'formulario':formulario},context_instance=RequestContext(request))

@login_required(login_url='/')
def cerrar(request):
	logout(request)
	return HttpResponseRedirect('/')

@login_required(login_url='/')
def humans(request):

	return render_to_response('home/humans2.txt',{'hola':"personas"},context_instance=RequestContext(request))