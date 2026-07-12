# ==============================
# MONGODB + CACHE + FAST SEARCH
# ==============================

from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI
import time

# ==============================
# CONNECTION
# ==============================

client = AsyncIOMotorClient(MONGO_URI)
db = client["AnimeBotDB"]

# Collections
users_col = db["users"]
groups_col = db["groups"]
anime_col = db["anime"]
warns_col = db["warns"]

# ==============================
# CACHE SYSTEM
# ==============================

ANIME_CACHE = []
CACHE_TIME = 0
CACHE_TTL = 300  # 5 minutes

# ==============================
# USERS SYSTEM
# ==============================

async def add_user(user_id: int):
    if not await users_col.find_one({"_id": user_id}):
        await users_col.insert_one({"_id": user_id})


async def get_all_users():
    return [u["_id"] async for u in users_col.find()]

async def remove_user(user_id: int):
    await users_col.delete_one({"_id": user_id})


async def remove_group(chat_id: int):
    await groups_col.delete_one({"_id": chat_id})


# ==============================
# GROUP SYSTEM
# ==============================

async def add_group(chat_id: int):
    if not await groups_col.find_one({"_id": chat_id}):
        await groups_col.insert_one({"_id": chat_id})


async def get_all_groups():
    return [g["_id"] async for g in groups_col.find()]


# ==============================
# ANIME SYSTEM (CACHED)
# ==============================

async def load_anime_cache():
    global ANIME_CACHE, CACHE_TIME

    ANIME_CACHE = [a async for a in anime_col.find()]
    CACHE_TIME = time.time()


async def get_all_anime():
    global CACHE_TIME

    # Reload cache if expired
    if time.time() - CACHE_TIME > CACHE_TTL or not ANIME_CACHE:
        await load_anime_cache()

    return ANIME_CACHE


async def add_anime_db(
    name,
    keys,
    sticker,
    hindi_link=None,
    english_link=None
):
    data = {
        "name": name,
        "keys": keys,
        "sticker": sticker
    }

    # Save only if provided
    if hindi_link:
        data["hindi_link"] = hindi_link

    if english_link:
        data["english_link"] = english_link

    # Backward compatibility
    if not hindi_link and not english_link:
        data["link"] = ""

    await anime_col.update_one(
        {"name": name},
        {"$set": data},
        upsert=True
    )

    # Refresh cache
    await load_anime_cache()


async def delete_anime_db(name):
    await anime_col.delete_one({"name": name})

    # 🔥 Refresh cache instantly
    await load_anime_cache()


# ==============================
# FAST SEARCH (INDEX BASED)
# ==============================

async def create_indexes():
    await anime_col.create_index("name")
    await anime_col.create_index("keys")


# ==============================
# WARN SYSTEM
# ==============================

WARN_LIMIT = 3

async def add_warn_db(chat_id, user_id, reason):
    data = await warns_col.find_one({"chat_id": chat_id, "user_id": user_id})

    if not data:
        await warns_col.insert_one({
            "chat_id": chat_id,
            "user_id": user_id,
            "count": 1,
            "reasons": [reason]
        })
        return 1

    new_count = data["count"] + 1
    reasons = data["reasons"] + [reason]

    await warns_col.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": new_count, "reasons": reasons}}
    )

    return new_count


async def get_warns_db(chat_id, user_id):
    data = await warns_col.find_one({"chat_id": chat_id, "user_id": user_id})
    return data if data else {"count": 0, "reasons": []}


async def reset_warns_db(chat_id, user_id):
    await warns_col.delete_one({"chat_id": chat_id, "user_id": user_id})
