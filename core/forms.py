import os
import re
import datetime
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


class CustomUserForm(UserCreationForm):
    full_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["full_name", "email", "password1", "password2"]

    def clean_full_name(self):
        full_name = self.cleaned_data.get("full_name", "").strip()
        if not re.match(r'^[A-Za-z ]+$', full_name):
            raise forms.ValidationError("Full name must contain letters and spaces only.")
        return full_name

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        domain = email.split("@")[-1]

        if domain not in settings.ALLOWED_EMAIL_DOMAINS:
            raise forms.ValidationError("Please use your company email.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if password and len(password) < 6:
            raise forms.ValidationError("Password must be at least 6 characters long.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        # store full_name in first_name for now
        user.first_name = self.cleaned_data.get("full_name", "")
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
            "expire_date",
        ]

    def clean_product_code(self):
        code = self.cleaned_data["product_code"].strip()
        if not re.match(r"^P\d+$", code):
            raise forms.ValidationError("Product Code must be like P001.")
        return code

    def clean_product_name(self):
        name = self.cleaned_data.get("product_name", "").strip()
        if not re.search(r"[A-Za-z]", name):
            raise forms.ValidationError("Product Name must contain letters.")
        return name

    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        if qty is not None and qty < 0:
            raise forms.ValidationError("Quantity must be greater than or equal to 0.")
        return qty

    def clean_cost_price(self):
        cost = self.cleaned_data["cost_price"]
        if cost is not None and cost < 0:
            raise forms.ValidationError("Cost Price cannot be negative.")
        return cost

    def clean_expire_date(self):
        expire_date = self.cleaned_data.get("expire_date")
        if expire_date and expire_date < datetime.date.today():
            raise forms.ValidationError("Expire Date must not be in the past.")
        return expire_date

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
            'accept': '.xlsx',
            'id': 'id_file',
        }),
        help_text='Only .xlsx files are allowed.',
    )

    def clean_file(self):
        uploaded_file = self.cleaned_data['file']
        ext = os.path.splitext(uploaded_file.name)[1].lower()

        if ext not in ['.xlsx']:
            raise forms.ValidationError(
                f'Unsupported file type "{ext}". Only Excel (.xlsx) files are allowed.'
            )

        max_mb = 10
        if uploaded_file.size > max_mb * 1024 * 1024:
            raise forms.ValidationError(f'File too large. Maximum allowed size is {max_mb} MB.')

        return uploaded_file