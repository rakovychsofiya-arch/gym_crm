
from django.db import models
from django.contrib import admin
from trainers.models import Trainer

class Client(models.Model):
     firstname=models.CharField(max_length=255, verbose_name=" Ім'я клієнта: ")
     lastname=models.CharField(max_length=255, verbose_name=" Прізвище клієнта:")
     phone=models.CharField(max_length=12,unique=True,verbose_name="Телефон:")
     
     trainer=models.ForeignKey(Trainer ,on_delete=models.SET_NULL,null=True,blank=True,verbose_name="Тренер")
     @property
     def active_abonement(self):
        # Ми перебираємо всі абонементи цього клієнта
        # (clientabonement_set - це стандартне ім'я для зворотного зв'язку в Django)
        for abonement in self.clientabonement_set.all():
            # Використовуємо твою властивість is_active, яку ти вже написала!
            if abonement.is_active:
                return abonement
        return None
     class Meta:
         verbose_name ="Клієнт"
         verbose_name_plural ="Клієнти"
         
     def __str__(self):
         return f"{self.firstname} {self.lastname} ({self.phone})"
admin.site.register(Client)