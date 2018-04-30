from django.contrib import admin
from djCell.apps.recargas.models import Monto,Recarga,SaldoSucursal, HistorialSaldo, SaldoStock

admin.site.register(Monto)
admin.site.register(Recarga)
admin.site.register(SaldoSucursal)
admin.site.register(HistorialSaldo)
admin.site.register(SaldoStock)