from django.contrib import admin
from djCell.apps.apartados.models import EstadoApartado, Apartado, HistorialApartado

admin.site.register(EstadoApartado)
admin.site.register(Apartado)
admin.site.register(HistorialApartado)
