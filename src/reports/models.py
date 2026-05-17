from django.db import models
from django.utils import timezone

class Report(models.Model):
    filename = models.CharField(max_length=256)
    path = models.FilePathField()
    date = models.DateTimeField(default=timezone.now)
    type = models.IntegerField()
    group = models.ForeignKey('social_entities.Group', on_delete=models.DO_NOTHING, null=True, blank=True,
                              related_name='report')
    user = models.OneToOneField('users.CustomUser', on_delete=models.CASCADE, related_name='group_reports')
