from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from sandbox import settings

def default_expires_at():
    return timezone.now() + settings.SHORT_TOKEN_LIFETIME

# Create your models here.
class CustomUser(AbstractUser):
    tg_link = models.CharField(max_length=255, blank=True, null=True)
    tg_id = models.IntegerField(blank=True, null=True)
    vk_link = models.CharField(max_length=255, blank=True, null=True)
    vk_id = models.IntegerField(blank=True, null=True)
    is_email_confirmed = models.BooleanField(default=False)


class TelegramToken(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, unique=True)
    short_token = models.CharField(max_length=64, unique=True)
    jwt_token = models.CharField(max_length=512)
    expires_at = models.DateTimeField(default=default_expires_at)

class VKTokens(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, unique=True)
    refresh_vk_token = models.CharField(max_length=512)
    access_vk_token = models.CharField(max_length=512)
    id_vk_token = models.CharField(max_length=512)
    expires_in = models.IntegerField()
    added_at = models.DateTimeField(default=default_expires_at)

class EmailActivate(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, unique=True)
    token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField(default=default_expires_at)

