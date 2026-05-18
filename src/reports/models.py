from django.db import models
from django.utils import timezone

class Report(models.Model):
    report_type = {
        "XLSX": "XLSX",
        "PDF": "PDF"
    }
    filename = models.CharField(max_length=256)
    path = models.CharField(max_length=512)
    date = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=4, choices=report_type)
    group = models.ForeignKey('social_entities.Group', on_delete=models.DO_NOTHING, null=True, blank=True,
                              related_name='report')
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='group_reports')
