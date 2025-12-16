from django.shortcuts import render,redirect,get_object_or_404
from clients.models import Client
from abonements.models import Abonements, ClientAbonement, Product, ProductSale
from trainers.models import  Trainer
from attendance.models import Attendance
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from itertools import chain
from operator import attrgetter
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

@login_required(login_url='/admin/login/')
def check_in(request):
   
   product=Product.objects.all()
   
   if request.method=='POST':
      form_type = request.POST.get('form_type')
      if form_type =='add_client':
         fname=request.POST.get('firstname')
         lname=request.POST.get('lastname')
         ph=request.POST.get('phone')
         
         if fname and lname and ph:
            client, created =Client.objects.get_or_create(
            phone=ph,
            defaults = {'firstname': fname,'lastname':lname}
         )
            if created:
               messages.success(request,f"Нового клієнта {fname} {lname} додано!")
            else:
               messages.warning(request,f"Клієнт з номером {ph} вже існує!")  
         return redirect(f'/check_in?query={ph}')
   
   search_query=request.GET.get('query')
   clients_result = None
   if search_query:
      clients_result=Client.objects.filter(
         Q(phone__icontains=search_query)|
         Q(lastname__icontains=search_query) |
         Q(firstname__icontains=search_query)
      )
   return render(request, 'check_in.html',{
                    'clients':clients_result,
                    'product': product
                  })

def process_check_in(request,client_id):
   client = get_object_or_404(Client, id = client_id )
   active_abonement = client.active_abonement
   if active_abonement:
          Attendance.objects.create(
          client=client,
          check_in_time=timezone.now(),
          abonements=active_abonement
         )
          
          if active_abonement.abonement.visit_count > 0:
            if active_abonement.visits_left  > 0:
                active_abonement.visits_left = active_abonement.visits_left - 1
                active_abonement.save ()
          messages.success(request,f"Візит клієнта {client.firstname} {client.lastname} відмічено!")
   else:
          messages.warning(request,f"Візит клієнта  {client.firstname} {client.lastname} НЕ відмічено!")  
   return redirect(f'/check_in?query={client.phone}')
         

def sell(request,client_id):
   client = get_object_or_404(Client, id = client_id )
   abonements_list=Abonements.objects.all()
   trainers_list=Trainer.objects.all()
   price = None
   selected_abonement_id= None
   selected_trainer_id= None
   
   if request.method == 'POST':
      abonement_id = request.POST.get('abonement_id')
      trainer_id = request.POST.get('trainer_id')
      method_payment  = request.POST.get('method_payment')
      get_price = request.POST.get('get_price')
      
      try:
         if abonement_id:
            selected_abonement_id = int(abonement_id) 
         if trainer_id:
            selected_trainer_id = int(trainer_id) 
      except ValueError:
         pass
      
      selected_abonement=Abonements.objects.get(id = abonement_id)
      final_price=selected_abonement.price
      selected_trainer = None
      
      if trainer_id:
      
         trainer=Trainer.objects.get(id=trainer_id)
         client.trainer=trainer
         client.save()
         selected_trainer = trainer
         
         real_visits =  selected_abonement.visit_count
         visits_to_count = real_visits 
         if real_visits > 20:
               visits_to_count = 12
         if real_visits == 0:
            visits_to_count = 1
         if visits_to_count > 0 :
            trainer_cost=trainer.price * visits_to_count
            final_price = final_price + trainer_cost
            
      price = final_price
      
      if get_price == 'price':
         return render(request, 'sell.html',{
            'client':client,
            'abonements':abonements_list,
            'trainers':trainers_list,
            'price': price,
            'selected_abonement_id' : selected_abonement_id,
            'selected_trainer_id' : selected_trainer_id,
         })
      elif get_price =='sell':
         if trainer_id:
             client.trainer= selected_trainer
             client.save()
              
    
      ClientAbonement.objects.create(
         client=client,
         abonement=selected_abonement,
         trainer=selected_trainer,
         method_payment = method_payment,
         start_date = timezone.now().date(),
         price = final_price
      )
      
      return redirect(f'/check_in?query={client.phone}')
   
  
   
   return render(request, 'sell.html',{
      'client':client,
      'abonements':abonements_list,
      'trainers':trainers_list
   })
