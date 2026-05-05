import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """ Define a model manager for User model with no username field """
    def _create_user(self, email, password=None, **extra_fields):
        """ Create and save a User with the given email and password """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', False)

        extra_fields.pop('username', None)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """ Create and save a SuperUser with the given email and password """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        extra_fields['is_active'] = True
        
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """ Custom user model that abstracts the default Django user"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(_('email address'), unique=True)

    avatar = models.URLField(_('avatar URL'), max_length=500, blank=True, null=True)
    is_verified = models.BooleanField(_('verified status'),default=False)
    
    objects: UserManager = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def full_name(self):
        """Return user's full name or fallback to email prefix."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email.split('@')[0]

    def __str__(self):
        return self.email
    

class EmailVerificationToken(models.Model):
    """ Model to store email verification tokens for users """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="verification_tokens",
        verbose_name=_("user") 
    )

    token = models.CharField(_("token"), max_length=255, unique=True) 
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    expires_at = models.DateTimeField(_("expires at"))
    is_used = models.BooleanField(_("is used"), default=False)

    class Meta:
        verbose_name = _("email verification token")
        verbose_name_plural = _("email verification tokens")

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
        
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Token for {self.user.email} - Valid: {not self.is_expired}"
    

class PasswordResetToken(models.Model):
    """ Model to store password reset tokens for users """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
        verbose_name=_("user")
    )

    token = models.CharField(_("token"), max_length=255, unique=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    expires_at = models.DateTimeField(_("expires at"))
    is_used = models.BooleanField(_("is used"), default=False)

    class Meta:
        verbose_name = _("password reset token")
        verbose_name_plural = _("password reset tokens")

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=2)
            
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Reset for {self.user.email}"