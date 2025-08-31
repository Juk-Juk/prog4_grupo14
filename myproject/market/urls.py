from market.views import product_list
from django.urls import path

urlpatterns = [
    path('', product_list, name="product_list"), #market
]