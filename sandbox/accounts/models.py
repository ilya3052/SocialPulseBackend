from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from sandbox import settings


# Create your models here.
class CustomUser(AbstractUser):
    REQUIRED_FIELDS = [""]
    tg_link = models.CharField(max_length=255, blank=True, null=True)
    tg_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    vk_link = models.CharField(max_length=255, blank=True, null=True)
    is_email_confirmed = models.BooleanField(default=False)


class TelegramToken(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    short_token = models.CharField(max_length=64, unique=True)
    jwt_token = models.CharField(max_length=512)
    expires_at = models.DateTimeField(default=timezone.now() + settings.TG_SHORT_TOKEN_LIFETIME)

class EmailActivation(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField(default=timezone.now() + timedelta(minutes=15))
