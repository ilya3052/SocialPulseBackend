from pathlib import Path

import requests
from asgiref.sync import async_to_sync, sync_to_async
from django.db.models import Count, Q
from django.utils.module_loading import import_string
from rest_framework import status
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import Channel, User

from common.config import ENCRYPTION_KEY
from common.utils import decrypt
from social_auth.services import get_tg_api_session
from social_entities.models import Group
from social_entities.utils import Status, Platforms
from social_pulse import settings


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
    service_key = decrypt(data.service_key, ENCRYPTION_KEY)

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
            if vk_id == str(contact.get('user_id')):
                return {"group_name": group_name, "group_id": group_id, "status": Status.Accepted}, status.HTTP_200_OK
        return ({"group_name": group_name, "group_id": group_id,
                 "status": Status.Unaccepted}, status.HTTP_406_NOT_ACCEPTABLE)
    else:
        return req.json(), req.status_code


@async_to_sync
async def check_tg_access(internal_data):
    service_account_model = import_string('service_accounts.models.ServiceAccount')
    service_account_data_model = import_string('service_accounts.models.ServiceAccountData')
    from social_auth.services import get_tg_api_session

    group_link = internal_data.get('groupLink')
    screen_name = group_link.split('/')[-1]
    service_account_id = internal_data.get('serviceAccount')

    service_account = await sync_to_async(
        lambda: service_account_model.objects.select_related('data').get(pk=service_account_id)
    )()
    data: service_account_data_model = service_account.data
    api: TelegramClient = get_tg_api_session(data.session_path)
    async with api:
        try:
            channel: Channel = await api.get_entity(screen_name)
            user: User = await api.get_entity(int(internal_data.get('user_social_id')))
            perm = await api.get_permissions(channel, user)
        except ValueError as VE:
            return {"msg": str(VE), "status": Status.Error}, status.HTTP_400_BAD_REQUEST
        except Exception as E:
            if 'target user is not a member' in str(E):
                return ({"group_name": channel.title, "group_id": channel.id,
                         "status": Status.Unaccepted}, status.HTTP_406_NOT_ACCEPTABLE)
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


def get_group_info(group_id, platform: Platforms, **kwargs):
    return get_group_info_function.get(platform)(group_id, **kwargs)


def get_vk_info(group_id, **kwargs):
    params = {
        'group_id': group_id,
        'fields': 'description',
        'v': 5.199
    }
    headers = {
        'Authorization': f'Bearer {kwargs.get('service_key')}',
    }

    req = requests.get(
        'https://api.vk.ru/method/groups.getById',
        headers=headers,
        params=params
    )
    if (code := req.status_code) != 200:
        return {"error_code": code}  # добавить информативные ошибки в зависимости от кода ответа

    data = req.json()
    group_data = data.get('response').get('groups')[0]
    return {"description": group_data.get('description'), "photo_url": group_data.get('photo_100')}


@async_to_sync
async def get_tg_info(group_id, **kwargs):
    api = get_tg_api_session(kwargs.get('session_path'))
    if not api:
        return {"error": "Не удалось получить объект api для связи с Telegram"}

    async with (api):
        channel = await api.get_entity(group_id)

        full_channel = await api(GetFullChannelRequest(channel))
        description = full_channel.full_chat.about

        media_root = Path(settings.MEDIA_ROOT)
        relative_path = Path('group_photos') / f"{group_id}.jpg"

        full_path = media_root / relative_path

        await api.download_profile_photo(channel, str(full_path))

    return {"description": description,
            "photo_url": f'https://socialpulse.sandbox.com/media/{str(relative_path).replace('\\', '/')}'}


get_group_info_function = {
    Platforms.VK: get_vk_info,
    Platforms.TG: get_tg_info
}


def delete_group(group_obj: Group, user):
    users_count = group_obj.users.count()
    if not group_obj.users.filter(id=user.id).exists():
        return status.HTTP_404_NOT_FOUND
    if users_count == 1:
        group_obj.delete()
        return status.HTTP_204_NO_CONTENT
    group_obj.users.remove(user)
    return status.HTTP_204_NO_CONTENT
