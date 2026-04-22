from icecream import ic
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
    def get_fields(self):
        fields = super().get_fields()
        exclude_fields = self.context.get('exclude_fields', [])
        for field in exclude_fields:
            fields.pop(field, None)
        return fields

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

    def update(self, instance, validated_data):
        instance.is_activated = validated_data.get('is_activated')
        instance.save()
        return instance

    class Meta:
        model = ServiceAccount
        fields = ('id', 'name', 'platform_id', 'is_activated', 'data', 'groups', 'groups_count')


