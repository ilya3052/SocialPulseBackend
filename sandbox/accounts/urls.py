from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView, TokenBlacklistView

from accounts.views import UserAPIView, TelegramCallbackView, UserAPIRegistration, TelegramTokenPairView, \
    TelegramConvertTokenView, UserChangePasswordView, TelegramBindingView, EmailActivationView, EmailSendMessageView, \
    VKCallbackView, DebugView, VKCallbackUser, UserSetPasswordView, GroupsView, PlatformsView, UserSocialDataView, \
    ServiceAccountsView, CheckGroupAccessView

urlpatterns = [

    path('register/', UserAPIRegistration.as_view(), name='register'),

    path(r'users/me/', UserAPIView.as_view(), name='me'),

    path('users/change-password/', UserChangePasswordView.as_view(), name='change_password'),
    path('users/set-password/', UserSetPasswordView.as_view(), name='set_password'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    path('tg/callback/', TelegramCallbackView.as_view(), name='tg_callback'),

    path('vk/callback/', VKCallbackView.as_view(), name='vk_callback'),
    path('vk/user/', VKCallbackUser.as_view(), name='vk_callback_user'),

    path('tg/bind/', TelegramBindingView.as_view(), name='tg_binding'),

    path('tg/token/short/', TelegramTokenPairView.as_view(), name='token_short'),
    path('tg/token/short/convert/', TelegramConvertTokenView.as_view(), name='token_convert'),

    path('email/send/', EmailSendMessageView.as_view(), name='email_send'),
    path('email/activate/', EmailActivationView.as_view(), name='email_activate'),

    path('debug/', DebugView.as_view(), name='error'),

    # после завершения перенести в другое приложение аналогично моделям сериализаторам и вьюхам
    path('groups/', GroupsView.as_view({"get": "list", "post": "create"}), name='groups'),
    path('groups/<int:pk>', GroupsView.as_view({"delete": "destroy"}), name='groups'),
    path('platforms/', PlatformsView.as_view({"get": "list", "post": "create"}), name='platforms'),
    path('users/get-social/', UserSocialDataView.as_view(), name='user-social-data'),
    path('service-account/', ServiceAccountsView.as_view(), name='add-service-account'),
    path('group/check-access/', CheckGroupAccessView.as_view(), name='check-group-access')
]
