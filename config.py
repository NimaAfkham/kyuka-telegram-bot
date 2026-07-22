import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_IDS = [int(uid.strip()) for uid in os.getenv("ALLOWED_USER_IDS", "").split(",") if uid.strip()]

DATABASE_URL = os.getenv("DATABASE_URL")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")          # e.g. NimaAfkham/Kyuka_Menu_UI
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "master")
GITHUB_MENU_PATH = os.getenv("GITHUB_MENU_PATH", "menu.json")

# Safety checks
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing in .env")
if not ALLOWED_USER_IDS:
    raise ValueError("ALLOWED_USER_IDS is missing in .env")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing in .env")
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN is missing in .env")