from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import REPORT_GROUP_ID
from database.mongo import (
    create_request,
    request_exists,
)

# ==========================
# Conversation States
# ==========================

ANIME = 1
LANGUAGE = 2
DUB = 3
SEASON = 4
EXTRA = 5

# ==========================
# /request
# ==========================

async def request_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "🎬 **Anime Request System**\n\n"
        "I'll ask you a few questions.\n"
        "You can cancel anytime using /cancel.\n\n"
        "📺 Question 1/5\n\n"
        "Send the Anime Name:",
        parse_mode="Markdown",
    )

    return ANIME


# ==========================
# Cancel Request
# ==========================

async def cancel_request(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "❌ Request cancelled."
    )

    return ConversationHandler.END


# ==========================
# Skip Extra
# ==========================

async def skip_extra(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["extra"] = "None"

    return await finish_request(update, context)


# ==========================
# Language Keyboard
# ==========================

def language_keyboard():

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🇮🇳 Hindi",
                    callback_data="lang_Hindi",
                ),
                InlineKeyboardButton(
                    "🇺🇸 English",
                    callback_data="lang_English",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🇮🇳 Tamil",
                    callback_data="lang_Tamil",
                ),
                InlineKeyboardButton(
                    "🇮🇳 Telugu",
                    callback_data="lang_Telugu",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🇮🇳 Kannada",
                    callback_data="lang_Kannada",
                ),
                InlineKeyboardButton(
                    "➕ Other",
                    callback_data="lang_Other",
                ),
            ],
        ]
    )


# ==========================
# Dub Keyboard
# ==========================

def dub_keyboard():

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Official Dub",
                    callback_data="dub_Official",
                )
            ],
            [
                InlineKeyboardButton(
                    "🎧 FanDub",
                    callback_data="dub_FanDub",
                )
            ],
            [
                InlineKeyboardButton(
                    "📺 Subbed",
                    callback_data="dub_Subbed",
                )
            ],
        ]
    )


# ==========================
# Anime Name
# ==========================

async def anime_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    anime = update.message.text.strip()

    if len(anime) < 2:
        await update.message.reply_text(
            "❌ Please enter a valid anime name."
        )
        return ANIME

    context.user_data["anime"] = anime

    # Duplicate request check
    exists = await request_exists(
        user_id=update.effective_user.id,
        anime=anime,
        language=""
    )

    if exists:
        await update.message.reply_text(
            "⚠️ You already have a pending request for this anime."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "🌐 Question 2/5\n\n"
        "Select Language:",
        reply_markup=language_keyboard()
    )

    return LANGUAGE


# ==========================
# Language Callback
# ==========================

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if not query.data.startswith("lang_"):
        return LANGUAGE

    language = query.data.replace("lang_", "")

    context.user_data["language"] = language

    await query.edit_message_text(
        f"✅ Language: {language}"
    )

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text="🎙️ Question 3/5\n\nSelect Dub Type:",
        reply_markup=dub_keyboard()
    )

    return DUB


# ==========================
# Dub Callback
# ==========================

async def dub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if not query.data.startswith("dub_"):
        return DUB

    dub = query.data.replace("dub_", "")

    context.user_data["dub"] = dub

    await query.edit_message_text(
        f"✅ Dub: {dub}"
    )

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=(
            "🎞️ Question 4/5\n\n"
            "Send Season or Movie.\n\n"
            "Example:\n"
            "Season 1\n"
            "Movie\n\n"
            "You can also send /skip"
        )
    )

    return SEASON


# ==========================
# Season
# ==========================

async def season(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["season"] = update.message.text.strip()

    await update.message.reply_text(
        "📝 Question 5/5\n\n"
        "Send any extra details.\n\n"
        "Or use /skip if none."
    )

    return EXTRA


# ==========================
# Skip Season
# ==========================

async def skip_season(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["season"] = "Not Specified"

    await update.message.reply_text(
        "📝 Question 5/5\n\n"
        "Send any extra details.\n\n"
        "Or use /skip if none."
    )

    return EXTRA


# ==========================
# Extra Details
# ==========================

async def extra(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["extra"] = update.message.text.strip()

    return await finish_request(update, context)


from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from config import REPORT_GROUP_ID


# ==========================
# Finish Request
# ==========================

async def finish_request(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    anime = context.user_data["anime"]
    language = context.user_data["language"]
    dub = context.user_data["dub"]
    season = context.user_data["season"]
    extra = context.user_data["extra"]

    # Save to MongoDB
    req_id = await create_request(
        user_id=user.id,
        username=user.username or "",
        full_name=user.full_name,
        anime=anime,
        language=language,
        dub=dub,
        season=season,
        extra=extra,
    )

    text = (
        "📥 <b>NEW ANIME REQUEST</b>\n\n"
        f"🆔 <b>{req_id}</b>\n\n"
        f"👤 <b>{user.full_name}</b>\n"
        f"🆔 <code>{user.id}</code>\n"
        f"🔗 @{user.username if user.username else 'No Username'}\n\n"

        f"📺 <b>Anime</b>\n"
        f"{anime}\n\n"

        f"🌐 <b>Language</b>\n"
        f"{language}\n\n"

        f"🎙 <b>Dub</b>\n"
        f"{dub}\n\n"

        f"🎞 <b>Season</b>\n"
        f"{season}\n\n"

        f"📝 <b>Extra Details</b>\n"
        f"{extra}\n\n"

        "🟡 <b>Status:</b> Pending"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Added",
                    callback_data=f"req_added:{req_id}"
                ),
                InlineKeyboardButton(
                    "🔄 Working",
                    callback_data=f"req_working:{req_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    "❌ Not Possible",
                    callback_data=f"req_denied:{req_id}"
                ),
                InlineKeyboardButton(
                    "📝 Reply",
                    callback_data=f"req_reply:{req_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    "🗑 Close",
                    callback_data=f"req_close:{req_id}"
                )
            ]
        ]
    )

    await context.bot.send_message(
        chat_id=REPORT_GROUP_ID,
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )

    await update.message.reply_text(
        f"✅ Your request has been submitted successfully!\n\n"
        f"🆔 Request ID: <code>{req_id}</code>\n\n"
        "Our admins will review it soon.",
        parse_mode="HTML",
    )

    context.user_data.clear()

    return ConversationHandler.END


