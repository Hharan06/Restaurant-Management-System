from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.home),
    path('customer',views.login_customer),
    path('manager',views.login_manager),
    path('login_cust',views.login_customer),
    path('login_man',views.login_manager),
    path('register',views.create_account_cust),
    path('registered',views.create_account_cust),
    path('register_man',views.create_account_man),
    path('registered_man',views.create_account_man),
    path('login_success',views.login_customer),
    path('login_succ',views.login_manager),
    path('add_item',views.add_food),
    path('submit_food',views.add_food),
    path('menu',views.menu,name="menu"),
    path('show_items',views.show_items,name="items"),
    path('add_to_cart',views.add_to_cart),
    path('show_orders',views.show_orders),
    path('pay',views.confirmation),
    path('delete_order',views.delete_order),
    path('delete_orders',views.delete_order),
    path('available_item',views.available_item,name="available_items"),
    path('delete_available/<str:name>',views.delete_available),
    path('process_payment',views.confirmation),
    path('status/<int:cust_id>',views.status)
]
