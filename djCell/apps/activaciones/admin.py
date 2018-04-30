from django.contrib import admin
from djCell.apps.activaciones.models import TipoActivacion, ActivacionEquipo, ActivacionExpress, ActivacionPlan

admin.site.register(TipoActivacion)
admin.site.register(ActivacionEquipo)
admin.site.register(ActivacionExpress)
admin.site.register(ActivacionPlan)