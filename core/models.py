from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

class Product_info(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product_code=models.CharField(max_length=100, unique=True)
    product_name=models.CharField(max_length=100,unique=True)
    description=models.TextField()
    item_category=models.CharField(max_length=500)
    cost_price=models.DecimalField(max_digits=500, decimal_places=2)
    selling_price=models.DecimalField(max_digits=500, decimal_places=2)
    quantity=models.IntegerField(null=False,default=1)
    expire_date=models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()
    


class Email_DB(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    to_email=models.EmailField(max_length=100,default='sivaprakash622003@gmail.com')
    cc_email=models.EmailField(max_length=100,null=True)
    subject=models.TextField(max_length=500)
    email_status=models.CharField(max_length=150,null=True,default="not updated")
    sent_at=models.DateField(auto_now_add=True)

class AuditLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    action = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class InvalidUploadRow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invalid_rows")
    product_code = models.CharField(max_length=255, blank=True)
    product_name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    item_category = models.CharField(max_length=255, blank=True)
    cost_price = models.CharField(max_length=255, blank=True)
    selling_price = models.CharField(max_length=255, blank=True)
    quantity = models.CharField(max_length=255, blank=True)
    expire_date = models.CharField(max_length=255, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)    

class UploadSummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="upload_summaries")
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)