from django.db import models


class ServiceAccount(models.Model):
    name = models.CharField(max_length=128)
    is_activated = models.BooleanField(default=False)
    app_id = models.CharField(unique=True, db_index=True, null=True, blank=True)
    platform = models.ForeignKey('social_entities.Platform', on_delete=models.CASCADE)


class ServiceAccountData(models.Model):
    service_key = models.CharField(max_length=256, blank=True, null=True)
    protected_key = models.CharField(max_length=256, blank=True, null=True)
    phone_number = models.CharField(max_length=11, blank=True, null=True, unique=True)
    session_path = models.CharField(max_length=256, blank=True, null=True)
    account = models.OneToOneField('ServiceAccount', on_delete=models.CASCADE, related_name='data')
