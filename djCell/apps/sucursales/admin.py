from django.contrib import admin
from djCell.apps.sucursales.models import EstadoSucursal, TipoSucursal, Sucursal, VendedorSucursal

admin.site.register(EstadoSucursal)
admin.site.register(TipoSucursal)
admin.site.register(Sucursal)
admin.site.register(VendedorSucursal)