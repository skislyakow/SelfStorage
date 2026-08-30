from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .forms import (
    CustomAuthenticationForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
)

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        form_class=CustomAuthenticationForm,
        redirect_authenticated_user=True,
        next_page='home'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html',
        form_class=CustomPasswordResetForm,
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url=reverse_lazy('users:password_reset_done'),
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html',
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        form_class=CustomSetPasswordForm,
        success_url=reverse_lazy('users:password_reset_complete'),
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html',
    ), name='password_reset_complete'),
]
