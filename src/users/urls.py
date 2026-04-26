from django.urls import path

from users.views import UserAPIRegistration, UserAPIView, UserChangePasswordView, UserSetPasswordView, \
    UserSocialDataView, OneTimeTokenView

urlpatterns = [
    path('register/', UserAPIRegistration.as_view(), name='register'),

    path(r'me/', UserAPIView.as_view(), name='me'),

    path('change-password/', UserChangePasswordView.as_view(), name='change_password'),
    path('set-password/', UserSetPasswordView.as_view(), name='set_password'),
    path('get-social/', UserSocialDataView.as_view(), name='user-social-data'),
    path('one-time-token/', OneTimeTokenView.as_view(), name='get-one-time-token')
]
