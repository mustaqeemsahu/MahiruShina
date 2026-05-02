# ==============================
# START HANDLER
# ==============================

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import FORCE_CHANNEL, REPORT_GROUP_ID, START_PHOTO
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

    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}")],
        [InlineKeyboardButton("➕ Add Me To Group", url=f"https://t.me/{bot_username}?startgroup=true")]
    ]

    text = (
        f"👋 Hey {user.first_name}\n\n"
        "🎌 Welcome to Anime Provider Bot\n\n"
        "Use me to search anime instantly 🔍\n\n"
        "<b>Commands:</b>\n"
        "• /anime Naruto\n"
        "• /search One Piece\n"
        "• /animelist\n"
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
