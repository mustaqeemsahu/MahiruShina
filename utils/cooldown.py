# ==============================
# COOLDOWN SYSTEM
# ==============================

import time

user_cooldown = {}

def check_cooldown(user_id):
    now = time.time()
    if user_id in user_cooldown:
        if now - user_cooldown[user_id] < 5:
            return False
    user_cooldown[user_id] = now
    return True
