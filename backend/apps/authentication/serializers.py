from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email as django_validate_email
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """ Serializer for user registration with robust validation """
    
    # UniqueValidator here gives clear feedback if the email is taken
    email = serializers.EmailField(
        required=True,
        validators=[
            django_validate_email, 
            UniqueValidator(queryset=User.objects.all(), message="A user with this email already exists.")
        ]
    )
    
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    
    password_confirm = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta: 
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password_confirm')

    def validate_email(self, value):
        return value.lower()
    
    def validate(self, attrs):
        # AC: Password matching logic
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        # Remove confirmation before passing to create_user
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)