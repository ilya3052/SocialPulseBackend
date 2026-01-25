from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView, TokenBlacklistView

from accounts.views import UserAPIUpdate, TGAuth

urlpatterns = [
    path(r'auth/', include('djoser.urls')),

    path(r'users/me/', UserAPIUpdate.as_view(), name='me'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.as_view(), name='token_verify'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('tg/', TGAuth.as_view())
]