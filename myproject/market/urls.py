from market import views
from django.urls import path

app_name = "market"

urlpatterns = [
    path('', views.product_list, name="product_list"),
    path('my_products', views.my_product_list, name="my_product_list"),
    path("create/", views.product_create, name="product_create"),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path("cart/", views.view_cart, name="view_cart"),
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('products/<int:product_id>/wishlist/', views.toggle_favorite, name='toggle_favorite'),
    path('cart/update/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('wishlist/', views.wishlist, name='wishlist'),
]