from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Product_info


class ProductInfoModelTests(TestCase):
    def test_product_info_can_be_created_with_required_fields(self):
        User = get_user_model()
        user = User.objects.create_user(username="tester", password="testpass123")

        product = Product_info.objects.create(
            user=user,
            product_code="P001",
            product_name="Sample Product",
            description="A test product",
            item_category="Tools",
            cost_price="10.50",
            selling_price="15.75",
            quantity=5,
            expire_date="2026-12-31",
        )

        self.assertTrue(Product_info.objects.filter(pk=product.pk).exists())
        self.assertEqual(product.user, user)
        self.assertEqual(product.product_code, "P001")
        self.assertEqual(product.product_name, "Sample Product")
        self.assertEqual(product.quantity, 5)
