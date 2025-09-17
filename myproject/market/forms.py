from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["title", "description", "brand", "price", "stock", "image"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }