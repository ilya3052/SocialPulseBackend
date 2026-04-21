from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_panel.models import Platform, ServiceAccount
from admin_panel.permissions import IsAdminOrReadOnly
from admin_panel.serializers import PlatformSerializer, ServiceAccountSerializer
from admin_panel.utils import get_account_with_minimum_loaded


class PlatformsView(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer


class ServiceAccountsView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        platform = (request.GET.dict()).get('platform')
        accounts = ServiceAccount.objects.filter(platform__alias=platform).prefetch_related('groups')
        try:
            account = get_account_with_minimum_loaded(accounts)
        except ValueError as VE:
            return Response(VE, status=status.HTTP_400_BAD_REQUEST)
        serializer = ServiceAccountSerializer(account)
        data = serializer.data
        return Response({"name": data.get('name'), "id": data.get('id')}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ServiceAccountSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
