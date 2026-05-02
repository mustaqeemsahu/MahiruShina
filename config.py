# ==============================
# CONFIG FILE (ENV + CONSTANTS)
# ==============================

from dotenv import load_dotenv
import os

load_dotenv()

# 🔐 ENV VARIABLES
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# ⚠️ SAFETY CHECK
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing in .env")

if not MONGO_URI:
    raise ValueError("MONGO_URI is missing in .env")

# ==============================
# BOT SETTINGS
# ==============================

FORCE_CHANNEL = "@Team_Sahuu"

ADMIN_IDS = [7953380478, 5208998008]

REPORT_GROUP_ID = -1003625335610

ANIME_PER_PAGE = 25

# ==============================
# MEDIA
# ==============================

START_PHOTO = "AgACAgUAAxkBAAICQGm1FC6u4tZ-_yIdBE69O2Cgk134AAImD2sbCjyoVYkRWpbe68nrAQADAgADeQADOgQ"
GROUP_PHOTO = "AgACAgUAAxkBAAICQGm1FC6u4tZ-_yIdBE69O2Cgk134AAImD2sbCjyoVYkRWpbe68nrAQADAgADeQADOgQ"

WELCOME_EMOJIS = ["👋", "✨", "🌸", "🔥", "💫"]
