from django.contrib import admin
from djCell.apps.contabilidad.models import Nomina, NominaEmpleado, TipoCuenta, CuentaEmpleado, HistorialEmpleado, Metas, Caja, Gastos,LineaCredito, HistLCredito, Cuenta, CuentaHistorial, HistorialCaja, EstadoPoliza

admin.site.register(TipoCuenta)
admin.site.register(NominaEmpleado)
admin.site.register(Nomina)
admin.site.register(CuentaEmpleado)
admin.site.register(HistorialEmpleado)
admin.site.register(Metas)
admin.site.register(Caja)
admin.site.register(HistorialCaja)
admin.site.register(Gastos)
admin.site.register(Cuenta)
admin.site.register(EstadoPoliza)
admin.site.register(CuentaHistorial)
admin.site.register(LineaCredito)
admin.site.register(HistLCredito)