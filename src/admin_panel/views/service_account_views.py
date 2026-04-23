from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from admin_panel.models import ServiceAccount
from admin_panel.permissions import ReadOnly
from admin_panel.serializers import ServiceAccountSerializer


class ServiceAccountsView(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        elif self.action in ('list', 'create', 'partial_update'):
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

    def partial_update(self, request, *args, **kwargs):
        instance = ServiceAccount.objects.get(pk=self.kwargs.get('pk'))
        if not instance:
            return Response({"msg": "Объект не найден"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ServiceAccountSerializer(instance, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = ServiceAccountSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

