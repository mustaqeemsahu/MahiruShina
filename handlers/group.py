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
            "🎌 <b>Mahiru Anime Provider Activated!</b>\n\n"
            "✨ I can now provide anime instantly in this group.\n\n"

            "<b>📌 How To Use</b>\n"
            "• <code>/anime Naruto</code> – Get anime\n"
            "• <code>/animelist</code> – Browse list\n"
            "• <code>/help</code> – All commands\n\n"

            "⚡ Or just type anime name directly!\n\n"

            "📢 <b>Our Network</b>: @Anime_Stream_Zone"
        )

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
        try:
            await context.bot.send_message(
                chat_id=REPORT_GROUP_ID,
                text=(
                    "<b>🤖 Bot Added To Group</b>\n\n"
                    f"👥 <b>Group:</b> {chat_title}\n"
                    f"🆔 <code>{chat_id}</code>\n"
                    f"👤 <b>Added By:</b> {adder.first_name if adder else 'Unknown'}\n"
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
            f"{random.choice(WELCOME_EMOJIS)} <b>Welcome</b> "
            f"<a href='tg://user?id={user.id}'>{user.first_name}</a> IN <b>{chat.title}</b>\n\n"
            "Hope you will enjoy here 😊\n"
            "Use me here for Anime Search 🔍\n"
            "/anime [name] & /animelist\n\n"
            "Enjoy & Share Anime With Your Friends 🎌"
        )

        try:
            await context.bot.send_message(chat.id, text, parse_mode="HTML")
        except:
            pass
