from enum import IntEnum, Enum


class Status(IntEnum):
    Accepted = 0
    Unaccepted = 1
    ContactsNotFound = 2
    Error = 3


class Platforms(Enum):
    VK = 'VK'
    TG = 'TG'
