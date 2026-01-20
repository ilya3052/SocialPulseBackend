from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class CustomUser(AbstractUser):
    tg_link = models.CharField(max_length=255, blank=True, null=True)
    vk_link = models.CharField(max_length=255, blank=True, null=True)
