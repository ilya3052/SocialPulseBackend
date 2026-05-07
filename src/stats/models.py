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


class BestPosts(models.Model):
    most_liked = models.IntegerField()
    most_reposted = models.IntegerField()
    most_commented = models.IntegerField()
    most_viewed = models.IntegerField()
    last_updated_at = models.DateTimeField(default=timezone.now)
    group = models.ForeignKey('social_entities.Group', on_delete=models.CASCADE, related_name='best_posts')

    def to_dict(self):
        fields = ['most_viewed', 'most_liked', 'most_commented', 'most_reposted']
        return {field: str(getattr(self, field)) for field in fields}


class Snapshot(models.Model):
    Type = {
        "Daily": "Daily",
        "Hourly": "Hourly"
    }
    timestamp = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=6, choices=Type)
    group = models.ForeignKey('social_entities.Group', on_delete=models.CASCADE,
                              related_name='snapshot_stats')  # Group.objects.get().snapshot_stats.all()


class SnapshotStats(models.Model):
    likes_count = models.IntegerField()
    views_count = models.IntegerField()
    participants_delta = models.IntegerField()
    repost_count = models.IntegerField()
    comms_count = models.IntegerField()
    coverage = models.IntegerField()
    snapshot = models.ForeignKey('Snapshot', on_delete=models.CASCADE,
                                 related_name='stats')  # Snapshot.objects.get().stats.all()
