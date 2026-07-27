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
    await groups_col.update_one(
        {"_id": chat_id},
        {"$set": {"_id": chat_id}},
        upsert=True
    )

async def remove_group(chat_id: int):
    await groups_col.delete_one({"_id": chat_id})

async def get_all_groups():
    groups = []
    async for group in groups_col.find({}):
        groups.append(group)
    return groups

async def total_groups():
    return await groups_col.count_documents({})


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

# ==========================================================
# REQUEST SYSTEM DATABASE
# ==========================================================

from datetime import datetime
import random

requests_col = db["requests"]


async def generate_request_id():
    """Generate unique request ID like REQ100123"""
    while True:
        req_id = f"REQ{random.randint(100000, 999999)}"
        exists = await requests_col.find_one({"_id": req_id})
        if not exists:
            return req_id


async def create_request(
    user_id: int,
    username: str,
    full_name: str,
    anime: str,
    language: str,
    dub: str,
    season: str,
    extra: str,
):
    req_id = await generate_request_id()

    data = {
        "_id": req_id,
        "user_id": user_id,
        "username": username or "",
        "full_name": full_name,
        "anime": anime,
        "language": language,
        "dub": dub,
        "season": season,
        "extra": extra,
        "status": "Pending",
        "admin_reply": "",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    await requests_col.insert_one(data)
    return req_id


async def get_request(req_id: str):
    return await requests_col.find_one({"_id": req_id})


async def update_request_status(
    req_id: str,
    status: str,
    admin_reply: str = "",
):
    await requests_col.update_one(
        {"_id": req_id},
        {
            "$set": {
                "status": status,
                "admin_reply": admin_reply,
                "updated_at": datetime.utcnow(),
            }
        },
    )


async def delete_request(req_id: str):
    await requests_col.delete_one({"_id": req_id})


async def get_pending_requests():
    requests = []
    async for req in requests_col.find({"status": "Pending"}):
        requests.append(req)
    return requests


async def get_user_requests(user_id: int):
    requests = []
    async for req in requests_col.find({"user_id": user_id}):
        requests.append(req)
    return requests


async def total_requests():
    return await requests_col.count_documents({})


async def pending_requests():
    return await requests_col.count_documents(
        {"status": "Pending"}
    )


async def request_exists(user_id: int, anime: str, language: str):
    """
    Prevent duplicate pending requests.
    """
    return await requests_col.find_one(
        {
            "user_id": user_id,
            "anime": {"$regex": f"^{anime}$", "$options": "i"},
            "language": language,
            "status": "Pending",
        }
            )


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
