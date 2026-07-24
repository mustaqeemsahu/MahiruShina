# ==============================
# GROUP HANDLER
# ==============================
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes

from config import GROUP_PHOTO, REPORT_GROUP_ID, WELCOME_EMOJIS
from database.mongo import add_group
from utils.helpers import now
import random

# ==============================
# BOT ADDED TO GROUP
# ==============================

async def chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):

    result = update.my_chat_member  # ✅ MUST use this

    if not result:
        return

    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    user = result.new_chat_member.user

    # ✅ Trigger ONLY when bot is added
    if user.id == context.bot.id and new_status in ("member", "administrator"):

        chat = result.chat
        chat_id = chat.id
        chat_title = chat.title or "Unknown Group"
        adder = result.from_user

        # ==============================
        # SAVE GROUP
        # ==============================
        try:
            await add_group(chat_id)
        except Exception as e:
            print(f"[ERROR] Add group failed: {e}")

        # ==============================
        # WELCOME MESSAGE
        # ==============================
        text = (
            "<b>ᴛʜᴀɴᴋꜱ ꜰᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ʜᴇʀᴇ!!</b>\n\n"
            "<b>ɪ ᴄᴀɴ ᴩʀᴏᴠɪᴅᴇ ᴀɴɪᴍᴇ ʜᴇʀᴇ ꜰᴏʀ ᴇᴠᴇʀʏᴏɴᴇ. ᴊᴜꜱᴛ ꜱᴇɴᴅ ᴀɴɪᴍᴇ ɴᴀᴍᴇ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴩ ᴛʜᴀɴ ɪ ᴡɪʟ ʏᴏᴜ ᴛʜᴀᴛ ᴀɴɪᴍᴇ ʟɪɴᴋ ᴛᴏ ᴡᴀᴛᴄʜ ᴀɴᴅ ᴇɴᴊᴏʏ!!</b>\n\n"

            "<b>ʜᴏᴡ ᴛᴏ ᴜꜱᴇ ᴍᴇ ?</b>\n"
            "• <code>/anime Naruto</code> – <b>ɢᴇᴛ ᴛʜᴀᴛ ᴀɴɪᴍᴇ</b>\n"
            "• <code>/animelist</code> – <b>ɢᴇᴛ ʟɪꜱᴛ ᴏꜰ ᴀʟʟ ᴀɴɪᴍᴇꜱ</b>\n"
            "• <code>/help</code> – <b>ᴛᴏ ꜱᴇᴇ ᴍʏ ᴀʟʟ ᴄᴏᴍᴍᴏɴᴀᴅꜱ</b>\n\n"

            "<b>ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ</b>: @Anime_Stream_Zone"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📢 ᴜᴩᴅᴀᴛᴇꜱ", url="https://t.me/Sahu_Bots"),
                InlineKeyboardButton("💬 ᴄʜᴀᴛ ɢᴄ", url="https://t.me/Anime_Search_Zone")
            ],
            [
                InlineKeyboardButton(
                    "➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ  ᴏᴜʀ ɢʀᴏᴜᴩ",
                    url=f"https://t.me/{context.bot.username}?startgroup=true"
                )
            ]
        ])

        # ==============================
        # SEND WELCOME MESSAGE
        # ==============================
        try:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=GROUP_PHOTO,
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"[ERROR] Photo send failed: {e}")
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"[ERROR] Message send failed: {e}")

# ==============================
# LOG TO REPORT GROUP
# ==============================

member_count = await context.bot.get_chat_member_count(chat_id)

try:
    await context.bot.send_message(
        chat_id=REPORT_GROUP_ID,
        text=(
            "<b>🤖 Bot Added To Group</b>\n\n"
            f"👥 <b>Group:</b> {chat_title}\n"
            f"🆔 <code>{chat_id}</code>\n"
            f"👥 <b>Total Members:</b> {member_count}\n"
            f"👤 <b>Added By:</b> <a href='tg://user?id={adder.id}'>{adder.first_name}</a>\n"
            f"🕒 <b>Time:</b> {now()}"
        ),
        parse_mode="HTML"
    )
except Exception as e:
    print(f"[ERROR] Log failed: {e}")


# ==============================
# WELCOME NEW USERS
# ==============================

async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.new_chat_members:
        return

    chat = update.effective_chat

    for user in update.message.new_chat_members:

        if user.is_bot:
            continue

        text = (
            f"{random.choice(WELCOME_EMOJIS)} <b>ᴡᴇʟᴄᴏᴍᴇ</b> "
            f"<a href='tg://user?id={user.id}'>{user.first_name}</a> <b>ɪɴ</b> <b>{chat.title}</b>\n\n"
            "<b>ꜱᴛᴀʏ ʜᴇʀᴇ ᴀɴᴅ ᴇɴᴊᴏʏ ᴡɪᴛʜ ᴜꜱ 💫</b>\n"
            "<b>ʏᴏᴜ ᴄᴀɴ ᴜꜱᴇ ᴍᴇ ʜᴇʀᴇ ꜰᴏʀ ᴀɴɪᴍᴇ ꜱᴇᴀʀᴄʜ</b>\n"
            "<code>/anime [name]</code> <b>&</b> <code>/animelist</code> <b>ᴏʀ ᴊᴜꜱᴛ ꜱᴇɴᴅ ᴅɪʀᴇᴄᴛ ᴀɴɪᴍᴇ ɴᴀᴍᴇ ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ</b>\n\n"
            "<b>ᴇɴᴊᴏʏ ᴀɴᴅ ꜱʜᴀʀᴇ ᴀɴɪᴍᴇ ᴡɪᴛʜ ʏᴏᴜʀ ꜰʀɪᴇɴᴅꜱ.</b>"
        )

        try:
            await context.bot.send_message(chat.id, text, parse_mode="HTML")
        except:
            pass
