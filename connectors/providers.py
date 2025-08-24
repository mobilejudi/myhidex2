# connectors/providers.py
import asyncio, time, json, websockets, structlog
from contextlib import asynccontextmanager
from dataclasses import dataclass

log = structlog.get_logger("providers")

@dataclass
class RpcProvider:
    name: str
    ws_url: str
    http_url: str

class WsSupervisor:
    def __init__(self, providers: list[RpcProvider]):
        self.providers = providers
        self.i = 0

    def current(self) -> RpcProvider:
        return self.providers[self.i]

    def next(self):
        self.i = (self.i + 1) % len(self.providers)

    @asynccontextmanager
    async def connect(self, max_size=8_000_000):
        prov = self.current()
        log.info("ws_connect", provider=prov.name)
        async with websockets.connect(prov.ws_url, ping_interval=20, ping_timeout=20, max_size=max_size) as ws:
            yield prov, ws

    async def failover(self, reason: str):
        log.warning("ws_failover", reason=reason, from_provider=self.current().name)
        self.next()
