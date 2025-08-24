# bus/idempotency.py
import redis.asyncio as redis
from config import settings

r = redis.from_url(settings.REDIS_URL)

async def seen_once(key: str, ttl_sec: int = 3600) -> bool:
    # setnx returns True if the key was set
    ok = await r.setnx(f"seen:{key}", "1")
    if ok:
        await r.expire(f"seen:{key}", ttl_sec)
    return not ok  # True if already seen
