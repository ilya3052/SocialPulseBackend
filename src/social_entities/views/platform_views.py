from rest_framework import viewsets

from admin_panel.models import Platform
from admin_panel.permissions import IsAdminOrReadOnly
from admin_panel.serializers import PlatformSerializer


class PlatformsView(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
