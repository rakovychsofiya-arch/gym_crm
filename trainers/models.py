
from django.db import models
from django.contrib import admin

class Trainer(models.Model):
    firstname=models.CharField(max_length=255, verbose_name=" Ім'я тренера: ")
    lastname=models.CharField(max_length=255, verbose_name=" Прізвище тренера:")
    phone=models.CharField(max_length=12,unique=True,verbose_name="Телефон:")
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Ціна за 1 тренування'
    )
    
    class Meta:
        verbose_name ="Тренер"
        verbose_name_plural ="Тренери"

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
admin.site.register(Trainer)