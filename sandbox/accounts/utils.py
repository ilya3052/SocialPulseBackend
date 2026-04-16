import json
import secrets
from enum import IntEnum


class Status(IntEnum):
    Accepted = 0
    Unaccepted = 1
    ContactsNotFound = 2
    Error = 3


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
