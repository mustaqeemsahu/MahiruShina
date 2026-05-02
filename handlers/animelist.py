# ==============================
# ANIMELIST HANDLER
# ==============================

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.mongo import get_all_anime
from config import ANIME_PER_PAGE

# ==============================
# BUILD PAGE
# ==============================

def build_page(animes, page):
    total = len(animes)
    total_pages = max(1, (total + ANIME_PER_PAGE - 1) // ANIME_PER_PAGE)

    page = max(1, min(page, total_pages))

    start = (page - 1) * ANIME_PER_PAGE
    end = start + ANIME_PER_PAGE

    return animes[start:end], page, total_pages


# ==============================
# /animelist
# ==============================

async def animelist(update: Update, context: ContextTypes.DEFAULT_TYPE):

    animes = await get_all_anime()

    if not animes:
        return await update.message.reply_text("❌ No anime added yet.")

    # sort
    animes = sorted(animes, key=lambda x: x["name"].lower())

    page_data, page, total_pages = build_page(animes, 1)

    text = f"<b>📜 Anime List</b>\nPage {page}/{total_pages}\n\n"

    for i, a in enumerate(page_data, start=1):
        text += f"{i}. <a href='{a['link']}'>{a['name']}</a>\n"

    keyboard = []
    if total_pages > 1:
        keyboard.append([
            InlineKeyboardButton("⬅️ Prev", callback_data="alist_1"),
            InlineKeyboardButton("➡️ Next", callback_data="alist_2")
        ])

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None,
        parse_mode="HTML",
        disable_web_page_preview=True
    )
