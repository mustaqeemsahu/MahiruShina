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
# AUTO SEARCH (TEXT MESSAGE)
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
# NORMALIZE TEXT
# ==============================

def normalize(text: str) -> str:
    text = text.lower()

    # remove symbols
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # replace - _
    text = re.sub(r"[-_]", " ", text)

    # remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==============================
# AUTO DELETE
# ==============================

async def auto_delete(message, sec=45):

    await asyncio.sleep(sec)

    try:
        await message.delete()
    except:
        pass


# ==============================
# DIRECT SEARCH
# ==============================

async def direct_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # safety
    if not update.message:
        return

    # raw message
    raw_text = update.message.text

    if not raw_text:
        return

    # normalize
    text = normalize(raw_text)

    # ignore commands
    if text.startswith("/"):
        return

    # ignore very short messages
    if len(text) < 2:
        return

    # database
    animes = await get_all_anime()

    matches = []

    # user words
    user_words = text.split()

    # ==============================
    # SEARCH SYSTEM
    # ==============================

    for anime in animes:

        anime_name = normalize(anime.get("name", ""))

        anime_keys = [
            normalize(k)
            for k in anime.get("keys", [])
        ]

        searchable = []

        # full anime name
        searchable.append(anime_name)

        # anime name words
        searchable.extend(anime_name.split())

        # keywords
        searchable.extend(anime_keys)

        found = False

        for word in user_words:

            # skip tiny words
            if len(word) <= 2:
                continue

            # exact match
            if word in searchable:
                found = True
                break

            # partial match
            for item in searchable:

                if word in item or item in word:
                    found = True
                    break

            if found:
                break

        if found:
            matches.append(anime)

    # ==============================
    # REMOVE DUPLICATES
    # ==============================

    unique_matches = []

    added = set()

    for anime in matches:

        if anime["name"] not in added:

            unique_matches.append(anime)

            added.add(anime["name"])

    matches = unique_matches

    # ==============================
    # NO RESULT
    # ==============================

    if not matches:
        return

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
                    "📢 Join Main Channel",
                    url=f"https://t.me/{FORCE_CHANNEL.replace('@', '')}"
                )
            ]
        ]

        try:

            sent = await update.message.reply_sticker(
                sticker=anime["sticker"],
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            asyncio.create_task(auto_delete(sent, 300))

        except:

            sent = await update.message.reply_text(
                f"🎌 {anime['name']}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            asyncio.create_task(auto_delete(sent, 300))

        return

    # ==============================
    # MULTIPLE RESULTS
    # ==============================

    keyboard = []

    for anime in matches[:10]:

        keyboard.append(
            [
                InlineKeyboardButton(
                    anime["name"],
                    callback_data=f"anime_{anime['name']}"
                )
            ]
        )

    sent = await update.message.reply_text(
        "🔎 Multiple Anime Found\n\nSelect One:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    asyncio.create_task(auto_delete(sent, 300))
