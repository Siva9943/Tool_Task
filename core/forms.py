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
    
class FormValidate(UserCreationForm):
    class Meta:
        modal=Product_info
        fields=['product_code','product_name','description','item_category','cost_price','selling_price','quantity','stock']
    
    