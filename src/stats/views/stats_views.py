from datetime import timedelta, UTC

from django.db.models import QuerySet, Q
from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from stats.models import Snapshot, SnapshotStats, AbsoluteStats, BestPostInfo
from stats.serializers import SnapshotSerializer, SnapshotStatsSerializer, AbsoluteStatsSerializer
from stats.utils import format_posts_info


class SnapshotView(viewsets.ModelViewSet):
    def get_queryset(self):
        return (Snapshot.objects.prefetch_related('stats')
                .filter(
                    Q(type__exact='DAILY', timestamp__gte=datetime.now(tz=UTC).date() - timedelta(days=30)) |
                          Q(type__exact='HOURLY', timestamp__gte=datetime.now(tz=UTC) - timedelta(days=1)),
                    group_id=self.kwargs.get('group_id'))
                .order_by('type', 'timestamp'))
    def get_serializer_context(self):
        context = super().get_serializer_context()

        exclude_fields_str = self.request.GET.get('exclude_fields')
        exclude_fields = exclude_fields_str.split(',') if exclude_fields_str else []

        context['exclude_fields'] = exclude_fields

        return context

    lookup_field = 'group_id'
    serializer_class = SnapshotSerializer
    permission_classes = [IsAuthenticated]


class SnapshotStatsView(viewsets.ModelViewSet):
    def get_serializer_context(self):
        context = super().get_serializer_context()

        exclude_fields_str = self.request.GET.get('exclude_fields')
        exclude_fields = exclude_fields_str.split(',') if exclude_fields_str else []

        context['exclude_fields'] = exclude_fields

        return context

    queryset = SnapshotStats.objects.all()
    serializer_class = SnapshotStatsSerializer
    permission_classes = [IsAuthenticated]


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
    permission_classes = [IsAuthenticated]


class BestPostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        group_id = self.kwargs.get('group_id')
        posts: QuerySet[BestPostInfo] = BestPostInfo.objects.select_related('group__platform').filter(
            group_id=group_id).all()
        if not posts:
            return Response({"error": "Статистика лучших постов пока недоступна"}, status=status.HTTP_200_OK)
        best_posts_info = format_posts_info(posts)
        return Response({**best_posts_info}, status=status.HTTP_200_OK)
