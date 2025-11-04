from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm

@login_required
def profile_view(request):
    profile = request.user.profile
    recent_products = request.user.products.all().filter(active=True).order_by('-created_at')[:3]
    
    return render(request, "profile.html", {
        "profile": profile,
        "recent_products": recent_products,
    })

@login_required
def edit_profile(request):
    profile = request.user.profile  
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")  #Return to profile page
    else:
        form = ProfileForm(instance=profile)

    return render(request, "profile_edit.html", {"form": form})