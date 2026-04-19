import json
import secrets
from enum import IntEnum, Enum
from typing import Union

from telethon import TelegramClient
import os


class Status(IntEnum):
    Accepted = 0
    Unaccepted = 1
    ContactsNotFound = 2
    Error = 3

class Platforms(Enum):
    VK = (1, 'vk')
    TG = (2, 'tg')

    def __init__(self, code: int, alias: str):
        self.code = code
        self.alias = alias

    @classmethod
    def _missing_(cls, value: Union[int, str]):
        if isinstance(value, str):
            val = value.strip().lower()
            for member in cls:
                if member.alias == val:
                    return member
        if isinstance(value, int):
            return cls._value2member_map_.get(value)
        raise ValueError(f"{value} некорректный параметр для {cls.__name__}")

    @property
    def id(self) -> int:
        return self.code

    @property
    def name(self) -> str:
        return self.alias

    def __int__(self) -> int:
        return self.code


def generate_short_token() -> str:
    url_token = secrets.token_urlsafe(48)
    return url_token


def prepare_message(token) -> str:
    url = f'https://socialpulse.sandbox.com/email/activate?token={token}'
    # добавить в сообщение больше информации, возможно даже сделать html шаблон в котором будут также отображаться некоторые данные пользователя
    message = f"Для подтверждения электронной почты перейдите по <a href=\"{url}\" target=_blank>ссылке</a>"

    return message


def try_parse_json(value):
    """
    Если value — строка с JSON, пытаемся распарсить.
    Иначе возвращаем как есть.
    """
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value

def get_tg_api_session(session_path):
    try:
        tg_api = TelegramClient(api_id=int(os.getenv("API_ID")), api_hash=os.getenv("API_HASH"), session=session_path)
        return tg_api
    except Exception as e:
        print(f"Ошибка создания TelegramClient: {e}")
        return None