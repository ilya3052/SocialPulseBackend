from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .serializers import CustomUserSerializer


class UserAPIUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
