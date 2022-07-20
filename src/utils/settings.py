import os
from dotenv import load_dotenv

from src.utils.utils import project_root

load_dotenv(project_root() / "docker/.env")

postgres = {
    "host": os.environ.get("POSTGRES_HOST"),
    "port": os.environ.get("POSTGRES_PORT"),
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
}

telegram = {
    "token": os.environ.get("API_TELEGRAM_TOKEN")
}

fastapi = {
    "secret": os.environ.get('API_SECRET', "SECRET"),
    "token_lifetime": 60*60*24*30  # 30 days lifetime
}