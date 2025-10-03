from market.views import product_create, product_list, product_delete, my_product_list
from django.urls import path

app_name = "market"

urlpatterns = [
    path('', product_list, name="product_list"),
    path('my_products', my_product_list, name="my_product_list"),
    path("create/", product_create, name="product_create"),
    path('products/<int:pk>/delete/', product_delete, name='product_delete'),
]