import io
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from .models import (
    Product_info,
    Email_DB,
    UploadSummary,
    InvalidUploadRow,
    AuditLog,
)


User = get_user_model()
YOURAPP = "core"
ALLOWED_DOMAINS = [".vercel.app", '127.0.0.1']


def msgs(response):
    """Helper: return list of message strings attached to a response's request."""
    return [str(m) for m in get_messages(response.wsgi_request)]




@override_settings(ALLOWED_EMAIL_DOMAINS=ALLOWED_DOMAINS)
class SignupViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("tool_signup_info")


    def test_get_signup_page_renders(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")
        self.assertFalse(response.context["otp_sent"])


    @patch(f"{YOURAPP}.views.send_email")
    def test_post_valid_signup_sends_otp_and_stores_session(self, mock_send_email):
        response = self.client.post(self.url, {
            "full_name": "Test User",
            "email": "newuser@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["otp_sent"])
        self.assertIn("signup_otp", self.client.session)
        self.assertIn("signup_pending_data", self.client.session)
        mock_send_email.assert_called_once()
        self.assertEqual(mock_send_email.call_args.kwargs.get("email_type"), "otp")


    @patch(f"{YOURAPP}.views.send_email")
    def test_post_signup_duplicate_email_rejected(self, mock_send_email):
        User.objects.create_user(username="dupe", email="dupe@example.com", password="pass12345")
        response = self.client.post(self.url, {
            "full_name": "Dupe User",
            "email": "dupe@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertIn("Username or email already exists.", msgs(response))
        mock_send_email.assert_not_called()


    @patch(f"{YOURAPP}.views.send_email")
    def test_verify_otp_correct_creates_user(self, mock_send_email):

        self.client.post(self.url, {
            "full_name": "OTP User",
            "email": "otpuser@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        otp = self.client.session["signup_otp"]


        response = self.client.post(self.url, {"action": "verify_otp", "otp": otp})
        self.assertRedirects(response, reverse("tool_login_info"))
        self.assertTrue(User.objects.filter(username="otpuser").exists())
        self.assertTrue(Email_DB.objects.filter(to_email="otpuser@example.com").exists())


    @patch(f"{YOURAPP}.views.send_email")
    def test_verify_otp_incorrect_shows_error_and_keeps_session(self, mock_send_email):
        self.client.post(self.url, {
            "full_name": "Bad OTP",
            "email": "badotp@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        response = self.client.post(self.url, {"action": "verify_otp", "otp": "000000"})
        self.assertIn("Invalid OTP. Please try again.", msgs(response))
        self.assertFalse(User.objects.filter(username="badotp").exists())


    @patch(f"{YOURAPP}.views.send_email")
    def test_verify_otp_expired_session_redirects(self, mock_send_email):
        response = self.client.post(self.url, {"action": "verify_otp", "otp": "123456"})
        self.assertRedirects(response, self.url)
        self.assertIn("Your verification session expired. Please try again.", msgs(response))


    @patch(f"{YOURAPP}.views.send_email")
    def test_verify_otp_too_many_attempts_blocks(self, mock_send_email):
        self.client.post(self.url, {
            "full_name": "Locked User",
            "email": "locked@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        session = self.client.session
        session["signup_otp_attempts"] = 5
        session.save()


        response = self.client.post(self.url, {"action": "verify_otp", "otp": "000000"})
        self.assertRedirects(response, self.url)
        self.assertIn("Too many attempts. Please start signup again.", msgs(response))




@override_settings(ALLOWED_EMAIL_DOMAINS=ALLOWED_DOMAINS)
class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("tool_login_info")
        self.user = User.objects.create_user(
            username="loginuser", email="loginuser@example.com", password="pass12345"
        )


    def test_get_login_page_renders(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # The view renders "registration/login.html", not a bare "login.html"
        self.assertTemplateUsed(response, "registration/login.html")


    def test_login_with_valid_username_and_password(self):
        response = self.client.post(self.url, {"email": "loginuser", "password": "pass12345"})
        self.assertRedirects(response, reverse("tool_dashboard"))


    def test_login_with_valid_email_and_password(self):
        response = self.client.post(self.url, {"email": "loginuser@example.com", "password": "pass12345"})
        self.assertRedirects(response, reverse("tool_dashboard"))


    def test_login_with_disallowed_email_domain(self):
        response = self.client.post(self.url, {"email": "someone@bad-domain.com", "password": "pass12345"})
        self.assertRedirects(response, self.url)
        # The view raises a domain-specific error, not the generic "Invalid credentials."
        self.assertIn("Invalid domain email.", msgs(response))


    def test_login_with_unknown_email(self):
        response = self.client.post(self.url, {"email": "unknown@example.com", "password": "pass12345"})
        self.assertRedirects(response, self.url)
        self.assertIn("Invalid credentials.", msgs(response))


    def test_login_with_wrong_password(self):
        response = self.client.post(self.url, {"email": "loginuser", "password": "wrongpass"})
        self.assertIn("Invalid credentials.", msgs(response))
        self.assertEqual(response.status_code, 200)


    def test_login_next_param_open_redirect_is_blocked(self):
        self.client.force_login(self.user)
        response = self.client.post(
            f"{self.url}?next=https://evil.example.com",
            {"email": "loginuser", "password": "pass12345"},
        )
    
        self.assertRedirects(response, reverse("tool_dashboard"))


    def test_login_next_param_safe_relative_url_is_honoured(self):
        response = self.client.post(
            f"{self.url}?next=/help/",
            {"email": "loginuser", "password": "pass12345"},
        )
        self.assertRedirects(response, reverse("tool_help_info"))


    def test_logout_requires_login(self):
        response = self.client.get(reverse("tool_logout_info"))
        self.assertNotEqual(response.status_code, 200)  # redirected to login (login_required)


    def test_logout_logs_user_out(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tool_logout_info"))
        self.assertRedirects(response, self.url)
        self.assertNotIn("_auth_user_id", self.client.session)





class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="dashuser", email="d@example.com", password="pass12345")
        self.other = User.objects.create_user(username="other", email="o@example.com", password="pass12345")


        Product_info.objects.create(
            user=self.user, product_code="P001", product_name="Apple Juice",
            description="Juice", item_category="Beverage",
            cost_price=100, selling_price=150, quantity=10,
        )
        Product_info.objects.create(
            user=self.user, product_code="P002", product_name="Banana Chips",
            description="Snack", item_category="Snacks",
            cost_price=600, selling_price=750, quantity=5,
        )
        Product_info.objects.create(
            user=self.other, product_code="P999", product_name="Not Mine",
            description="x", item_category="x",
            cost_price=50, selling_price=60, quantity=1,
        )


    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("tool_dashboard"))
        self.assertEqual(response.status_code, 302)


    def test_dashboard_only_shows_current_users_products(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tool_dashboard"))
        codes = [p.product_code for p in response.context["page_obj"]]
        self.assertIn("P001", codes)
        self.assertIn("P002", codes)
        self.assertNotIn("P999", codes)


    def test_dashboard_filter_by_product_code(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tool_dashboard"), {"product_code": "P001"})
        codes = [p.product_code for p in response.context["page_obj"]]
        self.assertEqual(codes, ["P001"])


    def test_dashboard_filter_by_product_name(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tool_dashboard"), {"product_name": "Apple Juice"})
        names = [p.product_name for p in response.context["page_obj"]]
        self.assertIn("Apple Juice", names)


    def test_dashboard_filter_by_cost_price_bracket(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tool_dashboard"), {"cost_price": "500"})
        prices = [p.cost_price for p in response.context["page_obj"]]
        self.assertTrue(all(p < 1000 for p in prices))


    def test_dashboard_pagination_10_per_page(self):
        self.client.force_login(self.user)
        for i in range(15):
            Product_info.objects.create(
                user=self.user, product_code=f"X{i}", product_name=f"Item {i}",
                description="d", item_category="c", cost_price=10, selling_price=20, quantity=1,
            )
        response = self.client.get(reverse("tool_dashboard"))
        self.assertEqual(len(response.context["page_obj"]), 10)



class UploadFileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="upuser", email="up@example.com", password="pass12345")
        self.client.force_login(self.user)
        self.url = reverse("tool_upload_info")


    def test_upload_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


    def test_get_redirects_to_dashboard(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("tool_dashboard"))


    def test_post_without_file_shows_error(self):
        response = self.client.post(self.url, {})
        self.assertRedirects(response, reverse("tool_dashboard"))
        # The view's actual message text has no "/CSV"
        self.assertIn("Please Upload an Excel file.", msgs(response))


    @patch(f"{YOURAPP}.views.process_upload_file")
    def test_post_valid_file_all_rows_success(self, mock_process):
        mock_process.return_value = {
            "template_error": None,
            "success_count": 5,
            "failed_count": 0,
            "invalid_rows": [],
        }
        upload_file = io.BytesIO(b"dummy,data")
        upload_file.name = "products.xlsx"
        response = self.client.post(self.url, {"file": upload_file})
        self.assertRedirects(response, reverse("tool_dashboard"))
        summary = UploadSummary.objects.get(user=self.user)
        self.assertEqual(summary.success_count, 5)
        self.assertEqual(summary.failed_count, 0)


    @patch(f"{YOURAPP}.views.send_email")
    @patch(f"{YOURAPP}.views.process_upload_file")
    def test_post_valid_file_with_invalid_rows_creates_error_report(self, mock_process, mock_send_email):
        mock_process.return_value = {
            "template_error": None,
            "success_count": 3,
            "failed_count": 2,
            "invalid_rows": [
                {"product_code": "BAD1", "product_name": "", "description": "", "item_category": "",
                 "cost_price": "", "selling_price": "", "quantity": "", "expire_date": "",
                 "error_message": "Missing product name"},
            ],
        }
        upload_file = io.BytesIO(b"dummy,data")
        upload_file.name = "products.xlsx"
        response = self.client.post(self.url, {"file": upload_file})
        self.assertRedirects(response, reverse("tool_dashboard"))
        self.assertEqual(InvalidUploadRow.objects.filter(user=self.user).count(), 1)
        mock_send_email.assert_called_once()


    @patch(f"{YOURAPP}.views.process_upload_file")
    def test_post_file_with_template_error(self, mock_process):
        mock_process.return_value = {
            "template_error": "Uploaded file does not match the expected template.",
            "success_count": 0,
            "failed_count": 0,
            "invalid_rows": [],
        }
        upload_file = io.BytesIO(b"dummy,data")
        upload_file.name = "wrong_template.xlsx"
        response = self.client.post(self.url, {"file": upload_file})
        self.assertRedirects(response, reverse("tool_dashboard"))
        summary = UploadSummary.objects.get(user=self.user)
        self.assertEqual(summary.success_count, 0)


    def test_previous_invalid_rows_cleared_on_new_upload(self):
        InvalidUploadRow.objects.create(
            user=self.user, product_code="OLD", product_name="Old row",
            description="", item_category="", cost_price="", selling_price="",
            quantity="", expire_date="", error_message="stale error",
        )
        with patch(f"{YOURAPP}.views.process_upload_file") as mock_process:
            mock_process.return_value = {
                "template_error": None, "success_count": 1, "failed_count": 0, "invalid_rows": [],
            }
            upload_file = io.BytesIO(b"dummy,data")
            upload_file.name = "products.xlsx"
            self.client.post(self.url, {"file": upload_file})
        self.assertFalse(InvalidUploadRow.objects.filter(product_code="OLD").exists())



# class ProductUpdateViewTests(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username="produser", email="pr@example.com", password="pass12345")
#         self.client.force_login(self.user)
#         self.product = Product_info.objects.create(
#             user=self.user, product_code="P100", product_name="Widget",
#             description="d", item_category="c", cost_price=100, selling_price=150, quantity=10,
#         )


#     def test_update_requires_login(self):
#         self.client.logout()
#         response = self.client.post(
#             reverse("product_update", args=[self.product.pk]), {"product_name": "New"}
#         )
#         self.assertEqual(response.status_code, 302)


#     def test_update_valid_data(self):
#         response = self.client.post(
#             reverse("product_update", args=[self.product.pk]),
#             {
#                 "product_code": "P100",
#                 "product_name": "Updated Widget",
#                 "description": "d",
#                 "item_category": "c",
#                 "cost_price": 120,
#                 "selling_price": 180,
#                 "quantity": 8,
#             },
#         )
#         self.assertRedirects(response, f"{reverse('tool_dashboard')}?page=1")
#         self.product.refresh_from_db()
#         self.assertEqual(self.product.product_name, "Updated Widget")


#     def test_update_invalid_data_shows_errors(self):
#         response = self.client.post(
#             reverse("product_update", args=[self.product.pk]),
#             {"product_code": "", "product_name": ""},
#         )
#         self.assertRedirects(response, f"{reverse('tool_dashboard')}?page=1")
#         self.product.refresh_from_db()
#         self.assertEqual(self.product.product_name, "Widget")  


#     def test_update_nonexistent_product_404(self):
#         response = self.client.post(reverse("product_update", args=[99999]), {})
#         self.assertEqual(response.status_code, 404)


#     def test_update_preserves_page_query_param(self):
#         response = self.client.post(
#             f"{reverse('product_update', args=[self.product.pk])}?page=3",
#             {
#                 "product_code": "P100", "product_name": "X", "description": "d",
#                 "item_category": "c", "cost_price": 1, "selling_price": 2, "quantity": 1,
#             },
#         )
#         self.assertRedirects(response, f"{reverse('tool_dashboard')}?page=3")



class ProductDeleteViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="deluser", email="del@example.com", password="pass12345")
        self.client.force_login(self.user)
        self.product = Product_info.objects.create(
            user=self.user, product_code="D100", product_name="ToDelete",
            description="d", item_category="c", cost_price=10, selling_price=20, quantity=1,
        )


    def test_delete_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("product_delete", args=[self.product.pk]))
        self.assertEqual(response.status_code, 302)


    def test_delete_removes_product(self):
        response = self.client.get(reverse("product_delete", args=[self.product.pk]))
        self.assertRedirects(response, f"{reverse('tool_dashboard')}?page=1")
        self.assertFalse(Product_info.objects.filter(pk=self.product.pk).exists())


    def test_delete_nonexistent_product_404(self):
        response = self.client.get(reverse("product_delete", args=[99999]))
        self.assertEqual(response.status_code, 404)



class HelpPageTests(TestCase):
    def test_help_page_accessible_without_login(self):
        response = self.client.get(reverse("tool_help_info"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "help.html")




class DownloadTemplateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="tplsuser", email="tpl@example.com", password="pass12345"
        )
        self.client.force_login(self.user)
        self.url = reverse("temp_excel")


    @patch(f"{YOURAPP}.views.os.path.exists", return_value=True)
    @patch(f"{YOURAPP}.views.open", create=True)
    def test_download_template_success(self, mock_open, mock_exists):
        mock_open.return_value = io.BytesIO(b"fake excel bytes")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


    @patch(f"{YOURAPP}.views.os.path.exists", return_value=False)
    def test_download_template_missing_file_404(self, mock_exists):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)



class DownloadInvalidExcelTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="excuser", email="ex@example.com", password="pass12345")
        self.client.force_login(self.user)
        self.url = reverse("download_invalid_excel")


    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


    def test_no_invalid_rows_redirects_with_error(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("tool_dashboard"))
        self.assertIn("No invalid data to download.", msgs(response))


    def test_downloads_excel_when_invalid_rows_exist(self):
        InvalidUploadRow.objects.create(
            user=self.user, product_code="BAD1", product_name="", description="",
            item_category="", cost_price="", selling_price="", quantity="",
            expire_date="", error_message="Missing product name",
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn("attachment", response["Content-Disposition"])




class ErrorDataPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="erruser", email="err@example.com", password="pass12345")
        self.client.force_login(self.user)
        self.url = reverse("upload_data_error")
        for i in range(30):
            InvalidUploadRow.objects.create(
                user=self.user, product_code=f"E{i}", product_name="x", description="",
                item_category="", cost_price="", selling_price="", quantity="",
                expire_date="", error_message="err",
            )


    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


    def test_normal_request_renders_full_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invalid_data.html")
        self.assertEqual(len(response.context["page_obj"]), 25)


    def test_ajax_request_returns_json(self):
        response = self.client.get(self.url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        data = response.json()
        self.assertIn("html", data)
        self.assertTrue(data["has_next"])


    def test_second_page_has_no_next(self):
        response = self.client.get(self.url, {"page": 2}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        data = response.json()
        self.assertFalse(data["has_next"])


class AuditLogSignalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="audituser", email="aud@example.com", password="pass12345")


    @override_settings(ALLOWED_EMAIL_DOMAINS=ALLOWED_DOMAINS)
    def test_successful_login_creates_audit_log(self):
        self.client.post(reverse("tool_login_info"), {"email": "audituser", "password": "pass12345"})
        self.assertTrue(AuditLog.objects.filter(user=self.user, action="LOGIN").exists())


    def test_logout_creates_audit_log(self):
        self.client.force_login(self.user)
        self.client.get(reverse("tool_logout_info"))
        self.assertTrue(AuditLog.objects.filter(user=self.user, action="LOGOUT").exists())


    @override_settings(ALLOWED_EMAIL_DOMAINS=ALLOWED_DOMAINS)
    def test_failed_login_creates_audit_log(self):
        self.client.post(reverse("tool_login_info"), {"email": "audituser", "password": "wrongpass"})
        self.assertTrue(
            AuditLog.objects.filter(user=None, action__startswith="FAILED LOGIN").exists()
        )