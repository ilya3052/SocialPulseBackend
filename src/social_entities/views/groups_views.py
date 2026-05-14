from datetime import datetime, timedelta

from django.db.models import Sum
from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from service_accounts.services import get_service_account_data
from social_entities.models import Group
from social_entities.permissions import IsAuthenticatedAndOwner
from social_entities.serializers import GroupSerializer, CompareGroupsSerializer
from social_entities.services import check_access_function, get_group_info
from social_entities.utils import Platforms
from stats.models import AbsoluteStats


class GroupsViewByID(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedAndOwner]
    serializer_class = GroupSerializer
    lookup_field = 'pk'

    def get_serializer_context(self):
        context = super().get_serializer_context()

        exclude_fields_str = self.request.GET.get('exclude_fields')
        exclude_fields = exclude_fields_str.split(',') if exclude_fields_str else []
        context['exclude_fields'] = exclude_fields

        return context

    def get_queryset(self):
        if self.request.user.is_staff and self.action == 'partial_update':
            return Group.objects.all()
        data = self.request.GET.copy()
        data.pop('exclude_fields')
        filter_kwargs = {}
        if 'q' in data:
            filter_kwargs['name__icontains'] = data.get('q')
        return (Group.objects
                .prefetch_related('users')
                .prefetch_related('abs_stats')
                .filter(users__in=[self.request.user], **filter_kwargs)
                .order_by('abs_stats__participants_count'))

    def create(self, request, *args, **kwargs):
        external_id = request.data.get('external_id')
        platform = request.data.get('platform_id')
        if not external_id or not platform:
            return Response(
                {"detail": "external_id и platform_id обязательны"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            group = Group.objects.get(external_id=external_id, platform=platform)
            group.users.add(self.request.user)
            return Response(status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            data = request.data.copy()
            data['users_ids'] = [self.request.user.id]
            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            group = serializer.save()
            # отсюда посылается сигнал post_save
            AbsoluteStats.objects.create(group=group)
            return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        user = request.user
        status_code = delete_group(group, user)
        return Response(status=status_code)


class GroupsViewBySlug(mixins.RetrieveModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticatedAndOwner]
    serializer_class = GroupSerializer
    lookup_field = 'slug'

    def get_serializer_context(self):
        context = super().get_serializer_context()

        exclude_fields_str = self.request.GET.get('exclude_fields')
        exclude_fields = exclude_fields_str.split(',') if exclude_fields_str else []
        context['exclude_fields'] = exclude_fields

        return context

    def get_queryset(self):
        return (Group.objects
                .prefetch_related('service_account__data')
                .select_related('platform')
                .prefetch_related('users'))

    def retrieve(self, request, *args, **kwargs):
        group = self.get_object()
        platform = Platforms(group.platform.alias)
        data = get_service_account_data(group.service_account, platform)

        options = {}
        if "service_key" in data:
            options['service_key'] = data.get('service_key')
        elif "session_path" in data:
            options['session_path'] = data.get('session_path')

        result = get_group_info(group.external_id, Platforms(group.platform.alias), **options)
        if "error_code" in result:
            return Response(status=result.get('error_code'))

        description = result.get('description')
        photo_url = result.get('photo_url')

        serializer = self.get_serializer(group)

        return Response({**serializer.data, "description": description, "photo_url": photo_url},
                        status=status.HTTP_200_OK)


class CheckGroupAccessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        internal_data: dict = request.data

        platform_alias = internal_data.get('platform')
        platform = Platforms(platform_alias)

        result, status_code = check_access_function.get(platform)(internal_data)
        return Response(result, status_code)


class CompareGroupsView(APIView):
    permission_classes = [IsAuthenticatedAndOwner]

    context = {
        'exclude_fields': ['last_updated_at']
    }

    def get(self, request, *args, **kwargs):
        # функционал вынесется в отдельный сервис когда будут реализовываться отчеты
        groups_ids_str = request.GET.dict().get('groups_ids', None)
        if not groups_ids_str:
            return Response({"error": "Не выбраны группы для сравнения"}, status=status.HTTP_404_NOT_FOUND)
        group_ids = list(map(int, groups_ids_str.split(',')))

        groups = (Group.objects
                  .select_related('platform')
                  .prefetch_related('abs_stats')
                  .prefetch_related('snapshot__stats')
                  .filter(id__in=group_ids, snapshot__timestamp__gte=(datetime.now() - timedelta(days=7)).date(),
                          snapshot__type='DAILY')
                  .annotate(increase=Sum('snapshot__stats__participants_delta')))

        serializer = CompareGroupsSerializer(groups, many=True, context=self.context)

        return Response(serializer.data, status=status.HTTP_200_OK)
