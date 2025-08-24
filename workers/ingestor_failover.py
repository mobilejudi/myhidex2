# workers/ingestor_failover.py
import asyncio, json, structlog
from tenacity import retry, wait_exponential_jitter
from connectors.providers import WsSupervisor
from config import settings
from bus.events import bus, STREAM_RAW, now_ms
from connectors.pumpfun import PUMPFUN_PROGRAM, parse_pumpfun_logs
from connectors.raydium import RAYDIUM_CP_PROGRAM, RAYDIUM_CLMM_PROGRAM, parse_raydium_logs
from connectors.helius_tx import get_tx

log = structlog.get_logger("ingestor.failover")
sup = WsSupervisor(settings.PROVIDERS)

SUBS = [
    ("logsSubscribe", {"mentions": [PUMPFUN_PROGRAM]}),
    ("logsSubscribe", {"mentions": [RAYDIUM_CP_PROGRAM]}),
    ("logsSubscribe", {"mentions": [RAYDIUM_CLMM_PROGRAM]}),
]

async def subscribe_all(ws):
    # renvoie les id -> topic
    ids = {}
    for i, (meth, param) in enumerate(SUBS, start=1):
        req = {"jsonrpc":"2.0","id":i,"method":meth,"params":[param, {"commitment":"confirmed"}]}
        await ws.send(json.dumps(req))
        ack = json.loads(await ws.recv())
        ids[i] = meth
    return ids

async def run():
    while True:
        try:
            async with sup.connect() as (prov, ws):
                await subscribe_all(ws)
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get("method") != "logsNotification":
                        continue
                    res = msg["params"]["result"]
                    evt = parse_pumpfun_logs(res) or parse_raydium_logs(res)
                    if not evt:
                        continue
                    # enrich
                    tx = await get_tx(evt["signature"])
                    if not tx:
                        continue
                    await bus.publish(STREAM_RAW, {
                        "token_mint": evt.get("mint"),
                        "source": evt["source"],
                        "kind": evt["kind"],
                        "signature": evt["signature"],
                        "slot": evt.get("slot"),
                        "uniq_smart_5m": 0,  # rempli par aggregator
                        "amount_sol": 0.0,
                        "ts_ms": now_ms(),
                    })
        except Exception as e:
            await sup.failover(str(e))
            await asyncio.sleep(1.5)
