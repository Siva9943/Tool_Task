from django.db import models
from django.contrib.auth.models import User
class Product_info(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product_code=models.CharField(max_length=20, unique=True)
    product_name=models.CharField(max_length=40)
    description=models.TextField()
    item_category=models.CharField(max_length=20)
    cost_price=models.DecimalField(max_digits=10, decimal_places=2)
    selling_price=models.DecimalField(max_digits=10, decimal_places=2)
    quantity=models.IntegerField(null=False)
    stock=models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Email_DB(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    to_email=models.EmailField(max_length=30,default='sivaprakash622003@gmail.com')
    cc_email=models.EmailField(max_length=30,null=True)
    subject=models.TextField(max_length=50)
    email_status=models.CharField(max_length=150,null=True,default="not updated")
    sent_at=models.DateField(auto_now_add=True)
