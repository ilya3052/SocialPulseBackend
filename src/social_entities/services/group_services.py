import requests
from asgiref.sync import async_to_sync, sync_to_async
from django.db.models import Count, Q
from rest_framework import status
from telethon import TelegramClient
from telethon.tl.types import Channel

from social_entities.models import Group
from social_entities.utils import Status, Platforms


def get_group_aggregated_info():
    result = Group.objects.all().aggregate(
        vk_count=Count('id', filter=Q(platform__alias='VK')),
        tg_count=Count('id', filter=Q(platform__alias='TG')))

    return {
        "vk_count": result.get('vk_count'),
        "tg_count": result.get('tg_count'),
    }


def check_vk_access(internal_data):
    from service_accounts.models import ServiceAccount, ServiceAccountData

    group_link = internal_data.get('groupLink')
    screen_name = group_link.split('/')[-1]
    vk_id = internal_data.get('user_social_id')
    service_account_id = internal_data.get('serviceAccount')

    service_account: ServiceAccount = ServiceAccount.objects.get(pk=service_account_id)
    data: ServiceAccountData = service_account.data
    service_key = data.service_key

    params = {
        'group_id': screen_name,
        'fields': 'contacts',
        'v': 5.199
    }
    headers = {
        'Authorization': f'Bearer {service_key}',
    }

    req = requests.get(
        'https://api.vk.ru/method/groups.getById',
        headers=headers,
        params=params
    )
    if req.status_code == 200:
        res_data = req.json()

        if 'error' in res_data:
            return {"msg": res_data['error']['error_msg'], "status": Status.Error}, status.HTTP_400_BAD_REQUEST

        group = res_data.get('response').get('groups')[0]
        group_name = group.get('name')
        group_id = group.get('id')
        contacts = group.get('contacts', None)

        if not contacts:
            return ({"group_name": group_name, "group_id": group_id,
                     "status": Status.ContactsNotFound}, status.HTTP_404_NOT_FOUND)

        for contact in contacts:
            print(contact, vk_id)
            if vk_id == str(contact.get('user_id')):
                return {"group_name": group_name, "group_id": group_id, "status": Status.Accepted}, status.HTTP_200_OK
        return ({"group_name": group_name, "group_id": group_id,
                 "status": Status.Unaccepted}, status.HTTP_406_NOT_ACCEPTABLE)
    else:
        return req.json(), req.status_code


@async_to_sync
async def check_tg_access(internal_data):
    from service_accounts.models import ServiceAccount, ServiceAccountData
    from social_auth.services import get_tg_api_session

    group_link = internal_data.get('groupLink')
    screen_name = group_link.split('/')[-1]
    service_account_id = internal_data.get('serviceAccount')

    service_account = await sync_to_async(
        lambda: ServiceAccount.objects.select_related('data').get(pk=service_account_id)
    )()
    data: ServiceAccountData = service_account.data
    api: TelegramClient = get_tg_api_session(data.session_path)
    async with api:
        try:
            channel: Channel = await api.get_entity(screen_name)
            perm = await api.get_permissions(channel, 'me')
        except ValueError as VE:
            return {"msg": str(VE), "status": Status.Error}, status.HTTP_400_BAD_REQUEST
        except Exception as E:
            return {"msg": str(E), "status": Status.Error}, status.HTTP_400_BAD_REQUEST

    is_admin = perm.is_admin

    if is_admin:
        return {"group_name": channel.title, "group_id": channel.id, "status": Status.Accepted}, status.HTTP_200_OK

    return ({"group_name": channel.title, "group_id": channel.id,
             "status": Status.Unaccepted}, status.HTTP_406_NOT_ACCEPTABLE)


check_access_function = {
    Platforms.VK: check_vk_access,
    Platforms.TG: check_tg_access
}
