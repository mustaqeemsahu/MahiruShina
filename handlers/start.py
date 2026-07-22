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

    chat_type = "👤 Private" if update.effective_chat.type == "private" else "👥 Group"

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
            f"📍 Type: {chat_type}\n"
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
            InlineKeyboardButton("📢 𝗨𝗽𝗱𝗮𝘁𝗲𝘀", url="https://t.me/Sahu_Bots"),
            InlineKeyboardButton("💬 𝗦𝘂𝗽𝗽𝗼𝗿𝘁", url="https://t.me/Anime_Search_Zone")
        ],
        [
            InlineKeyboardButton(
                "➕ 𝗔𝗱𝗱 𝗠𝗲 𝗧𝗼 𝗬𝗼𝘂𝗿 𝗚𝗿𝗼𝘂𝗽",
                url=f"https://t.me/{context.bot.username}?startgroup=true"
            )
        ]
    ])

    # 📝 Message
    text = (
        f"👋 ʜᴇʏ {user.first_name}\n\n"
        "🎌 <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴀɴɪᴍᴇ ꜱᴇᴀʀᴄʜᴇʀ ʙᴏᴛ</b>\n\n"
        "<b><blockquote>ɪ ᴄᴀɴ ʜᴇʟᴩ ʏᴏᴜ ᴛᴏ ꜰɪɴᴅ ʏᴏᴜʀ ᴀɴɪᴍᴇ. ᴊᴜꜱᴛ ᴛʏᴩᴇ ᴀɴɪᴍᴇ ɴᴀᴍᴇ ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴡᴀᴛᴄʜ</blockquote></b>\n\n"
        "<b>ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴩ ᴀɴᴅ ᴍᴀᴋᴇ ᴛʜᴀᴛ ꜱɪᴍᴩʟᴇ ɢʀᴏᴜᴩ ɪɴᴛᴏ ᴀɴɪᴍᴇ ꜰɪɴᴅɪɴɢ ɢʀᴏᴜᴩ ʙʏ ᴊᴜꜱᴛ ᴀᴅᴅɪɴɢ ᴍᴇ ᴛʜᴇʀᴇ. ɪ ᴡɪʟʟ ᴩʀᴏᴠɪᴅᴇ ᴀɴɪᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴩ ᴀʟꜱᴏ. ꜰʀᴏᴍ ᴛʜɪꜱ ʏᴏᴜʀ ᴍᴇᴍʙᴇʀꜱ ᴄᴀɴ ᴀʟꜱᴏ ᴇɴᴊᴏʏ ᴀɴɪᴍᴇ ᴛʜᴇʀᴇ. </b>\n"
        "📢 ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ :- @Anime_Stream_Zone"
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
