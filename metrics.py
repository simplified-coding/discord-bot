import os
from prometheus_client import start_http_server

from dotenv import load_dotenv
load_dotenv()

def prometheus():
    start_http_server(9091)