import requests
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from social_auth.models import VKTokens

User = get_user_model()


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
                user.set_unusable_password()
                user.save()
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

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        data = request.data
        user = self.get_object()
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
        response = req.json().get('response')[0]
        old_user = User.objects.filter(vk_id=response.get('id')).first()
        if old_user:
            old_user.delete()
        user.vk_id = response.get('id')
        user.vk_link = 'https://vk.ru/' + response.get('screen_name')
        user.save()
        return Response(status=status.HTTP_200_OK)
