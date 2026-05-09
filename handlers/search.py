# ==============================
# SEARCH HANDLER
# ==============================

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.mongo import get_all_anime
from utils.cooldown import check_cooldown
from utils.filters import force_sub
from config import FORCE_CHANNEL

# ==============================
# PARTIAL SEARCH (/search)
# ==============================

async def improved_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await force_sub(update, context):
        return

    user_id = update.effective_user.id

    if not check_cooldown(user_id):
        return await update.message.reply_text("⏳ Wait 5 sec")

    query = " ".join(context.args).lower()

    if not query:
        return await update.message.reply_text("Example: /search Naruto")

    animes = await get_all_anime()

    matches = [
        a for a in animes
        if query in a["name"].lower() or any(query in k for k in a["keys"])
    ]

    if not matches:
        return await update.message.reply_text("❌ No Anime Found.")

    text = "🎌 Results:\n\n"
    for a in matches[:5]:
        text += f"• {a['name']}\n"

    await update.message.reply_text(text)


# ==============================
# BUTTON SEARCH (/btn)
# ==============================

async def button_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await force_sub(update, context):
        return

    query = " ".join(context.args).lower()

    if not query:
        return await update.message.reply_text("Example: /btn Naruto")

    animes = await get_all_anime()

    matches = [
        a for a in animes
        if query in a["name"].lower() or any(query in k for k in a["keys"])
    ]

    if not matches:
        return await update.message.reply_text("❌ No Anime Found.")

    keyboard = [
        [InlineKeyboardButton(a["name"], callback_data=f"anime_{a['name']}")]
        for a in matches[:5]
    ]

    await update.message.reply_text(
        "🎌 Select Anime:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==============================
# AUTO SEARCH (KEYWORD IN SENTENCE)
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
from config import FORCE_CHANNEL


# ==============================
# NORMALIZE
# ==============================

def normalize(text: str) -> str:

    text = text.lower()

    text = re.sub(r"[^a-z0-9\s]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==============================
# AUTO DELETE
# ==============================

async def auto_delete(message, sec=300):

    await asyncio.sleep(sec)

    try:
        await message.delete()
    except:
        pass


# ==============================
# DIRECT SEARCH
# ==============================

async def direct_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    raw_text = update.message.text

    if not raw_text:
        return

    # ignore commands
    if raw_text.startswith("/"):
        return

    # normalize sentence
    text = normalize(raw_text)

    animes = await get_all_anime()

    matches = []

    # ==============================
    # KEYWORD DETECTION
    # ==============================

    for anime in animes:

        anime_name = anime.get("name", "")

        anime_keys = anime.get("keys", [])

        found_keyword = None

        # check anime name also
        all_keywords = anime_keys + [anime_name]

        for keyword in all_keywords:

            keyword = normalize(keyword)

            # keyword exists in sentence
            if keyword and keyword in text:

                found_keyword = keyword
                break

        if found_keyword:

            matches.append({
                "anime": anime,
                "keyword": found_keyword,
                "length": len(found_keyword)
            })

    # no result
    if not matches:
        return

    # ==============================
    # LONGEST KEYWORD FIRST
    # ==============================

    matches.sort(
        key=lambda x: x["length"],
        reverse=True
    )

    # remove duplicates
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

        keyboard = [
            [
                InlineKeyboardButton(
                    "🎬 Watch & Download",
                    url=anime["link"]
                )
            ],
            [
                InlineKeyboardButton(
                    "📢 Join Channel",
                    url=f"https://t.me/{FORCE_CHANNEL.replace('@', '')}"
                )
            ]
        ]

        try:

            sent = await update.message.reply_sticker(
                sticker=anime["sticker"],
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        except:

            sent = await update.message.reply_text(
                anime["name"],
                reply_markup=InlineKeyboardMarkup(keyboard)
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
        "🔎 Multiple Anime Found",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    asyncio.create_task(auto_delete(sent))
