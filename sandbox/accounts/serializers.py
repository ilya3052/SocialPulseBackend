from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import CustomUser, TelegramToken, EmailActivate
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
        user = CustomUser.objects.create_user(**validated_data, password=password)
        return user


class TelegramTokenPairSerializer(serializers.Serializer):
    jwt_token = serializers.CharField(write_only=True, max_length=512)

    class Meta:
        model = TelegramToken
        fields = ('user', 'jwt_token')
        read_only_fields = ('short_token',)

    def create(self, validated_data):
        user = self.context['request'].user
        jwt_token = self.validated_data['jwt_token']
        short_token = generate_short_token()

        TelegramToken.objects.filter(user=user).delete()

        token_pair = TelegramToken.objects.create(user=user, jwt_token=jwt_token, short_token=short_token)
        return token_pair


class UserPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)
    new_password = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": 'Passwords don\'t match'})

        if data["old_password"] == data["new_password"]:
            raise serializers.ValidationError({
                "new_password": "New password must be different from old password"
            })

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
        fields = ('id', 'first_name', 'password', 'last_name', 'username', 'email', 'tg_link', 'vk_link', 'tg_id')
        read_only_fields = ('id', 'password')

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)

        instance.tg_link = validated_data.get('tg_link', instance.tg_link)
        instance.tg_id = validated_data.get('tg_id', instance.tg_id)

        # instance.vk_link = validated_data.get('vk_link', instance.vk_link)

        instance.save()
        return instance


class EmailActivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailActivate
        fields = ('user', 'token')
        read_only_fields = ('user',)
