from rest_framework import serializers

from social_auth.models import EmailActivate


class EmailActivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailActivate
        fields = ('user', 'token')
        read_only_fields = ('user',)
