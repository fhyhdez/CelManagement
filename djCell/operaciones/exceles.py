# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect,HttpResponse
import xlwt
from datetime import datetime, timedelta, date
import time
def estiloTitulo():
	font = xlwt.Font() # Create the Font 
	font.bold = True 
	font.underline = True 
	
	style = xlwt.XFStyle() # Create the Style 
	style.font = font # Apply the Font to the Style 
	return style

def estiloContenido():
	font = xlwt.Font() # Create the Font 
	font.bold = True 

	borders = xlwt.Borders() # Create Borders 
	borders.top = xlwt.Borders.DASHED 
	borders.bottom = xlwt.Borders.DOUBLE 
	borders.left = xlwt.Borders.HAIR 
	
	alignment = xlwt.Alignment() # Create Alignment 
	alignment.vert = xlwt.Alignment.WRAP_AT_RIGHT
	
	style = xlwt.XFStyle() # Create Style 
	style.borders = borders # Add Borders to Style 
	style.font = font
	style.alignment = alignment # Add Alignment to Style

	return style

def libro(archivo, nlib, titulo, encabezados, titulos, contenido):
	libro=archivo.add_sheet(nlib)

	libro.write(0, 0, titulo, estiloTitulo())#titulo 
	if encabezados:
		c=0
		for dato in encabezados:
			libro.write(2, c, dato,estiloTitulo())#Datos extras
			c+=1

	c=0
	for t in titulos:
		libro.write(4, c, t, estiloContenido())#Datos estras
		c+=1

	y=5
	for linea in contenido:
		x=0
		for dato in linea:
			libro.write(y, x, str(dato).encode('utf-8'))
			x+=1
		y+=1
	return archivo

