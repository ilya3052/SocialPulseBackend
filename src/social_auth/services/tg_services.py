import os

from dotenv import load_dotenv
from telethon import TelegramClient

from common.config import API_ID, API_HASH

load_dotenv()


def get_tg_api_session(session_path):
    try:
        tg_api = TelegramClient(api_id=API_ID, api_hash=API_HASH, session=session_path)
        return tg_api
    except Exception as e:
        print(f"Ошибка создания TelegramClient: {e}")
        return None
