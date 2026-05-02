# ==============================
# FILTERS
# ==============================

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus

from config import FORCE_CHANNEL, ADMIN_IDS

BOT_STATUS = {"active": True}

# Bot ON/OFF
async def check_bot_status(update: Update):
    if not BOT_STATUS["active"]:
        await update.message.reply_text("🚧 Bot under maintenance")
        return False
    return True

# Force Sub
async def force_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id in ADMIN_IDS:
        return True

    try:
        member = await context.bot.get_chat_member(FORCE_CHANNEL, user_id)

        if member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        ]:
            return True

    except:
        pass

    keyboard = [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}")]]

    await update.message.reply_text(
        "❌ Join channel to use bot",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return False
