import hmac

from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import logout, login, authenticate
from django.db.models import Q
from .forms import *
from .models import Product_info, Email_DB
import pandas as pd
from django.views import View

from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView,PasswordChangeDoneView,PasswordResetDoneView
from django.contrib.auth.mixins import LoginRequiredMixin
import os
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product_info
from .services import process_upload_file
from django.contrib import messages
from .forms import *
from django.contrib.auth.models import User
from .forms import CustomUserForm
from .models import Email_DB
from django.db import models
from simple_history.models import HistoricalRecords
from .services import *
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
import os
from .tasks import *
from django.core.paginator import Paginator
from django.utils.http import url_has_allowed_host_and_scheme
import io
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
import random
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from email_ops.utils.email_service import send_email
User = get_user_model()

# signup
def signup_user(request):

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "verify_otp":
            submitted_otp = request.POST.get("otp", "").strip()
            session_otp = request.session.get("signup_otp")
            pending_data = request.session.get("signup_pending_data")

            if not session_otp or not pending_data:
                messages.error(request, "Your verification session expired. Please try again.")
                request.session.pop("signup_otp", None)
                request.session.pop("signup_pending_data", None)
                return redirect("tool_signup_info")
            attempts = request.session.get("signup_otp_attempts", 0)
            if attempts >= 5:
                messages.error(request, "Too many attempts. Please start signup again.")
                request.session.pop("signup_otp", None)
                request.session.pop("signup_pending_data", None)
                request.session.pop("signup_otp_attempts", None)
                return redirect("tool_signup_info")

            if not hmac.compare_digest(str(submitted_otp), str(session_otp)):
                request.session["signup_otp_attempts"] = attempts + 1
                messages.error(request, "Invalid OTP. Please try again.")
                form = CustomUserForm(initial=pending_data)
                return render(request, "signup.html", {"form": form, "allowed_domains": settings.ALLOWED_EMAIL_DOMAINS, "otp_sent": True})

            email = pending_data["email"].lower()
            username = email.split("@")[0]

            if User.objects.filter(Q(username=username) | Q(email=email)).exists():
                messages.error(request, "Username or email already exists.")
                request.session.pop("signup_otp", None)
                request.session.pop("signup_pending_data", None)
                request.session.pop("signup_otp_attempts", None)
                return redirect("tool_signup_info")
            form = CustomUserForm(pending_data)
            if form.is_valid():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=pending_data["password1"],
                    first_name=pending_data["full_name"],
                )

                Email_DB.objects.create(
                    user=user,
                    to_email=user.email,
                    subject="Account Creation Successful",
                    email_status="Pending",
                )

                send_email(
                    email_type="signup",
                    to=user.email,
                    context={"user": {"username": user.username, "email": user.email, "first_name": user.first_name}},
                    user_id=user.id,
                )

                request.session.pop("signup_otp", None)
                request.session.pop("signup_pending_data", None)
                request.session.pop("signup_otp_attempts", None)
                messages.success(request, "Account created successfully.")
                return redirect("tool_login_info")
            else:
                messages.error(request, "Something went wrong. Please sign up again.")
                request.session.pop("signup_otp", None)
                request.session.pop("signup_pending_data", None)
                request.session.pop("signup_otp_attempts", None)
                return redirect("tool_signup_info")

        form = CustomUserForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"].lower()
            username = email.split("@")[0]
            if User.objects.filter(
                Q(username=username) | Q(email=email)
            ).exists():
                messages.error(request, "Username or email already exists.")
                return render(request, "signup.html", {"form": form, "allowed_domains": settings.ALLOWED_EMAIL_DOMAINS})

            otp = f"{random.randint(100000, 999999)}"
            request.session["signup_otp"] = otp
            request.session["signup_otp_attempts"] = 0
            request.session["signup_pending_data"] = {
                "full_name": form.cleaned_data["full_name"],
                "email": email,
                "password1": form.cleaned_data["password1"],
                "password2": form.cleaned_data["password2"],
            }
            request.session.set_expiry(600)

            send_email(
                    email_type="otp",
                    to=email,
                    context={
                        "user": {"username": username, "email": email, "full_name": form.cleaned_data["full_name"]},
                        "otp": otp,
                    },
                )

            messages.success(request, "We sent a verification code to your email.")
            return render(request, "signup.html", {"form": CustomUserForm(initial=request.session["signup_pending_data"]), "allowed_domains": settings.ALLOWED_EMAIL_DOMAINS, "otp_sent": True})

        return render(request, "signup.html", {"form": form, "allowed_domains": settings.ALLOWED_EMAIL_DOMAINS})

    form = CustomUserForm()
    return render(request, "signup.html", {"form": form, "allowed_domains": settings.ALLOWED_EMAIL_DOMAINS, "otp_sent": False})





