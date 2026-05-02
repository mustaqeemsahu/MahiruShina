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

async def direct_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    text = update.message.text.lower()

    if text.startswith("/"):
        return

    animes = await get_all_anime()

    matches = []

    for anime in animes:

        score = 0
        name = anime["name"].lower()

        if name in text:
            score += 5

        for word in text.split():
            if word in name:
                score += 2

        for key in anime["keys"]:
            if key in text:
                score += 3

        if score > 0:
            anime["score"] = score
            matches.append(anime)

    if not matches:
        return

    matches = sorted(matches, key=lambda x: x["score"], reverse=True)[:5]

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

    keyboard = [
        [InlineKeyboardButton(a["name"], callback_data=f"anime_{a['name']}")]
        for a in matches
    ]

    await update.message.reply_text(
        "🔎 Multiple anime found",
        reply_markup=InlineKeyboardMarkup(keyboard)
  )
