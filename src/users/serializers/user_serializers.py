from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import CustomUser


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


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # поле пароля оставить только в разработке, в идеале его быть не должно
        fields = ('id', 'first_name', 'password', 'last_name', 'username',
                  'email', 'tg_link', 'vk_link', 'tg_id', 'vk_id', 'is_email_confirmed', 'is_staff')
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


class UserSocialDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('tg_link', 'vk_link')
