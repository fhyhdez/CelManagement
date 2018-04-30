from django.contrib import admin
from djCell.apps.clientes.models import ClienteFacturacion, ClienteServicio, Mayorista

admin.site.register(ClienteServicio)
admin.site.register(ClienteFacturacion)
admin.site.register(Mayorista)