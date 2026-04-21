from django.db.models.aggregates import Count
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_panel.models import Platform, ServiceAccount
from admin_panel.permissions import IsAdminOrReadOnly, ReadOnly
from admin_panel.serializers import PlatformSerializer, ServiceAccountSerializer
from admin_panel.utils import get_group_aggregated_info, get_service_accounts_aggregated_info, \
    get_service_accounts_loading


class PlatformsView(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer


class ServiceAccountsView(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        elif self.action in ('list', 'create'):
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [ReadOnly]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, *args, **kwargs):
        account = (
            ServiceAccount.objects.filter(platform__alias=self.kwargs.get('platform'))
            .prefetch_related('groups')
            .annotate(
                groups_count=Count('groups')
            )
            .order_by('name', 'groups_count')
        ).first()

        context = {
            'exclude_fields': [
                'platform_id', 'data', 'groups', 'groups_count'
            ]
        }

        serializer = ServiceAccountSerializer(account, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        accounts = (
            ServiceAccount.objects.all()
            .prefetch_related('groups')
            .annotate(
                groups_count=Count('groups')
            )
        )

        context = {
            'exclude_fields': [
                'data', 'groups'
            ]
        }

        serializer = ServiceAccountSerializer(accounts, many=True, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = ServiceAccountSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SummaryAdminPanelView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        group_data = get_group_aggregated_info()
        service_account_data = get_service_accounts_aggregated_info()
        service_account_loading = get_service_accounts_loading()

        return Response({
            "group_info": {
                **group_data,
            },
            "service_account_info": {
                **service_account_data,
            },
            "service_account_loading_info": {
                **service_account_loading
            }
        }, status=status.HTTP_200_OK)
