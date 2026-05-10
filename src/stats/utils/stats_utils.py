from enum import Enum

from icecream import ic

from social_entities.utils import Platforms
from stats.models import BestPostInfo

def format_posts_info(posts):
    posts_data = {
        "most_liked": {},
        "most_commented": {},
        "most_reposted": {},
        "most_viewed": {},
    }

    last_updated_at = None

    for post in posts: #type: BestPostInfo
        if not last_updated_at:
            posts_data['last_updated_at'] = post.last_updated_at
        posts_data[post.post_type.lower()] = {
            'text': post.content,
            'metrics': {
                "views": post.views_count,
                "likes": post.likes_count,
                "comments": post.comms_count,
                "reposts": post.reposts_count
            }
        }
        match Platforms(post.group.platform.alias):
            case Platforms.VK:
                posts_data[post.post_type.lower()]['link'] = f'https://vk.ru/wall-{post.group.external_id}_{post.post_id}'
            case Platforms.TG:
                posts_data[post.post_type.lower()]['link'] = f'{post.group.link}/{post.post_id}'

    return posts_data



