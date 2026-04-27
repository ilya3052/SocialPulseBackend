from django.contrib.auth import get_user_model
from rest_framework import serializers

from service_accounts.models import ServiceAccount
from users.serializers import CustomUserSerializer

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    from social_entities.models import Platform

    platform = serializers.SerializerMethodField(read_only=True)

    platform_id = serializers.PrimaryKeyRelatedField(
        queryset=Platform.objects.all(),
        source='platform',
        write_only=True
    )
    user = CustomUserSerializer(read_only=True, many=True)  # а надо ли возвращать?
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        many=True,
        write_only=True
    )

    service_account_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceAccount.objects.all(),
        source='service_account'
    )

    def get_platform(self, obj):
        from social_entities.serializers import PlatformSerializer

        if not obj.platform:
            return None
        serializer = PlatformSerializer(obj.platform, context=self.context)
        return serializer.data

    class Meta:
        from social_entities.models import Group

        model = Group
        fields = ('id', 'name', 'link', 'external_id', 'added_at',
                  'platform_id', 'platform',
                  'user', 'user_id',
                  'service_account_id')
