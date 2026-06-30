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

import asyncio

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import (
    RetryAfter,
    Forbidden,
    BadRequest,
)

from config import ADMIN_IDS
from database.mongo import (
    get_all_users,
    get_all_groups,
    remove_user,
    remove_group,
)


# ============================================================
# Helper Functions
# ============================================================

async def _copy_message(context, msg, chat_id, pin=False):

    try:

        sent = await msg.copy(chat_id=chat_id)

        if pin:

            try:
                await context.bot.pin_chat_message(
                    chat_id=chat_id,
                    message_id=sent.message_id,
                    disable_notification=True,
                )
            except Exception:
                pass

        return True

    except RetryAfter as e:

        await asyncio.sleep(e.retry_after)

        try:

            sent = await msg.copy(chat_id=chat_id)

            if pin:

                try:
                    await context.bot.pin_chat_message(
                        chat_id=chat_id,
                        message_id=sent.message_id,
                        disable_notification=True,
                    )
                except Exception:
                    pass

            return True

        except Exception:
            return False

    except (Forbidden, BadRequest):
        return False

    except Exception:
        return False


async def _forward_message(context, msg, chat_id, pin=False):

    try:

        sent = await context.bot.forward_message(
            chat_id=chat_id,
            from_chat_id=msg.chat_id,
            message_id=msg.message_id,
        )

        if pin:

            try:
                await context.bot.pin_chat_message(
                    chat_id=chat_id,
                    message_id=sent.message_id,
                    disable_notification=True,
                )
            except Exception:
                pass

        return True

    except RetryAfter as e:

        await asyncio.sleep(e.retry_after)

        try:

            sent = await context.bot.forward_message(
                chat_id=chat_id,
                from_chat_id=msg.chat_id,
                message_id=msg.message_id,
            )

            if pin:

                try:
                    await context.bot.pin_chat_message(
                        chat_id=chat_id,
                        message_id=sent.message_id,
                        disable_notification=True,
                    )
                except Exception:
                    pass

            return True

        except Exception:
            return False

    except (Forbidden, BadRequest):
        return False

    except Exception:
        return False


async def _send_report(update, context,
                       users_total,
                       users_success,
                       users_failed,
                       groups_total,
                       groups_success,
                       groups_failed):

    report = (
        "✅ <b>Broadcast Completed</b>\n\n"

        "👤 <b>Users</b>\n"
        f"• Total : <code>{users_total}</code>\n"
        f"• Success : <code>{users_success}</code>\n"
        f"• Failed : <code>{users_failed}</code>\n\n"

        "👥 <b>Groups</b>\n"
        f"• Total : <code>{groups_total}</code>\n"
        f"• Success : <code>{groups_success}</code>\n"
        f"• Failed : <code>{groups_failed}</code>\n\n"

        "📊 <b>Overall</b>\n"
        f"• Total : <code>{users_total + groups_total}</code>\n"
        f"• Success : <code>{users_success + groups_success}</code>\n"
        f"• Failed : <code>{users_failed + groups_failed}</code>"
    )

    try:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=report,
            parse_mode="HTML",
        )
    except Exception:
        pass

    return report 

# ============================================================
# /bc  (Copy Broadcast)
# ============================================================

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    if not update.message.reply_to_message:
        return await update.message.reply_text(
            "❌ Reply to a message to broadcast."
        )

    msg = update.message.reply_to_message

    users = await get_all_users()
    groups = await get_all_groups()

    users_total = len(users)
    groups_total = len(groups)

    users_success = 0
    users_failed = 0

    groups_success = 0
    groups_failed = 0

    total = users_total + groups_total
    processed = 0

    status = await update.message.reply_text(
        f"🚀 Broadcast Started...\n\n"
        f"📤 Total Chats : {total}"
    )

    # ---------------- USERS ---------------- #

    for user_id in users:

        ok = await _copy_message(
            context=context,
            msg=msg,
            chat_id=user_id,
            pin=False,      # Telegram bots cannot pin in user DMs
        )

        if ok:
            users_success += 1
        else:
            users_failed += 1

        processed += 1

        if processed % 100 == 0:

            await status.edit_text(
                "🚀 Broadcasting...\n\n"
                f"Processed : {processed}/{total}\n"
                f"Users : {users_success}/{users_total}\n"
                f"Groups : {groups_success}/{groups_total}"
            )

    # ---------------- GROUPS ---------------- #

    for group_id in groups:

        ok = await _copy_message(
            context=context,
            msg=msg,
            chat_id=group_id,
            pin=True,
        )

        if ok:
            groups_success += 1
        else:
            groups_failed += 1

        processed += 1

        if processed % 100 == 0:

            await status.edit_text(
                "🚀 Broadcasting...\n\n"
                f"Processed : {processed}/{total}\n"
                f"Users : {users_success}/{users_total}\n"
                f"Groups : {groups_success}/{groups_total}"
            )

    report = await _send_report(
        update,
        context,
        users_total,
        users_success,
        users_failed,
        groups_total,
        groups_success,
        groups_failed,
    )

    await status.edit_text(
        report,
        parse_mode="HTML",
    )

# ============================================================
# /fbc (Forward Broadcast)
# ============================================================

async def forward_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    if not update.message.reply_to_message:
        return await update.message.reply_text(
            "❌ Reply to a message to forward broadcast."
        )

    msg = update.message.reply_to_message

    users = await get_all_users()
    groups = await get_all_groups()

    users_total = len(users)
    groups_total = len(groups)

    users_success = 0
    users_failed = 0

    groups_success = 0
    groups_failed = 0

    total = users_total + groups_total
    processed = 0

    status = await update.message.reply_text(
        f"🚀 Forward Broadcast Started...\n\n"
        f"📤 Total Chats : {total}"
    )

    # ---------------- USERS ---------------- #

    for user_id in users:

        ok = await _forward_message(
            context=context,
            msg=msg,
            chat_id=user_id,
            pin=False
        )

        if ok:
            users_success += 1
        else:
            users_failed += 1

        processed += 1

        if processed % 100 == 0:

            await status.edit_text(
                "🚀 Forward Broadcasting...\n\n"
                f"Processed : {processed}/{total}\n"
                f"Users : {users_success}/{users_total}\n"
                f"Groups : {groups_success}/{groups_total}"
            )

    # ---------------- GROUPS ---------------- #

    for group_id in groups:

        ok = await _forward_message(
            context=context,
            msg=msg,
            chat_id=group_id,
            pin=True
        )

        if ok:
            groups_success += 1
        else:
            groups_failed += 1

        processed += 1

        if processed % 100 == 0:

            await status.edit_text(
                "🚀 Forward Broadcasting...\n\n"
                f"Processed : {processed}/{total}\n"
                f"Users : {users_success}/{users_total}\n"
                f"Groups : {groups_success}/{groups_total}"
            )

    report = await _send_report(
        update,
        context,
        users_total,
        users_success,
        users_failed,
        groups_total,
        groups_success,
        groups_failed,
    )

    await status.edit_text(
        report,
        parse_mode="HTML",
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
