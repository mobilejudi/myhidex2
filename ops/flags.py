# ops/flags.py
import redis.asyncio as redis
from config import settings

r = redis.from_url(settings.REDIS_URL)

async def flag_enabled(name: str, default: bool = True) -> bool:
    v = await r.get(f"flag:{name}")
    if v is None:
        return default
    return v == "1"

async def set_flag(name: str, enable: bool):
    await r.set(f"flag:{name}", "1" if enable else "0")
