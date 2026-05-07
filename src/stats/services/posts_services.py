import requests
from asgiref.sync import async_to_sync

from social_auth.services import get_tg_api_session
from social_entities.utils import Platforms
from stats.models import BestPosts


def get_best_posts_info(best_posts_obj, platform, **kwargs):
    return get_posts_info_by_platform_functions.get(platform)(best_posts_obj, **kwargs)


def get_vk_best_posts_info(best_post_obj: BestPosts, service_key):
    posts_ids = best_post_obj.to_dict()

    group = best_post_obj.group
    group_id = group.external_id
    posts_ids_with_group_id = ','.join(list(map(lambda item: f'-{group_id}_{item}', posts_ids.values())))

    params = {
        'posts': posts_ids_with_group_id,
        'v': 5.199
    }
    headers = {
        'Authorization': f'Bearer {service_key}',
    }
    req = requests.get(
        'https://api.vk.ru/method/wall.getById',
        headers=headers,
        params=params
    )
    # добавить обработку ошибок

    items = req.json().get('response').get('items')
    items_by_id = {str(item.get('id')): item for item in items}
    posts_data = {
        "most_viewed": {},
        "most_liked": {},
        "most_commented": {},
        "most_reposted": {},
    }

    for metric, post_id in posts_ids.items():
        item = items_by_id.get(str(post_id))
        if item:
            item_id = item.get('id')
            posts_data[metric] = {
                'link': f'https://vk.ru/wall-{group_id}_{item_id}',
                'text': item.get('text'),
                'metrics': {
                    "views": item.get('views', {}).get('count', 0),
                    "likes": item.get('likes', {}).get('count', 0),
                    "comments": item.get('comments', {}).get('count', 0),
                    "reposts": item.get('reposts', {}).get('count', 0)
                }
            }

    return posts_data


@async_to_sync
async def get_tg_best_posts_info(best_post_obj: BestPosts, session_path):
    api = get_tg_api_session(session_path)
    group = best_post_obj.group
    group_id = group.external_id

    posts_ids = best_post_obj.to_dict()

    async with api:
        channel = await api.get_entity(group_id)
        name = channel.username
        messages = await api.get_messages(channel, ids=list(map(int, posts_ids.values())))

    posts_data = {
        "most_viewed": {},
        "most_liked": {},
        "most_commented": {},
        "most_reposted": {},
    }

    items_by_id = {str(message.id): message for message in messages}

    for metric, post_id in posts_ids.items():
        item = items_by_id.get(str(post_id))
        reactions_count = 0
        if item.reactions:
            for reaction in item.reactions.results:
                reactions_count += reaction.count
        if item:
            item_id = item.id
            posts_data[metric] = {
                'link': f'https://t.me/{name}/{item_id}',
                'text': item.message,
                'metrics': {
                    "views": item.views,
                    "likes": reactions_count,
                    "comments": item.replies or 0,
                    "reposts": item.forwards
                }
            }
    return posts_data


get_posts_info_by_platform_functions = {
    Platforms.VK: get_vk_best_posts_info,
    Platforms.TG: get_tg_best_posts_info
}
