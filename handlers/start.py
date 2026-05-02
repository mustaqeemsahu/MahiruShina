# ==============================
# START HANDLER
# ==============================

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import REPORT_GROUP_ID, START_PHOTO
from database.mongo import add_user
from utils.helpers import now

# ==============================
# START COMMAND
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    user_id = user.id

    # ✅ Save user in DB
    await add_user(user_id)

    # 🔥 Log to report group
    try:
        await context.bot.send_message(
            REPORT_GROUP_ID,
            f"🚀 <b>Bot Started</b>\n\n"
            f"👤 User: {user.first_name}\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"🕒 Time: {now()}",
            parse_mode="HTML"
        )
    except:
        pass

    # 🔗 Buttons
    bot_username = (await context.bot.get_me()).username

    keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📢 Updates Channel", url="https://t.me/Sahu_Bots"),
                InlineKeyboardButton("💬 Support Chat", url="https://t.me/Anime_Search_Zone")
            ],
            [
                InlineKeyboardButton(
                    "➕ Add Me To Your Group",
                    url=f"https://t.me/{context.bot.username}?startgroup=true"
                )
            ]
        ])

    text = (
        f"👋 Hey {user.first_name}\n\n"
        "🎌 Welcome to Mahiru Anime Provider\n\n"
        "I help you find anime instantly in groups & private chats.\n\n"
        "<b>📌 Commands</b>\n"
        "• /anime [name] – Get anime instantly\n"
        "• /search Naruto – Partial search\n"
        "• /animelist – View Available anime list\n\n"
        "✨ Invite friends to this bot and enjoy with them 🎟\n"
        "Our Main Network @Anime_Stream_Zone"
    )

    try:
        await update.message.reply_photo(
            photo=START_PHOTO,
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
    except:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
