from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

def get_token_expiry():
    return timezone.now() + timedelta(minutes=15)

class CustomUser(AbstractUser):
    tg_link = models.CharField(max_length=255, blank=True, null=True)
    tg_id = models.IntegerField(blank=True, null=True)
    vk_link = models.CharField(max_length=255, blank=True, null=True)
    vk_id = models.IntegerField(blank=True, null=True)
    is_email_confirmed = models.BooleanField(default=False)
    groups = models.ManyToManyField('social_entities.Group')

class OneTimeToken(models.Model):
    token = models.CharField(max_length=32, unique=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='one_time_token')
    expires_at = models.DateTimeField(default=get_token_expiry)