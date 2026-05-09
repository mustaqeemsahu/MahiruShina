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
        "❌ 𝗔𝗖𝗖𝗘𝗦 𝗗𝗘𝗡𝗜𝗘𝗗!!!\n\n𝐘𝐎𝐔 𝐌𝐔𝐒𝐓 𝐉𝐎𝐈𝐍 𝐎𝐔𝐑 𝐌𝐀𝐈𝐍 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 𝐓𝐎 𝐔𝐒𝐄 𝐓𝐇𝐈𝐒 𝐁𝐎𝐓 𝐀𝐍𝐃 𝐒𝐄𝐀𝐑𝐂𝐇 𝐔𝐍𝐋𝐈𝐌𝐈𝐓𝐄𝐃 𝐀𝐍𝐈𝐌𝐄 𝐇𝐄𝐑𝐄.\n\n𝐓𝐇𝐀𝐍𝐊 𝐘𝐎𝐔 & 𝐒𝐔𝐏𝐏𝐎𝐑𝐓 𝐔𝐒",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return False
