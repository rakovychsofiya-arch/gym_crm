"""
URL configuration for gym_admin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from attendance.views import check_in, sell, process_check_in, edit_client, pay_debt, shop_page,reports,sell_product

urlpatterns = [
    path('admin/', admin.site.urls),
    path('check_in',check_in, name='check_in_page'),
    path('process_check_in/<int:client_id>',process_check_in, name='process_check_in'),
    path('sell_membership/<int:client_id>', sell , name='sell_membership'),
    path('edit_client/<int:client_id>',edit_client, name='edit_client'),
    path('sell_product',sell_product, name='sell_product'),
    path('pay_debt/<int:sale_id>/', pay_debt, name='pay_debt'),
    path('reports', reports, name='reports_page'),
    path('shop/', shop_page, name='shop_page'),
]
