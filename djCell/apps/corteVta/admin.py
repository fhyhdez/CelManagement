from django.contrib import admin
from djCell.apps.corteVta.models import TipoGastoSucursal, GastosSucursal, CorteVenta, DiferenciasCorte, VentasCorte, RecargasVendidoCorte

admin.site.register(TipoGastoSucursal)
admin.site.register(GastosSucursal)
admin.site.register(CorteVenta)
admin.site.register(DiferenciasCorte)
admin.site.register(VentasCorte)
admin.site.register(RecargasVendidoCorte)