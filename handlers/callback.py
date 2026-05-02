# ==============================
# CALLBACK HANDLER
# ==============================

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.mongo import get_all_anime
from handlers.animelist import build_page
from config import ANIME_PER_PAGE, FORCE_CHANNEL


# ==============================
# BUTTON CLICK
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

        for a in animes:
            if a["name"].lower() == name:

                keyboard = [
                    [InlineKeyboardButton("🎬 Watch & Download", url=a["link"])],
                    [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}")]
                ]

                await query.message.reply_sticker(
                    sticker=a["sticker"],
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                break

    # ==============================
    # PAGINATION
    # ==============================
    elif data.startswith("alist_"):

        page = int(data.split("_")[1])

        animes = sorted(animes, key=lambda x: x["name"].lower())

        page_data, page, total_pages = build_page(animes, page)

        text = f"<b>📜 Anime List</b>\nPage {page}/{total_pages}\n\n"

        start_no = (page - 1) * ANIME_PER_PAGE

        for i, a in enumerate(page_data, start=start_no + 1):
            text += f"{i}. <a href='{a['link']}'>{a['name']}</a>\n"

        prev_p = page - 1 if page > 1 else 1
        next_p = page + 1 if page < total_pages else total_pages

        keyboard = [[
            InlineKeyboardButton("⬅️ Prev", callback_data=f"alist_{prev_p}"),
            InlineKeyboardButton("➡️ Next", callback_data=f"alist_{next_p}")
        ]]

        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
