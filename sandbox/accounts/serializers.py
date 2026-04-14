from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import CustomUser, TelegramToken, EmailActivate, Platform, Group, ServiceAccount, \
    ServiceAccountData
from accounts.utils import generate_short_token


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('Passwords don\'t match')
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2', None)
        email = validated_data.pop('email')
        user = CustomUser.objects.create_user(**validated_data, password=password, email=email)
        return user


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


class UserPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)
    new_password = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": 'Пароли не совпадают.'})

        if data["old_password"] == data["new_password"]:
            raise serializers.ValidationError({
                "new_password": "Новый пароль не должен совпадать со старым."
            })

        validate_password(data['new_password'])

        return data


class UserSetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)

    def validate(self, data):
        request = self.context.get('request')

        if request.user.has_usable_password():
            raise serializers.ValidationError({"password_error": "Невозможно установить пароль!"})

        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": 'Пароли не совпадают.'})

        validate_password(data['new_password'])
        return data


class TelegramBindingSerializer(serializers.Serializer):
    tg_id = serializers.CharField(write_only=True, allow_null=True, allow_blank=True)
    tg_link = serializers.CharField(write_only=True, allow_null=True, allow_blank=True)

    def update(self, instance, validated_data):
        instance.tg_id = validated_data.get('tg_id', instance.tg_id)
        instance.tg_link = validated_data.get('tg_link', instance.tg_link)
        instance.save()
        return instance


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # поле пароля оставить только в разработке, в идеале его быть не должно
        fields = ('id', 'first_name', 'password', 'last_name', 'username',
                  'email', 'tg_link', 'vk_link', 'tg_id', 'vk_id', 'is_email_confirmed')
        read_only_fields = ('id', 'password')

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)

        instance.tg_link = validated_data.get('tg_link', instance.tg_link)
        instance.tg_id = validated_data.get('tg_id', instance.tg_id)

        instance.vk_id = validated_data.get('vk_id', instance.vk_id)
        instance.vk_link = validated_data.get('vk_link', instance.vk_link)

        instance.save()
        return instance


class EmailActivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailActivate
        fields = ('user', 'token')
        read_only_fields = ('user',)


# после завершения перенести в другое приложение аналогично моделям

class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ('id', 'name', 'alias')


class GroupSerializer(serializers.ModelSerializer):
    platform = PlatformSerializer(read_only=True)
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

    class Meta:
        model = Group
        fields = ('name', 'link', 'external_id', 'added_at',
                  'platform_id', 'platform',
                  'user', 'user_id',
                  'service_account_id')


class ServiceAccountDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceAccountData
        fields = ('service_key', 'protected_key', 'phone_number', 'session_path')


class ServiceAccountSerializer(serializers.ModelSerializer):
    data = ServiceAccountDataSerializer()
    groups = GroupSerializer(many=True, read_only=True)
    platform_id = serializers.PrimaryKeyRelatedField(
        queryset=Platform.objects.all(),
        source='platform'
    )

    def create(self, validated_data):
        data = validated_data.pop('data')
        service_account = ServiceAccount.objects.create(**validated_data)
        ServiceAccountData.objects.create(account=service_account, **data)
        return service_account

    class Meta:
        model = ServiceAccount
        fields = ('id', 'name', 'platform_id', 'data', 'groups')


class UserSocialDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('tg_link', 'vk_link')
