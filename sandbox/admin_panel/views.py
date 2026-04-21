from django.db.models.aggregates import Count
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.admin_panel import Platform, ServiceAccount
from src.admin_panel.permissions import IsAdminOrReadOnly, ReadOnly
from src.admin_panel.serializers import PlatformSerializer, ServiceAccountSerializer


class PlatformsView(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer


class ServiceAccountsView(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request, *args, **kwargs):
        account = (
            ServiceAccount.objects.all()
            .prefetch_related('groups')
            .annotate(
                groups_count=Count('groups')
            )
            .order_by('name', 'groups_count')
        )

        serializer = ServiceAccountSerializer(account, many=True)

        data = serializer.data
        return Response([
            {
                "id": account_data.get('id'),
                "name": account_data.get('name'),
                "platform": account_data.get('platform_id'),
            } for account_data in data
        ], status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        account = (
            ServiceAccount.objects.filter(platform__alias=self.kwargs.get('platform'))
            .prefetch_related('groups')
            .annotate(
                groups_count=Count('groups')
            )
            .order_by('name', 'groups_count')
        ).first()

        serializer = ServiceAccountSerializer(account)
        data = serializer.data
        return Response({"name": data.get('name'), "id": data.get('id')}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = ServiceAccountSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoadingOnServiceAccounts(APIView):
    permission_classes = [ReadOnly]

    def get(self, request, *args, **kwargs):
        accounts = (
            ServiceAccount.objects.all()
            .prefetch_related('groups')
            .annotate(
                groups_count=Count('groups')
            )
        )

        min_l_acc = accounts.order_by('groups_count', 'name').first()
        max_l_acc = accounts.order_by('-groups_count', '-name').first()


        min_l_acc_serializer = ServiceAccountSerializer(min_l_acc)
        min_l_acc_serializer_data = min_l_acc_serializer.data

        max_l_acc_serializer = ServiceAccountSerializer(max_l_acc)
        max_l_acc_serializer_data = max_l_acc_serializer.data

        return Response(
            {
                "min": {
                    "id": min_l_acc_serializer_data.get('id'),
                    "name": min_l_acc_serializer_data.get('name'),
                    "count": min_l_acc_serializer_data.get('groups_count')
                },
                "max": {
                    "id": max_l_acc_serializer_data.get('id'),
                    "name": max_l_acc_serializer_data.get('name'),
                    "count": max_l_acc_serializer_data.get('groups_count')
                }
            }, status=status.HTTP_200_OK)


class SummaryAdminPanelView(APIView):
    pass
