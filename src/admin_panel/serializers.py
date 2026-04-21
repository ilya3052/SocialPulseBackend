from rest_framework import serializers

from admin_panel.models import Platform, ServiceAccountData, ServiceAccount


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ('id', 'name', 'alias')

class ServiceAccountDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceAccountData
        fields = ('service_key', 'protected_key', 'phone_number', 'session_path')


class ServiceAccountSerializer(serializers.ModelSerializer):
    data = ServiceAccountDataSerializer()
    groups = serializers.SerializerMethodField(read_only=True)
    groups_count = serializers.IntegerField(read_only=True)
    platform_id = serializers.PrimaryKeyRelatedField(
        queryset=Platform.objects.all(),
        source='platform'
    )

    def create(self, validated_data):
        data = validated_data.pop('data')
        service_account = ServiceAccount.objects.create(**validated_data)
        ServiceAccountData.objects.create(account=service_account, **data)
        return service_account

    def get_groups(self, obj):
        from accounts.serializers import GroupSerializer
        groups = obj.groups.all()
        serializer = GroupSerializer(groups, many=True, context=self.context)
        return serializer.data

    class Meta:
        model = ServiceAccount
        fields = ('id', 'name', 'platform_id', 'data', 'groups', 'groups_count')