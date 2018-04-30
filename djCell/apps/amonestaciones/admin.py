from django.contrib import admin
from djCell.apps.amonestaciones.models import TipoAmonestacion, Amonestacion, Sancion

admin.site.register(TipoAmonestacion)
admin.site.register(Amonestacion)
admin.site.register(Sancion)