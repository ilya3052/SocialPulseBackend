import threading
from smtplib import SMTPException

from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from SocialPulse import settings
from accounts.models import CustomUser, EmailActivate
from accounts.utils import generate_short_token, prepare_message


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


class EmailSendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user: CustomUser = self.get_object()
        email = user.email
        token = generate_short_token()
        message = prepare_message(token)

        email_activate_instance = EmailActivate.objects.filter(user=user).first()
        if email_activate_instance:
            email_activate_instance.delete()

        EmailActivate.objects.create(user=user, token=token)

        try:
            threading.Thread(
                target=send_confirmation_email,
                args=(message, email),
                daemon=True
            ).start()
        except SMTPException as smtp:
            return Response({"smtp_error": smtp})
        return Response({"status": "Письмо с подтверждением отправлено"}, status=status.HTTP_200_OK)


class EmailActivationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        token_pair: EmailActivate = EmailActivate.objects.filter(token=token).first()
        if not token_pair:
            return Response({"token": "Произошла ошибка при обработке токена"}, status=status.HTTP_410_GONE)

        if token_pair.expires_at < timezone.now():
            token_pair.delete()
            return Response({"error": "Время действия ссылки истекло, отправьте подтверждение заново"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = token_pair.user
        user.is_email_confirmed = True
        user.save()
        token_pair.delete()
        return Response({"status": "Email подтвержден"}, status=status.HTTP_200_OK)
