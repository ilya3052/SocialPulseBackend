from django.urls import path, include, re_path
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView, TokenBlacklistView

from accounts.views import UserAPIUpdate, TGAuth

urlpatterns = [
    path(r'auth/', include('djoser.urls')),

    path(r'users/me/', UserAPIUpdate.as_view(), name='me'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.as_view(), name='token_verify'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    re_path('^social/', include('social_django.urls', namespace='social')),
    re_path(r'^auth/', include('drf_social_oauth2.urls', namespace='drf')),
]