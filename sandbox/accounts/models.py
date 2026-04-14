from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from sandbox import settings


def default_expires_at():
    return timezone.now() + settings.SHORT_TOKEN_LIFETIME


class CustomUser(AbstractUser):
    tg_link = models.CharField(max_length=255, blank=True, null=True)
    tg_id = models.IntegerField(blank=True, null=True)
    vk_link = models.CharField(max_length=255, blank=True, null=True)
    vk_id = models.IntegerField(blank=True, null=True)
    is_email_confirmed = models.BooleanField(default=False)
    groups = models.ManyToManyField('Group')


class TelegramToken(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, unique=True)
    short_token = models.CharField(max_length=64, unique=True)
    access_token = models.CharField(max_length=512)
    refresh_token = models.CharField(max_length=512)
    expires_at = models.DateTimeField(default=default_expires_at)


class VKTokens(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, unique=True)
    refresh_vk_token = models.CharField(max_length=512)
    access_vk_token = models.CharField(max_length=512)
    id_vk_token = models.TextField()
    expires_in = models.IntegerField()
    added_at = models.DateTimeField(default=default_expires_at)


class EmailActivate(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, unique=True)
    token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField(default=default_expires_at)


# после завершения аккаунтов модели будут вынесены в отдельное приложение

class Platform(models.Model):
    alias = models.CharField(max_length=16, db_index=True)
    name = models.CharField(max_length=128)


class Group(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["external_id", "platform"],
                name='uq_group_platform_external'
            )
        ]

    name = models.CharField(max_length=128)
    link = models.CharField(max_length=256)
    external_id = models.BigIntegerField(db_index=True)
    added_at = models.DateTimeField(default=default_expires_at)
    platform = models.ForeignKey('Platform', on_delete=models.CASCADE)
    user = models.ManyToManyField('CustomUser')
    service_account = models.ForeignKey('ServiceAccount', on_delete=models.SET_NULL, null=True, related_name='groups')


class ServiceAccount(models.Model):
    name = models.CharField(max_length=128)
    platform = models.ForeignKey('Platform', on_delete=models.CASCADE)


class ServiceAccountData(models.Model):
    service_key = models.CharField(max_length=256, blank=True, null=True)
    protected_key = models.CharField(max_length=256, blank=True, null=True)
    phone_number = models.CharField(max_length=16, blank=True, null=True)
    session_path = models.CharField(max_length=256, blank=True, null=True)
    account = models.OneToOneField('ServiceAccount', on_delete=models.CASCADE, related_name='data')
