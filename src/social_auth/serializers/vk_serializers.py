from rest_framework import serializers

from social_auth.models import VKTokens


class VKTokensSerializer(serializers.ModelSerializer):
    class Meta:
        model = VKTokens
        fields = ('access_vk_token', 'refresh_vk_token', 'id_vk_token')
