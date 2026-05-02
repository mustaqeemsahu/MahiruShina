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

async def anime_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_bot_status(update):
        return

    if not await force_sub(update, context):
        return

    query = " ".join(context.args).lower()

    if not query:
        return await update.message.reply_text("❌ Example: /anime Naruto")

    animes = await get_all_anime()

    matches = [
        a for a in animes
        if query == a["name"].lower() or any(query in k for k in a["keys"])
    ]

    if not matches:
        return await update.message.reply_text("❌ No Anime Found.")

    # Single result
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

    # Multiple results
    keyboard = [
        [InlineKeyboardButton(a["name"], callback_data=f"anime_{a['name']}")]
        for a in matches[:10]
    ]

    await update.message.reply_text(
        f"🔎 Multiple results for <b>{query}</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
