from django.urls import path
from . import views

app_name = 'receipts'

urlpatterns = [
    path('products/cart/download/', views.download_cart_receipt, name='download_cart_receipt'),
]