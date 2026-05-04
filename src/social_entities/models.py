from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from unidecode import unidecode

from social_pulse import settings


def default_expires_at():
    return timezone.now() + settings.SHORT_TOKEN_LIFETIME


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
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    platform = models.ForeignKey('Platform', on_delete=models.CASCADE)
    user = models.ManyToManyField('users.CustomUser')
    service_account = models.ForeignKey('service_accounts.ServiceAccount', on_delete=models.SET_NULL, null=True,
                                        related_name='groups')

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        return super().save(*args, **kwargs)


class Platform(models.Model):
    alias = models.CharField(max_length=16, db_index=True)
    name = models.CharField(max_length=128)
