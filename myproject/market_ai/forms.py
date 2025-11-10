from django import forms
#from market.models import Product

class PriceSuggestForm(forms.Form):
    title = forms.CharField(max_length=200)
    description = forms.CharField(widget=forms.Textarea, required=False)
    marca = forms.CharField(max_length=100, required=False)
    current_price = forms.DecimalField(max_digits=12, decimal_places=2, required=False)

class ChatForm(forms.Form):
    message = forms.CharField(
        max_length=500,  # Limit message length
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escribe tu mensaje aquí...',
            'autocomplete': 'off',
            'id': 'id_message',
            'maxlength': '500'
        }),
        label='',
        error_messages={
            'required': 'Por favor escribe un mensaje',
            'max_length': 'El mensaje es demasiado largo (máximo 500 caracteres)'
        }
    )
    
    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if len(message) < 2:
            raise forms.ValidationError('El mensaje debe tener al menos 2 caracteres')
        return message