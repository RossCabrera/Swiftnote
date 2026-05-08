import logging
from typing import Any, Dict, Optional, cast

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import EmailVerificationToken, PasswordResetToken
from .models import User as SwiftUser
from .serializers import (PasswordResetConfirmSerializer,
                          PasswordResetRequestSerializer,
                          RegistrationSerializer,
                          SwiftNoteTokenObtainPairSerializer)
from .utils import send_password_reset_email, send_verification_email

User = get_user_model()
logger = logging.getLogger(__name__)

REFRESH_COOKIE_NAME = 'refresh_token'


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    """
    Attach the refresh token as a secure, httpOnly cookie to the response.
    - httponly=True  → JavaScript cannot read it (XSS protection)
    - secure=True    → Only sent over HTTPS (set based on DEBUG flag)
    - samesite='Lax' → Sent on same-site requests and top-level navigation (CSRF protection)
    - path           → Scoped to auth endpoints so the cookie isn't sent on every request
    """
    max_age = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax',
        max_age=max_age,
        path='/api/auth/',
    )


class RegisterView(APIView):
    """
    POST /api/auth/register/
    
    Register a new user account. Creates an inactive, unverified user
    and sends a verification email.
    """
    permission_classes = [AllowAny]
    throttle_scope = 'registration'

    def post(self, request) -> Response:
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
        data: Dict[str, Any] = request.data if request.data is not None else {}
        email: Optional[str] = data.get('email')
        
        if not email:
            return Response(
                {"error": _("Email is required.")},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
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

            return Response(
                {"message": _("If an account exists, a verification link has been sent.")},
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {"message": _("If an account exists, a verification link has been sent.")},
                status=status.HTTP_200_OK
            )


class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login/

    Authenticate a user and return a JWT access token in the body.
    The refresh token is set as a secure httpOnly cookie — never exposed to JavaScript.
    """
    serializer_class = SwiftNoteTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh_token = response.data.pop('refresh', None)
            if refresh_token:
                _set_refresh_cookie(response, refresh_token)
        return response


class CookieTokenRefreshView(APIView):
    """
    POST /api/auth/refresh/

    Silently refreshes the access token using the httpOnly refresh cookie.
    Returns a new access token in the response body.
    The refresh cookie is automatically updated if token rotation is enabled.
    """
    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        refresh_token = request.COOKIES.get(REFRESH_COOKIE_NAME)

        if not refresh_token:
            return Response(
                {"error": _("Refresh token not found.")},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response(
                {"error": _("Refresh token is invalid or has expired. Please log in again.")},
                status=status.HTTP_401_UNAUTHORIZED
            )

        response = Response({'access': str(serializer.validated_data['access'])})

        if 'refresh' in serializer.validated_data:
            _set_refresh_cookie(response, str(serializer.validated_data['refresh']))

        return response

class LogoutView(APIView):
    """
    POST /api/auth/logout/

    Blacklists the refresh token (read from the httpOnly cookie) and clears the cookie.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request) -> Response:
        refresh_token = request.COOKIES.get(REFRESH_COOKIE_NAME)

        if not refresh_token:
            return Response(
                {"error": _("Refresh token not found.")},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            logger.warning(f"Logout blacklist failed: {e}")

        response = Response(
            {"message": _("Successfully logged out.")},
            status=status.HTTP_205_RESET_CONTENT
        )
        response.delete_cookie(REFRESH_COOKIE_NAME, path='/api/auth/')
        return response


class CurrentUserView(APIView):
    """
    GET /api/auth/current-user/

    Returns the currently authenticated user's profile.
    Called by the frontend on every page load (checkSession) to restore
    the user object from the httpOnly cookie session without a full login.
    Requires a valid access token in the Authorization header.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request) -> Response:
        user = cast(SwiftUser, request.user)
        return Response({
            'id': str(user.id),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.full_name,
            'avatar': user.avatar,
            'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
            'age': user.age,
            'is_verified': user.is_verified,
        })


class PasswordResetRequestView(APIView):
    """
    POST /api/auth/password-reset/
    
    Request a password reset email. Sends a secure, time-limited token
    to the user's email address if the account exists.
    """
    permission_classes = [AllowAny]
    throttle_scope = 'password_reset'

    def post(self, request) -> Response:
        data = cast(Dict[str, Any], request.data if request.data is not None else {})
        serializer = PasswordResetRequestSerializer(data=data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        valid_data = cast(Dict[str, Any], serializer.validated_data)
        email = valid_data.get('email')
        
        try:
            user = cast(SwiftUser, User.objects.get(email=email))
            
            if user.is_verified:
                success, message = send_password_reset_email(user)
                if not success:
                    logger.error(f"Password reset email failed for {email}: {message}")
                    return Response(
                        {"error": _("Failed to send reset email. Please try again later.")},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            return Response(
                {"message": _("If an account exists with this email, you will receive a password reset link.")},
                status=status.HTTP_200_OK
            )
            
        except User.DoesNotExist:
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

            if user.check_password(new_password):
                return Response(
                    {"error": _("Your new password must be different from your current password.")},
                    status=status.HTTP_400_BAD_REQUEST
                )

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
        
class GoogleLoginView(APIView):
    """
    POST /api/auth/google/
    
    Authenticate with Google OAuth2.
    Expected payload: {"access_token": "google_access_token"}
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        access_token = request.data.get('access_token')
        
        if not access_token:
            return Response(
                {"error": _("Google access token is required.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify token with Google
        google_response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if google_response.status_code != 200:
            return Response(
                {"error": _("Invalid Google token.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        google_data = google_response.json()
        email = google_data.get('email', '').lower()
        first_name = google_data.get('given_name', '')
        last_name = google_data.get('family_name', '')
        avatar = google_data.get('picture', '')
        
        if not email:
            return Response(
                {"error": _("Email not provided by Google.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = SwiftUser.objects.filter(email=email).first()
    
        
        if user:
            if not user.is_verified:
                return Response(
                    {"error": _("Please verify your email first. Check your inbox or request a new verification link.")},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if not user.first_name and first_name:
                user.first_name = first_name
            if not user.last_name and last_name:
                user.last_name = last_name
            if not user.avatar and avatar:
                user.avatar = avatar

            if any([first_name and not user.first_name, 
                    last_name and not user.last_name, 
                    avatar and not user.avatar]):
                user.save()
        else:
            user = SwiftUser.objects.create_user(
                email=email,
                password=None,
                first_name=first_name,
                last_name=last_name,
                avatar=avatar,
                is_verified=True,
                is_active=True
            )


        refresh = RefreshToken.for_user(user)

        response = Response({
            'access': str(refresh.access_token),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.full_name,
                'avatar': user.avatar,
                'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
                'age': user.age,
                'is_verified': user.is_verified,
            }
        })
        _set_refresh_cookie(response, str(refresh))
        return response