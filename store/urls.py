# store/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Store pages
    path('', views.store, name="store"),
    path('product/<int:pk>/', views.product_detail, name="product_detail"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    
    # Cart logic
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),

    # Authentication
    path('register/', views.register_user, name='register'),
    # store/urls.py
    path('login/', views.login_user, name='login'), 
    path('logout/', views.logout_user, name='logout'),

    # Order History
    path('order_history/', views.order_history, name='order_history'),
]