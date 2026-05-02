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

    message = update.effective_message
    user = update.effective_user

    if not message or not user:
        return

    user_id = user.id

    # ✅ Save user in DB
    try:
        await add_user(user_id)
    except Exception as e:
        print(f"Add user error: {e}")

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
    except Exception as e:
        print(f"Log error: {e}")

    # 🔗 Buttons
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

    # 📝 Message
    text = (
        f"👋 Hey {user.first_name}\n\n"
        "🎌 <b>Welcome to Mahiru Anime Provider</b>\n\n"
        "I help you find anime instantly in groups & private chats.\n\n"
        "<b>📌 Commands</b>\n"
        "• <code>/anime [name]</code> – Get anime instantly\n"
        "• <code>/search Naruto</code> – Partial search\n"
        "• <code>/animelist</code> – View available anime list\n\n"
        "✨ Invite your friends and enjoy together 🎟\n"
        "📢 Our Network: @Anime_Stream_Zone"
    )

    # 📤 Send Message Safely
    try:
        await message.reply_photo(
            photo=START_PHOTO,
            caption=text,
            reply_markup=keyboard,  # ✅ FIXED
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Photo send failed: {e}")
        await message.reply_text(
            text,
            reply_markup=keyboard,  # ✅ FIXED
            parse_mode="HTML"
        )
