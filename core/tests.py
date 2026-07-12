from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class SignupOtpFlowTests(TestCase):
    def test_signup_requires_otp_before_creating_user(self):
        User = get_user_model()

        with patch("core.views.send_mail_gmail") as mock_send_mail:
            response = self.client.post(
                reverse("tool_signup_info"),
                {
                    "full_name": "Test User",
                    "email": "test@company.com",
                    "password1": "StrongPass123",
                    "password2": "StrongPass123",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["otp_sent"])
        self.assertEqual(User.objects.count(), 0)
        self.assertTrue(mock_send_mail.called)

        otp = self.client.session["signup_otp"]

        verify_response = self.client.post(
            reverse("tool_signup_info"),
            {"otp": otp, "action": "verify_otp"},
        )

        self.assertEqual(verify_response.status_code, 302)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(email="test@company.com")
        self.assertEqual(user.first_name, "Test User")