def exportCompras(query,eqGral,acGral,eqSuc,acSuc,nombre):
	wb = xlwt.Workbook(encoding = 'utf-8')
	if eqGral:
		wb = libro(wb, 'eq_Gral', query, [], ['Demanda','Equipo'], eqGral)

	if eqSuc:
		wb = libro(wb, 'eq_Suc', query, [], ['Demanda','Equipo','Sucursal'], eqSuc)

	if acGral:
		wb = libro(wb, 'ac_Gral', query, [], ['Demanda','Accesorio'], acGral)

	if acSuc:
		wb = libro(wb, 'ac_Suc', query, [], ['Demanda','Accesorio','Sucursal'], acSuc)

	filename = "GeneracionComprasVentas%s_%s.xls" % (datetime.now().date(),nombre)
	response = HttpResponse(mimetype='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename='+filename
	wb.save(response)
	return response

#elmo no se que sean???, preguntar a fatima, paresen los encabezados
# parese que quiere todos los datos en una misma hoja
#por el nombre de los datos, supongo que es 'l'  de libro, no estoy seguro, preguntar a fatima
def mismoLibro(libro, fila, titulos, contenido):
	c=0
	for t in titulos:
		libro.write(fila, c, t, estiloContenido())#Datos estras
		c+=1
	y=1
	for linea in contenido:
		x=0
		for dato in linea:
			libro.write(fila+y, x, str(dato).encode('utf-8'))
			x+=1
		y+=1

	return libro
def exportMovimiento(folio,query,elmo,l1,l2,l3,l4,l5):
	wb = xlwt.Workbook(encoding = 'utf-8')
	ws0 = wb.add_sheet(folio)
	ws0.write(0, 0,query,estiloTitulo())
	#encabezado
	col = 0
	for x in elmo:
		ws0.write(2, col, x, estiloTitulo())
		col = col + 1
	row = 4
	no = len(l1)
	no2 = len(l2)
	no3 = len(l3)
	no4 = len(l4)
	no5 = len(l5)
	#lista de equipos
	if l1:
		pass
	#lista de expres
	if l2:
		col = 0
		row = row + no + 3
		header = ['ICC','No.Asignado']
		nCol = len(header)
		for x in header:
			ws0.write(row, col, x, estiloContenido())
			col = col + 1
		row = row + 2
		for i in range(no2):
			col = 0
			for j in range(nCol):
				item = str(l2[i][j]).encode('utf-8')
				ws0.write(row, col,item )
				col = col + 1
			row = row + 1
	#lista de accesorios
	if l3:
		col = 0
		row = row + no2 + 3
		header = ['Codigo','Accesorio']
		nCol = len(header)
		for x in header:
			ws0.write(row, col, x,estiloContenido())
			col = col + 1
		row = row + 2
		for i in range(no3):
			col = 0
			for j in range(nCol):
				item = str(l3[i][j]).encode('utf-8')
				ws0.write(row, col,item )
				col = col + 1
			row = row + 1
	#list de fichas
	if l4:
		col = 0
		row = row + no3 + 3
		header = ['Nominacion','Ficha']
		nCol = len(header)
		for x in header:
			ws0.write(row, col, x, estiloContenido())
			col = col + 1
		row = row + 2
		for i in range(no4):
			col = 0
			for j in range(nCol):
				item = str(l4[i][j]).encode('utf-8')
				ws0.write(row, col,item )
				col = col + 1
			row = row + 1
	#saldo
	if l5:
		col = 0
		row = row + no4 + 3
		header = ['Saldo Transferido']
		nCol = len(header)
		for x in header:
			ws0.write(row, col, x, estiloContenido())
			col = col + 1
		row = row + 2
		for i in range(no5):
			col = 0
			for j in range(nCol):
				item = str(l5[i][j]).encode('utf-8')
				ws0.write(row, col,item )
				col = col + 1
			row = row + 1

	filename = "Movimiento%s_%s.xls" % (folio,datetime.now().date())
	response = HttpResponse(mimetype='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename='+filename
	wb.save(response)
	return response

def export_To_Excel_ActivacionG(query,result,result2,nombre): # para activaciones
	wb = xlwt.Workbook(encoding = 'utf-8')
	header = ['Sucursal','Tipo Activacion','Equipo','IMEI','ICC','No Asignado','Curp','Fecha']
	header2 = ['Sucursal','Tipo Activacion','Express ICC','No Asignado','Curp','Fecha']
	
	if result:
		ws0 = wb.add_sheet('Rep_Equipos')
		ws0.write(0, 0,query,estiloTitulo())
		col = 0
		no = len(result)
		for x in header:
			ws0.write(2, col, x,estiloContenido())
			col = col + 1
		row = 3
		for i in range(no):
			col = 0
			for j in range(7):
				item = str(result[i][col]).encode('utf-8')
				ws0.write(row, col,item )
				col = col + 1
			row = row + 1
	if result2:
		ws1 = wb.add_sheet('Rep_Express')
		ws1.write(0, 0,query,estiloTitulo())
		no2 = len(result2)
		col = 0
		for x in header2:
			ws1.write(2, col, x,estiloContenido())
			col = col + 1
		row = 3
		for i in range(no2):
			col = 0
			for j in range(5):
				item = str(result2[i][col]).encode('utf-8')
				ws1.write(row, col,item )
				col = col + 1
			row = row + 1
	filename = "ActivacionesReporte%s_%s.xls" % (datetime.now().date(),nombre)
	response = HttpResponse(mimetype='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename='+filename
	wb.save(response)
	return response
	

def exportPapeletas(query,result,header):
	wb = xlwt.Workbook(encoding = 'utf-8')
	ws0 = wb.add_sheet('papeletas')
	ws0.write(0, 0,query,estiloTitulo())
	nCol = len(header)
	col = 0
	no = len(result)
	for x in header:
		ws0.write(2, col, x,estiloContenido())
		col = col + 1
	row = 3
	for i in range(no):
		col = 0
		for j in range(nCol):
			item = result[i][j].encode('utf-8')
			ws0.write(row, col,item )
			col = col + 1
		row = row + 1
	
	filename = "reportePapeletas_%s.xls" % (datetime.now().date())
	response = HttpResponse(mimetype='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename='+filename
	wb.save(response)
	return response

def export_To_Excel_Planes(query,header, result):
	wb = xlwt.Workbook(encoding = 'utf-8')
	if result:
		ws0 = wb.add_sheet('Rep_Planes')
		ws0.write(0, 0,query,estiloTitulo())
		col = 0
		no = len(result)
		nCol = len(header)
		for x in header:
			ws0.write(2, col, x,estiloContenido())
			col = col + 1
		row = 3
		for i in range(no):
			col = 0
			for j in range(nCol):
				item = str(result[i][j]).encode('utf-8')
				ws0.write(row, col,item )
				col = col + 1
			row = row + 1
	
	filename = "ActivacionReporte%s_%s.xls" % (datetime.now().date(),'Plan')
	response = HttpResponse(mimetype='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename='+filename
	wb.save(response)
	return response


def exportarNomina(folio,header,takoyaky):
	wb = xlwt.Workbook(encoding = 'utf-8')
	ws0 = wb.add_sheet('nomina')
	ws0.write(0, 0,'Nomina'+' '+folio)
	#encabezado
	col = 0
	row = 3
	no = len(takoyaky)
	#empleados en nomina
	if takoyaky:
		col = 0
		nCol = len(header)
		for x in header:
			ws0.write(row, col, x, estiloTitulo())
			col = col + 1
		row = row + 2
		for i in range(no):
			col = 0
			for j in range(nCol):
				item = (takoyaky[i][j])#.encode('utf-8')
				ws0.write(row, col,item )
				col = col + 1
			row = row + 1
	
	filename = "Nomina%s_%s.xls" % (folio,datetime.now().date())
	response = HttpResponse(mimetype='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename='+filename
	wb.save(response)
	return response


def exportInventario(l1,l2,l3,l4,sucursal):
	wb = xlwt.Workbook(encoding = 'utf-8')
	no = len(l1)
	no2 = len(l2)
	no3 = len(l3)
	no4 = len(l4)
	#lista de equipos
	if l1:
		ws0 = wb.add_sheet('Equipos')
		ws0.write(0, 0,'Equipos Existentes al Momento en Sucursal')
		col = 0
		row = 2
		header = ['Equipo','IMEI','ICC','No.Asignado','Accesorio','Observaciones']
		nCol = len(header)
		for x in header:
			ws0.write(row, col, x)
			col = col + 1
		row = row + 2
		for i in range(no):
			col = 0
			for j in range(nCol):
				item = str(l1[i][j]).encode('utf-8')
				ws0.write(row, col,item )
				col = col + 1
			row = row + 1
	#lista de expres
	if l2:
		ws1 = wb.add_sheet('Expres')
		ws1.write(0, 0,'Expres Existentes al Momento en Sucursal')
		col = 0
		row = 2
		header = ['ICC','No.Asignado','Observaciones']
		nCol = len(header)
		for x in header:
			ws1.write(row, col, x)
			col = col + 1
		row = row + 2
		for i in range(no2):
			col = 0
			for j in range(nCol):
				item = str(l2[i][j]).encode('utf-8')
				ws1.write(row, col,item )
				col = col + 1
			row = row + 1
	#lista de accesorios
	if l3:
		ws2 = wb.add_sheet('Accesorios')
		ws2.write(0, 0,'Accesorios Existentes al Momento en Sucursal')
		col = 0
		row = 2
		header = ['Codigo','Accesorio','Observaciones']
		nCol = len(header)
		for x in header:
			ws2.write(row, col, x)
			col = col + 1
		row = row + 2
		for i in range(no3):
			col = 0
			for j in range(nCol):
				item = str(l3[i][j]).encode('utf-8')
				ws2.write(row, col,item )
				col = col + 1
			row = row + 1
	#list de fichas
	if l4:
		ws3 = wb.add_sheet('Fichas')
		ws3.write(0, 0,'Fichas Existentes al Momento en Sucursal')
		col = 0
		row = 2
		header = ['Nominacion','Ficha','Observaciones']
		nCol = len(header)
		for x in header:
			ws3.write(row, col, x)
			col = col + 1
		row = row + 2
		for i in range(no4):
			col = 0
			for j in range(nCol):
				item = str(l4[i][j]).encode('utf-8')
				ws3.write(row, col,item )
				col = col + 1
			row = row + 1

	filename = "Invetario%s_%s.xls" % (datetime.now().date(),sucursal)
	response = HttpResponse(mimetype='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename='+filename
	wb.save(response)
	return response
	