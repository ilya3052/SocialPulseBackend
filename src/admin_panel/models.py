from django.db import models


class Platform(models.Model):
    alias = models.CharField(max_length=16, db_index=True)
    name = models.CharField(max_length=128)


class ServiceAccount(models.Model):
    name = models.CharField(max_length=128)
    is_activated = models.BooleanField(default=False)
    platform = models.ForeignKey('Platform', on_delete=models.CASCADE)


class ServiceAccountData(models.Model):
    service_key = models.CharField(max_length=256, blank=True, null=True)
    protected_key = models.CharField(max_length=256, blank=True, null=True)
    phone_number = models.CharField(max_length=16, blank=True, null=True)
    session_path = models.CharField(max_length=256, blank=True, null=True)
    account = models.OneToOneField('ServiceAccount', on_delete=models.CASCADE, related_name='data')
