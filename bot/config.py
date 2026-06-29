import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

# Asosiy papka
BASE_DIR = Path(__file__).resolve().parent.parent

# Bot sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
TIMEZONE = os.getenv("TIMEZONE", "Asia/Tashkent")

# Database
DB_PATH = os.getenv("DB_PATH", "database.db")
DB_URL = f"sqlite+aiosqlite:///{BASE_DIR / DB_PATH}"

# Premium limitlar
FREE_LIMITS = {
    "content_checks_per_day": 3,
    "max_children": 1,
    "report_history_days": 7,
    "keyword_count": 10,
    "test_per_month": 1,
}

PREMIUM_LIMITS = {
    "content_checks_per_day": 999,
    "max_children": 5,
    "report_history_days": 90,
    "keyword_count": 999,
    "test_per_month": 4,
}
