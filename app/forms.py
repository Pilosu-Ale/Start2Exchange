from django import forms
from .models import Order, Profile
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(OrderForm, self).__init__(*args, **kwargs)

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

    def clean(self):
        price = self.cleaned_data['price']
        position = self.cleaned_data['position']
        quantity = self.cleaned_data['quantity']
        profile = Profile.objects.get(user=self.user)
        balance = profile.balance
        if price <= 0:
            raise forms.ValidationError("Price must be greater than 0")
        elif quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than 0")
        elif price * quantity > balance and position == "BUY":
            raise forms.ValidationError("You don't have enough money")
        elif position == "SELL" and quantity > profile.BTC_wallet:
            raise forms.ValidationError("You don't have enough Bitcoins")




