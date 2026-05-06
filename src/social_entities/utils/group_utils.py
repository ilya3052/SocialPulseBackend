from enum import IntEnum, Enum
from typing import Union


class Status(IntEnum):
    Accepted = 0
    Unaccepted = 1
    ContactsNotFound = 2
    Error = 3


class Platforms(Enum):
    VK = 'vk'
    TG = 'tg'
