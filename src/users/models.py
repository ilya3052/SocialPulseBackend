from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    tg_link = models.CharField(max_length=255, blank=True, null=True)
    tg_id = models.IntegerField(blank=True, null=True)
    vk_link = models.CharField(max_length=255, blank=True, null=True)
    vk_id = models.IntegerField(blank=True, null=True)
    is_email_confirmed = models.BooleanField(default=False)
    groups = models.ManyToManyField('social_entities.Group')
