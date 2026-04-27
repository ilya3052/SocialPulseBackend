from datetime import timedelta

from django.db import models
from django.utils import timezone


def get_token_expiry():
    return timezone.now() + timedelta(minutes=15)


class ServiceAccount(models.Model):
    name = models.CharField(max_length=128)
    is_activated = models.BooleanField(default=False)
    app_id = models.CharField(unique=True, db_index=True, null=True, blank=True)
    platform = models.ForeignKey('social_entities.Platform', on_delete=models.CASCADE)


class OneTimeToken(models.Model):
    token = models.CharField(max_length=32, unique=True)
    account = models.OneToOneField(ServiceAccount, on_delete=models.CASCADE, related_name='one_time_token')
    expires_at = models.DateTimeField(default=get_token_expiry)


class ServiceAccountData(models.Model):
    service_key = models.CharField(max_length=256, blank=True, null=True)
    protected_key = models.CharField(max_length=256, blank=True, null=True)
    phone_number = models.CharField(max_length=11, blank=True, null=True, unique=True)
    session_path = models.CharField(max_length=256, blank=True, null=True)
    account = models.OneToOneField('ServiceAccount', on_delete=models.CASCADE, related_name='data')
