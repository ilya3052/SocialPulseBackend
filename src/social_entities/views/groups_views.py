from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from service_accounts.services import get_service_account_data
from social_entities.models import Group
from social_entities.permissions import IsAuthenticatedAndOwner
from social_entities.serializers import GroupSerializer
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
        return Group.objects.filter(user__in=[self.request.user])

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user_id'] = [self.request.user.id]

        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        # отсюда посылается сигнал post_save
        group = serializer.instance
        AbsoluteStats.objects.create(group=group)
        return Response(status=status.HTTP_201_CREATED)


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
                .select_related('service_account')
                .prefetch_related('service_account__data')
                .select_related('platform')
                .prefetch_related('user'))

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

        return Response({**serializer.data, "description": description, "photo_url": photo_url}, status=status.HTTP_200_OK)



class CheckGroupAccessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        internal_data: dict = request.data

        platform_alias = internal_data.get('platform')
        platform = Platforms(platform_alias)

        result, status_code = check_access_function.get(platform)(internal_data)
        return Response(result, status_code)
