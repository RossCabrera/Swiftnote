from datetime import date
from typing import Any, Dict, cast

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email as django_validate_email
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User as SwiftUser

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """ 
    Serializer for user registration. Validates email uniqueness, 
    password strength, and password confirmation.
    """
    
    email = serializers.EmailField(
        required=True,
        validators=[
            django_validate_email,
            UniqueValidator(
                queryset=User.objects.all(), 
                message=_("A user with this email already exists.")
            )
        ],
        error_messages={
            'required': _('Email is required.'),
            'invalid': _('Enter a valid email address.'),
        }
    )
    
    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
        error_messages={
            'max_length': _('First name is too long.'),
        }
    )
    
    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        error_messages={
            'max_length': _('Last name is too long.'),
        }
    )
    
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'},
        error_messages={
            'required': _('Password is required.'),
            'blank': _('Password cannot be blank.'),
        }
    )
    
    password_confirm = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'},
        error_messages={
            'required': _('Please confirm your password.'),
        }
    )
    
    class Meta: 
        model = User
        fields = ('email', 'first_name', 'last_name', 'date_of_birth', 'password', 'password_confirm')
        extra_kwargs = {
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
        }

    def validate_email(self, value):
        """Normalize email to lowercase"""
        return value.lower()
    
    def validate_date_of_birth(self, value):
        if value:
            today = date.today()
            age = today.year - value.year - (
                (today.month, today.day) < (value.month, value.day)
            )
            if age < 13:
                raise serializers.ValidationError("You must be at least 13 years old.")
        return value
    
    def validate(self, attrs):
        """Ensure passwords match"""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError({
                "password_confirm": _("Password fields didn't match.")
            })
        return attrs
    
    def create(self, validated_data):
        """Create user with validated data"""
        # Remove confirmation before passing to create_user
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


class SwiftNoteTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that checks if the user's email is verified 
    before allowing login.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize login field error messages
        self.fields['email'].error_messages = {
            'required': _('Email is required.'),
            'blank': _('Email cannot be blank.'),
        }
        self.fields['password'].error_messages = {
            'required': _('Password is required.'),
            'blank': _('Password cannot be blank.'),
        }
    
    def validate(self, attrs):
        # Attempt authentication
        try:
            data = cast(Dict[str, Any], super().validate(attrs))
        except exceptions.AuthenticationFailed as e:
            # Check if user exists but is unverified for better error message
            email = attrs.get('email', '').lower()
            try:
                user = cast(SwiftUser, User.objects.get(email=email)) 
                if not user.is_verified:
                    raise exceptions.AuthenticationFailed(
                        _("Your email is not verified. Please check your inbox.")
                    )
            except User.DoesNotExist:
                pass
            # Re-raise with generic message for security
            raise exceptions.AuthenticationFailed(
                _("Invalid email or password.")
            ) from e
        
        user = cast(SwiftUser, self.user)
        
        # Double-check verification status (security)
        if not user.is_verified:
            raise exceptions.AuthenticationFailed(
                _("Your email is not verified. Please check your inbox.")
            )
        
        # Add user info to response
        data['user'] = {
            'id': str(user.id),
            'uuid': str(user.id),  
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.full_name,
            'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
            'age': user.age,
            'is_verified': user.is_verified,
        }
        
        return data

    @classmethod
    def get_token(cls, user):
        """
        Override to add custom claims to the JWT token
        """
        user = cast(SwiftUser, user)
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['user_id'] = str(user.id)
        
        # Add name claims (optional, useful for frontend)
        if user.first_name:
            token['first_name'] = user.first_name
        if user.last_name:
            token['last_name'] = user.last_name
        
        return token

class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset email
    """
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': _('Email is required.'),
            'invalid': _('Enter a valid email address.'),
            'blank': _('Email cannot be blank.'),
        }
    )
    
    def validate_email(self, value):
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming password reset with token
    """
    token = serializers.CharField(
        required=True,
        error_messages={
            'required': _('Reset token is required.'),
            'blank': _('Reset token cannot be blank.'),
        }
    )
    
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        write_only=True,
        style={'input_type': 'password'},
        error_messages={
            'required': _('New password is required.'),
            'blank': _('New password cannot be blank.'),
        }
    )
    
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        error_messages={
            'required': _('Please confirm your new password.'),
            'blank': _('Password confirmation cannot be blank.'),
        }
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": _("Passwords didn't match.")
            })
        return attrs
