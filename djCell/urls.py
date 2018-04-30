from django.conf.urls import patterns, url, include
'''from django.conf.urls import patterns, include, url'''

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'djCell.views.home', name='home'),
    # url(r'^djCell/', include('djCell.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^',include('djCell.interface.home.urls')),
    url(r'^administracion/',include('djCell.interface.admingral.urls')),
    url(r'^contabilidad/',include('djCell.interface.contabilidad.urls')),
    url(r'^compras/',include('djCell.interface.compras.urls')),
    url(r'^ventas/',include('djCell.interface.ventas.urls')),
    url(r'^activaciones/',include('djCell.interface.activaciones.urls')),
    url(r'^planes/',include('djCell.interface.planes.urls')),
    url(r'^servicios/',include('djCell.interface.servicios.urls')),
    #quitar despues de poner los datos en el sistema
    url(r'^datos/',include('djCell.interface.installData.urls')),
)
