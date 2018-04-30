from django.contrib import admin
from djCell.apps.personal.models import Area, Puesto, Empleado, Permiso, Usuario

admin.site.register(Area)
admin.site.register(Puesto)
admin.site.register(Empleado)
admin.site.register(Permiso)
admin.site.register(Usuario)