from rest_framework import serializers
from reports.models import Report


class ReportSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        exclude_fields = self.context.get('exclude_fields', [])

        for field in exclude_fields:
            fields.pop(field, None)
        return fields

    class Meta:
        model = Report
        fields = ('id', 'filename', 'path', 'date', 'type', 'user', 'group')
