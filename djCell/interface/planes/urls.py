from django.conf.urls import patterns, url, include
'''from django.conf.urls.defaults import patterns,url'''

urlpatterns=patterns('djCell.interface.planes.views',
	url(r'^$','index_view', name='vista_principal'),
	
	url(r'^solicitudes/todos/$','planes_solicitudes_todos_view', name='vista_planes_solicitudes_todos'),
	url(r'^solicitudes/consultar/$','planes_solicitudes_consultar_view', name='vista_planes_solicitudes_consultar'),
	url(r'^seguimiento/$','planes_seguimiento_view', name='vista_planes_seguimiento'),
	url(r'^activar/actualizar/$','planes_activar_actualizar_view', name='vista_planes_activar_actualizar'),
	url(r'^activar/consultar/$','planes_activar_consultar_view', name='vista_planes_activar_consultar'),
	url(r'^servicios/solicitudes/$','planes_servicios_solicitudes_view', name='vista_planes_servicios_solicitudes'),
	url(r'^servicios/reporte/$','planes_servicios_reporte_view', name='vista_planes_servicios_reporte'),
	url(r'^portabilidades/solicitudes/$','planes_portabilidades_solicitudes_view', name='vista_planes_portabilidades_solicitudes'),
	url(r'^portabilidades/consultar/$','planes_portabilidades_consultar_view', name='vista_planes_portabilidades_consultar'),
	url(r'^catalogo_planes/nuevo/$','planes_catalogo_planes_nuevo_view', name='vista_planes_catalogo_planes_nuevo'),
	url(r'^catalogo_planes/consultar/$','planes_catalogo_planes_consultar_view', name='vista_planes_catalogo_planes_consultar'),
	url(r'^reportes/portabilidades/$','planes_reportes_portabilidades_view', name='vista_planes_reportes_portabilidades'),
	url(r'^reportes/planes_solicitados/$','planes_reportes_planes_solicitados_view', name='vista_planes_reportes_planes_solicitados'),
	url(r'^reportes/actualizar_solicitud/$','planes_reportes_actualizar_solicitud_view', name='vista_planes_reportes_actualizar_solicitud'),
	url(r'^reportes/por_entregar/$','planes_reportes_por_entregar_view', name='vista_planes_reportes_por_entregar'),
	url(r'^sucursales/papeletas/$','planes_sucursales_papeletas_view', name='vista_planes_sucursales_papeletas'),
)