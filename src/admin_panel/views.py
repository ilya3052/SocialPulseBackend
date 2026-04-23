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



