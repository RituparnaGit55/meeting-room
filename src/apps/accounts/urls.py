from django.urls import path
from . import views

urlpatterns = [
    # API URLs
    path("api/register/", views.RegisterView.as_view(), name="api-register"),
    path("api/login/", views.LoginView.as_view(), name="api-login"),
    path("api/refresh/", views.RefreshTokenView.as_view(), name="api-token-refresh"),
    path("api/logout/", views.LogoutView.as_view(), name="api-logout"),
    path("api/me/", views.UserProfileView.as_view(), name="api-user-profile"),
    path("api/change-password/", views.ChangePasswordView.as_view(), name="api-change-password"),
    path("api/verify-email/<str:token>/", views.EmailVerificationView.as_view(), name="api-verify-email"),
    path("api/resend-verification/", views.ResendVerificationEmailView.as_view(), name="api-resend-verification"),
    path("api/forgot-password/", views.PasswordResetRequestView.as_view(), name="api-forgot-password"),
    path("api/reset-password/<str:token>/", views.PasswordResetView.as_view(), name="api-reset-password"),
    path("api/google/", views.GoogleOAuthView.as_view(), name="api-google-oauth"),
    
    # Web URLs
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("verify-email/<str:token>/", views.verify_email_view, name="verify-email"),
    path("forgot-password/", views.forgot_password_view, name="forgot-password"),
    path("forgot-password/done/", views.forgot_password_done_view, name="forgot-password-done"),
    path("reset-password/<str:token>/", views.reset_password_view, name="reset-password"),
    path("reset-password/success/", views.reset_password_success_view, name="reset-password-success"),
    path("profile/", views.profile_view, name="profile"),
    path("change-password/", views.change_password_view, name="change-password"),
]
