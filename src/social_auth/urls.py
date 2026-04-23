from django.urls import path

from social_auth.views import EmailSendMessageView, EmailActivationView, TelegramBindingView, TelegramCallbackView, \
    TelegramTokenPairView, TelegramConvertTokenView, VKCallbackView, VKCallbackUser

urlpatterns = [
    path('email/send/', EmailSendMessageView.as_view(), name='email_send'),
    path('email/activate/', EmailActivationView.as_view(), name='email_activate'),

    path('tg/bind/', TelegramBindingView.as_view(), name='tg_binding'),
    path('tg/callback/', TelegramCallbackView.as_view(), name='tg_callback'),
    path('tg/token/short/', TelegramTokenPairView.as_view(), name='token_short'),
    path('tg/token/short/convert/', TelegramConvertTokenView.as_view(), name='token_convert'),

    path('vk/callback/', VKCallbackView.as_view(), name='vk_callback'),
    path('vk/user/', VKCallbackUser.as_view(), name='vk_callback_user'),
]
