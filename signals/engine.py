import asyncio, structlog
from bus.events import bus, STREAM_RAW, STREAM_SIGNALS, now_ms
from storage.db import SessionLocal, Signal
from signals.rules import Context, strength

log = structlog.get_logger("signals.engine")

# Mémoire courte des agrégats (à remplacer par Timescale requêtes)
state = {
    # token_id: { "smart_buy_sol": deque[(ts, amount)], ... }
}

def get_context_from_event(ev) -> Context | None:
    # TODO: convertir un raw log/tx en features agrégées
    # Exemple basique:
    token_id = ev.get("token_id")
    if not token_id:
        return None
    buys_smart = ev.get("smart_buy_sol_5m", 0.0)
    uniq = ev.get("uniq_smart_5m", 0)
    return Context(
        token_id=token_id,
        buys_smart_sol_5m=buys_smart,
        unique_smart_buyers_5m=uniq,
        ret_1m=ev.get("ret_1m", 0.0),
        ret_5m=ev.get("ret_5m", 0.0),
        liquidity_usd=ev.get("liquidity_usd", 0.0),
        price_impact_1sol_bps=ev.get("impact_bps", 50.0),
        risk_penalties=ev.get("risk_pen", 1.0),
    )

async def run():
    async for _, ev in bus.consume(STREAM_RAW, "signals", "signals-1"):
        ctx = get_context_from_event(ev)
        if not ctx:
            continue
        score, reason = strength(ctx)
        if score < 1.0:
            continue
        async with SessionLocal() as s:
            s.add(Signal(token_id=ctx.token_id, ts_ms=now_ms(), score=score, reason=reason))
            await s.commit()
        await bus.publish(STREAM_SIGNALS, {"token_id": ctx.token_id, "score": score, "reason": reason})
        log.info("signal", token_id=ctx.token_id, score=round(score,2))
