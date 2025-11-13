from django.contrib import admin
from .models import Product
from django.contrib.auth.models import User
import random

@admin.action(description='Create 50 test products')
def create_test_products(modeladmin, request, queryset):
    categories = Product.CATEGORY_CHOICES
    
    for i in range(50):
        Product.objects.create(
            title=f'Test Product {i+1}',
            description=f'This is test product number {i+1}',
            category=random.choice(categories),
            brand='TestBrand',
            price=random.uniform(10, 10000),
            stock=random.randint(1, 15),
            seller=request.user,
            active=True
        )
    
    modeladmin.message_user(request, "Created 50 test products")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
        list_display = ("title", "seller", "brand", "price", "active", "created_at")     # columnas que ves en la lista
        search_fields = ("title", "description", "brand", "seller__username")            # campos por los que podés buscar
        list_filter = ("active", "created_at", "seller")                                 # filtros en la barra lateral
        actions = [create_test_products]