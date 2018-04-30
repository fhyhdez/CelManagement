from django.contrib import admin
from djCell.apps.stocks.models import StockEquipo, StockExpres, StockAccesorio, StockFicha

admin.site.register(StockFicha)
admin.site.register(StockAccesorio)
admin.site.register(StockExpres)
admin.site.register(StockEquipo)