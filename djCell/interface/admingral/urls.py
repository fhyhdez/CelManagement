from django.conf.urls import patterns, url, include
from django.contrib.auth.forms import AdminPasswordChangeForm

urlpatterns=patterns('djCell.interface.admingral.views',
	url(r'^$','index_view', name='vista_principal'),

	url(r'^ventas/gerencia/reportes/$','ventas_gerencia_reportes_view', name='vista_ventas_gerencia_reportes'),
	url(r'^ventas/gerencia/eventos/$','ventas_gerencia_eventos_view', name='vista_ventas_gerencia_eventos'),
	url(r'^ventas/gerencia/amonestacion/agregar/$','ventas_gerencia_amonestacion_agregar_view', name='vista_ventas_gerencia_amonestacion_agregar'),
	url(r'^ventas/gerencia/amonestacion/consultar/$','ventas_gerencia_amonestacion_consultar_view', name='vista_ventas_gerencia_amonestacion_consultar'),
	url(r'^ventas/apartados/clientes/$','ventas_apartados_clientes_view', name='vista_ventas_apartados_clientes'),
	url(r'^ventas/apartados/historial/$','ventas_apartados_historial_view', name='vista_ventas_apartados_historial'),
	url(r'^ventas/caja_sucursales/$','ventas_caja_sucursales_view', name='vista_ventas_caja_sucursales'),
	url(r'^ventas/metas/asignar/$','ventas_metas_asignar_view', name='vista_ventas_metas_asignar'),
	url(r'^ventas/metas/consultar/$','ventas_metas_consultar_view', name='vista_ventas_metas_consultar'),

	url(r'^gerencia/sancion/agregar/$','gerencia_sancion_agregar_view', name='vista_gerencia_sancion_agregar'),
	url(r'^gerencia/sancion/consultar/$','gerencia_sancion_consultar_view', name='vista_gerencia_sancion_consultar'),


	url(r'^activaciones/reporte/$','activaciones_reporte_view', name='vista_activaciones_reporte'),

	url(r'^planes/solicitudes/todos/$','planes_solicitudes_todos_view', name='vista_planes_solicitudes_todos'),
	url(r'^planes/servicios/reportes/$','planes_servicios_reportes_view', name='vista_planes_servicios_reportes'),
	url(r'^planes/portabilidades/consultar/$','planes_portabilidades_consultar_view', name='vista_planes_portabilidades_consultar'),
	url(r'^planes/planes/nuevo/$','planes_planes_nuevo_view', name='vista_planes_planes_nuevo'),
	url(r'^planes/planes/actualizar/$','planes_planes_actualizar_view', name='vista_planes_planes_actualizar'),

	url(r'^servicios/catalogo/reporte/$','servicios_catalogo_reporte_view', name='vista_servicios_catalogo_reporte'),
	#url(r'^servicios/clientes/nuevo/$','servicios_clientes_nuevo_view', name='vista_servicios_clientes_nuevo'),
	url(r'^servicios/clientes/historial/$','servicios_clientes_historial_view', name='vista_servicios_clientes_historial'),
	url(r'^servicios/seguimiento/flexeo_porta/$','servicios_seguimiento_flexeo_porta_view', name='vista_servicios_seguimiento_flexeo_porta'),
	url(r'^servicios/seguimiento/flexeos/$','servicios_seguimiento_flexeos_view', name='vista_servicios_seguimiento_flexeos'),
	url(r'^servicios/seguimiento/reparaciones/$','servicios_seguimiento_reparaciones_view', name='vista_servicios_seguimiento_reparaciones'),
	url(r'^servicios/inventario/accesorios/$','servicios_inventario_accesorios_view', name='vista_servicios_inventario_accesorios'),
	url(r'^servicios/inventario/refacciones/$','servicios_inventario_refacciones_view', name='vista_servicios_inventario_refacciones'),
	url(r'^servicios/inventario/eqobsoletos/$','servicios_inventario_eqobsoletos_view', name='vista_servicios_inventario_eqobsoletos'),

	url(r'^departamentos/reporte/$','departamentos_reporte_view', name='vista_departamentos_reporte'),
	url(r'^sucursales/reporte/$','sucursales_reporte_view', name='vista_sucursales_reporte'),
	url(r'^sucursales/vendedores/$','sucursales_vendedores_view', name='vista_sucursales_vendedores'),
	url(r'^sucursales/papeletas/$','admin_sucursales_papeletas_view', name='vista_admin_sucursales_papeletas'),
	url(r'^admin_contab/metas/$','admin_contab_metas_view', name='vista_admin_contab_metas'),
	url(r'^admin_contab/edo_cta/$','admin_contab_edo_cta_view', name='vista_admin_contab_edo_cta'),
	url(r'^admin_contab/nomina/$','admin_contab_nomina_view', name='vista_admin_contab_nomina'),
	
	url(r'^autorizaciones/cancelaciones/$','autorizaciones_cancelaciones_view', name='vista_autorizaciones_cancelaciones'),
	url(r'^autorizaciones/papelera/$','autorizaciones_papelera_view', name='vista_autorizaciones_papelera'),
	url(r'^reportes/pro_sin_mov/$','reportes_pro_sin_mov_view', name='vista_reportes_pro_sin_mov'),

	url(r'^usuarios/agregar/$','usuarios_agregar_view', name='vista_usuarios_agregar'),
	url(r'^usuarios/actualizar/$','usuarios_actualizar_view', name='vista_usuarios_actualizar'),
	url(r'^usuarios/vendedores/$','usuarios_vendedores_view', name='vista_usuarios_vendedores'),
)