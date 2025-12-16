
from django.contrib import admin
from django.db import models
from django.utils import timezone
from clients.models import Client
from abonements.models import ClientAbonement

class Attendance(models.Model):
    client = models.ForeignKey(Client,on_delete=models.CASCADE,verbose_name="Клієнт")
    check_in_time=models.DateTimeField(default=timezone.now,verbose_name="Час візиту")
     
    abonements=models.ForeignKey(ClientAbonement,on_delete=models.SET_NULL,null=True,blank=True,verbose_name="Абонемент")
    class Meta:
        verbose_name =" Відвідування "
        verbose_name_plural ="Відвідування"
        ordering=['-check_in_time']
        
    def __str__(self):
         return f"{self.client}-{self.check_in_time.strftime('%Y - %m - %d %H : %M ')}"
admin.site.register(Attendance)