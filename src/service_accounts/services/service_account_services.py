from django.db.models import Count, Q

from common.config import ENCRYPTION_KEY
from common.utils import decrypt
from service_accounts.models import ServiceAccount, ServiceAccountData
from social_entities.utils import Platforms


def get_service_accounts_aggregated_info():
    result = ServiceAccount.objects.all().aggregate(
        vk_count=Count('id', filter=Q(platform__alias='VK')),
        tg_count=Count('id', filter=Q(platform__alias='TG')))

    return {
        "vk_count": result.get('vk_count'),
        "tg_count": result.get('tg_count'),
    }


def get_service_accounts_loading():
    accounts = (
        ServiceAccount.objects.all()
        .prefetch_related('groups')
        .annotate(
            groups_count=Count('groups')
        )
    )

    min_l_acc: ServiceAccount = accounts.order_by('groups_count', 'name').first()
    max_l_acc: ServiceAccount = accounts.order_by('-groups_count', '-name').first()

    return {
        "min": {
            "id": min_l_acc.id,
            "name": min_l_acc.name,
            "count": min_l_acc.groups_count
        },
        "max": {
            "id": max_l_acc.id,
            "name": max_l_acc.name,
            "count": max_l_acc.groups_count
        },
    }

def get_service_account_data(service_account: ServiceAccount, platform: Platforms):
    data: ServiceAccountData = service_account.data
    match platform:
        case Platforms.VK:
            return {"service_key": decrypt(data.service_key, ENCRYPTION_KEY)}
        case Platforms.TG:
            return {"session_path": data.session_path}
