# ==============================
# CALLBACK HANDLER
# ==============================

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes

from database.mongo import get_all_anime, get_all_groups, remove_group, total_groups
from handlers.animelist import build_page
from config import ANIME_PER_PAGE, FORCE_CHANNEL


# ===========================================
# GROUPS PAGINATION
# ===========================================

async def groups_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if not query.data.startswith("groups_"):
        return

    page = int(query.data.split("_")[1])

    PER_PAGE = 5

    all_groups = await get_all_groups()

    start = page * PER_PAGE
    end = start + PER_PAGE

    total = await total_groups()

    text = (
        f"🏘 <b>Total Groups :</b> {total}\n"
        f"📄 <b>Page :</b> {page+1}\n\n"
    )

    for data in all_groups[start:end]:

        chat_id = data["_id"]

        try:
            chat = await context.bot.get_chat(chat_id)
            members = await context.bot.get_chat_member_count(chat_id)
            me = await context.bot.get_chat_member(chat_id, context.bot.id)

            status = "👑 Admin" if me.status == "administrator" else "👤 Member"

            try:
                invite = chat.invite_link if me.status == "administrator" else "Unavailable"
            except:
                invite = "Unavailable"

            text += (
                f"📌 <b>{chat.title}</b>\n"
                f"🆔 <code>{chat.id}</code>\n"
                f"👥 {members} Members\n"
                f"🤖 {status}\n"
                f"🔗 {invite}\n\n"
            )

        except:
            await remove_group(chat_id)

    buttons = []

    row = []

    if page > 0:
        row.append(
            InlineKeyboardButton(
                "⬅ Previous",
                callback_data=f"groups_{page-1}"
            )
        )

    if end < len(all_groups):
        row.append(
            InlineKeyboardButton(
                "➡ Next",
                callback_data=f"groups_{page+1}"
            )
        )

    if row:
        buttons.append(row)

    buttons.append(
        [
            InlineKeyboardButton(
                "🔄 Refresh",
                callback_data=f"groups_{page}"
            )
        ]
    )

    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ==============================
# BUTTON BUILDER
# ==============================

def build_buttons(anime):

    keyboard = []

    hindi = anime.get("hindi_link")
    english = anime.get("english_link")
    old_link = anime.get("link")  # Backward compatibility

    # Hindi Button
    if hindi and hindi != "-":
        keyboard.append([
            InlineKeyboardButton(
                "🇮🇳 Watch In Hindi",
                url=hindi
            )
        ])

    # English Button
    if english and english != "-":
        keyboard.append([
            InlineKeyboardButton(
                "🇺🇸 Watch In English",
                url=english
            )
        ])

    # Old Database Support
    if (
        (not hindi or hindi == "-")
        and (not english or english == "-")
        and old_link
    ):
        keyboard.append([
            InlineKeyboardButton(
                "🎬 Watch & Download",
                url=old_link
            )
        ])

    # Join Channel
    keyboard.append([
        InlineKeyboardButton(
            "📢 Join Main Channel",
            url=f"https://t.me/{FORCE_CHANNEL.replace('@', '')}"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


# ==============================
# CALLBACK HANDLER
# ==============================

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    animes = await get_all_anime()

    # ==============================
    # ANIME BUTTON
    # ==============================
    if data.startswith("anime_"):
        name = data.replace("anime_", "").lower()

        for anime in animes:
            if anime["name"].lower() == name:
                try:
                    await query.message.reply_sticker(
                        sticker=anime["sticker"],
                        reply_markup=build_buttons(anime)
                    )
                except Exception:
                    await query.message.reply_text(
                        anime["name"],
                        reply_markup=build_buttons(anime)
                    )
                return

    # ==============================
    # IGNORE BUTTON
    # ==============================
    elif data == "ignore":
        await query.answer(
            "Please Use Prev/Next Button Only",
            show_alert=False
        )

    # ==============================
    # PAGINATION
    # ==============================
    elif data.startswith("alist_"):
        page = int(data.split("_")[1])

        animes = sorted(
            animes,
            key=lambda x: x["name"].lower()
        )

        page_data, page, total_pages = build_page(animes, page)

        text = (
            f"<b>📜 Anime List</b>\n"
            f"📄 Page {page}/{total_pages}\n\n"
        )

        start_no = (page - 1) * ANIME_PER_PAGE

        for i, anime in enumerate(page_data, start=start_no + 1):
            hindi = anime.get("hindi_link", "-")
            english = anime.get("english_link", "-")

            text += f"<b>{i}) {anime['name']}</b> ➪ "

            links = []

            if hindi and hindi != "-":
                links.append(f"<a href='{hindi}'>🇮🇳 Hindi</a>")

            if english and english != "-":
                links.append(f"<a href='{english}'>🇺🇸 English</a>")

            if links:
                text += " | ".join(links)
            else:
                text += "❌ No Link"

            text += "\n"

        prev_page = page - 1 if page > 1 else 1
        next_page = page + 1 if page < total_pages else total_pages

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Prev",
                    callback_data=f"alist_{prev_page}"
                ),
                InlineKeyboardButton(
                    f"{page}/{total_pages}",
                    callback_data="ignore"
                ),
                InlineKeyboardButton(
                    "Next ➡️",
                    callback_data=f"alist_{next_page}"
                ),
            ]
        ])

        await query.message.edit_text(
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=keyboard,
                )

