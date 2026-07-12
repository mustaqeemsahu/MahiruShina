# ==============================
# CALLBACK HANDLER
# ==============================

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes

from database.mongo import get_all_anime
from handlers.animelist import build_page
from config import ANIME_PER_PAGE, FORCE_CHANNEL


# ==============================
# BUTTON BUILDER
# ==============================

def build_buttons(anime):

    keyboard = []

    hindi = anime.get("hindi_link")
    english = anime.get("english_link")
    old_link = anime.get("link")  # Backward compatibility

    row = []

    if hindi:
        row.append(
            InlineKeyboardButton(
                "🇮🇳 Watch In Hindi",
                url=hindi
            )
        )

    if english:
        row.append(
            InlineKeyboardButton(
                "🇺🇸 Watch In English",
                url=english
            )
        )

    if not hindi and not english and old_link:
        row.append(
            InlineKeyboardButton(
                "🎬 Watch & Download",
                url=old_link
            )
        )

    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(
            "📢 Join Main Channel",
            url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


# ==============================
# CALLBACK HANDLER
# ==============================

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    animes = await get_all_anime()

    # ==============================
    # ANIME BUTTON
    # ==============================

    if data.startswith("anime_"):

        name = data.replace("anime_", "").lower()

        for anime in animes:

            if anime["name"].lower() == name:

                try:

                    await query.message.reply_sticker(
                        sticker=anime["sticker"],
                        reply_markup=build_buttons(anime)
                    )

                except Exception:

                    await query.message.reply_text(
                        anime["name"],
                        reply_markup=build_buttons(anime)
                    )

                return

    # ==============================
    # PAGINATION
    # ==============================

    elif data.startswith("alist_"):

        page = int(data.split("_")[1])

        animes = sorted(
            animes,
            key=lambda x: x["name"].lower()
        )

        page_data, page, total_pages = build_page(
            animes,
            page
        )

        text = (
            f"<b>📜 Anime List</b>\n"
            f"Page {page}/{total_pages}\n\n"
        )

        start_no = (page - 1) * ANIME_PER_PAGE

        for i, anime in enumerate(
            page_data,
            start=start_no + 1
        ):

            # Prefer Hindi > English > Old Link
            link = (
                anime.get("hindi_link")
                or anime.get("english_link")
                or anime.get("link", "#")
            )

            text += (
                f"{i}. "
                f"<a href='{link}'>{anime['name']}</a>\n"
            )

        prev_page = page - 1 if page > 1 else 1
        next_page = (
            page + 1
            if page < total_pages
            else total_pages
        )

        keyboard = [[
            InlineKeyboardButton(
                "⬅️ Prev",
                callback_data=f"alist_{prev_page}"
            ),
            InlineKeyboardButton(
                "➡️ Next",
                callback_data=f"alist_{next_page}"
            )
        ]]

        await query.message.edit_text(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(keyboard)
                    )
