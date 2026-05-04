from typing import cast

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle

# Local imports
from .serializers import RegistrationSerializer
from .models import EmailVerificationToken, User as SwiftUser # 

from .utils import send_verification_email

User = get_user_model()

class RegisterView(APIView):
    """ API view for user registration """
    permission_classes = [AllowAny]
    throttle_scope = 'registration' 

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        email = request.data.get('email')
        if email and User.objects.filter(email=email.lower()).exists():
            return Response(
                {"error": "An account with this email already exists."}, 
                status=status.HTTP_409_CONFLICT
            )

        if serializer.is_valid():
            with transaction.atomic():
                user = cast(SwiftUser, serializer.save())
                
                success, message = send_verification_email(user)
                if not success:
                    transaction.set_rollback(True)
                    return Response(
                        {"error": f"Registration failed: {message}"}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    
            return Response(
                {"message": "Registration successful! Please check your email to verify your account."}, 
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    """ View to handle the logic when a user clicks the email link """
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'verify_email'

    def post(self, request):
        token_str = request.data.get('token')
        
        if not token_str:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token_obj = EmailVerificationToken.objects.get(token=token_str)
            
            if token_obj.is_used:
                return Response({"error": "This link has already been used."}, status=status.HTTP_400_BAD_REQUEST)
            
            if token_obj.is_expired:
                return Response({"error": "This link has expired."}, status=status.HTTP_400_BAD_REQUEST)

            user: SwiftUser = token_obj.user
            user.is_verified = True
            user.is_active = True
            user.save()
            
            token_obj.is_used = True
            token_obj.save()

            return Response({"message": "Email verified successfully!"}, status=status.HTTP_200_OK)

        except EmailVerificationToken.DoesNotExist:
            return Response({"error": "Invalid verification token."}, status=status.HTTP_400_BAD_REQUEST)

class ResendVerificationView(APIView):
    """ View to handle resending the verification email"""
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'resend_email'

    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = cast(SwiftUser, User.objects.get(email=email.lower()))
            
            if user.is_verified:
                return Response({"message": "This account is already verified."}, status=status.HTTP_200_OK)

            success, message = send_verification_email(user)
            if not success:
                return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "If an account exists, a new link has been sent."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"message": "If an account exists, a new link has been sent."}, status=status.HTTP_200_OK)