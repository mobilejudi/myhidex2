import asyncio, structlog, time
from connectors.solana_ws import stream_logs
from bus.events import bus, STREAM_RAW, now_ms

log = structlog.get_logger("ingestor")

async def on_event(evt):
    # Transforme l’événement log en message brut simplifié
    # TODO: parser les logs Pump.fun/Raydium pour extraire mint, montant, wallet, etc.
    payload = {
        "token_id": evt.get("value", {}).get("signature", 0) % 1000000,  # placeholder
        "smart_buy_sol_5m": 3.2,  # TODO
        "uniq_smart_5m": 2,
        "ret_1m": 0.05,
        "ret_5m": 0.12,
        "liquidity_usd": 80000.0,
        "impact_bps": 60.0,
        "risk_pen": 0.5,
        "ts_ms": now_ms(),
    }
    await bus.publish(STREAM_RAW, payload)

async def run():
    await stream_logs(on_event)
