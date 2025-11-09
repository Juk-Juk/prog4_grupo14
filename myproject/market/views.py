from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import ProductForm
from .models import Product, Cart, CartItem
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings
import mercadopago
import environ

env = environ.Env()

def product_list(request):
    if not request.user.is_anonymous:
        products = Product.objects.filter(active=True).exclude(seller=request.user).order_by("-created_at")
    else:
        products = Product.objects.filter(active=True).order_by("-created_at")
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')

    if category_filter:
        products = products.filter(category=category_filter)

    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(brand__icontains=search_query)
        )

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = Product.CATEGORY_CHOICES

    return render(request, "product_list.html", {
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": category_filter,
        "search_query": search_query,
    })

@login_required
def my_product_list(request):
    products = Product.objects.filter(active=True, seller=request.user).order_by("-created_at")
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')

    if category_filter:
        products = products.filter(category=category_filter)

    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(brand__icontains=search_query)
        )

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = Product.CATEGORY_CHOICES

    return render(request, "my_product_list.html", {
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": category_filter,
        "search_query": search_query,
    })

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

#Add to Cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Get quantity from POST request, default to 1
    quantity = int(request.POST.get('quantity', 1))
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    # Calculate new total quantity in cart
    new_quantity = item.quantity + quantity if not item_created else quantity
    
    # Check if there's enough stock for the total quantity
    if new_quantity > product.stock:
        messages.error(request, f'Solo hay {product.stock} unidades disponibles')
        return redirect(request.META.get('HTTP_REFERER', 'market:product_list'))
    
    # Update cart item quantity
    item.quantity = new_quantity
    item.save()

    # Decrease product stock
    product.stock -= quantity
    product.save()
    
    messages.success(request, f'{quantity} producto(s) agregado(s) al carrito')
    return redirect("market:view_cart")

#Delete from Cart
@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)

    # Restore stock when removing from cart
    product.stock += cart_item.quantity
    product.active = True 
    product.save()

    cart_item.delete()
    messages.success(request, 'Producto eliminado del carrito')
    return redirect("market:view_cart")

#View Cart
@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, "shopping_cart.html", {"cart": cart})

#Update Cart
@login_required
def update_cart_quantity(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        
        action = request.POST.get('action')
        
        if action == 'increase':
            if product.stock >= 1:
                cart_item.quantity += 1
                product.stock -= 1
                cart_item.save()
                product.save()
                messages.success(request, 'Cantidad actualizada')
            else:
                messages.error(request, 'No hay mas stock disponible')
        
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                product.stock += 1
                cart_item.save()
                product.save()
                messages.success(request, 'Cantidad actualizada')
            else:
                messages.error(request, 'La cantidad mínima es 1')
    
    return redirect("market:view_cart")

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

@login_required
@require_POST
def process_cart_payment(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        api_key = env("MERCADOPAGO_ACCESS_TOKEN")
        
        if not cart_items:
            return JsonResponse({'error': 'Carrito vacío'}, status=400)
        
        # Initialize MercadoPago SDK
        sdk = mercadopago.SDK(api_key)
        
        # Prepare items for MercadoPago
        items = []
        for item in cart_items:
            items.append({
                "title": item.product.title,
                "quantity": item.quantity,
                "unit_price": float(item.product.price),
                "currency_id": "ARS",
            })
        
        # Create preference
        preference_data = {
            "items": items,
            "back_urls": {
                "success": request.build_absolute_uri("/pago-exitoso/"),
                "failure": request.build_absolute_uri("/products/cart/"),
                "pending": request.build_absolute_uri("/pago-pendiente/"),
            },
            "auto_return": "approved",
        }
        preference = sdk.preference().create(preference_data)
        return JsonResponse({
            "init_point": preference["response"]["init_point"]
        })
        
        
    except Cart.DoesNotExist:
        return JsonResponse({'error': 'Carrito no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

""" @login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    # Decrease stock for all items
    for item in cart.items.all():
        product = item.product
        product.stock -= item.quantity
        if product.stock == 0:
            product.active = False
        product.save()
    
    # Clear cart after purchase
    cart.items.all().delete()
    
    messages.success(request, '¡Compra realizada exitosamente!')
    return redirect('market:product_list') """