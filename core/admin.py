from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Product_info

@admin.register(Product_info)
class ProductAdmin(SimpleHistoryAdmin):
    pass