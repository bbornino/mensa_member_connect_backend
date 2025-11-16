# mensa_member_connect/utils/email_utils.py

from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def notify_admin_new_registration(user_email, user_name):
    """
    Notify admin that a new user registered and is awaiting approval.
    """
    subject = f"New MENSA Registration Awaiting Approval: {user_name}"
    message = f"A new user has registered with email: {user_email}.\nPlease review and approve."
    logger.info(
        "[EMAIL] Attempting to notify admin (%s) about new user: %s",
        settings.ADMIN_EMAIL,
        user_email,
    )

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],  # set ADMIN_EMAIL in settings.py
            fail_silently=False,
        )
        logger.info(
            "[EMAIL] Successfully sent notification to %s",
            settings.ADMIN_EMAIL,
        )
    except Exception as e:
        logger.error(
            "[EMAIL] Failed to send notification to admin: %s",
            e,
        )


def notify_user_registration(user_email, user_name):
    """
    Notify the new user that their registration was received and is awaiting approval.
    """
    subject = "MENSA Registration Received"
    message = (
        f"Hello {user_name},\n\n"
        "Thank you for registering with MENSA. Your account is awaiting approval by our team. "
        "You will be notified once it is active.\n\n"
        "Best regards,\nThe MENSA Team"
    )

    logger.info(
        "[EMAIL] Attempting to send registration confirmation to %s", user_email
    )

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        logger.info(
            "[EMAIL] Successfully sent registration confirmation to %s", user_email
        )
    except Exception as e:
        logger.error(
            "[EMAIL] Failed to send registration confirmation to %s: %s", user_email, e
        )


def notify_user_approval(user_email, user_name):
    """
    Send an email to a user notifying them that their account has been approved.
    """
    subject = "Your MENSA account has been approved!"
    message = f"Hi {user_name},\n\nYour account has been approved by the MENSA admin. You can now log in and start connecting with others.\n\nWelcome aboard!\n\n– MENSA Team"

    logger.info("[EMAIL] Attempting to send account approval email to %s", user_email)

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        logger.info(
            "[EMAIL] Successfully sent account approval email to %s", user_email
        )
    except Exception as e:
        logger.error(
            "[EMAIL] Failed to send account approval email to %s: %s", user_email, e
        )


def notify_expert_new_message(expert_email: str, seeker_name: str, message: str):
    subject = f"New Connection Request from {seeker_name}"
    body = f"You have received a new connection request:\n\nFrom: {seeker_name}\nMessage: {message}"
    logger.info(
        "[EMAIL] Attempting to send new connection request email to %s from %s",
        expert_email,
        seeker_name,
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[expert_email],
            fail_silently=False,
        )
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
