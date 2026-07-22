from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Product_info,
    Email_DB,
    AuditLog,
    UploadSummary,
)


@admin.register(Product_info)
class ProductAdmin(SimpleHistoryAdmin):
    list_display = (
        "product_code",
        "product_name",
        "item_category",
        "cost_price",
        "selling_price",
        "quantity",
        "expire_date",
        "user",
        "updated_at",
    )
    search_fields = ("product_code", "product_name", "item_category")
    list_filter = ("item_category", "user")


@admin.register(Email_DB)
class EmailDBAdmin(admin.ModelAdmin):
    list_display = ("user", "to_email", "cc_email", "subject", "email_status", "sent_at")
    search_fields = ("to_email", "cc_email", "subject")
    list_filter = ("email_status", "sent_at")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "role",
        "action",
        "login_time",
        "logout_time",
        "ip_address",
        "created_at",
    )
    search_fields = ("username", "ip_address")
    list_filter = ("action", "role")



@admin.register(UploadSummary)
class UploadSummaryAdmin(admin.ModelAdmin):
    list_display = ("user", "success_count", "failed_count", "created_at")
    list_filter = ("user",)