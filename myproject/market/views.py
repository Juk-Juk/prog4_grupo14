from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .models import Product, Cart, CartItem
from django.contrib import messages

@login_required
def product_list(request):
    products = Product.objects.filter(active=True).exclude(seller=request.user).order_by("-created_at")
    return render(request, "product_list.html", {"products": products})

@login_required
def my_product_list(request):
    products = Product.objects.filter(active=True, seller=request.user).order_by("-created_at")
    return render(request, "my_product_list.html", {"products": products})

#Create Product
@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, '¡Producto creado exitosamente!')
            return redirect("market:my_product_list")
        else:
            if 'image' in form.errors:
                messages.error(request, form.errors['image'][0])
            else:
                messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ProductForm()
    return render(request, "product_form.html", {"form": form})

#Edit Product
@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("market:product_list")
    else:
        form = ProductForm(instance=product)
    return render(request, "product_form.html", {"form": form})

#Delete Product
@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == "POST":
        product.active = False
        product.save()
        return redirect("market:my_product_list")
    return render(request, "my_product_list.html", {"product": product})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    item.quantity += 1
    item.save()
    messages.success(request, 'Producto agregado al carrito')
    return redirect("market:view_cart")

@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    cart_item.delete()
    messages.success(request, 'Producto eliminado del carrito')
    return redirect("market:view_cart")

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, "shopping_cart.html", {"cart": cart})