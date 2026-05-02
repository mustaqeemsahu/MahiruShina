# ==============================
# MAIN BOT FILE (WEBHOOK MODE)
# ==============================

import os
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
# MAIN
# ==============================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # DB init
    import asyncio

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_indexes())
    loop.run_until_complete(load_anime_cache())
    print("✅ Database Connected")
except Exception as e:
    print(f"⚠️ Database Error: {e}")

    # ==========================
    # COMMANDS
    # ==========================
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

    # ADMIN
    app.add_handler(CommandHandler("add", add_anime))
    app.add_handler(CommandHandler("del", del_anime))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("bulkadd", bulk_add))

    # MESSAGE
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, direct_search))

    # CALLBACK / INLINE
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(InlineQueryHandler(inline_query))

    # GROUP EVENTS
    app.add_handler(ChatMemberHandler(chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members))

    # ==========================
    # WEBHOOK SETUP
    # ==========================

    PORT = int(os.environ.get("PORT", 10000))

    RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")

    if not RENDER_URL:
        raise ValueError("RENDER_EXTERNAL_URL not set!")

    WEBHOOK_URL = f"{RENDER_URL}/{BOT_TOKEN}"

    print(f"🌐 Webhook URL: {WEBHOOK_URL}")

    # RUN WEBHOOK
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=WEBHOOK_URL,
    )


# ==============================
# ENTRY
# ==============================
if __name__ == "__main__":
    main()
