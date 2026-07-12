from django.contrib import admin
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', login_user, name='tool_login_info'),
    path('logout/', logout_user, name='tool_logout_info'),
    path('signup/', signup_user, name='tool_signup_info'),
    path('home/', upload, name='tool_home_info'),
    path('upload/', upload_file, name='tool_upload_info'),
    path('dashboard/', dashboard, name='tool_dashboard'),
    path('product/update/<int:pk>/', ProductUpdateView.as_view(), name='product_update'),
    path('product/delete/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'),
    path('change-password/', MyPasswordChange.as_view(), name='change_password'),
    path('change-password/done/',MyPasswordChangeDoneView.as_view(),name='password_change_done'),
    path('temp/download',download_template,name='temp_excel'),
    path('download-invalid-excel/', download_invalid_excel, name='download_invalid_excel'),
    path('error_data_page',error_data_page,name='upload_data_error'),
    path('password_reset',auth_views.PasswordResetView.as_view(template_name="register/password_reset_form.html"),name="password_reset"),
    path('password_reset_done/',auth_views.PasswordResetDoneView.as_view(template_name="register/password_reset_done.html"),name="password_reset_done"),
    path("reset/<uidb64>/<token>/",auth_views.PasswordResetConfirmView.as_view(template_name="register/password_reset_confirm.html"),name="password_reset_confirm"),
    path("reset_done/",auth_views.PasswordResetCompleteView.as_view(template_name="register/password_reset_complete.html"),name="password_reset_complete"),
]
 