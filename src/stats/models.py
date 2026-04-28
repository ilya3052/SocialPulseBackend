from django.db import models
from django.utils import timezone


class AbsoluteStats(models.Model):
    likes_count = models.IntegerField()
    views_count = models.IntegerField()
    participants_count = models.IntegerField()
    repost_count = models.IntegerField()
    comms_count = models.IntegerField()
    last_updated_at = models.DateTimeField(default=timezone.now)

    group = models.ForeignKey('social_entities.Group', on_delete=models.CASCADE, related_name='stats')

