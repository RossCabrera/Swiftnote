from datetime import timedelta

import resend
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from .models import EmailVerificationToken

resend.api_key = settings.RESEND_API_KEY

def send_verification_email(user):
    # Check for tokens created in the last 60 seconds
    recent_token = EmailVerificationToken.objects.filter(
        user=user, 
        created_at__gte=timezone.now() - timedelta(minutes=1)
    ).exists()
    
    if recent_token:
        return False, "Please wait a minute before requesting another email."

    # Create the Token 
    token_obj = EmailVerificationToken.objects.create(user=user)
    
    # Prepare the Email
    verify_url = f"https://swiftnote.app/verify?token={token_obj.token}"
    context = {
        'user_email': user.email,
        'verify_url': verify_url,
    }
    
    html_content = render_to_string('emails/verify_email.html', context)

    params = {
        "from": "Swiftnote <onboarding@resend.dev>",
        "to": [user.email],
        "subject": "Confirm your email for Swiftnote",
        "html": html_content,
    }

    try:
        resend.Emails.send({
            "from": "Swiftnote <onboarding@resend.dev>",
            "to": [user.email],
            "subject": "Confirm your email for Swiftnote",
            "html": html_content,
        })
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)