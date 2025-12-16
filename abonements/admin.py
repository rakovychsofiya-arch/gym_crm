from django.contrib import admin
from .models import Abonements,ClientAbonement,Product,ProductSale
# Register your models here.

admin.site.register(Abonements)

class ClientAbonementAdmin(admin.ModelAdmin):
    list_display=('client','abonement','start_date','end_date','is_active')
    list_filter=('start_date','end_date','abonement')
    readonly_fields=('end_date','price','visits_left')
    
admin.site.register(ClientAbonement,ClientAbonementAdmin)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
       list_display=('name','price','quantity')
       search_fields=('name',)# Рядок для пошуку товару по назві
       list_editable=('price','quantity')
       
@admin.register(ProductSale)
class ProductAdminSale(admin.ModelAdmin):
    list_display=('product','client','date','amount','price','method_payment')
    list_filter=('product','date','method_payment')
    date_hierarchy='date' #Навігація по датах