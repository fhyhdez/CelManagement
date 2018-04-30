from django.contrib import admin
from djCell.apps.credito.models import EstadoSubdistribuidor, EstadoCredito, Subdistribuidor, Credito, HistorialSubdistribuidor

admin.site.register(EstadoSubdistribuidor)
admin.site.register(EstadoCredito)
admin.site.register(Subdistribuidor)
admin.site.register(Credito)
admin.site.register(HistorialSubdistribuidor)