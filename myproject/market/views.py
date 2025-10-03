from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .models import Product
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
    return render(request, "market/product_form.html", {"form": form})

#Delete Product
@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == "POST":
        product.active = False
        product.save()
        return redirect("market:product_list")
    return render(request, "market/product_list.html", {"product": product})