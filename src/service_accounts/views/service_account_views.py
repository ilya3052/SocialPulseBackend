from secrets import token_hex

from django.db.models import Count
from icecream import ic
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from service_accounts.models import ServiceAccount, OneTimeToken
from service_accounts.permissions import ReadOnly
from service_accounts.serializers import ServiceAccountSerializer


class ServiceAccountsView(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        elif self.action in ('list', 'create', 'partial_update', 'destroy'):
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [ReadOnly]
        return [permission() for permission in permission_classes]

    queryset = ServiceAccount.objects.all()

    def retrieve(self, request, *args, **kwargs):
        account = (
            ServiceAccount.objects.filter(platform__alias=self.kwargs.get('platform'))
            .prefetch_related('groups')
            .annotate(
                groups_count=Count('groups')
            )
            .order_by('name', 'groups_count')
        ).first()

        if not account:
            return Response({"msg": "Сервисный аккаунт не найден"}, status=status.HTTP_404_NOT_FOUND)

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
            .annotate(
                groups_count=Count('groups')
            )
        )

        context = {
            'exclude_fields': [
                'data', 'groups', 'platform_id', 'app_id'
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
        return Response(status=status.HTTP_201_CREATED)


class ServiceAccountActivateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        account_id = self.kwargs.get('account_id')

        if user.is_staff:
            token = token_hex(16)
            token_instance = OneTimeToken.objects.filter(account_id=account_id).first()
            if token_instance:
                token_instance.delete()
            OneTimeToken.objects.create(account_id=account_id, token=token)
            return Response({"token": token}, status=status.HTTP_201_CREATED)
        else:
            return Response({"msg": "Недостаточно прав"}, status=status.HTTP_403_FORBIDDEN)