# def signup_user(request):
#     if request.method == "POST":
#         form = CustomUserForm(request.POST)
#         email = request.POST.get("email")
#         username = email.split("@")[0]

#         if User.objects.filter(Q(username=username) | Q(email=email)).exists():
#             messages.error(request, "Username or email already exists.")
#             return redirect("tool_login_info")
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.username = username
#             user.save()
#             Email_DB.objects.create(
#                 user=user,
#                 to_email=user.email,
#                 subject="Account Creation Successful",
#                 email_status="Pending",
#             )

#             subject = "Account Creation Successful"

#             message = f"""
#                 Hi {user.first_name or user.username},
#                 Your account has been created successfully.

#             Username: {user.username}
#             Email: {user.email}
#             Thank you. """
#             send_email(
#                 user_id=user.id,
#                 subject=subject,
#                 message=message,
#                 to=user.email
#             )
#             messages.success(request,"Account created successfully.")
#             return redirect("tool_login_info")
#         return render(request,"signup.html",{"form": form})
#     form = CustomUserForm()
#     return render(request,"signup.html",{"form": form})

# login safe 

def safe_login_redirect(request):
    next_url = request.GET.get("next")

    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts=settings.ALLOWED_HOSTS,
        require_https=request.is_secure(),
    ):
        return redirect(next_url)

    display_name = request.user.first_name or request.user.username
    messages.success(request, f"Welcome back, {display_name}!")

    return redirect("tool_dashboard")

def login_user(request):
    if request.method == "POST":
        email_or_username = request.POST.get("email")
        password = request.POST.get("password")
        username = email_or_username
        if "@" in email_or_username:
            email = email_or_username.lower().strip()
            domain = email.split("@")[1]
            if domain not in settings.ALLOWED_EMAIL_DOMAINS:
                messages.error(
                    request,
                    "Invalid domain email."
                )
                return redirect("tool_login_info")

            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
            except User.DoesNotExist:
                messages.error(
                    request,
                    "Invalid credentials."
                )
                return redirect("tool_login_info")
        user = authenticate(
            request,
            username=username,
            password=password
        )
        if user:
            login(request,user)
            messages.success(
                request,
                "Login successful!"
            )
            return safe_login_redirect(request)
        messages.error(
            request,
            "Invalid credentials."
        )
    return render(request,"login.html")

@login_required
def logout_user(request):
    logout(request)
    return redirect('tool_login_info')


@login_required
def upload(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    products = Product_info.objects.filter(user=request.user).order_by('-id')
    product_code = request.GET.get('product_code', '').strip()
    product_name = request.GET.get('product_name', '').strip()
    cost_price = request.GET.get('cost_price', '').strip()

    if product_code:
        products = products.filter(product_code__icontains=product_code)

    if product_name:
        first_letter = product_name[0]
        products = products.filter(
            Q(product_name__icontains=product_name) | Q(product_name__istartswith=first_letter)
        )

    if cost_price.isdigit():
        price_limit = int(cost_price)
        if price_limit < 500:
            products = products.filter(cost_price__lt=500)
        elif price_limit < 1000:
            products = products.filter(cost_price__lt=1000)
        elif price_limit < 2000:
            products = products.filter(cost_price__lt=2000)

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = UploadFileForm()

    upload_summary = UploadSummary.objects.filter(user=request.user).first()
    invalid_rows = InvalidUploadRow.objects.filter(user=request.user)

    summary = {
        "success_count": upload_summary.success_count if upload_summary else 0,
        "failed_count": upload_summary.failed_count if upload_summary else 0,
        "invalid_rows": invalid_rows, 
    }

    return render(request, 'dashboard.html', {
        'page_obj': page_obj,
        'form': form,
        'summary': summary,
    })

@login_required
def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if "file" not in request.FILES:
            messages.error(request, "Please Upload an Excel/CSV file.")
            return redirect("tool_dashboard")
        if form.is_valid():
            uploaded_file = form.cleaned_data["file"]
            result = process_upload_file(request.user, uploaded_file)

            # Clear previous upload's leftovers
            InvalidUploadRow.objects.filter(user=request.user).delete()

            if result["template_error"]:
                messages.error(request, result["template_error"])
                UploadSummary.objects.update_or_create(
                    user=request.user,
                    defaults={"success_count": 0, "failed_count": 0}
                )
            else:
                if result["failed_count"] > 0:
                    messages.warning(
                        request,
                        f'{result["success_count"]} rows uploaded successfully. '
                        f'{result["failed_count"]} rows failed validation.')
                else:
                    messages.success(request, f' {result["success_count"]} rows uploaded successfully.')

                UploadSummary.objects.update_or_create(
                    user=request.user,
                    defaults={
                        "success_count": result["success_count"],
                        "failed_count": result["failed_count"],
                    }
                )
                invalid_rows = result.get("invalid_rows", [])
                if invalid_rows:
                    InvalidUploadRow.objects.bulk_create([
                        InvalidUploadRow(
                            user=request.user,
                            product_code=row.get('product_code', ''),
                            product_name=row.get('product_name', ''),
                            description=row.get('description', ''),
                            item_category=row.get('item_category', ''),
                            cost_price=row.get('cost_price', ''),
                            selling_price=row.get('selling_price', ''),
                            quantity=row.get('quantity', ''),
                            expire_date=row.get('expire_date', ''),
                            error_message=row.get('error_message', ''),
                        ) for row in invalid_rows
                    ])
                    send_email(
                        email_type="error_report",
                        to=request.user.email,
                        context={"invalid_rows": invalid_rows},)
                    
            return redirect("tool_dashboard")
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)
            return redirect("tool_dashboard")
    return redirect("tool_dashboard")


