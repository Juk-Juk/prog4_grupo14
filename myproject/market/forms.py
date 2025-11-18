from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'brand', 'category', 'stock', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Título',
            'description': 'Descripción',
            'price': 'Precio',
            'brand': 'Marca',
            'category': 'Categoría',
            'stock': 'Stock',
            'image': 'Imagen',
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:   # Limit to 5MB
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('El tamaño máximo de la imagen debe ser 5MB')
        return image