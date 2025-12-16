
from django.contrib import admin
from django.db import models
from django.utils import timezone
import datetime
from clients.models import Client
from trainers.models import Trainer

class Abonements(models.Model):
    name=models.CharField(max_length=100, verbose_name="Абонемент: ")
    price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Ціна")
    duration_days=models.IntegerField(default=30,verbose_name="Тривалість абонемента:")
    visit_count=models.IntegerField(default=0,verbose_name="К-сть візитів")
    class Meta:
        verbose_name =" Тип абонемета"
        verbose_name_plural ="Тип абонементів"
        
    def __str__(self):
        return f"{self.name} ({self.price}грн)"

class ClientAbonement(models.Model):
    client = models.ForeignKey(Client,on_delete=models.CASCADE,verbose_name="Клієнт")
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Тренер")
  #Підтягується клієнт з табл клієнт за ід(зовн ключ)
    abonement=models.ForeignKey(Abonements,on_delete=models.PROTECT,verbose_name="Тип абонемета")
    purchase_date=models.DateField(default=timezone.now,verbose_name="Дата покупки")
    start_date=models.DateField(verbose_name="Дата початку")
    end_date=models.DateField(verbose_name="Дата закінчення")

    price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Ціна")
    visits_left=models.IntegerField(default=0,verbose_name="Залишилось візитів")
    types_of_payment = [
        ('cash','Готівка'),
        ('card','Карта'),
    ]
    method_payment = models.CharField(
        max_length=10,
        choices=types_of_payment,
        default='card',
        verbose_name='Спосіб оплати'
    )
    def save(self,*args,**kwargs):
      if not self.pk:
         self.end_date=self.start_date+datetime.timedelta(days=self.abonement.duration_days)
         self.visits_left=self.abonement.visit_count
         
         if not self.price:
             self.price=self.abonement.price
         
      super().save(*args,**kwargs)
         
    @property
    def is_active(self):
        today=timezone.now().date()
        is_date_active=self.start_date <= today <= self.end_date
        has_visits=True
        if self.abonement.visit_count > 0:
            has_visits=self.visits_left > 0
        return is_date_active and has_visits
    class Meta: 
        verbose_name =" Абонемент клієнта "
        verbose_name_plural ="Всі абонементи"
    def __str__(self):
        return f"{self.client}-{self.abonement.name}"
    
class Product(models.Model):
    name = models.CharField(max_length=100,verbose_name="Товар ",unique=True)
    price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Ціна")
    quantity=models.IntegerField(default=0,verbose_name='Залишок товару')
    def __str__(self):
        return f"{self.name} - {self.price}"
    class Meta: 
        verbose_name =" Товар "
        verbose_name_plural ="Кількість товару"
    
class ProductSale(models.Model):
    client = models.ForeignKey(Client,on_delete=models.CASCADE,verbose_name="Клієнт", null=True, blank=True)
    product = models.ForeignKey(Product,on_delete=models.PROTECT,verbose_name="Товар ")
    date=models.DateTimeField(verbose_name="Дата покупки: ")
    amount=models.IntegerField(default=0,verbose_name="Кількість")
    price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Ціна")
    types_of_payment=[
        ('cash','Готівка'),
        ('card','Карта'),
        ('no_paid','НЕ оплачено!')
    ]
    method_payment = models.CharField(
        max_length=10,
        choices=types_of_payment,
        default='card',
        verbose_name='Спосіб оплати'
    )
    def save(self,*args,**kwargs):
        if not self.price:
            self.price = self.product.price * self.amount
            #Списання проданого товару з складу
        if not self.pk: 
            self.product.quantity = self.product.quantity - self.amount
            self.product.save()
            
        super().save(*args,**kwargs)
                
