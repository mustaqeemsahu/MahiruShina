# ==============================
# INLINE HANDLER
# ==============================

from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedSticker
from telegram.ext import ContextTypes, Update

from database.mongo import get_all_anime
from config import FORCE_CHANNEL


# ==============================
# INLINE QUERY
# ==============================

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.inline_query.query.lower().strip()

    if not query:
        return

    animes = await get_all_anime()

    results = []

    # 🔥 Promo
    keyboard = [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}")]]

    results.append(
        InlineQueryResultArticle(
            id="promo",
            title="🔥 Anime Bot",
            input_message_content=InputTextMessageContent(
                "🔥 <b>Anime Provider Bot</b>\n\nSearch anime instantly!",
                parse_mode="HTML"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    )

    # 🔍 Anime Results
    for a in animes:
        if query in a["name"].lower() or any(query in k for k in a["keys"]):

            kb = [
                [InlineKeyboardButton("🎬 Watch & Download", url=a["link"])],
                [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}")]
            ]

            results.append(
                InlineQueryResultCachedSticker(
                    id=f"stk_{a['name']}",
                    sticker_file_id=a["sticker"],
                    reply_markup=InlineKeyboardMarkup(kb)
                )
            )

        if len(results) >= 10:
            break

    await update.inline_query.answer(results, cache_time=1)
