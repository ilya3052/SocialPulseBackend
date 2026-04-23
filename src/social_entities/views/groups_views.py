import requests
from asgiref.sync import async_to_sync, sync_to_async
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from telethon import TelegramClient
from telethon.tl.types import Channel

from accounts.models import Group
from accounts.serializers import GroupSerializer
from accounts.utils import Platforms, Status, get_tg_api_session


class GroupsView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer

    def get_queryset(self):
        return Group.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user_id'] = [self.request.user.id]

        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response(status=status.HTTP_201_CREATED)


def check_vk_access(internal_data):
    from admin_panel.models import ServiceAccount, ServiceAccountData
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
    from admin_panel.models import ServiceAccount, ServiceAccountData
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


class CheckGroupAccessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        internal_data: dict = request.data
        print(internal_data)

        platform_alias = internal_data.get('platform')
        platform = Platforms(platform_alias)

        result, status_code = check_access_function.get(platform)(internal_data)
        print(result, status_code)
        return Response(result, status_code)
