# workers/ingestor_real.py
import asyncio, json, websockets, structlog, time
from tenacity import retry, wait_exponential_jitter
from config import settings
from connectors.pumpfun import PUMPFUN_PROGRAM, parse_pumpfun_logs
from connectors.raydium import RAYDIUM_CP_PROGRAM, RAYDIUM_CLMM_PROGRAM, parse_raydium_logs
from connectors.helius_tx import get_tx
from smartmoney.registry import registry
from bus.events import bus, STREAM_RAW, now_ms

log = structlog.get_logger("ingestor.real")

def _sub_req(method: str, params: dict, idn: int):
    return {"jsonrpc":"2.0","method":method,"id":idn,"params":[params,{"commitment":"confirmed"}]}

@retry(wait=wait_exponential_jitter(1, 10))
async def run():
    programs = [PUMPFUN_PROGRAM, RAYDIUM_CP_PROGRAM, RAYDIUM_CLMM_PROGRAM]
    async with websockets.connect(settings.HELIUS_WS, ping_interval=20, ping_timeout=20, max_size=6_000_000) as ws:
        # subscribe logs for programs
        for i, pg in enumerate(programs, start=1):
            req = {"jsonrpc":"2.0","id":i,"method":"logsSubscribe",
                   "params":[{"mentions":[pg]}, {"commitment":"confirmed"}]}
            await ws.send(json.dumps(req))
            await ws.recv()  # ack

        log.info("ws_ready", subs=len(programs))
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("method") != "logsNotification":
                continue
            res = msg["params"]["result"]
            # parse both
            evt = parse_pumpfun_logs(res) or parse_raydium_logs(res)
            if not evt:
                continue

            sig = evt["signature"]
            tx = await get_tx(sig)  # enrichissement précis
            if not tx:
                continue

            # Features: détecter acheteurs smart money (addresses dans tx)
            accts = (tx.get("transaction", {}) or {}).get("message", {}).get("accountKeys", [])
            accts_lower = [a.get("pubkey","").lower() if isinstance(a, dict) else str(a).lower() for a in accts]
            uniq_smart = len({a for a in accts_lower if registry.contains(a)})

            payload = {
                "token_mint": evt.get("mint"),
                "signature": sig,
                "slot": evt.get("slot"),
                "source": evt["source"],
                "kind": evt["kind"],
                "uniq_smart_5m": uniq_smart,
                # placeholders supplémentaires; le moteur de signaux agrègera
                "amount_sol": 0.0,
                "ts_ms": now_ms(),
            }
            await bus.publish(STREAM_RAW, payload)
