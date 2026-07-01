from django.db import models
from django.contrib.auth.models import User
class Product_info(models.Model):
    product_code=models.CharField(max_length=20, unique=True)
    product_name=models.CharField(max_length=40)
    description=models.TextField()
    item_category=models.CharField(max_length=20)
    cost_price=models.DecimalField(max_digits=10, decimal_places=2)
    selling_price=models.DecimalField(max_digits=10, decimal_places=2)
    quantity=models.IntegerField(null=False)
    stock=models.BooleanField(default=True)

    
