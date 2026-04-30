from rest_framework import viewsets

from stats.models import Snapshot, SnapshotStats, AbsoluteStats
from stats.serializers import SnapshotSerializer, SnapshotStatsSerializer, AbsoluteStatsSerializer


class SnapshotView(viewsets.ModelViewSet):
    queryset = Snapshot.objects.all()
    serializer_class = SnapshotSerializer

class SnapshotStatsView(viewsets.ModelViewSet):
    queryset = SnapshotStats.objects.all()
    serializer_class = SnapshotStatsSerializer

class AbsoluteStatsView(viewsets.ModelViewSet):
    def get_serializer_context(self):
        context = super().get_serializer_context()

        exclude_fields_str = self.request.GET.get('exclude_fields')
        exclude_fields = exclude_fields_str.split(',') if exclude_fields_str else []

        context['exclude_fields'] = exclude_fields

        return context

    lookup_field = 'group_id'
    queryset = AbsoluteStats.objects.all()
    serializer_class = AbsoluteStatsSerializer