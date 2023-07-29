import os
from prometheus_client import start_http_server

from dotenv import load_dotenv
load_dotenv()

def key(key):
    return f'discord_bot.{key}'

def prometheus():
    start_http_server(9091)