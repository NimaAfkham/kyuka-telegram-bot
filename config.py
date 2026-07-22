import os
from dotenv import load_dotenv

# Load .env file if it exists (for local development)
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_IDS = [
    int(uid.strip())
    for uid in os.getenv("ALLOWED_USER_IDS", "").split(",")
    if uid.strip()
]

DATABASE_URL = os.getenv("DATABASE_URL")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "master")
GITHUB_MENU_PATH = os.getenv("GITHUB_MENU_PATH", "menu.json")

# Soft checks (only raise if really missing)
missing = []
if not TELEGRAM_BOT_TOKEN:
    missing.append("TELEGRAM_BOT_TOKEN")
if not ALLOWED_USER_IDS:
    missing.append("ALLOWED_USER_IDS")
if not DATABASE_URL:
    missing.append("DATABASE_URL")
if not GITHUB_TOKEN:
    missing.append("GITHUB_TOKEN")
if not GITHUB_REPO:
    missing.append("GITHUB_REPO")

if missing:
    raise ValueError(f"Missing required environment variables: {', '.join(missing)}")