# ==============================
# MAIN BOT FILE
# ==============================

import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ChatMemberHandler,
    InlineQueryHandler
)

# 🔧 Import Config
from config import BOT_TOKEN

# 🔥 Import Handlers (you will create these next)
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
    ping
)

# ==============================
# LOGGING
# ==============================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ==============================
# MAIN FUNCTION
# ==============================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

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
    app.add_handler(CommandHandler("admins", adminlist_command))
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
    # GROUP EVENTS
    # ==============================
    app.add_handler(ChatMemberHandler(chat_member_update, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members))

    # ==============================
    # CALLBACK & INLINE
    # ==============================
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(InlineQueryHandler(inline_query))

    # ==============================
    # AUTO SEARCH (TEXT)
    # ==============================
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, direct_search))

    print("🚀 Bot Started Successfully!")
    app.run_polling(drop_pending_updates=True)

# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    main()
