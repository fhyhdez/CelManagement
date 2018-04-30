from django.contrib import admin
from djCell.apps.almacen.models import AlmacenEquipo, AlmacenExpres, AlmacenAccesorio, AlmacenFicha

admin.site.register(AlmacenEquipo)
admin.site.register(AlmacenExpres)
admin.site.register(AlmacenAccesorio)
admin.site.register(AlmacenFicha)