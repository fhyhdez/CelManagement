from django.conf.urls import patterns, url, include
'''from django.conf.urls.defaults import patterns,url'''

urlpatterns=patterns('djCell.interface.installData.views',
	url(r'^$','index_view', name='vista_principal'),
	url(r'^agregar/$','datos_iniciales_view', name='vista_agregar_datos'),

)