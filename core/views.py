from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import logout, login, authenticate
from django.db.models import Q
from .forms import *
from .models import Product_info, Email_DB
import pandas as pd
from django.views import View

from django.conf import settings
from .tasks import build_error_table
from django.core.mail import EmailMultiAlternatives
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
from .tasks import send_account_creation_email
from django.db import models
from simple_history.models import HistoricalRecords
from .services import *
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
import os
from django.core.paginator import Paginator

def signup_user(request):
    if request.method == "POST":
        form = CustomUserForm(request.POST)
        email=request.POST.get('email')
        username=email.split('@')[-1]
       
        if User.objects.filter(Q(username=username) | Q(email=email)).exists():
            messages.error(request, "Username or email already exists.")
            return redirect('tool_login_info')

        if form.is_valid():
            user = form.save()
            Email_DB.objects.create(
                user=user,
                to_email=user.email,
                subject="Account Creation Successful",
                email_status="Pending",
            )
            send_account_creation_email(user.id)
            messages.success(request, "Account created successfully." )
            return redirect("tool_login_info")
        return render(request,"signup.html",{"form": form})
    form = CustomUserForm()
    return render(request,"signup.html",{"form": form})


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


@login_required
def upload(request):
    return render(request, 'home.html')


@login_required
def dashboard(request):
    products = Product_info.objects.filter(user=request.user)

    paginator = Paginator(products, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "dashboard.html", {
        "page_obj": page_obj,
    })


@login_required
def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)

        if "file" not in request.FILES:
            messages.error(request, "Please select an Excel file.")
            return redirect("tool_home_info")

        if form.is_valid():
            uploaded_file = form.cleaned_data["file"]
            result = process_upload_file(request.user, uploaded_file)

            if result["template_error"]:
                messages.error(request, result["template_error"])
                return redirect("tool_home_info")

            if result["failed_count"] > 0:
                messages.warning(
                    request,
                    f'{result["success_count"]} rows uploaded successfully. '
                    f'{result["failed_count"]} rows failed validation.'
                )
            else:
                messages.success(
                    request,
                    f'All {result["success_count"]} rows uploaded successfully.'
                )

            products = Product_info.objects.filter(user=request.user)

            paginator = Paginator(products, 8)  
            page_number = request.GET.get("page")
            page_obj = paginator.get_page(page_number)

            print(page_obj,"hello siva")
            return render(
                request,
                "dashboard.html",
                {
                    "page_obj": page_obj,
                    "errors": result["invalid_rows"],
                    "summary": result,
                },
            )

    else:
        form = UploadFileForm()

    return render(request, "home.html", {"form": form})

 
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
    

# @login_required
# def upload_file(request):
#     if request.method == "POST":
#         email=request.user.email
#         print(email)

#         file = request.FILES.get("file")
#         if not file:
#             messages.error(request, "No file uploaded.")
#             return redirect("tool_home_info")

#         try:
#             if file.name.endswith(".csv"):
#                 df = pd.read_csv(file)
#             elif file.name.endswith((".xlsx", ".xls")):
#                 df = pd.read_excel(file)
#             else:
#                 messages.error(request, "Please upload a CSV or Excel file.")
#                 return redirect("tool_home_info")

#             df.columns = df.columns.astype(str).str.strip().str.lower()
#             headings = df.columns

#             required_columns = [
#                 "product_code",
#                 "product_name",
#                 "description",
#                 "item_category",
#                 "cost_price",
#                 "selling_price",
#                 "quantity",
#                 'expire_date',
#             ]

#             missing_columns = [col for col in required_columns if col not in headings]

#             if missing_columns:
#                 messages.error(
#                     request,
#                     f"Missing columns: {', '.join(missing_columns)}. "
#                     "Please modify your file and upload it again."
#                 )
#                 return redirect("tool_home_info")
                        
#             errors = []
#             valid_products = []
#             for index, row in df.iterrows():
#                 row_errors = row_validate(row, index + 2)

#                 if row_errors:
#                     errors.extend(row_errors)
#                     continue

#                 valid_products.append(
#                     Product_info(
#                         user=request.user,
#                         product_code=str(row["product_code"]).strip(),
#                         product_name=str(row["product_name"]).strip(),
#                         description=str(row["description"]).strip(),
#                         item_category=str(row["item_category"]).strip(),
#                         cost_price=float(row["cost_price"]),
#                         selling_price=float(row["selling_price"]),
#                         quantity=int(row["quantity"]),
#                         date=row['expire_date']
#                     )
#                 )
            
#             if valid_products is not None:
#                 Product_info.objects.bulk_create(valid_products)
#                 messages.success(request, f"{len(valid_products)} products uploaded successfully.")
#             elif errors is not None:
#                 messages.error(request,"Error in uploaded data. A detailed report has been sent to your email. Please correct the file and upload it again.")
#                 print(errors,"heelloe siva")
#                 # body=build_error_table(errors)
#                 # send_validation_email(email=request.user.email,body=body,)
#                 html_body=build_error_table(errors)
#                 msg = EmailMultiAlternatives(
#                     subject="Upload Validation Report",
#                     body="sample",
#                     from_email=settings.DEFAULT_FROM_EMAIL,
#                     to=[email],)
#                 msg.attach_alternative(html_body, "text/html")
#                 msg.send()
#                 data = Product_info.objects.filter(user=request.user)
#             return render(request, "dashboard.html", {"data": data})
#         except Exception as e:
#             messages.error(request,"Error in uploaded data. A detailed report has been sent to your email. Please correct the file and upload it again.")
#             print(errors,"heelloe siva")
#             html_body=build_error_table(errors)
#             msg = EmailMultiAlternatives(
#                 subject="Upload Validation Report",
#                 body="sample",
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 to=[email],)
#             msg.attach_alternative(html_body, "text/html")
#             msg.send()
        
#             # body=build_error_table(errors)
#             # send_validation_email(email=request.user.email,body=body,)
#             return redirect("tool_home_info")
        
#     return render(request, "home.html")


class ProductUpdateView(LoginRequiredMixin, View):

    def post(self, request, pk):
        product = get_object_or_404(Product_info, id=pk)
        post_data = request.POST.copy()

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
        products = Product_info.objects.filter(user=request.user)
        paginator = Paginator(products, 8)  
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        messages.success(request, f"{product.product_name} deleted successfully.")
        return redirect("tool_dashboard")


def custom_404(request, exception):
    return render(request, "error_page.html", status=404)


def custom_500(request):
    return render(request, "500.html", status=500)



class MyPasswordChange(PasswordChangeView):
    template_name = 'register/password_change_form.html'
    success_url = reverse_lazy('password_change_done')

class MyPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'register/password_change_done.html'




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



def product_list(request):
    products=products.objects.all()
    paginator=Paginator(products,2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard.html', {'page_obj': page_obj})