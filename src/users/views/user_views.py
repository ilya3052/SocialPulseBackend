from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.module_loading import import_string
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import UserRegisterSerializer, CustomUserSerializer, UserPasswordSerializer, \
    UserSetPasswordSerializer, UserSocialDataSerializer

User = get_user_model()


class UserAPIRegistration(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
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
            "tokens": tokens,
        }, status=status.HTTP_201_CREATED)


class UserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=request.user.id)

        vk_tokens_model = import_string("social_auth.models.VKTokens")
        vk_tokens_serializer = import_string("social_auth.serializers.vk_serializers.VKTokensSerializer")
        token_serializer = None

        if user.vk_id:
            tokens = vk_tokens_model.objects.filter(user=user).first()
            token_serializer = vk_tokens_serializer(tokens)

        tokens = None

        if token_serializer:
            tokens = token_serializer.data

        serializer = CustomUserSerializer(user)
        has_password = user.has_usable_password()
        return Response({"data": serializer.data, "has_password": has_password, "tokens": tokens}, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=request.user.id)

        if request.data.get('tg_id', None):
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


class UserSetPasswordView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSetPasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()

        serializer = self.get_serializer(user, data=request.data, context={"request": request})

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


class UserSocialDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSocialDataSerializer(self.request.user, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)
