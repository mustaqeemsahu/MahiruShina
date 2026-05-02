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

    name = update.message.text.replace("/del", "", 1).strip().lower()
    await delete_anime_db(name)

    await update.message.reply_text("✅ Deleted (if existed).")


# ==============================
# EXACT SEARCH (/anime)
# ==============================

import re
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


# 🔥 Normalize
def normalize(text: str) -> str:
    return re.sub(r'[-_]', ' ', text.lower()).strip()


async def anime_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await force_sub_wrapper(update, context):
        return
    if not await check_bot_status(update):
        return

    raw_query = " ".join(context.args)
    query = normalize(raw_query)

    if not query:
        return await update.message.reply_text("❌ Example: /anime Naruto")

    d = load()
    matches = []

    for a in d["anime"].values():
        name = normalize(a["name"])
        keys = [normalize(k) for k in a.get("keys", [])]

        # ✅ STRICT MATCH ONLY
        if query == name or query in keys:
            matches.append(a)

    # 🔥 Logging
    try:
        await context.bot.send_message(
            REPORT_GROUP_ID,
            f"🔍 <b>Anime Search</b>\n"
            f"User: {update.effective_user.first_name}\n"
            f"ID: <code>{update.effective_user.id}</code>\n"
            f"Query: {query}",
            parse_mode="HTML"
        )
    except:
        pass

    if not matches:
        msg = await update.message.reply_text("❌ No Anime Found.")
        asyncio.create_task(auto_delete(msg, 10))
        return

    # ✅ Single result
    if len(matches) == 1:
        a = matches[0]

        keyboard = [
            [InlineKeyboardButton("🎬 Watch & Download", url=a["link"])],
            [InlineKeyboardButton("📢 Join Main Channel", url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}")]
        ]

        return await update.message.reply_sticker(
            sticker=a["sticker"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ✅ Multiple (rare, only if duplicate keywords)
    text = f"🔎 <b>Multiple anime found for</b> <code>{query}</code>\n\n"

    keyboard = [
        [InlineKeyboardButton(a["name"], callback_data=f"anime_{a['name']}")]
        for a in matches
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
        )
