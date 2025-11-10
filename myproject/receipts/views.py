from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from market.models import Cart
from .utils import generate_cart_receipt

@login_required
def download_cart_receipt(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    # Generate PDF
    pdf = generate_cart_receipt(cart, request.user)
    
    # Create HTTP response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="carrito_{request.user.username}.pdf"'
    
    return response