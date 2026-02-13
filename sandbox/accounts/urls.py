from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView, TokenBlacklistView

from accounts.serializers import UserPasswordSerializer
from accounts.views import UserAPIUpdate, TelegramCallbackView, UserAPIRegistration, TelegramTokenPairView, \
    TelegramConvertTokenView, UserChangePasswordView, TelegramBindingView, EmailActivationView, EmailSendMessageView, \
    VKCallbackView, DebugView, VKCallbackUser

urlpatterns = [

    path('register/', UserAPIRegistration.as_view(), name='register'),

    path(r'users/me/', UserAPIUpdate.as_view(), name='me'),

    path('users/change-password/', UserChangePasswordView.as_view(), name='change_password'),

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

]
