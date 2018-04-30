from django.conf.urls import patterns, url, include
'''from django.conf.urls.defaults import patterns,url'''

urlpatterns=patterns('djCell.interface.home.views',
	url(r'^$','index_view', name='vista_principal'),
	url(r'^aunNoDeclarado$','usuario_anonimo',name= "vista_usuario_anonimo"),	
	url(r'^NoTienePermiso$','sin_permiso',name= "vista_usuario_sin_previlegio"),
	url(r'^cerrar/$', 'cerrar'),
	url(r'^humans.txt$', 'humans'),
)