from market.models import Product
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import PasswordResetView
from django.contrib import messages

def home(request):
    products = Product.objects.filter(active=True).order_by("-created_at")[:6]  # últimos 6
    return render(request, "home.html", {"products": products})

# SignUp View
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Cuenta creada exitosamente! Inicia sesión.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'account/signup.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenido, {user.username}!")
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'account/login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

# Password Reset View
def password_reset_view(request):
    return PasswordResetView.as_view(template_name='account/password_reset.html')(request)