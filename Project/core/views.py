from django.shortcuts import redirect, render,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout,login,authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from .forms import CustomUserForm
from .models import Product_info
import pandas as pd

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .bulk_upload import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View





def login_user(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")

        allowed_domains = ["inees.com"]
    
        if email.split('@')[-1] not in allowed_domains:
            messages.error(request, "Please use a valid Domain email address.")
            return redirect("tool_login_info")
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect("tool_login_info")
        
        user = authenticate(request,username=user_obj.username,password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")            
            return redirect("tool_dashboard")
        else:
            messages.error(request, "Invalid email or password.")
            return redirect("tool_login_info")

    return render(request, "login.html")

@login_required
def logout_user(request):
    logout(request)
    return redirect('tool_login_info')

def signup_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        allowed_domains = ["inees.com"]

        if not email or '@' not in email:
            messages.error(request, "Invalid email format.")
            return render(request, 'signup.html')

        domain = email.split('@')[1]

        if domain not in allowed_domains:
            messages.error(request, "Please use a valid domain email address.")
            return render(request, 'signup.html')
        
        if User.objects.filter(Q(username=username) | Q(email=email)).exists():
            messages.error(request, "Username or email already exists.")
            return render(request, 'signup.html')

        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully.")
            return redirect('tool_login_info')

        else:
            messages.error(request, "Please correct the errors below.")
            return render(request, 'signup.html', {'form': form})

    return render(request, 'signup.html')

@login_required
def upload(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    data=Product_info.objects.all()
    return render(request,'dashboard.html',{'data':data})

@login_required
def upload_file(request):
    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            messages.error(request, "No file uploaded.")
            return redirect("tool_dashboard")
        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            elif file.name.endswith((".xlsx", ".xls")):
                df = pd.read_excel(file)
            else:
                messages.error(request, "Please upload a CSV or Excel file.")
                return redirect("tool_dashboard")
            
            df.columns = df.columns.astype(str).str.strip().str.lower()
            headings = df.columns
            print("Headings:", headings)
            required_columns = ["product_code","product_name","description","item_category","cost_price","selling_price","quantity","stock",]

            missing_columns = [col for col in required_columns if col not in headings]

            if missing_columns:
                messages.error(
                    request,
                    f"Missing columns: {', '.join(missing_columns)}. "
                    "Please modify your file and upload it again."
                )
                return redirect("tool_dashboard")

            # existing_codes = set(
            #     Product_info.objects.filter(
            #         product_code__in=df["product_code"]
            #     ).values_list("product_code", flat=True)
            # )

            # if existing_codes:
            #     messages.error(
            #         request,
            #         f"These Product Codes already exist: {', '.join(existing_codes)}"
            #     )
            #     return redirect("tool_dashboard")
    
            errors = []
            products = []

            for index, row in df.iterrows():
                row_errors = validate_row(row, index + 2)
                products.append(
                    Product_info(
                        product_code=row["product_code"],
                        product_name=row["product_name"],
                        description=row["description"],
                        item_category=row["item_category"],
                        cost_price=float(row["cost_price"]),
                        selling_price=float(row["selling_price"]),
                        quantity=int(row["quantity"]),
                        stock=True if str(row["stock"]).lower() in ["true", "1", "yes"] else False,
                )
            )

            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect("tool_dashboard")

            Product_info.objects.bulk_create(products)
            data=Product_info.objects.all()
            messages.success(
                request,
                f"{len(products)} products uploaded successfully."
            )
            return redirect('tool_dashboard')

        except Exception as e:
            messages.error(request, str(e))
            return redirect("tool_dashboard")
    return render(request,'dashboard.html',{'data':data})


class ProductUpdateView(LoginRequiredMixin, View):

    def post(self, request, pk):
        product = get_object_or_404(Product_info, id=pk)
        product_code=request.POST.get('product_code')
        product.product_name = request.POST.get("product_name")
        product.description = request.POST.get("description")
        product.item_category = request.POST.get("item_category")
        product.cost_price = request.POST.get("cost_price")
        product.selling_price = request.POST.get("selling_price")
        product.quantity = request.POST.get("quantity")
        product.stock = request.POST.get("stock") == "True"

        product.save()

        messages.success(request, f"{product.product_name} updated successfully.")
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

