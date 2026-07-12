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
        f"<b>📜 Anime List</b>\n"
        f"Page {page}/{total_pages}\n\n"
    )

    keyboard = []

    start_no = (page - 1) * ANIME_PER_PAGE

    for i, anime in enumerate(page_data, start=start_no + 1):

        hindi = anime.get("hindi_link")
        english = anime.get("english_link")
        old = anime.get("link")

        # BOTH LANGUAGES
        if hindi and english:

            text += f"{i}. {anime['name']} 👇\n"

            keyboard.append([
                InlineKeyboardButton(
                    anime["name"],
                    callback_data=f"anime_{anime['name']}"
                )
            ])

        # HINDI ONLY
        elif hindi:

            text += (
                f"{i}. "
                f"<a href='{hindi}'>{anime['name']}</a>\n"
            )

        # ENGLISH ONLY
        elif english:

            text += (
                f"{i}. "
                f"<a href='{english}'>{anime['name']}</a>\n"
            )

        # OLD DATABASE
        elif old:

            text += (
                f"{i}. "
                f"<a href='{old}'>{anime['name']}</a>\n"
            )

        else:

            text += f"{i}. {anime['name']}\n"

    if total_pages > 1:

        keyboard.append([
            InlineKeyboardButton(
                "⬅️ Prev",
                callback_data="alist_1"
            ),
            InlineKeyboardButton(
                "➡️ Next",
                callback_data="alist_2"
            )
        ])

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
    )
