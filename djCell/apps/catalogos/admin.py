from django.contrib import admin
from djCell.apps.catalogos.models import Estado, Ciudad, Colonia, CP, Zona

admin.site.register(Estado)
admin.site.register(Ciudad)
admin.site.register(Colonia)
admin.site.register(CP)
admin.site.register(Zona)