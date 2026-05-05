# apps/authentication/views.py

import logging
from typing import cast, Dict, Any, Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import EmailVerificationToken, PasswordResetToken
from .models import User as SwiftUser
from .serializers import (
    RegistrationSerializer,
    SwiftNoteTokenObtainPairSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from .utils import send_verification_email, send_password_reset_email

User = get_user_model()
logger = logging.getLogger(__name__)


class RegisterView(APIView):
    """
    POST /api/auth/register/
    
    Register a new user account. Creates an inactive, unverified user
    and sends a verification email.
    """
    permission_classes = [AllowAny]
    throttle_scope = 'registration'

    def post(self, request) -> Response:
        # Safely get data - request.data is typically a dict
        data: Dict[str, Any] = request.data if request.data is not None else {}
        serializer = RegistrationSerializer(data=data)
        
        if serializer.is_valid():
            with transaction.atomic():
                user = cast(SwiftUser, serializer.save())
                
                success, message = send_verification_email(user)
                if not success:
                    transaction.set_rollback(True)
                    logger.error(f"Registration email failed for {user.email}: {message}")
                    return Response(
                        {"error": _("Registration failed. Please try again later.")},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            return Response(
                {"message": _("Registration successful! Please check your email to verify your account.")},
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    """
    POST /api/auth/verify-email/
    
    Verify a user's email address using a token sent via email.
    """
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'verify_email'

    def post(self, request) -> Response:
        # Safely get data
        data: Dict[str, Any] = request.data if request.data is not None else {}
        token_str: Optional[str] = data.get('token')
        
        if not token_str:
            return Response(
                {"error": _("Token is required.")},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token_obj = EmailVerificationToken.objects.get(token=token_str)
            
            if token_obj.is_used:
                return Response(
                    {"error": _("This verification link has already been used.")},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if token_obj.is_expired:
                return Response(
                    {"error": _("This verification link has expired.")},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user: SwiftUser = token_obj.user
            user.is_verified = True
            user.is_active = True
            user.save()
            
            token_obj.is_used = True
            token_obj.save()

            logger.info(f"Email verified successfully for user: {user.email}")
            
            return Response(
                {"message": _("Email verified successfully!")},
                status=status.HTTP_200_OK
            )

        except EmailVerificationToken.DoesNotExist:
            return Response(
                {"error": _("Invalid verification token.")},
                status=status.HTTP_400_BAD_REQUEST
            )


class ResendVerificationView(APIView):
    """
    POST /api/auth/resend-verification/
    
    Allows users to request a new verification email if they haven't verified yet.
    For security, always returns the same message whether email exists or not.
    """
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'resend_email'

    def post(self, request) -> Response:
        # Safely get data
        data: Dict[str, Any] = request.data if request.data is not None else {}
        email: Optional[str] = data.get('email')
        
        if not email:
            return Response(
                {"error": _("Email is required.")},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Cast to SwiftUser to access is_verified
            user = cast(SwiftUser, User.objects.get(email=email.lower()))
            
            if user.is_verified:
                return Response(
                    {"message": _("If an account exists, a verification link has been sent.")},
                    status=status.HTTP_200_OK
                )

            success, message = send_verification_email(user)
            if not success:
                logger.warning(f"Resend verification failed for {email}: {message}")
                return Response(
                    {"error": _("Failed to send email. Please try again later.")},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Always return same message for security (don't reveal if user exists)
            return Response(
                {"message": _("If an account exists, a verification link has been sent.")},
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            # Always return same message for security
            return Response(
                {"message": _("If an account exists, a verification link has been sent.")},
                status=status.HTTP_200_OK
            )


class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login/
    
    Authenticate a user and return JWT access/refresh tokens.
    Uses custom serializer to check email verification status.
    """
    serializer_class = SwiftNoteTokenObtainPairSerializer


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    
    Blacklist the refresh token to log out the user.
    Requires authentication.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request) -> Response:
        try:
            # Safely get data
            data = cast(Dict[str, Any], request.data)
            refresh_token = data.get("refresh")
            
            if not refresh_token:
                return Response(
                    {"error": _("Refresh token is required.")},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {"message": _("Successfully logged out.")},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            logger.warning(f"Logout failed: {e}")
            return Response(
                {"error": _("Invalid token.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        

class PasswordResetRequestView(APIView):
    """
    POST /api/auth/password-reset/
    
    Request a password reset email. Sends a secure, time-limited token
    to the user's email address if the account exists.
    """
    permission_classes = [AllowAny]
    throttle_scope = 'password_reset'

    def post(self, request) -> Response:
        # Safely get data
        data = cast(Dict[str, Any], request.data if request.data is not None else {})
        serializer = PasswordResetRequestSerializer(data=data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        valid_data = cast(Dict[str, Any], serializer.validated_data)
        email = valid_data.get('email')
        
        try:
            # Cast to SwiftUser to access is_verified
            user = cast(SwiftUser, User.objects.get(email=email))
            
            if user.is_verified:
                success, message = send_password_reset_email(user)
                if not success:
                    logger.error(f"Password reset email failed for {email}: {message}")
                    return Response(
                        {"error": _("Failed to send reset email. Please try again later.")},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            # Always return same message for security
            return Response(
                {"message": _("If an account exists with this email, you will receive a password reset link.")},
                status=status.HTTP_200_OK
            )
            
        except User.DoesNotExist:
            # Same message for security - don't reveal if email exists
            return Response(
                {"message": _("If an account exists with this email, you will receive a password reset link.")},
                status=status.HTTP_200_OK
            )


class PasswordResetConfirmView(APIView):
    """
    POST /api/auth/password-reset/confirm/
    
    Reset password using a valid token. Token must be unused and not expired.
    """
    permission_classes = [AllowAny]
    throttle_scope = 'password_reset_confirm'

    def post(self, request) -> Response:
        # Safely get data
        data = cast(Dict[str, Any], request.data)
        serializer = PasswordResetConfirmSerializer(data=data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        v_data = cast(Dict[str, Any], serializer.validated_data)
        token_str = v_data.get('token')
        new_password = v_data.get('new_password')
        
        try:
            token_obj = PasswordResetToken.objects.get(token=token_str)
            
            if token_obj.is_used:
                return Response(
                    {"error": _("This password reset link has already been used.")},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if token_obj.is_expired:
                return Response(
                    {"error": _("This password reset link has expired.")},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = cast(SwiftUser, token_obj.user)
            user.set_password(new_password)
            user.save()
            
            token_obj.is_used = True
            token_obj.save()
            
            logger.info(f"Password reset successful for user: {user.email}")
            
            return Response(
                {"message": _("Password reset successful. You can now log in with your new password.")},
                status=status.HTTP_200_OK
            )
            
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"error": _("Invalid password reset token.")},
                status=status.HTTP_400_BAD_REQUEST
            )


class PasswordResetVerifyView(APIView):
    """
    POST /api/auth/password-reset/verify/
    
    Verify if a password reset token is valid (not used, not expired).
    Returns 200 if valid, 400 otherwise.
    """
    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        # Safely get data
        data: Dict[str, Any] = request.data if request.data is not None else {}
        token_str: Optional[str] = data.get('token')
        
        if not token_str:
            return Response(
                {"error": _("Token is required.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            token_obj = PasswordResetToken.objects.get(token=token_str)
            
            if token_obj.is_used:
                return Response(
                    {"error": _("Reset link has already been used.")},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if token_obj.is_expired:
                return Response(
                    {"error": _("Reset link has expired.")},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {"message": _("Token is valid.")},
                status=status.HTTP_200_OK
            )
            
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"error": _("Invalid token.")},
                status=status.HTTP_400_BAD_REQUEST
            )