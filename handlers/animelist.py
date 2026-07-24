# ==============================
# ANIMELIST HANDLER
# ==============================

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes

from database.mongo import get_all_anime
from config import ANIME_PER_PAGE


# ==============================
# BUILD PAGE
# ==============================

def build_page(animes, page):

    total = len(animes)

    total_pages = max(
        1,
        (total + ANIME_PER_PAGE - 1) // ANIME_PER_PAGE
    )

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
        return await update.message.reply_text(
            "❌ No anime added yet."
        )

    animes = sorted(
        animes,
        key=lambda x: x["name"].lower()
    )

    page_data, page, total_pages = build_page(
        animes,
        1
    )

    text = (
    "📚 <b>Our Anime Collection</b>\n\n"
    "╭━━━━━━━━━━━━━━━━━━╮\n"
    f"📄 <b>Page :</b> {page}/{total_pages}\n"
    f"🎬 <b>Total :</b> {len(animes)} Anime\n"
    "╰━━━━━━━━━━━━━━━━━━╯\n\n"
)

start_no = (page - 1) * ANIME_PER_PAGE

for i, anime in enumerate(
    page_data,
    start=start_no + 1
):

    hindi = anime.get("hindi_link", "-")
    english = anime.get("english_link", "-")
    old = anime.get("link", "-")

    text += f"<b>{i}. {anime['name']}</b>\n"
    text += "➥ "

    links = []

    # Hindi
    if hindi and hindi != "-":
        links.append(
            f"<a href='{hindi}'>🇮🇳 Hindi</a>"
        )

    # English
    if english and english != "-":
        links.append(
            f"<a href='{english}'>🇺🇸 English</a>"
        )

    # Old Database Support
    if old and old != "-" and not links:
        links.append(
            f"<a href='{old}'>🔰 Watch</a>"
        )

    if links:
        text += " | ".join(links)
    else:
        text += "❌ No Link Available"

    text += "\n\n"

    prev_page = page - 1 if page > 1 else 1
    next_page = page + 1 if page < total_pages else total_pages

    keyboard = []

    if total_pages > 1:
        keyboard.append([
            InlineKeyboardButton(
                "⬅️ Prev",
                callback_data=f"alist_{prev_page}"
            ),
            InlineKeyboardButton(
                f"{page}/{total_pages}",
                callback_data="ignore"
            ),
            InlineKeyboardButton(
                "Next ➡️",
                callback_data=f"alist_{next_page}"
            )
        ])

    await update.message.reply_text(
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(keyboard)
        if keyboard else None
    )
