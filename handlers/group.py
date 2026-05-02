# ==============================
# GROUP HANDLER
# ==============================

from telegram import Update
from telegram.ext import ContextTypes

from config import GROUP_PHOTO, REPORT_GROUP_ID, WELCOME_EMOJIS
from database.mongo import add_group
from utils.helpers import now
import random

# ==============================
# BOT ADDED TO GROUP
# ==============================

async def chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):

    result = update.chat_member

    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    user = result.new_chat_member.user

    if user.id == context.bot.id and new_status in ("member", "administrator"):

        chat = result.chat
        chat_id = chat.id
        adder = result.from_user

        await add_group(chat_id)

        # 🔥 Premium Emoji Text
        text = (
            "<b><tg-emoji emoji-id='5368324170671202286'></tg-emoji> Mahiru Anime Provider Activated!</b>\n\n"
            "I can now provide anime instantly in this group.\n\n"

            "<b><tg-emoji emoji-id='5427052514094619126'></tg-emoji> How to Use</b>\n"
            "Use <code>/help</code> To See My All Commands\n"
            "• <code>/anime</code> Search Anime Name\n"
            "• <code>/animelist</code> Browse Anime\n\n"

            "<tg-emoji emoji-id='5398004068667180923'></tg-emoji> Enjoy anime with your friends."
        )

        # 🔥 Buttons with Premium Emoji
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

        try:
            await context.bot.send_photo(
                chat_id,
                photo=GROUP_PHOTO,
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except:
            await context.bot.send_message(
                chat_id,
                text,
                parse_mode="HTML",
                reply_markup=keyboard
            )

        # 🔥 Log
        try:
            await context.bot.send_message(
                REPORT_GROUP_ID,
                f"<b>Bot Added</b>\n\n"
                f"👥 {chat.title}\n"
                f"🆔 <code>{chat_id}</code>\n"
                f"👤 {adder.first_name}\n"
                f"🕒 {now()}",
                parse_mode="HTML"
            )
        except:
            pass


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
            f"<a href='tg://user?id={user.id}'>{user.first_name}</a>\n\n"
            "Enjoy anime here 🎌\n"
            "Use /anime & /animelist"
        )

        try:
            await context.bot.send_message(chat.id, text, parse_mode="HTML")
        except:
            pass
