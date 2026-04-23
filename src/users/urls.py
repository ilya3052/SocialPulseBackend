from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView, TokenBlacklistView

from users.views import UserAPIRegistration, UserAPIView, UserChangePasswordView, UserSetPasswordView, \
    UserSocialDataView

urlpatterns = [
    path('register/', UserAPIRegistration.as_view(), name='register'),

    path(r'users/me/', UserAPIView.as_view(), name='me'),

    path('users/change-password/', UserChangePasswordView.as_view(), name='change_password'),
    path('users/set-password/', UserSetPasswordView.as_view(), name='set_password'),
    path('users/get-social/', UserSocialDataView.as_view(), name='user-social-data'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
]
