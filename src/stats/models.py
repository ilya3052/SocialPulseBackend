from django.db import models
from django.utils import timezone


class AbsoluteStats(models.Model):
    likes_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)
    participants_count = models.IntegerField(default=0)
    repost_count = models.IntegerField(default=0)
    comms_count = models.IntegerField(default=0)
    posts_count = models.IntegerField(default=0)
    last_updated_at = models.DateTimeField(default=timezone.now)

    group = models.ForeignKey('social_entities.Group', on_delete=models.CASCADE, related_name='abs_stats')


class BestPostInfo(models.Model):
    likes_count = models.IntegerField()
    comms_count = models.IntegerField()
    views_count = models.IntegerField()
    reposts_count = models.IntegerField()
    post_id = models.IntegerField()
    content = models.CharField(max_length=150)
    post_type = models.CharField(max_length=16)
    last_updated_at = models.DateTimeField(default=timezone.now)
    group = models.ForeignKey('social_entities.Group', on_delete=models.CASCADE, related_name='best_posts')


class Snapshot(models.Model):
    Type = {
        "DAILY": "DAILY",
        "HOURLY": "HOURLY"
    }
    timestamp = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=6, choices=Type)
    group = models.ForeignKey('social_entities.Group', on_delete=models.CASCADE,
                              related_name='snapshot')  # Group.objects.get().snapshot.all()


class SnapshotStats(models.Model):
    likes_count = models.IntegerField()
    views_count = models.IntegerField()
    participants_delta = models.IntegerField()
    repost_count = models.IntegerField()
    comms_count = models.IntegerField()
    coverage = models.IntegerField()
    snapshot = models.ForeignKey('Snapshot', on_delete=models.CASCADE,
                                 related_name='stats')  # Snapshot.objects.get().stats.all()
