"""
URL configuration for Project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core.views import *
from django.conf import settings
from django.conf.urls.static import static




# handler404 = "yourapp.views.custom_404"
# handler500 = "yourapp.views.custom_500"


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',login_user,name='tool_login_info'),
    path('logout/',logout_user,name='tool_logout_info'),
    path('signup/',signup_user,name='tool_signup_info'),
    path('home/',upload,name='tool_home_info'),
    path('upload/',upload_file,name='tool_upload_info'),
    path('dashboard/',dashboard,name="tool_dashboard"),
    path('product/update/<int:pk>/',ProductUpdateView.as_view(),name='product_update'),
    path('product/delete/<int:pk>/',ProductDeleteView.as_view(),name='product_delete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
