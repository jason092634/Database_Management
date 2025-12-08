import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

# Redis（用來記錄查詢次數、排行榜）
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST"),
    "port": int(os.getenv("REDIS_PORT")),
    "password": os.getenv("REDIS_PASSWORD"),
    "db": int(os.getenv("REDIS_DB")),
}

ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")