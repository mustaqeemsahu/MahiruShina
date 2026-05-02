# ==============================
# ADMIN + BROADCAST SYSTEM
# ==============================

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_IDS
from database.mongo import get_all_users, get_all_groups, users_col, groups_col


# ==============================
# STATS
# ==============================

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    users = await get_all_users()
    groups = await get_all_groups()

    await update.message.reply_text(
        f"📊 Stats\n\n👤 Users: {len(users)}\n👥 Groups: {len(groups)}"
    )


# ==============================
# BROADCAST (COPY MESSAGE)
# ==============================

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    if not update.message.reply_to_message:
        return await update.message.reply_text(
            "❌ Reply to a message to broadcast"
        )

    msg = update.message.reply_to_message

    users = await get_all_users()
    groups = await get_all_groups()

    total = users + groups

    success = 0
    failed = 0

    status = await update.message.reply_text("🚀 Broadcasting...")

    for chat_id in total:
        try:
            await msg.copy(chat_id=chat_id)
            success += 1
        except:
            failed += 1

    await status.edit_text(
        f"✅ Broadcast Done\n\n✔ Success: {success}\n❌ Failed: {failed}"
    )


# ==============================
# BULK ADD USERS / GROUPS
# ==============================

async def bulk_add(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    if not context.args:
        return await update.message.reply_text(
            "❌ Usage:\n"
            "/bulkadd user 12345 67890\n"
            "/bulkadd group -100123 -100456"
        )

    mode = context.args[0].lower()
    ids = context.args[1:]

    if not ids:
        return await update.message.reply_text("❌ No IDs given")

    success = 0
    failed = 0

    for i in ids:
        try:
            _id = int(i)

            if mode == "user":
                if not await users_col.find_one({"_id": _id}):
                    await users_col.insert_one({"_id": _id})
            elif mode == "group":
                if not await groups_col.find_one({"_id": _id}):
                    await groups_col.insert_one({"_id": _id})
            else:
                return await update.message.reply_text("❌ Use 'user' or 'group'")

            success += 1
        except:
            failed += 1

    await update.message.reply_text(
        f"✅ Bulk Add Done\n\n✔ Success: {success}\n❌ Failed: {failed}"
    )
