# mensa_member_connect/utils/email_utils.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging
import os
import requests

logger = logging.getLogger(__name__)


def send_email_via_mailgun_api(
    to_email: str,
    subject: str,
    text_content: str,
    html_content: str = None,
    from_email: str = None,
    reply_to: str = None
) -> bool:
    """
    Send email using Mailgun HTTP API (more reliable than SMTP in cloud environments).
    
    Returns True if successful, False otherwise.
    """
    # Get Mailgun API credentials from environment
    mailgun_api_key = os.environ.get("MAILGUN_API_KEY")
    mailgun_domain = os.environ.get("MAILGUN_DOMAIN") or os.environ.get("MAILGUN_SENDING_DOMAIN")
    
    if not mailgun_api_key or not mailgun_domain:
        logger.warning(
            "[EMAIL] Mailgun API credentials not configured. "
            "Set MAILGUN_API_KEY and MAILGUN_DOMAIN environment variables."
        )
        return False
    
    # Determine Mailgun API endpoint (US or EU)
    mailgun_region = os.environ.get("MAILGUN_REGION", "us").lower()
    if mailgun_region == "eu":
        api_url = f"https://api.eu.mailgun.net/v3/{mailgun_domain}/messages"
    else:
        api_url = f"https://api.mailgun.net/v3/{mailgun_domain}/messages"
    
    # Use provided from_email or default
    from_address = from_email or settings.DEFAULT_FROM_EMAIL
    
    # Prepare the request
    # Note: Mailgun API expects "to" as a string, not a list
    data = {
        "from": from_address,
        "to": to_email,
        "subject": subject,
        "text": text_content,
    }
    
    if html_content:
        data["html"] = html_content
    
    # Add reply-to header if provided
    if reply_to:
        data["h:Reply-To"] = reply_to
    
    try:
        response = requests.post(
            api_url,
            auth=("api", mailgun_api_key),
            data=data,
            timeout=10  # HTTP API is much faster than SMTP
        )
        
        if response.status_code == 200:
            logger.info("[EMAIL] Successfully sent email via Mailgun API to %s", to_email)
            return True
        else:
            logger.error(
                "[EMAIL] Mailgun API error: Status %s, Response: %s",
                response.status_code,
                response.text
            )
            return False
            
    except requests.exceptions.Timeout:
        logger.error("[EMAIL] Mailgun API request timed out")
        return False
    except requests.exceptions.RequestException as e:
        logger.error("[EMAIL] Mailgun API request failed: %s", e)
        return False


def notify_admin_new_registration(user_email, user_name, first_name=None, last_name=None):
    """
    Notify admin that a new user registered and is awaiting approval.
    """
    context = {
        'user_email': user_email,
        'user_name': user_name,
        'first_name': first_name or '',
        'last_name': last_name or '',
    }
    
    subject = render_to_string('emails/admin_new_registration_subject.txt', context).strip()
    text_content = render_to_string('emails/admin_new_registration.txt', context)
    html_content = render_to_string('emails/admin_new_registration.html', context)
    
    logger.info(
        "[EMAIL] Attempting to notify admin (%s) about new user: %s",
        settings.ADMIN_EMAIL,
        user_email,
    )

    # Try Mailgun API first (more reliable), fall back to SMTP
    use_mailgun_api = os.environ.get("USE_MAILGUN_API", "True").lower() in ("1", "true", "yes")
    
    if use_mailgun_api:
        success = send_email_via_mailgun_api(
            to_email=settings.ADMIN_EMAIL,
            subject=subject,
            text_content=text_content,
            html_content=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL
        )
        if success:
            return
        logger.warning("[EMAIL] Mailgun API failed, falling back to SMTP")
    
    # Fallback to SMTP
    try:
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],  # set ADMIN_EMAIL in settings.py
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(
            "[EMAIL] Successfully sent notification to %s",
            settings.ADMIN_EMAIL,
        )
    except Exception as e:
        logger.error(
            "[EMAIL] Failed to send notification to admin: %s",
            e,
        )


def notify_user_registration(user_email, user_name, first_name=None, last_name=None):
    """
    Notify the new user that their registration was received and is awaiting approval.
    """
    context = {
        'user_email': user_email,
        'user_name': user_name,
        'first_name': first_name or '',
        'last_name': last_name or '',
    }
    
    subject = render_to_string('emails/user_registration_subject.txt', context).strip()
    text_content = render_to_string('emails/user_registration.txt', context)
    html_content = render_to_string('emails/user_registration.html', context)

    logger.info(
        "[EMAIL] Attempting to send registration confirmation to %s", user_email
    )

    # Try Mailgun API first (more reliable), fall back to SMTP
    use_mailgun_api = os.environ.get("USE_MAILGUN_API", "True").lower() in ("1", "true", "yes")
    
    if use_mailgun_api:
        success = send_email_via_mailgun_api(
            to_email=user_email,
            subject=subject,
            text_content=text_content,
            html_content=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL
        )
        if success:
            return
        logger.warning("[EMAIL] Mailgun API failed, falling back to SMTP")
    
    # Fallback to SMTP
    try:
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(
            "[EMAIL] Successfully sent registration confirmation to %s", user_email
        )
    except Exception as e:
        logger.error(
            "[EMAIL] Failed to send registration confirmation to %s: %s", user_email, e
        )


