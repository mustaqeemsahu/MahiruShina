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
# AUTO SEARCH (TEXT)
# ==============================

import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# 🔥 Normalize function (BONUS TRICK)
def normalize(text: str) -> str:
    return re.sub(r'[-_]', ' ', text.lower()).strip()


async def direct_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    # ✅ Normalize user input
    text = normalize(update.message.text)

    # ❌ Ignore commands
    if text.startswith("/"):
        return

    # ❌ Ignore useless short inputs
    if len(text) < 3:
        return

    # ✅ Extract meaningful words only
    words = [w for w in text.split() if len(w) >= 3]

    animes = await get_all_anime()
    matches = []

    for anime in animes:
        score = 0

        # ✅ Normalize anime name
        name = normalize(anime["name"])

        # ✅ Exact phrase match (highest priority)
        if text in name:
            score += 10

        # ✅ Keyword match
        for key in anime.get("keys", []):
            key = normalize(key)
            if key in text:
                score += 8

        # ✅ Word match (only meaningful words)
        for word in words:
            if word in name:
                score += 3

        if score > 0:
            anime_copy = anime.copy()  # ❗ prevent modifying original data
            anime_copy["score"] = score
            matches.append(anime_copy)

    if not matches:
        return

    # ✅ Sort by best match
    matches = sorted(matches, key=lambda x: x["score"], reverse=True)[:5]

    # ✅ Single result → direct response
    if len(matches) == 1:
        a = matches[0]

        keyboard = [
            [InlineKeyboardButton("🎬 Watch & Download", url=a["link"])],
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}")]
        ]

        return await update.message.reply_sticker(
            sticker=a["sticker"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ✅ Multiple results → show selection
    keyboard = [
        [InlineKeyboardButton(a["name"], callback_data=f"anime_{a['name']}")]
        for a in matches
    ]

    await update.message.reply_text(
        "🔎 Multiple anime found",
        reply_markup=InlineKeyboardMarkup(keyboard)
        )
