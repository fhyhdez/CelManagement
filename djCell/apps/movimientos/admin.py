from django.contrib import admin
from djCell.apps.movimientos.models import TipoMovimiento, Movimiento, ListaEquipo, ListaExpres, ListaAccesorio, ListaFichas, TransferenciaSaldo

admin.site.register(TipoMovimiento)
admin.site.register(Movimiento)
admin.site.register(ListaEquipo)
admin.site.register(ListaExpres)
admin.site.register(ListaAccesorio)
admin.site.register(ListaFichas)
admin.site.register(TransferenciaSaldo)
