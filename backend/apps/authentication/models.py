import secrets
import uuid
from datetime import timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """ Custom user model that abstracts the default Django user"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)

    avatar = models.URLField(_('avatar URL'), max_length=500, blank=True, null=True)
    is_verified = models.BooleanField(_('verified status'),default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

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