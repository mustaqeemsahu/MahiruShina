# ==============================
# ANIME HANDLER
# ==============================

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import ADMIN_IDS, FORCE_CHANNEL
from database.mongo import add_anime_db, delete_anime_db, get_all_anime
from utils.filters import force_sub, check_bot_status
# ==============================
# ADD ANIME
# ==============================

async def add_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    text = update.message.text.replace("/add", "", 1).strip()

    parts = [p.strip() for p in text.split("|")]

    if len(parts) != 5:
        return await update.message.reply_text(
            "❌ <b>Format:</b>\n\n"
            "<code>/add Anime Name | keyword1, keyword2 | STICKER_ID | HINDI_LINK_OR_- | ENGLISH_LINK_OR_-</code>\n\n"
            "<b>Examples:</b>\n\n"
            "<code>/add Solo Leveling | solo leveling, sl | STICKER_ID | https://t.me/hindi | https://t.me/english</code>\n\n"
            "<code>/add Naruto | naruto | STICKER_ID | https://t.me/hindi | -</code>\n\n"
            "<code>/add One Piece | one piece | STICKER_ID | - | https://t.me/english</code>",
            parse_mode="HTML"
        )

    name, keywords, sticker, hindi_link, english_link = parts

    keys = [
        k.strip().lower()
        for k in keywords.split(",")
        if k.strip()
    ]

    # Convert "-" to None
    if hindi_link == "-":
        hindi_link = None

    if english_link == "-":
        english_link = None

    await add_anime_db(
        name=name,
        keys=keys,
        sticker=sticker,
        hindi_link=hindi_link,
        english_link=english_link
    )

    msg = (
        f"✅ <b>Anime Added Successfully!</b>\n\n"
        f"🎬 <b>Name:</b> <code>{name}</code>\n"
        f"🔑 <b>Keywords:</b> <code>{', '.join(keys)}</code>\n"
        f"🇮🇳 <b>Hindi:</b> {'✅ Added' if hindi_link else '❌ Not Available'}\n"
        f"🇺🇸 <b>English:</b> {'✅ Added' if english_link else '❌ Not Available'}"
    )

    await update.message.reply_text(
        msg,
        parse_mode="HTML"
    )

# ==============================
# DELETE ANIME
# ==============================

async def del_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    name = update.message.text.replace("/del", "", 1).strip().lower()
    await delete_anime_db(name)

    await update.message.reply_text("✅ Deleted (if existed).")


# ==============================
# EXACT SEARCH (/anime)
# ==============================

import re
import asyncio

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import ContextTypes

from config import FORCE_CHANNEL, REPORT_GROUP_ID
from utils.filters import force_sub, check_bot_status
from database.mongo import get_all_anime


# ==============================
# NORMALIZE
# ==============================

def normalize(text: str) -> str:
    return re.sub(r"[-_]", " ", text.lower()).strip()


# ==============================
# AUTO DELETE
# ==============================

async def auto_delete(message, sec=10):
    await asyncio.sleep(sec)

    try:
        await message.delete()
    except:
        pass


# ==============================
# ANIME SEARCH
# ==============================

async def anime_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # FORCE SUB
    if not await force_sub(update, context):
        return

    # BOT STATUS
    if not await check_bot_status(update):
        return

    # QUERY
    raw_query = " ".join(context.args)

    if not raw_query:
        return await update.message.reply_text(
            "❌ Example:\n/anime Naruto"
        )

    query = normalize(raw_query)

    # DATABASE
    anime_list = await get_all_anime()

    matches = []

    for a in anime_list:

        name = normalize(a.get("name", ""))

        keys = [
            normalize(k)
            for k in a.get("keys", [])
        ]

        # STRICT MATCH
        if query == name or query in keys:
            matches.append(a)

    # LOG SEARCH
    try:
        await context.bot.send_message(
            chat_id=REPORT_GROUP_ID,
            text=(
                f"🔍 <b>Anime Search</b>\n\n"
                f"👤 User: {update.effective_user.first_name}\n"
                f"🆔 ID: <code>{update.effective_user.id}</code>\n"
                f"🔎 Query: <code>{query}</code>"
            ),
            parse_mode="HTML"
        )
    except:
        pass

    # NO RESULT
    if not matches:

        msg = await update.message.reply_text(
            "❌ No Anime Found."
        )

        asyncio.create_task(auto_delete(msg, 10))
        return

    # SINGLE RESULT
    if len(matches) == 1:

        a = matches[0]

        keyboard = [
            [
                InlineKeyboardButton(
                    "🎬 Watch & Download",
                    url=a["link"]
                )
            ],
            [
                InlineKeyboardButton(
                    "📢 Join Main Channel",
                    url=f"https://t.me/{FORCE_CHANNEL.replace('@', '')}"
                )
            ]
        ]

        return await update.message.reply_sticker(
            sticker=a["sticker"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # MULTIPLE RESULTS
    text = (
        f"🔎 <b>Multiple Anime Found</b>\n"
        f"Query: <code>{query}</code>"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                a["name"],
                callback_data=f"anime_{a['name']}"
            )
        ]
        for a in matches
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
