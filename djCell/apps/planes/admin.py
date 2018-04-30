from django.contrib import admin
from djCell.apps.planes.models import EstadoSolicitud, Solicitud, TipoRelacion, Banco, Plan, DetallePlan, ServiciosPlan

admin.site.register(EstadoSolicitud)
admin.site.register(Solicitud)
admin.site.register(TipoRelacion)
admin.site.register(Banco)
admin.site.register(Plan)
admin.site.register(DetallePlan)
admin.site.register(ServiciosPlan)