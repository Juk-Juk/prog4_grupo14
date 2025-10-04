from market.views import product_create, product_list, product_delete, my_product_list, view_cart, add_to_cart, remove_from_cart
from django.urls import path

app_name = "market"

urlpatterns = [
    path('', product_list, name="product_list"),
    path('my_products', my_product_list, name="my_product_list"),
    path("create/", product_create, name="product_create"),
    path('products/<int:pk>/delete/', product_delete, name='product_delete'),
    path("cart/", view_cart, name="view_cart"),
    path("add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path('remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
]