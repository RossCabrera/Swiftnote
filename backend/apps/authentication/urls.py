from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (GoogleLoginView, LoginView, LogoutView,
                    PasswordResetConfirmView, PasswordResetRequestView,
                    PasswordResetVerifyView, RegisterView,
                    ResendVerificationView, VerifyEmailView)

urlpatterns = [
    # Registration & Email Verification
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
    
    # Login & Token Management
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Password Reset
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/verify/', PasswordResetVerifyView.as_view(), name='password-reset-verify'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    path('google/', GoogleLoginView.as_view(), name='google-login'),
]