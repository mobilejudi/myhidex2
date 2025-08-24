import asyncio, json, websockets, structlog
from tenacity import retry, wait_exponential_jitter, stop_after_attempt
from config import settings

log = structlog.get_logger("solana.ws")

SUB_TEMPLATE = {
  "jsonrpc": "2.0",
  "id": 1,
  "method": "logsSubscribe",
  "params": [{"mentions": []}, {"commitment": "confirmed"}]
}

PUMP_FUN_PROGRAMS = [
    "C2xn1J…",  # TODO: vrais Program IDs
]
RAYDIUM_PROGRAMS = [
    "4Rh7y…",
]

@retry(wait=wait_exponential_jitter(1, 10), stop=stop_after_attempt(10))
async def stream_logs(on_event):
    async with websockets.connect(settings.HELIUS_WS, ping_interval=20, ping_timeout=20, max_size=4_000_000) as ws:
        # subscribe multiple programs
        sub_ids = []
        for progs in (PUMP_FUN_PROGRAMS, RAYDIUM_PROGRAMS):
            req = SUB_TEMPLATE | {"id": len(sub_ids)+1, "params": [{"mentions": progs}, {"commitment": "confirmed"}]}
            await ws.send(json.dumps(req))
            ack = await ws.recv()
            sub_ids.append(ack)

        log.info("subscriptions_ready", count=len(sub_ids))
        while True:
            raw = await ws.recv()
            evt = json.loads(raw)
            if evt.get("method") == "logsNotification":
                await on_event(evt["params"]["result"])
