"""
Celery tasks for the users app.
Background tasks for user management and notifications.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, user_id):
    """
    Send a welcome email to a newly registered user.

    Args:
        user_id: The ID of the user to send the email to
    """
    try:
        from users.models import User

        user = User.objects.get(id=user_id)

        subject = 'Welcome to APN & SIM Management System'
        message = f"""
        Hello {user.first_name or user.username},

        Welcome to the APN & SIM Management System!

        Your account has been successfully created for {user.organization.name if user.organization else 'the system'}.

        You can now log in and start managing your SIM inventory.

        Best regards,
        The Backspace Technologies Team
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        logger.info(f"Welcome email sent to user {user.username}")
        return {'status': 'success', 'user_id': user_id}

    except Exception as exc:
        logger.error(f"Error sending welcome email to user {user_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, user_id, reset_token):
    """
    Send a password reset email to a user.

    Args:
        user_id: The ID of the user
        reset_token: The password reset token
    """
    try:
        from users.models import User

        user = User.objects.get(id=user_id)

        subject = 'Password Reset Request'
        message = f"""
        Hello {user.first_name or user.username},

        You have requested to reset your password for the APN & SIM Management System.

        Your reset token: {reset_token}

        If you did not request this, please ignore this email.

        Best regards,
        The Backspace Technologies Team
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        logger.info(f"Password reset email sent to user {user.username}")
        return {'status': 'success', 'user_id': user_id}

    except Exception as exc:
        logger.error(f"Error sending password reset email to user {user_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def cleanup_inactive_users():
    """
    Periodic task to clean up inactive user accounts.
    Run this task daily to deactivate users who haven't logged in for 90 days.
    """
    from users.models import User
    from django.utils import timezone
    from datetime import timedelta

    ninety_days_ago = timezone.now() - timedelta(days=90)

    inactive_users = User.objects.filter(
        last_login__lt=ninety_days_ago,
        is_active=True
    )

    count = inactive_users.count()
    inactive_users.update(is_active=False)

    logger.info(f"Deactivated {count} inactive users")
    return {'status': 'success', 'deactivated_count': count}
