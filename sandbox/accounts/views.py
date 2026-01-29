from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_telegram_login.authentication import verify_telegram_authentication
from django_telegram_login.errors import NotTelegramDataError, TelegramDataIsOutdatedError
from rest_framework import status, generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from sandbox import settings
from .models import TelegramToken, CustomUser
from .serializers import CustomUserSerializer, UserRegisterSerializer, TelegramTokenPairSerializer, \
    UserPasswordSerializer, TelegramBindingSerializer

from icecream import ic

User: CustomUser = get_user_model()


class UserAPIRegistration(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
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


class UserAPIUpdate(APIView):
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

        if request.data.get('tg_id'):
            old_user = User.objects.filter(tg_id=request.data.get('tg_id')).first()
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
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.validated_data.get("old_password")):
            return Response({"error": "Неверный старый пароль"}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response({"error": "Произошла ошибка при привязке аккаунта, проверьте правильность введенных данных"}, status=status.HTTP_400_BAD_REQUEST)

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
        try:
            user = User.objects.get(tg_id=telegram_id)
        except User.DoesNotExist:
            try:
                user = User.objects.create(
                    tg_id=telegram_id,
                    tg_link='https://t.me/' + data.get('username', telegram_id),
                    first_name=data.get('first_name', ''),
                    username=data.get('username', f'tg_{telegram_id}'),
                )
            except IntegrityError as ie:
                return Response({'error': f'Ошибка создания пользователя: {str(ie)}'},
                                status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            'access': str(refresh.access_token),
            # 'user' : {
            #     'id': user.id,
            #     'username': user.username,
            # }
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

        access = token_pair.jwt_token
        token_pair.delete()
        return Response({"access": access}, status=status.HTTP_200_OK)


class EmailActivationView(APIView):
    permission_classes = [AllowAny]
    # def post(self, request, *args, **kwargs):