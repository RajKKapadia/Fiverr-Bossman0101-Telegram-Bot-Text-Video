import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TELEGRAM_BOT_API_KEY = os.getenv("TELEGRAM_BOT_API_KEY")
LUMA_API_KEY = os.getenv("LUMA_API_KEY")

WAIT_TIME = 300
