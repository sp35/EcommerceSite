from django import forms
from core.models import Order


class AddMoneyForm(forms.Form):
    money = forms.IntegerField(label='Amount', min_value=0)


class OrderForm(forms.ModelForm):
	class Meta:
		model = Order
		fields = ['order_items']