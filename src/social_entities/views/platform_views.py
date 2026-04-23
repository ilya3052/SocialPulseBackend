from rest_framework import viewsets

from social_entities.models import Platform
from social_entities.permissions import IsAdminOrReadOnly
from social_entities.serializers import PlatformSerializer


class PlatformsView(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
