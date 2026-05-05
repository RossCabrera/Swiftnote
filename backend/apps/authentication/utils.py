from datetime import timedelta

import resend
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from .models import EmailVerificationToken, PasswordResetToken

resend.api_key = settings.RESEND_API_KEY


def send_verification_email(user):
    """
    Send email verification link to user.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Check for tokens created in the last 60 seconds (rate limiting)
    recent_token = EmailVerificationToken.objects.filter(
        user=user, 
        created_at__gte=timezone.now() - timedelta(minutes=1)
    ).exists()
    
    if recent_token:
        return False, force_str(_("Please wait a minute before requesting another email."))

    # Create the Token 
    token_obj = EmailVerificationToken.objects.create(user=user)
    
    # Prepare the Email
    verify_url = f"https://swiftnote.app/verify?token={token_obj.token}"



    context = {  
        'verify_url': verify_url,
        'user_full_name': user.full_name,
    }
    
    html_content = render_to_string('emails/verify_email.html', context)
    
    # Email subject - convert to string for Resend API
    subject = force_str(_("Confirm your email for Swiftnote"))

    try:
        resend.Emails.send({
            "from": "Swiftnote <onboarding@resend.dev>",
            "to": [user.email],
            "subject": subject,
            "html": html_content,
        })
        return True, force_str(_("Email sent successfully"))
    except Exception as e:
        return False, str(e)


def send_password_reset_email(user):
    """
    Send password reset link to user.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Check for recent password reset tokens (rate limiting)
    recent_token = PasswordResetToken.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(minutes=1)
    ).exists()
    
    if recent_token:
        return False, force_str(_("Please wait a minute before requesting another password reset email."))
    
    # Create the Token
    token_obj = PasswordResetToken.objects.create(user=user)
    
    # Prepare the Email
    reset_url = f"https://swiftnote.app/reset-password?token={token_obj.token}"
    context = {
        'reset_url': reset_url,
        'expires_hours': 2,
        'user_full_name': user.full_name,
    }
    
    html_content = render_to_string('emails/password_reset.html', context)
    
    # Email subject - convert to string for Resend API
    subject = force_str(_("Reset your Swiftnote password"))

    try:
        resend.Emails.send({
            "from": "Swiftnote <onboarding@resend.dev>",
            "to": [user.email],
            "subject": subject,
            "html": html_content,
        })
        return True, force_str(_("Password reset email sent successfully"))
    except Exception as e:
        return False, str(e)