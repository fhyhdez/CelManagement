from django.db import models
from django.contrib.auth.models import User
from djCell.apps.personal.models import Empleado


class Comision(models.Model):
	empleado  	 = models.ForeignKey(Empleado)
	comEquipoKit = models.DecimalField(max_digits=10, decimal_places=2)
	comEquipoTip = models.DecimalField(max_digits=10, decimal_places=2)
	comPlanes 	 = models.DecimalField(max_digits=10, decimal_places=2)
	comServicios = models.DecimalField(max_digits=10, decimal_places=2)
	mes 		 = models.DateField()
	pagado = models.BooleanField()
	fxPago = models.DateField(null=True,blank=True)
	def __unicode__(self):
		comisiones="%s %s %s %s %s %s %s"%(self.empleado.curp, self.empleado.nombre, self.mes,self.comEquipoKit, self.comEquipoTip, self.comPlanes, self.comServicios)
		return comisiones

	class Meta:
		ordering = ['mes','empleado','pagado']