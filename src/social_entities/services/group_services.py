from django.db.models import Count, Q


def get_group_aggregated_info():
    from accounts.models import Group
    result = Group.objects.all().aggregate(
        vk_count=Count('id', filter=Q(platform__alias='VK')),
        tg_count=Count('id', filter=Q(platform__alias='TG')))

    return {
        "vk_count": result.get('vk_count'),
        "tg_count": result.get('tg_count'),
    }
