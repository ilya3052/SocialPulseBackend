from rest_framework import viewsets

from stats.models import Snapshot, SnapshotStats, AbsoluteStats
from stats.serializers.stats_serializers import SnapshotSerializer, SnapshotStatsSerializer, AbsoluteStatsSerializer


class SnapshotView(viewsets.ModelViewSet):
    queryset = Snapshot.objects.all()
    serializer_class = SnapshotSerializer

class SnapshotStatsView(viewsets.ModelViewSet):
    queryset = SnapshotStats.objects.all()
    serializer_class = SnapshotStatsSerializer

class AbsoluteStatsView(viewsets.ModelViewSet):
    queryset = AbsoluteStats.objects.all()
    serializer_class = AbsoluteStatsSerializer