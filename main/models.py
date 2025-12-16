from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import datetime
# Create your models here.
#Тренери
class Trainer(models.Model):
    firstname=models.CharField(max_length=255, verbose_name=" Ім'я тренера: ")
    lastname=models.CharField(max_length=255, verbose_name=" Прізвище тренера:")
    
    phone=models.CharField(max_length=12,unique=True,verbose_name="Телефон:")
    class Meta:
        verbose_name ="Тренер"
        verbose_name_plural ="Тренери"

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
    
#Клієнти  
class Client(models.Model):
     firstname=models.CharField(max_length=255, verbose_name=" Ім'я клієнта: ")
     lastname=models.CharField(max_length=255, verbose_name=" Прізвище клієнта:")
     phone=models.CharField(max_length=12,unique=True,verbose_name="Телефон:")
     
     trainer=models.ForeignKey( Trainer,on_delete=models.SET_NULL,null=True,blank=True,verbose_name="Тренер")
     class Meta:
         verbose_name ="Клієнт"
         verbose_name_plural ="Клієнти"
         
     def __str__(self):
         return f"{self.firstname} {self.lastname} ({self.phone})"

#Абонементи
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
  #Підтягується клієнт з табл клієнт за ід(зовн ключ)
    abonement=models.ForeignKey(Abonements,on_delete=models.PROTECT,verbose_name="Тип абонемета")
    purchase_date=models.DateField(default=timezone.now,verbose_name="Дата покупки")
    start_date=models.DateField(verbose_name="Дата початку")
    end_date=models.DateField(verbose_name="Дата закінчення")

    price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Ціна")
    visits_left=models.IntegerField(default=0,verbose_name="Залишилось візитів")
    def save(self,*args,**kwargs):
      if not self.pk:
         self.end_date=self.start_date+timezone.timedelta(days=self.abonements.duration_days)
         self.visits_left=self.abonement.visit_count
         self.price=self.abonements.price
         super().save(*args,**kwargs)
         
    @property
    def is_active(self):
        today=timezone.now().date()
        is_date_active=self.start_date <= today <= self.end_date
        has_visits=True
        if self.abonement.visit.count > 0:
            has_visits=self.visits_left > 0
        return is_date_active and has_visits
    class Meta: 
        verbose_name =" Абонемент клієнта "
        verbose_name_plural ="Всі абонементи"
    def __str__(self):
        return f"{self.client}-{self.abonement.name}"

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