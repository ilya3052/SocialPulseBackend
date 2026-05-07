from asgiref.sync import async_to_sync

from social_entities.utils import Platforms


def get_best_posts_info(best_posts_obj, platform, **kwargs):
    return get_posts_info_by_platform_functions.get(platform)(best_posts_obj, kwargs)


def get_vk_best_posts_info(best_post_obj, platform, **kwargs):
    pass


@async_to_sync
def get_tg_best_posts_info(best_post_obj, platform, **kwargs):
    pass


get_posts_info_by_platform_functions = {
    Platforms.VK: get_vk_best_posts_info,
    Platforms.TG: get_tg_best_posts_info
}
