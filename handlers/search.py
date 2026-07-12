# ==============================
# SEARCH HANDLER
# ==============================

import re
import asyncio

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import ContextTypes

from database.mongo import get_all_anime
from utils.cooldown import check_cooldown
from utils.filters import force_sub
from config import FORCE_CHANNEL


# ==============================
# NORMALIZE
# ==============================

def normalize(text: str):

    text = text.lower()

    text = re.sub(r"[^a-z0-9\s]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==============================
# AUTO DELETE
# ==============================

async def auto_delete(message, sec=43200):

    await asyncio.sleep(sec)

    try:
        await message.delete()
    except:
        pass


# ==============================
# BUTTON BUILDER
# ==============================

def build_buttons(anime):

    keyboard = []

    hindi = anime.get("hindi_link")
    english = anime.get("english_link")

    # Backward compatibility
    old_link = anime.get("link")

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

    # Old database support
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
# PARTIAL SEARCH
# ==============================

async def improved_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await force_sub(update, context):
        return

    user_id = update.effective_user.id

    if not check_cooldown(user_id):
        return await update.message.reply_text(
            "⏳ Wait 5 sec"
        )

    query = " ".join(context.args).lower()

    if not query:
        return await update.message.reply_text(
            "Example:\n/search Naruto"
        )

    animes = await get_all_anime()

    matches = [
        anime for anime in animes
        if query in anime["name"].lower()
        or any(query in key.lower() for key in anime.get("keys", []))
    ]

    if not matches:
        return await update.message.reply_text(
            "❌ No Anime Found."
        )

    text = "🎌 Search Results\n\n"

    for anime in matches[:5]:
        text += f"• {anime['name']}\n"

    await update.message.reply_text(text)


# ==============================
# BUTTON SEARCH
# ==============================

async def button_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await force_sub(update, context):
        return

    query = " ".join(context.args).lower()

    if not query:
        return await update.message.reply_text(
            "Example:\n/btn Naruto"
        )

    animes = await get_all_anime()

    matches = [
        anime for anime in animes
        if query in anime["name"].lower()
        or any(query in key.lower() for key in anime.get("keys", []))
    ]

    if not matches:
        return await update.message.reply_text(
            "❌ No Anime Found."
        )

    keyboard = []

    for anime in matches[:5]:

        keyboard.append([
            InlineKeyboardButton(
                anime["name"],
                callback_data=f"anime_{anime['name']}"
            )
        ])

    await update.message.reply_text(
        "🎌 Select Anime",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==============================
# DIRECT SEARCH
# ==============================

async def direct_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    raw_text = update.message.text

    if not raw_text:
        return

    if raw_text.startswith("/"):
        return

    text = normalize(raw_text)

    animes = await get_all_anime()

    matches = []
    # ==============================
    # FIND MATCHES
    # ==============================

    for anime in animes:

        anime_name = anime.get("name", "")
        anime_keys = anime.get("keys", [])

        found_keyword = None

        all_keywords = anime_keys + [anime_name]

        for keyword in all_keywords:

            keyword = normalize(keyword)

            if keyword and keyword in text:
                found_keyword = keyword
                break

        if found_keyword:

            matches.append({
                "anime": anime,
                "keyword": found_keyword,
                "length": len(found_keyword)
            })

    if not matches:
        return

    # ==============================
    # LONGEST KEYWORD FIRST
    # ==============================

    matches.sort(
        key=lambda x: x["length"],
        reverse=True
    )

    final_matches = []
    added = set()

    for item in matches:

        anime = item["anime"]

        if anime["name"] not in added:

            final_matches.append(anime)
            added.add(anime["name"])

    matches = final_matches[:5]

    # ==============================
    # SINGLE RESULT
    # ==============================

    if len(matches) == 1:

        anime = matches[0]

        markup = build_buttons(anime)

        try:

            sent = await update.message.reply_sticker(
                sticker=anime["sticker"],
                reply_markup=markup
            )

        except Exception:

            sent = await update.message.reply_text(
                anime["name"],
                reply_markup=markup
            )

        asyncio.create_task(auto_delete(sent))

        return

    # ==============================
    # MULTIPLE RESULTS
    # ==============================

    keyboard = []

    for anime in matches:

        keyboard.append([
            InlineKeyboardButton(
                anime["name"],
                callback_data=f"anime_{anime['name']}"
            )
        ])

    sent = await update.message.reply_text(
        "🔎 Multiple Anime Found\n\nSelect one below.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    asyncio.create_task(auto_delete(sent))
