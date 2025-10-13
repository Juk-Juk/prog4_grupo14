from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .models import Product, Cart, CartItem
from django.contrib import messages
from django.http import JsonResponse

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
            messages.success(request, 'Producto actualizado exitosamente')
            return redirect("market:my_product_list")
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = ProductForm(instance=product)
    return render(request, "product_form.html", {"form": form, "product":product})

#Delete Product
@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == "POST":
        product.delete()
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

@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user in product.favorited_by.all():
        product.favorited_by.remove(request.user)
        is_favorited = False
        message = 'Producto eliminado de la lista de deseos'
    else:
        product.favorited_by.add(request.user)
        is_favorited = True
        message = 'Producto agregado a la lista de deseos'
    
    # If it's an AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_favorited': is_favorited, 'message': message})
    
    # Otherwise, redirect as before (for non-JS browsers)
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'market:product_list'))

@login_required
def wishlist(request):
    favorite_products = Product.objects.filter(favorited_by=request.user, active=True)
    return render(request, "wishlist.html", {"products": favorite_products})