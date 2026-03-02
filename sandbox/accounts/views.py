import json
import logging
from smtplib import SMTPException

from django.contrib.auth import get_user_model
from django.contrib.sites import requests
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_telegram_login.authentication import verify_telegram_authentication
from django_telegram_login.errors import NotTelegramDataError, TelegramDataIsOutdatedError
from icecream import ic
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

import requests

from sandbox import settings
from .logger import setup_logger
from .models import TelegramToken, CustomUser, EmailActivate, VKTokens
from .serializers import CustomUserSerializer, UserRegisterSerializer, TelegramTokenPairSerializer, \
    UserPasswordSerializer, TelegramBindingSerializer
from .utils import generate_short_token, prepare_message, try_parse_json

User: CustomUser = get_user_model()

logger = setup_logger(log_file="sandbox/logs/debug.log")

class UserAPIRegistration(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        ic(request.data)
        serializer = UserRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
            },
            "tokens": tokens,
        }, status=status.HTTP_201_CREATED)


class UserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=request.user.id)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=request.user.id)

        # по идее этот сценарий срабатывает лишь в одном случае - в случае привязки аккаунта тг к текущему
        # если пользователь имеет созданный обычный аккаунт и также он авторизовался через тг то у него создано два аккаунта
        # и при привязке тг аккаунта к созданному аккаунту (без тг) аккаунт авторизованный через тг удаляется

        if request.data.get('tg_id', None):
            old_user = User.objects.filter(tg_id=request.data.get('tg_id')).first()
            if old_user:
                old_user.delete()

        if request.data.get('vk_id', None):

            old_user = User.objects.filter(vk_id=request.data.get('vk_id')).first()
            if old_user:
                old_user.delete()

        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangePasswordView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()

        serializer = self.get_serializer(user, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        if not user.check_password(serializer.validated_data.get("old_password")):
            return Response({"wrong_old_password": "Неверно указан старый пароль"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data.get("new_password"))
        user.save()

        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

        outstanding_tokens = OutstandingToken.objects.filter(user=user, expires_at__gt=timezone.now())
        for token in outstanding_tokens:
            BlacklistedToken.objects.get_or_create(token=token)

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_200_OK)


class TelegramBindingView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TelegramBindingSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        print('данные вне условия')
        print(request.data)
        if request.data.get('tg_id', None):
            print('данные внутри условия')
            print(request.data)
            users = User.objects.filter(tg_id=request.data.get('tg_id'))
            if users:
                return Response(
                    {"error": "Произошла ошибка при привязке аккаунта, проверьте правильность введенных данных"},
                    status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(user, data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class TelegramCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        data = request.GET.dict()
        try:
            is_valid = verify_telegram_authentication(
                bot_token=settings.TELEGRAM_BOT_TOKEN,
                request_data=data
            )

        except (NotTelegramDataError, TelegramDataIsOutdatedError) as error:
            return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        if not is_valid:
            return Response({'error': 'Некорректные данные Telegram'}, status=status.HTTP_400_BAD_REQUEST)

        telegram_id = data.get('id')
        username = 'tg_' + data.get('username', telegram_id)
        first_name = data.get('first_name', '')
        try:
            user = User.objects.get(tg_id=telegram_id)
        except User.DoesNotExist:
            try:
                user = User.objects.create(
                    tg_id=telegram_id,
                    tg_link='https://t.me/' + username.split('_')[1],
                    first_name=first_name,
                    username=username,
                )
            except IntegrityError as ie:
                return Response({'error': f'Ошибка создания пользователя: {str(ie)}'},
                                status=status.HTTP_400_BAD_REQUEST)

        # попытаться получить актуальные токены для юзера если он существует
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            'access': str(refresh.access_token),
            'user' : {
                'id': user.id,
                'username': user.username,
            }
        }, status=status.HTTP_200_OK)


class VKCallbackView(APIView):

    def post(self, request, *args, **kwargs):
        internal_data = request.data

        internal_access_token = internal_data.get('access_token')
        internal_id_token = internal_data.get('id_token')
        internal_refresh_token = internal_data.get('refresh_token')
        expires_in = internal_data.get('expires_in')

        params = {
            'fields': 'screen_name',
            'v': 5.199
        }
        headers = {
            'Authorization': f'Bearer {internal_access_token}',
        }

        req = requests.get(
            'https://api.vk.ru/method/users.get',
            headers=headers,
            params=params
        )

        data = req.json().get('response')[0]
        vk_id = data.get('id')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        screen_name = data.get('screen_name')

        try:
            user = User.objects.get(vk_id=vk_id)
        except User.DoesNotExist:
            try:
                user = User.objects.create(
                    username='vk_' + screen_name,
                    first_name=first_name,
                    last_name=last_name,
                    vk_id=vk_id,
                    vk_link='https://vk.ru/' + screen_name,
                )
            except IntegrityError as ie:
                return Response({'error': f'Ошибка создания пользователя: {str(ie)}'},
                                status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)

        vk_token_instance = VKTokens.objects.filter(user=user).first()

        if vk_token_instance and timezone.timedelta(
                vk_token_instance.expires_in) + vk_token_instance.added_at < timezone.now():
            vk_token_instance.delete()

            VKTokens.objects.create(
                user=user,
                refresh_vk_token=internal_refresh_token,
                id_vk_token=internal_id_token,
                access_vk_token=internal_access_token,
                expires_in=expires_in,
            )

        if not vk_token_instance:
            VKTokens.objects.create(
                user=user,
                refresh_vk_token=internal_refresh_token,
                id_vk_token=internal_id_token,
                access_vk_token=internal_access_token,
                expires_in=expires_in,
            )

        return Response({'request': {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'vk_id': str(vk_id),
        }}, status=status.HTTP_200_OK)


class VKCallbackUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data

        access_token = data.get('vk_token')
        params = {
            'fields': 'screen_name',
            'v': 5.199
        }
        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        req = requests.get(
            'https://api.vk.ru/method/users.get',
            headers=headers,
            params=params
        )
        ic(req.json())
        response = req.json().get('response')[0]
        return Response({'username': response.get('screen_name')}, status=status.HTTP_200_OK)


class TelegramTokenPairView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = TelegramTokenPairSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token_pair = serializer.save()
        return Response({
            "short_token": token_pair.short_token,
        }, status=status.HTTP_201_CREATED)


class TelegramConvertTokenView(APIView):
    def post(self, request, *args, **kwargs):
        token_pair = get_object_or_404(TelegramToken, short_token=request.data['token'])
        if token_pair.expires_at < timezone.now():
            token_pair.delete()
            return Response({"error": "Время жизни токена истекло"}, status=status.HTTP_400_BAD_REQUEST)

        access = token_pair.jwt_token
        token_pair.delete()
        return Response({"access": access}, status=status.HTTP_200_OK)


class EmailSendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user: CustomUser = self.get_object()
        email = user.email
        token = generate_short_token()
        message = prepare_message(token)
        try:
            send_mail(
                subject="Подтверждение электронной почты",
                message="",
                html_message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False)
        except SMTPException as smtp:
            return Response({"smtp_error": smtp})

        email_activate_instance = EmailActivate.objects.filter(user=user).first()
        if email_activate_instance:
            email_activate_instance.delete()

        EmailActivate.objects.create(user=user, token=token)

        return Response({"status": "Письмо с подтверждением отправлено"}, status=status.HTTP_200_OK)


class EmailActivationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        token_pair: EmailActivate = EmailActivate.objects.filter(token=token).first()
        if not token_pair:
            return Response({"error": "Произошла ошибка при подтверждении email"}, status=status.HTTP_400_BAD_REQUEST)

        if token_pair.expires_at < timezone.now():
            token_pair.delete()
            return Response({"error": "Время действия ссылки истекло, отправьте подтверждение заново"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = token_pair.user
        user.is_email_confirmed = True
        user.save()
        token_pair.delete()
        return Response({"status": "Email подтвержден"}, status=status.HTTP_200_OK)


class DebugView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data

        # пробуем распарсить вложенные JSON-строки
        parsed_data = {
            key: try_parse_json(value)
            for key, value in data.items()
        }

        formatted_json = json.dumps(
            parsed_data,
            indent=4,
            ensure_ascii=False
        )

        logger.debug("Incoming request data:\n%s", formatted_json)

        return Response({"status": "ok"}, status=status.HTTP_200_OK)
