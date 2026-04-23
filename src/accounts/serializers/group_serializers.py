from rest_framework import serializers

from accounts.models import CustomUser, Group
from .user_serializers import CustomUserSerializer
from admin_panel.models import Platform, ServiceAccount


class GroupSerializer(serializers.ModelSerializer):
    platform = serializers.SerializerMethodField(read_only=True)

    platform_id = serializers.PrimaryKeyRelatedField(
        queryset=Platform.objects.all(),
        source='platform',
        write_only=True
    )
    user = CustomUserSerializer(read_only=True, many=True)  # а надо ли возвращать?
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='user',
        many=True,
        write_only=True
    )

    service_account_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceAccount.objects.all(),
        source='service_account'
    )

    def get_platform(self, obj: Group):
        if not obj.platform:
            return None
        from admin_panel.serializers import PlatformSerializer
        serializer = PlatformSerializer(obj.platform, context=self.context)
        return serializer.data

    class Meta:
        model = Group
        fields = ('id', 'name', 'link', 'external_id', 'added_at',
                  'platform_id', 'platform',
                  'user', 'user_id',
                  'service_account_id')
