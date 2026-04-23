from django.utils import timezone

from SocialPulse import settings


def default_expires_at():
    return timezone.now() + settings.SHORT_TOKEN_LIFETIME