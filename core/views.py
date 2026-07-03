from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from .form import CustomUserForm, FormValidate
from .models import Product_info, Email_DB
import pandas as pd

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from core.validation import row_validate
from .tasks import send_validation_email,build_error_table
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeDoneView
from django.contrib.auth.mixins import LoginRequiredMixin


from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect



from django.db import models
from simple_history.models import HistoricalRecords

class ToolRecord(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    history = HistoricalRecords()


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('password_change_done')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'change_password.html', {'form': form})


def password_change_done(request):
    return render(request, 'password_change_done.html')

def login_user(request):

    if request.method == "POST":
        email_or_username = request.POST.get("email")
        password = request.POST.get("password")

        allowed_domains = ["inessconsulting.com", "gmail.com"]
        if "@" in email_or_username:
            email = email_or_username

            if email.split("@")[1] not in allowed_domains:
                messages.error(request, "Invalid domain email.")
                return redirect("tool_login_info")

            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
            except User.DoesNotExist:
                messages.error(request, "Invalid email or password.")
                return redirect("tool_login_info")

        else:
            username = email_or_username

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("tool_home_info")

        messages.error(request, "Invalid credentials.")
        return redirect("tool_login_info")

    return render(request, "login.html")


@login_required
def logout_user(request):
    logout(request)
    return redirect('tool_login_info')

def signup_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = email.split('@')[0] if email else None
        allowed_domains = ["inessconsulting.com", 'gmail.com']

        if not email or '@' not in email:
            messages.error(request, "Invalid email format.")
            return redirect('tool_signup_info')

        domain = email.split('@')[1]

        if domain not in allowed_domains:
            messages.error(request, "Please use a valid domain email address.")
            return redirect('tool_signup_info')

        if User.objects.filter(Q(username=username) | Q(email=email)).exists():
            messages.error(request, "Username or email already exists.")
            return redirect('tool_login_info')

        form = CustomUserForm(request.POST)
        if form.is_valid():
            user_obj = form.save()
            subject = "Account Creation Successfull"
            message = f"""Hi {user_obj.first_name or user_obj.username},Your account has been created successfully. Username: {user_obj.username} Email: {user_obj.email} 
                    Thank you. """

            try:
                send_mail_gmail(
                    to_email=user_obj.email,
                    cc_email=None,
                    subject=subject,
                    message=message
                )

                Email_DB.objects.create(
                    user=user_obj,
                    to_email=user_obj.email,
                    subject=subject,
                    email_status="Sent"
                )

            except Exception as e:
                Email_DB.objects.create(
                    user=user_obj,
                    to_email=user_obj.email,
                    subject=subject,
                    email_status=f"Failed: {e}"
                )

            messages.success(request, "Account created successfully.")
            return redirect("tool_login_info")

        else:
            messages.error(request, "Please correct the errors below.")
            return render(request, 'signup.html', {'form': form})

    return render(request, 'signup.html')


@login_required
def upload(request):
    return render(request, 'home.html')


@login_required
def dashboard(request):
    data = Product_info.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'data': data})


@login_required
def upload_file(request):
    if request.method == "POST":
        email=request.user.email
        print(email)

        file = request.FILES.get("file")
        if not file:
            messages.error(request, "No file uploaded.")
            return redirect("tool_home_info")

        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            elif file.name.endswith((".xlsx", ".xls")):
                df = pd.read_excel(file)
            else:
                messages.error(request, "Please upload a CSV or Excel file.")
                return redirect("tool_home_info")

            df.columns = df.columns.astype(str).str.strip().str.lower()
            headings = df.columns

            required_columns = [
                "product_code",
                "product_name",
                "description",
                "item_category",
                "cost_price",
                "selling_price",
                "quantity",
                "stock",
            ]

            missing_columns = [col for col in required_columns if col not in headings]

            if missing_columns:
                messages.error(
                    request,
                    f"Missing columns: {', '.join(missing_columns)}. "
                    "Please modify your file and upload it again."
                )
                return redirect("tool_home_info")
                        
            errors = []
            valid_products = []
            for index, row in df.iterrows():
                row_errors = row_validate(row, index + 2)

                if row_errors:
                    errors.extend(row_errors)
                    continue

                valid_products.append(
                    Product_info(
                        user=request.user,
                        product_code=str(row["product_code"]).strip(),
                        product_name=str(row["product_name"]).strip(),
                        description=str(row["description"]).strip(),
                        item_category=str(row["item_category"]).strip(),
                        cost_price=float(row["cost_price"]),
                        selling_price=float(row["selling_price"]),
                        quantity=int(row["quantity"]),
                        stock=str(row["stock"]).strip().lower() in ["true", "1", "yes"],
                    )
                )
            
            if valid_products is not None:
                Product_info.objects.bulk_create(valid_products)
                messages.success(request, f"{len(valid_products)} products uploaded successfully.")
            elif errors is not None:
                messages.error(request,"Error in uploaded data. A detailed report has been sent to your email. Please correct the file and upload it again.")
                print(errors,"heelloe siva")
                # body=build_error_table(errors)
                # send_validation_email(email=request.user.email,body=body,)
                html_body=build_error_table(errors)
                msg = EmailMultiAlternatives(
                    subject="Upload Validation Report",
                    body="sample",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email],)
                msg.attach_alternative(html_body, "text/html")
                msg.send()
                data = Product_info.objects.filter(user=request.user)
            return render(request, "dashboard.html", {"data": data})
        except Exception as e:
            messages.error(request,"Error in uploaded data. A detailed report has been sent to your email. Please correct the file and upload it again.")
            print(errors,"heelloe siva")
            html_body=build_error_table(errors)
            msg = EmailMultiAlternatives(
                subject="Upload Validation Report",
                body="sample",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],)
            msg.attach_alternative(html_body, "text/html")
            msg.send()
        
            # body=build_error_table(errors)
            # send_validation_email(email=request.user.email,body=body,)
            return redirect("tool_home_info")
        
    return render(request, "home.html")


class ProductUpdateView(LoginRequiredMixin, View):

    def post(self, request, pk):
        product = get_object_or_404(Product_info, id=pk)
        post_data = request.POST.copy()
        post_data.setdefault("stock", product.stock)

        form = FormValidate(post_data, instance=product)

        if form.is_valid():
            form.save()
            messages.success(request, f"{product.product_code} updated successfully.")
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)

        return redirect("tool_dashboard")


class ProductDeleteView(LoginRequiredMixin, View):

    def get(self, request, pk):
        product = get_object_or_404(Product_info, id=pk)
        product.delete()

        messages.success(request, f"{product.product_name} deleted successfully.")
        return redirect("tool_dashboard")


def custom_404(request, exception):
    return render(request, "error_page.html", status=404)


def custom_500(request):
    return render(request, "500.html", status=500)


from dotenv import load_dotenv
load_dotenv()
import os


def send_mail_gmail(to_email, cc_email, subject, message):
    connection = get_connection(
        host='smtp.gmail.com',
        port=587,
        username=os.getenv('EMAIL_HOST_USER'),
        password=os.getenv('EMAIL_HOST_PASSWORD'),
        use_tls=True,
    )

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=os.getenv('EMAIL_HOST_USER'),
        to=[to_email],
        cc=[cc_email] if cc_email else [],
        connection=connection,
    )

    email.send()