from rest_framework import serializers

from accounts.models import TelegramToken
from accounts.utils import generate_short_token


class TelegramTokenPairSerializer(serializers.Serializer):
    access_token = serializers.CharField(write_only=True, max_length=512)
    refresh_token = serializers.CharField(write_only=True, max_length=512)

    class Meta:
        model = TelegramToken
        fields = ('user', 'access_token', 'refresh_token')
        read_only_fields = ('short_token',)

    def create(self, validated_data):
        user = self.context['request'].user
        access_token = self.validated_data['access_token']
        refresh_token = self.validated_data['refresh_token']
        short_token = generate_short_token()

        TelegramToken.objects.filter(user=user).delete()

        token_pair = TelegramToken.objects.create(user=user, access_token=access_token, refresh_token=refresh_token,
                                                  short_token=short_token)
        return token_pair


class TelegramBindingSerializer(serializers.Serializer):
    tg_id = serializers.CharField(write_only=True, allow_null=True, allow_blank=True)
    tg_link = serializers.CharField(write_only=True, allow_null=True, allow_blank=True)

    def update(self, instance, validated_data):
        instance.tg_id = validated_data.get('tg_id', instance.tg_id)
        instance.tg_link = validated_data.get('tg_link', instance.tg_link)
        instance.save()
        return instance
