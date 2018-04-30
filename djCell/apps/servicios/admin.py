from django.contrib import admin
from djCell.apps.servicios.models import TipoReparacion, EstadoReparacion,Reparacion, EquipoReparacion, HistorialClienteReparacion,comisionesReparacion

admin.site.register(TipoReparacion)
admin.site.register(EstadoReparacion)
admin.site.register(Reparacion)
admin.site.register(EquipoReparacion)
admin.site.register(HistorialClienteReparacion)
admin.site.register(comisionesReparacion)