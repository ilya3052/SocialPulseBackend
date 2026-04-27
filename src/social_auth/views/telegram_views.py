from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_telegram_login.authentication import verify_telegram_authentication
from django_telegram_login.errors import NotTelegramDataError, TelegramDataIsOutdatedError
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from social_auth.models import TelegramToken
from social_auth.serializers import TelegramBindingSerializer, TelegramTokenPairSerializer
from social_pulse import settings

User = get_user_model()


class TelegramBindingView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TelegramBindingSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        if request.data.get('tg_id', None):
            users = User.objects.filter(tg_id=request.data.get('tg_id'))
            if users:
                return Response(
                    {"error": "Произошла ошибка при привязке аккаунта, проверьте правильность введенных данных"},
                    status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(user, data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(status=status.HTTP_200_OK)


class TelegramCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        data = request.GET.dict()
        str_data = {k: str(v) for k, v in data.items()}
        try:
            is_valid = verify_telegram_authentication(
                bot_token=settings.TELEGRAM_BOT_TOKEN,
                request_data=str_data
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
                user.set_unusable_password()
                user.save()
            except IntegrityError as ie:
                return Response({'error': f'Ошибка создания пользователя: {str(ie)}'},
                                status=status.HTTP_400_BAD_REQUEST)

        # попытаться получить актуальные токены для юзера если он существует
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


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

        access = token_pair.access_token
        refresh = token_pair.refresh_token
        token_pair.delete()
        return Response({
            "access": access,
            "refresh": refresh,
        }, status=status.HTTP_200_OK)
