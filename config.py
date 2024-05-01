import os
from dotenv import load_dotenv


load_dotenv()


API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

DB_USERNAME = 'denis'
DB_NAME = 'pyrogram'
DB_HOST = 'localhost'
DB_PORT = 5432
DB_PASSWORD = os.getenv('DB_PASSWORD')