import os

from dotenv import load_dotenv

load_dotenv('.env')

ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
