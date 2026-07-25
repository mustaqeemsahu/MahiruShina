# ==============================
# GROUP HANDLER
# ==============================

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import ContextTypes

from config import GROUP_PHOTO, REPORT_GROUP_ID, WELCOME_EMOJIS
from database.mongo import add_group, remove_group
from utils.helpers import now
import random


# ==============================
# BOT ADDED TO GROUP
# ==============================

async def chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):

    result = update.my_chat_member

    if not result:
        return

    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    user = result.new_chat_member.user

    # =================================
    # BOT REMOVED FROM GROUP
    # =================================
    if (
        user.id == context.bot.id
        and new_status in ("left", "kicked")
    ):
        try:
            await remove_group(result.chat.id)
        except Exception as e:
            print(f"[ERROR] Remove group failed: {e}")
        return

    # Trigger only when bot is added
    if (
        user.id == context.bot.id
        and old_status in ("left", "kicked")
        and new_status in ("member", "administrator")
    ):

        chat = result.chat
        chat_id = chat.id
        chat_title = chat.title or "Unknown Group"
        adder = result.from_user

        # Save Group
        try:
            await add_group(chat_id)
        except Exception as e:
            print(f"[ERROR] Add group failed: {e}")

        # Member Count
        try:
            member_count = await context.bot.get_chat_member_count(chat_id)
        except Exception:
            member_count = "Unknown"

        # Welcome Caption
        text = (
            "<b>ᴛʜᴀɴᴋꜱ ꜰᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ʜᴇʀᴇ!!</b>\n\n"
            "<b>ɪ ᴄᴀɴ ᴩʀᴏᴠɪᴅᴇ ᴀɴɪᴍᴇ ʜᴇʀᴇ ꜰᴏʀ ᴇᴠᴇʀʏᴏɴᴇ. ᴊᴜꜱᴛ ꜱᴇɴᴅ ᴀɴɪᴍᴇ ɴᴀᴍᴇ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴩ ᴀɴᴅ ɪ'ʟʟ ꜱᴇɴᴅ ʏᴏᴜ ᴛʜᴇ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ.</b>\n\n"

            "<b>ʜᴏᴡ ᴛᴏ ᴜꜱᴇ ᴍᴇ?</b>\n"
            "• <code>/anime Naruto</code> – <b>ɢᴇᴛ ᴛʜᴀᴛ ᴀɴɪᴍᴇ</b>\n"
            "• <code>/animelist</code> – <b>ɢᴇᴛ ᴀʟʟ ᴀɴɪᴍᴇꜱ</b>\n"
            "• <code>/help</code> – <b>ꜱᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ</b>\n\n"

            "<b>ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ:</b> @Anime_Stream_Zone"
        )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📢 ᴜᴘᴅᴀᴛᴇꜱ",
                        url="https://t.me/Sahu_Bots",
                    ),
                    InlineKeyboardButton(
                        "💬 ᴄʜᴀᴛ ɢᴄ",
                        url="https://t.me/Anime_Search_Zone",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                        url=f"https://t.me/{context.bot.username}?startgroup=true",
                    )
                ],
            ]
        )

        # Send Welcome
        try:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=GROUP_PHOTO,
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        except Exception as e:
            print(f"[ERROR] Photo send failed: {e}")

            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode="HTML",
                    reply_markup=keyboard,
                )
            except Exception as e:
                print(f"[ERROR] Message send failed: {e}")

        # Log To Report Group
        try:
            await context.bot.send_message(
                chat_id=REPORT_GROUP_ID,
                parse_mode="HTML",
                text=(
                    "<b>🤖 Bot Added To Group</b>\n\n"
                    f"👥 <b>Group:</b> {chat_title}\n"
                    f"🆔 <b>Group ID:</b> <code>{chat_id}</code>\n"
                    f"👤 <b>Added By:</b> "
                    f"<a href='tg://user?id={adder.id}'>{adder.first_name}</a>\n"
                    f"👥 <b>Total Members:</b> {member_count}\n"
                    f"🕒 <b>Time:</b> {now()}"
                ),
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

        # Ignore bots
        if user.is_bot:
            continue

        text = (
            f"{random.choice(WELCOME_EMOJIS)} <b>ᴡᴇʟᴄᴏᴍᴇ</b> "
            f"<a href='tg://user?id={user.id}'>{user.first_name}</a> "
            f"<b>ᴛᴏ</b> <b>{chat.title}</b>\n\n"

            "<b>🌸 ʜᴏᴘᴇ ʏᴏᴜ ᴇɴᴊᴏʏ ʏᴏᴜʀ ꜱᴛᴀʏ ʜᴇʀᴇ.</b>\n\n"

            "<b><blockquote expandable>🔍 ᴀɴɪᴍᴇ ꜱᴇᴀʀᴄʜ:</b>\n"
            "• <code>/anime</code> <b>[Name]</b>\n"
            "• <code>/animelist</code> - <b>ᴛᴏ ɢᴇᴛ ᴀʟʟ ᴀɴɪᴍᴇ ʟɪꜱᴛ</b>\n"
            "• <b>ᴏʀ ꜱɪᴍᴩʟʏ ꜱᴇɴᴅ ᴀɴɪᴍᴇ ɴᴀᴍᴇ ʜᴇʀᴇ</blockquote></b>\n\n"

            "<b>🎌 ᴇɴᴊᴏʏ ᴡᴀᴛᴄʜɪɴɢ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀɴɪᴍᴇ ᴀɴᴅ ꜱʜᴀʀᴇ ᴡɪᴛʜ ʏᴏᴜʀ ꜰʀɪᴇɴᴅꜱ</b>"
        )

        try:
            await context.bot.send_message(
                chat_id=chat.id,
                text=text,
                parse_mode="HTML",
            )
        except Exception as e:
            print(f"[ERROR] Welcome failed: {e}")
