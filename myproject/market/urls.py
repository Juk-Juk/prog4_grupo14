from market.views import product_create, product_list
from django.urls import path

urlpatterns = [
    path('', product_list, name="product_list"),
    path("create/", product_create, name="product_create"),
]