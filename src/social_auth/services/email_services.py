from django.core.mail import send_mail

from social_pulse import settings


def send_confirmation_email(message, email):
    try:
        send_mail(
            subject="Подтверждение электронной почты",
            message="",
            html_message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False)
    except Exception:
        raise
