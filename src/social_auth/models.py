from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from social_pulse import settings

User = get_user_model()


def default_expires_at():
    return timezone.now() + settings.SHORT_TOKEN_LIFETIME


class TelegramToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    short_token = models.CharField(max_length=64, unique=True)
    access_token = models.CharField(max_length=512)
    refresh_token = models.CharField(max_length=512)
    expires_at = models.DateTimeField(default=default_expires_at)


class VKTokens(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    refresh_vk_token = models.CharField(max_length=512)
    access_vk_token = models.CharField(max_length=512)
    id_vk_token = models.TextField()
    expires_in = models.IntegerField()
    added_at = models.DateTimeField(default=default_expires_at)


class EmailActivate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField(default=default_expires_at)
