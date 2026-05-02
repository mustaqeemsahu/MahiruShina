# ==============================
# ANIME HANDLER
# ==============================

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.mongo import add_anime_db, delete_anime_db, get_all_anime
from config import ADMIN_IDS, FORCE_CHANNEL

# ==============================
# ADD ANIME
# ==============================

async def add_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    text = update.message.text.replace("/add", "", 1).strip()
    parts = [p.strip() for p in text.split("|") if p.strip()]

    if len(parts) != 4:
        return await update.message.reply_text(
            "❌ Format:\n/add Anime Name | keyword1, keyword2 | STICKER_ID | LINK"
        )

    name, keywords, sticker, link = parts
    keys = [k.strip().lower() for k in keywords.split(",")]

    await add_anime_db(name, keys, sticker, link)

    await update.message.reply_text(f"✅ Anime Added: {name}")


# ==============================
# DELETE ANIME
# ==============================

async def del_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    name = update