def edit_client(request,client_id):
   client = get_object_or_404(Client, id = client_id )
   if request.method == 'POST':
      new_fname=request.POST.get('firstname')
      new_lname=request.POST.get('lastname')
      new_ph=request.POST.get('phone')
   
      if  new_fname and new_lname and new_ph:
         client.firstname= new_fname
         client.lastname=new_lname
         client.phone=new_ph
         client.save()
         messages.success(request,f"Дані клієнта {client.firstname} {client.lastname} успішно оновлені!")
         return redirect(f'/check_in?query={client.phone}')
   
   return render(request, 'edit_client.html', {'client':client})
# 1. НОВА ФУНКЦІЯ: Сторінка магазину
def shop_page(request):
    products = Product.objects.all().order_by('name') # Товари по алфавіту
    clients = Client.objects.all() # Для пошуку клієнта
    
    return render(request, 'shop_page.html', {
        'products': products,
        'clients': clients
    })
def sell_product(request):
   if request.method=='POST':
      product_id = request.POST.get('product_id')
      client_id = request.POST.get('client_id')
      amount = int(request.POST.get('amount',1))
      types_of_payment=request.POST.get('method_payment')
      client = None
      if not client_id and types_of_payment == 'no_paid':
         messages.error(request,'Гість не може купляти в борг!')
         return redirect('shop_page')  
       
      product = get_object_or_404(Product, id = product_id )

      if client_id:
         client=Client.objects.get(id=client_id)
      
      ProductSale.objects.create(
         client=client,
         product=product,
         amount=amount,
         date=timezone.now(),
         method_payment=types_of_payment,
         price=product.price * amount
      )
      who = f"{client.firstname} {client.lastname}" if client else "Гостя"
      messages.success(request,f"Продано {product.name}, ({amount} шт.) для {who}")   
   return redirect('shop_page')
#  1. ДОДАЙ ЦЮ МАЛЕНЬКУ ФУНКЦІЮ (можна перед def reports)
def get_total(queryset):
    # Ця функція бере список (queryset), рахує суму і повертає 0, якщо пусто
    result = queryset.aggregate(total=Sum('price'))
    return result['total'] or 0
 
def reports(request):
    # Отримуємо дати з URL (якщо вони там є)
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    # 1. Початкові запити (поки що беремо ВСЕ)
    abonement_sales = ClientAbonement.objects.all()
    product_sales = ProductSale.objects.all()
    # 2. ФІЛЬТРАЦІЯ (Якщо обрали дати)
    if date_from:
        abonement_sales = abonement_sales.filter(purchase_date__gte=date_from)
        # Для DateTimeField використовуємо __date__gte, щоб ігнорувати час
        product_sales = product_sales.filter(date__date__gte=date_from)
    if date_to:
        abonement_sales = abonement_sales.filter(purchase_date__lte=date_to)
        product_sales = product_sales.filter(date__date__lte=date_to)
    # 3. ПІДРАХУНОК СУМ (Вже по відфільтрованих даних)
  # 1. Сума за абонементи
    sum_abonements = get_total(abonement_sales)
    # 2. Сума за товари (Реальні гроші)
    # exclude('not_paid') означає "виключити неоплачені"
    sum_products_real = get_total(product_sales.exclude(method_payment='no_paid'))
    # 3. Сума боргів
    # filter('not_paid') означає "тільки неоплачені"
    total_debt = get_total(product_sales.filter(method_payment='no_paid'))
    total_money = sum_abonements + sum_products_real
    # 4. ОБ'ЄДНАННЯ ТА СОРТУВАННЯ
    for a in abonement_sales:
        a.type = 'abonement'
        a.date_sort = a.purchase_date
    for p in product_sales:
        p.type = 'product'
        p.date_sort = p.date.date()
    combined_history = sorted(
        chain(abonement_sales, product_sales),
        key=attrgetter('date_sort'),
        reverse=True
    )
    return render(request, 'reports.html', {
        'history': combined_history,
        'total_money': total_money,
        'sum_abonements': sum_abonements,
        'sum_products': sum_products_real,
        'total_debt': total_debt,
        'date_from': date_from,
        'date_to': date_to
    })

 #НОВА ФУНКЦІЯ: ПОГАШЕННЯ БОРГУ
def pay_debt(request, sale_id):
    sale = get_object_or_404(ProductSale, id=sale_id)
    
    if request.method == 'POST':
        # Адмін вибирає, як клієнт віддає борг (готівка чи карта)
        method_payment = request.POST.get('types_of_payment')
        
        if method_payment in ['cash', 'card']:
             sale.method_payment = method_payment
             sale.save() # Просто оновлюємо статус, склад не чіпаємо!
             messages.success(request, f" Борг по чеку #{sale.id} погашено!")
            
    return redirect('reports_page')