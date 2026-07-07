import os
import re
import datetime
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


class CustomUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        domain = email.split("@")[-1]

        if domain not in settings.ALLOWED_EMAIL_DOMAINS:
            raise forms.ValidationError("Please use your company email.")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = user.email.split("@")[0]

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
        ]

    def clean_product_code(self):
        code = self.cleaned_data["product_code"].strip()
        if not re.match(r"^P\d+$", code):
            raise forms.ValidationError("Product Code must be like P001.")
        return code

    def clean_product_name(self):
        name = self.cleaned_data.get("product_name", "").strip()
        if not re.search(r"[A-Za-z]", name):
            raise forms.ValidationError("Product Name must contain letters, not just numbers.")
        return name

    def clean_description(self):
        description = self.cleaned_data.get("description", "").strip()
        if not re.search(r"[A-Za-z]", description):
            raise forms.ValidationError("Description must contain letters, not just numbers.")
        return description

    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        if qty < 0:
            raise forms.ValidationError("Quantity must be greater than or equal to 0.")
        return qty

    def clean_cost_price(self):
        cost = self.cleaned_data["cost_price"]
        if cost < 0:
            raise forms.ValidationError("Cost Price cannot be negative.")
        return cost

    def clean(self):
        cleaned_data = super().clean()
        cost = cleaned_data.get("cost_price")
        selling = cleaned_data.get("selling_price")

        if cost is not None and selling is not None and selling < cost:
            self.add_error("selling_price", "Selling Price must be greater than or equal to Cost Price.")
        return cleaned_data


class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='Select CSV or Excel file',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx',
            'id': 'id_file',
        }),
        help_text='Only .csv and .xlsx files are allowed.',
    )

    def clean_file(self):
        uploaded_file = self.cleaned_data['file']
        ext = os.path.splitext(uploaded_file.name)[1].lower()

        if ext not in ['.csv', '.xlsx']:
            raise forms.ValidationError(
                f'Unsupported file type "{ext}". Only CSV and Excel (.xlsx) files are allowed.'
            )

        max_mb = 10
        if uploaded_file.size > max_mb * 1024 * 1024:
            raise forms.ValidationError(f'File too large. Maximum allowed size is {max_mb} MB.')

        return uploaded_file