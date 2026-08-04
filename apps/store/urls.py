from django.urls import path

from . import views

urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/payment/', views.payment_gateway, name='payment_gateway'),
    path('order/<int:order_id>/confirmation/', views.order_confirmation, name='order_confirmation'),
]
