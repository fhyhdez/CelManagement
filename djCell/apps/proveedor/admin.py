from django.contrib import admin
from djCell.apps.proveedor.models import Proveedor, FormaPago,Factura

admin.site.register(Proveedor)
admin.site.register(FormaPago)
admin.site.register(Factura)