def notify_user_approval(user_email, user_name, first_name=None, last_name=None):
    """
    Send an email to a user notifying them that their account has been approved.
    """
    context = {
        'user_email': user_email,
        'user_name': user_name,
        'first_name': first_name or '',
        'last_name': last_name or '',
    }
    
    subject = render_to_string('emails/user_approval_subject.txt', context).strip()
    text_content = render_to_string('emails/user_approval.txt', context)
    html_content = render_to_string('emails/user_approval.html', context)

    logger.info("[EMAIL] Attempting to send account approval email to %s", user_email)

    # Try Mailgun API first (more reliable), fall back to SMTP
    use_mailgun_api = os.environ.get("USE_MAILGUN_API", "True").lower() in ("1", "true", "yes")
    
    if use_mailgun_api:
        success = send_email_via_mailgun_api(
            to_email=user_email,
            subject=subject,
            text_content=text_content,
            html_content=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL
        )
        if success:
            return
        logger.warning("[EMAIL] Mailgun API failed, falling back to SMTP")
    
    # Fallback to SMTP
    try:
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(
            "[EMAIL] Successfully sent account approval email to %s", user_email
        )
    except Exception as e:
        logger.error(
            "[EMAIL] Failed to send account approval email to %s: %s", user_email, e
        )


def notify_expert_new_message(
    expert_email: str, 
    seeker_name: str, 
    message: str, 
    seeker_first_name=None, 
    seeker_last_name=None,
    seeker_email=None,
    local_group_name=None,
    preferred_contact_method=None
):
    # Format preferred contact method for display
    contact_method_display = ''
    if preferred_contact_method:
        contact_method_map = {
            'email': 'Email',
            'phone': 'Phone call',
            'video_call': 'Video call (Zoom, etc.)',
            'in_person': 'In-person meeting',
            'other': 'Other (specify in message)'
        }
        contact_method_display = contact_method_map.get(preferred_contact_method, preferred_contact_method)
    
    context = {
        'expert_email': expert_email,
        'seeker_name': seeker_name,
        'seeker_first_name': seeker_first_name or '',
        'seeker_last_name': seeker_last_name or '',
        'seeker_email': seeker_email or '',
        'local_group_name': local_group_name or '',
        'preferred_contact_method': preferred_contact_method or '',
        'preferred_contact_method_display': contact_method_display,
        'message': message,
    }
    
    subject = render_to_string('emails/expert_new_message_subject.txt', context).strip()
    text_content = render_to_string('emails/expert_new_message.txt', context)
    html_content = render_to_string('emails/expert_new_message.html', context)
    
    logger.info(
        "[EMAIL] Attempting to send new connection request email to %s from %s",
        expert_email,
        seeker_name,
    )

    # Try Mailgun API first (more reliable), fall back to SMTP
    use_mailgun_api = os.environ.get("USE_MAILGUN_API", "True").lower() in ("1", "true", "yes")
    
    if use_mailgun_api:
        success = send_email_via_mailgun_api(
            to_email=expert_email,
            subject=subject,
            text_content=text_content,
            html_content=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            reply_to=seeker_email if seeker_email else None
        )
        if success:
            return
        logger.warning("[EMAIL] Mailgun API failed, falling back to SMTP")
    
    # Fallback to SMTP
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[expert_email],
            reply_to=[seeker_email] if seeker_email else [],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(
            "[EMAIL] Successfully sent new connection request email to %s from %s",
            expert_email,
            seeker_name,
        )
    except Exception as e:
        logger.error(
            "[EMAIL] Failed to send new connection request email to %s from %s: %s",
            expert_email,
            seeker_name,
            e,
        )


def send_password_reset_email(user_email: str, user_name: str, reset_link: str, first_name=None, last_name=None):
    """
    Sends a password reset email to the user with the given reset link.

    Args:
        user_email: The recipient's email address.
        user_name: The recipient's full name.
        reset_link: The URL for the password reset.
        first_name: The recipient's first name (optional).
        last_name: The recipient's last name (optional).
    """
    context = {
        'user_email': user_email,
        'user_name': user_name,
        'first_name': first_name or '',
        'last_name': last_name or '',
        'reset_link': reset_link,
    }
    
    subject = render_to_string('emails/password_reset_subject.txt', context).strip()
    text_content = render_to_string('emails/password_reset.txt', context)
    html_content = render_to_string('emails/password_reset.html', context)

    logger.info("[EMAIL] Attempting to send password reset email to %s", user_email)

    # Try Mailgun API first (more reliable), fall back to SMTP
    use_mailgun_api = os.environ.get("USE_MAILGUN_API", "True").lower() in ("1", "true", "yes")
    
    if use_mailgun_api:
        success = send_email_via_mailgun_api(
            to_email=user_email,
            subject=subject,
            text_content=text_content,
            html_content=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL
        )
        if success:
            return
        # If API fails, fall through to SMTP as backup
        logger.warning("[EMAIL] Mailgun API failed, falling back to SMTP")
    
    # Fallback to SMTP
    try:
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info("[EMAIL] Successfully sent password reset email to %s", user_email)
    except Exception as e:
        # Log the error but don't raise - let the calling function handle it
        logger.error(
            "[EMAIL] Failed to send password reset email to %s: %s", user_email, e
        )
        # Re-raise so calling code knows email failed (but can still return success to user)
        raise
