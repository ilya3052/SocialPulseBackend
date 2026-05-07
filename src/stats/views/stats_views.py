from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.config import ENCRYPTION_KEY
from common.utils import decrypt
from social_entities.utils import Platforms
from stats.models import Snapshot, SnapshotStats, AbsoluteStats, BestPosts
from stats.serializers import SnapshotSerializer, SnapshotStatsSerializer, AbsoluteStatsSerializer
from stats.services import get_best_posts_info


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
    permission_classes = [IsAuthenticated]


class BestPostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        params = request.GET.dict()
        group_id = self.kwargs.get('group_id')
        platform = params.get('platform')
        if not platform:
            return Response({"error": "Не указана целевая платформа"}, status=status.HTTP_404_NOT_FOUND)

        platform = Platforms(platform)
        posts: BestPosts = BestPosts.objects.select_related('group__service_account__data').filter(group_id=group_id).first()
        if not posts:
            return Response({"error": "Статистика лучших постов пока недоступна"})
        data = posts.group.service_account.data

        options = {}

        if platform == Platforms.TG:
            options['session_path'] = data.session_path
        elif platform == Platforms.VK:
            options['service_key'] = decrypt(data.service_key, ENCRYPTION_KEY)

        best_posts_info = get_best_posts_info(posts, platform, **options)
        return Response({**best_posts_info, "last_updated_at": posts.last_updated_at}, status=status.HTTP_200_OK)
