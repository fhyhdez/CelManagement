from django.conf.urls import patterns, url, include
'''from django.conf.urls.defaults import patterns,url'''

urlpatterns=patterns('djCell.interface.activaciones.views',
	url(r'^$','index_view', name='vista_principal'),

	url(r'^equipo/buscar/$','activaciones_equipo_buscar_view', name='vista_activaciones_equipo_buscar'),
	url(r'^express/buscar/$','activaciones_express_buscar_view', name='vista_activaciones_express_buscar'),
	url(r'^reporte/$','activaciones_reporte_view', name='vista_activaciones_reporte'),
	url(r'^reportes/activados/$','activaciones_reportes_activados_view', name='vista_activaciones_reportes_activados'),
	url(r'^reportes/kit/$','activaciones_reportes_kit_view', name='vista_activaciones_reportes_kit'),
	url(r'^reportes/tip/$','activaciones_reportes_tip_view', name='vista_activaciones_reportes_tip'),
	url(r'^reportes/paq_g/$','activaciones_reportes_paq_g_view', name='vista_activaciones_reportes_paq_g'),
	url(r'^reportes/otros/$','activaciones_reportes_otros_view', name='vista_activaciones_reportes_otros'),
	url(r'^reportes/consultar/$','activaciones_reportes_consultar_view', name='vista_activaciones_reportes_consultar'),
	url(r'^reportes/activado_s_vta/$','activaciones_reportes_activado_s_vta_view', name='vista_activaciones_reportes_activado_s_vta'),
	url(r'^resultado/operacion/$','resultado_activacion_view', name='vista_resultado_activacion'),

)