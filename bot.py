# ==============================
# MAIN BOT FILE
# ==============================

import asyncio
import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    InlineQueryHandler,
    filters,
)

# Config
from config import BOT_TOKEN

# Database
from database.mongo import load_anime_cache, create_indexes

# Handlers
from handlers.start import start
from handlers.anime import anime_search, add_anime, del_anime
from handlers.search import improved_anime, button_search, direct_search
from handlers.animelist import animelist
from handlers.group import chat_member_update, welcome_new_members
from handlers.callback import button_click
from handlers.inline import inline_query
from handlers.admin import stats, broadcast, bulk_add
from handlers.misc import (
    help_cmd,
    id_command,
    owner_command,
    adminlist_command,
    roast_user,
    ping,
)

# ==============================
# LOGGING
# ==============================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ==============================
# MAIN FUNCTION
# ==============================

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # 🔹 Load DB cache
    await create_indexes()
    await load_anime_cache()

    # ==============================
    # USER COMMANDS
    # ==============================

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("anime", anime_search))
    app.add_handler(CommandHandler("search", improved_anime))
    app.add_handler(CommandHandler("btn", button_search))
    app.add_handler(CommandHandler("animelist", animelist))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("owner", owner_command))
    app.add_handler(CommandHandler("adminlist", adminlist_command))
    app.add_handler(CommandHandler("roast", roast_user))
    app.add_handler(CommandHandler("ping", ping))

    # ==============================
    # ADMIN COMMANDS
    # ==============================

    app.add_handler(CommandHandler("add", add_anime))
    app.add_handler(CommandHandler("del", del_anime))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("bc", broadcast))
    app.add_handler(CommandHandler("bulkadd", bulk_add))

    # ==============================
    # MESSAGE HANDLERS
    # ==============================

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, direct_search))

    # ==============================
    # CALLBACK / INLINE
    # ==============================

    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(InlineQueryHandler(inline_query))

    # ==============================
    # GROUP EVENTS
    # ==============================

    # New members join
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members)
    )

    # Bot added / removed
    app.add_handler(
        ChatMemberHandler(chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER)
    )

    # ==============================
    # START BOT
    # ==============================

    print("🚀 Bot Started Successfully...")
    await app.run_polling()


# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    asyncio.run(main())
