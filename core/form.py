import re

from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email']
        user.username = email.split('@')[0]
        user.email = email

        if commit:
            user.save()

        return user
    
class FormValidate(forms.ModelForm):

    class Meta:
        model = Product_info
        fields = [
            "product_code",
            "product_name",
            "description",
            "item_category",
            "cost_price",
            "selling_price",
            "quantity",
            "stock",
        ]

    def clean_product_code(self):
        code = self.cleaned_data["product_code"].strip()

        if not re.match(r"^P\d+$", code):
            raise forms.ValidationError(
                "Product Code must be like P001."
            )

        return code
    
    def clean_product_name(self):
        name = self.cleaned_data.get("product_name", "").strip()
        if not re.search(r"[A-Za-z]", name):
            raise forms.ValidationError(
                "Product Name must contain letters, not just numbers."
            )
        return name
    def clean_description(self):
        description = self.cleaned_data.get("description", "").strip()
        if not re.search(r"[A-Za-z]", description):
            raise forms.ValidationError(
                "Description must contain letters, not just numbers."
            )
        return description

    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        if qty < 0:
            raise forms.ValidationError(
                "Quantity must be greater than or equal to 0."
            )
        return qty

    def clean_cost_price(self):
        cost = self.cleaned_data["cost_price"]
        if cost < 0:
            raise forms.ValidationError(
                "Cost Price cannot be negative."
            )

        return cost

    def clean(self):
        cleaned_data = super().clean()
        cost = cleaned_data.get("cost_price")
        selling = cleaned_data.get("selling_price")

        if cost is not None and selling is not None and selling < cost:
            self.add_error("selling_price","Selling Price must be greater than or equal to Cost Price.")
        return cleaned_data