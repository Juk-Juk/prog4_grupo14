from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.models import User
from django.contrib import messages

def home(request):
    if request.method == 'POST':
      form_type = request.POST.get('form_type')

      if form_type == 'login':
        username = request.POST.get('login')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
            return redirect('/')  # Stay on home page
      elif form_type == 'signup':
          username = request.POST.get('username')
          email = request.POST.get('email')
          password1 = request.POST.get('password1')
          password2 = request.POST.get('password2')
          
          if password1 == password2:
              try:
                  user = User.objects.create_user(username=username, email=email, password=password1)
                  messages.success(request, '¡Cuenta creada exitosamente!')
                  login(request, user)
              except:
                  messages.error(request, 'Error al crear la cuenta')
          else:
              messages.error(request, 'Las contraseñas no coinciden')
          return redirect('/')
    
    return render(request, 'home.html')

# SignUp View
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Cuenta creada exitosamente! Inicia sesión.')
            return redirect('/')
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