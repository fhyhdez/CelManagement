from django.contrib import admin
from djCell.apps.ventas.models import EstadoVenta, Venta,VentaEquipo,VentaExpres,VentaAccesorio,VentaFichas,VentaRecarga,VentaPlan,Renta, Cancelaciones, VentaMayoreo,TipoPago, Anticipo

admin.site.register(EstadoVenta)
admin.site.register(Venta)
admin.site.register(VentaEquipo)
admin.site.register(VentaExpres)
admin.site.register(VentaAccesorio)
admin.site.register(VentaFichas)
admin.site.register(VentaRecarga)
admin.site.register(VentaPlan)
admin.site.register(Renta)
admin.site.register(Cancelaciones)
admin.site.register(VentaMayoreo)
admin.site.register(TipoPago)
admin.site.register(Anticipo)