from .models import User, UserManager
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email as django_validate_email


class UserRegistrationSerializer(serializers.ModelSerializer):
    """ Serializer for user registration """
    password = serializers.CharField(write_only=True, required= True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, 
                                                 required=True)
    
    class Meta: 
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password_confirm')

    def validate_email(self, value):
        django_validate_email(value)
        return value.lower()
    
    def validate(self, attrs):
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError({"password": "Password fields didn't match."})
            return attrs
    
    def create(self, validated_data):
            validated_data.pop('password_confirm')
            return User.objects.create_user(**validated_data)
    

        
        
    