from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('price', 'quantity', 'position')
        POSITION_CHOICES = (
            ('BUY', 'BUY'),
            ('SELL', 'SELL')
        )
        widgets = {
            'position': forms.Select(choices=POSITION_CHOICES, attrs={'class': 'form-control'})
        }
