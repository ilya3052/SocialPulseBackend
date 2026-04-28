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


class Snapshot(models.Model):
    Platforms = {
        "VK": "Вконтакте",
        "TG": "Telegram"
    }
    timestamp = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=2, choices=Platforms)
    group = models.ForeignKey('social_entities.Group', on_delete=models.CASCADE, related_name='snapshot_stats')


class SnapshotStats(models.Model):
    likes_count = models.IntegerField()
    views_count = models.IntegerField()
    participants_count = models.IntegerField()
    repost_count = models.IntegerField()
    comms_count = models.IntegerField()
    coverage = models.IntegerField()
    last_updated_at = models.DateTimeField(default=timezone.now)
    snapshot = models.ForeignKey('Snapshot', on_delete=models.CASCADE, related_name='stats') # Snapshot.objects.get().stats.all()