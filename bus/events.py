import json, time
from typing import AsyncIterator
import redis.asyncio as redis
from config import settings

STREAM_RAW = "events.raw"
STREAM_SIGNALS = "signals.out"
STREAM_SMART = "smart.activity"

class EventBus:
    def __init__(self):
        self.r = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def publish(self, stream: str, payload: dict):
        await self.r.xadd(stream, {"d": json.dumps(payload, separators=(",", ":"))})

    async def consume(self, stream: str, group: str, consumer: str) -> AsyncIterator[dict]:
        try:
            await self.r.xgroup_create(stream, group, id="$", mkstream=True)
        except Exception:
            pass
        last_id = ">"
        while True:
            resp = await self.r.xreadgroup(group, consumer, {stream: last_id}, count=100, block=5000)
            if not resp:
                continue
            for _, msgs in resp:
                for msg_id, data in msgs:
                    yield msg_id, json.loads(data["d"])
                    await self.r.xack(stream, group, msg_id)

bus = EventBus()
now_ms = lambda: int(time.time()*1000)
