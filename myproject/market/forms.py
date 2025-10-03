from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["title", "description", "brand", "price", "stock", "image"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:   # Limit to 5MB
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('El tamaño máximo de la imagen debe ser 5MB')
        return image