class ProductUpdateView(LoginRequiredMixin, View):
 
    def post(self, request, pk):
        product = get_object_or_404(Product_info, id=pk)
        form = FormValidate(request.POST, instance=product)
 
        if form.is_valid():
            form.save()
            messages.success(request, f"{product.product_code} updated successfully.")
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)
 
        return redirect("tool_dashboard")
    


class ProductUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product_info, id=pk)
        form = FormValidate(request.POST, instance=product)

        if form.is_valid():
            form.save()
            messages.success(request, f"{product.product_code} updated successfully.")
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)

        page = request.GET.get("page", 1)
        return redirect(f"{reverse_lazy('tool_dashboard')}?page={page}")

class ProductDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        product = get_object_or_404(Product_info, id=pk)
        product.delete()
        messages.success(request, f"{product.product_name} deleted successfully.")
        page = request.GET.get("page", 1)
        return redirect(f"{reverse_lazy('tool_dashboard')}?page={page}")


def help_page(request):
    return render(request, "help.html")


def custom_404(request, exception):
    return render(request, "404.html", status=404)


def custom_500(request):
    return render(request, "500.html", status=500)



class MyPasswordChange(PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('password_change_done')

class MyPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'




def download_template(request):
    file_path = os.path.join(
        settings.BASE_DIR,
        "static",
        "files",
        "Product_Template.xlsx"
    )

    if os.path.exists(file_path):
        return FileResponse(
            open(file_path, "rb"),
            as_attachment=True,
            filename="Product_Template.xlsx"
        )
    raise Http404("File not found")




@login_required
def download_invalid_excel(request):
    invalid_rows = InvalidUploadRow.objects.filter(user=request.user).values(
        'product_code', 'product_name', 'description', 'item_category',
        'cost_price', 'selling_price', 'quantity', 'expire_date', 'error_message'
    )

    if not invalid_rows:
        messages.error(request, "No invalid data to download.")
        return redirect("tool_dashboard")

    data_to_export = []
    for row in invalid_rows:
        data_to_export.append({
            'Product code*': row['product_code'],
            'Product name*': row['product_name'],
            'Description': row['description'],
            'Item category': row['item_category'],
            'Cost price': row['cost_price'],
            'Selling price*': row['selling_price'],
            'Quantity*': row['quantity'],
            'Expire date(YYYY-MM-DD)': row['expire_date'],
            'Error Message': row['error_message'],
        })

    df = pd.DataFrame(data_to_export)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Invalid Rows')
    output.seek(0)
    response = FileResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        filename=f"invalid_products_{datetime.date.today().strftime('%Y%m%d')}.xlsx"
    )
    return response



# Signals 

from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed
)
from django.dispatch import receiver
from .models import AuditLog

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action="LOGIN",
        ip_address=request.META.get("REMOTE_ADDR")
    )

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action="LOGOUT",
        ip_address=request.META.get("REMOTE_ADDR")
    )

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    AuditLog.objects.create(
        user=None,
        action=f"FAILED LOGIN ({credentials.get('username')})",
        ip_address=request.META.get("REMOTE_ADDR")
    )








ROWS_PER_PAGE = 25
 
 
@login_required
def error_data_page(request):
    errors_qs = InvalidUploadRow.objects.filter(user=request.user).order_by('id')

    paginator = Paginator(errors_qs, ROWS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    upload_summary = UploadSummary.objects.filter(user=request.user).first()

    summary = {
        "success_count": upload_summary.success_count if upload_summary else 0,
        "failed_count": upload_summary.failed_count if upload_summary else 0,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            'invalid_data_rows.html',
            {'errors': page_obj},
            request=request
        )
        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next(),
        })

    return render(request, 'invalid_data.html', {
        'page_obj': page_obj,
        'summary': summary,
    })