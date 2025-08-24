# signals/engine_real.py
import structlog, asyncio
from bus.events import bus, STREAM_RAW, STREAM_SIGNALS, now_ms
from storage.db import SessionLocal, Signal, Token
from signals.rules import Context, strength
from signals.aggregator import agg
from risk.engine import spl_mint_risk, top_holders_heuristic, honeypot_simulation
from trading.jupiter import get_quote_buy

log = structlog.get_logger("signals.real")

async def run():
    async for _, ev in bus.consume(STREAM_RAW, "signals-real", "sig-r1"):
        mint = ev.get("token_mint")
        if not mint:
            continue

        # Update feature aggregator (TODO: derive amount_sol from tx parsing)
        agg.add(mint, ev["ts_ms"], ev.get("amount_sol", 0.0), ev.get("uniq_smart_5m", 0))

        feats = agg.features(mint, ev["ts_ms"])

        # Risk checks (authorities, holders)
        r_info = await spl_mint_risk(mint)
        holders = await top_holders_heuristic(mint)

        risk_pen = 0.0
        if r_info["mint_active"]:
            risk_pen += 0.8
        if r_info["freeze_active"]:
            risk_pen += 0.8
        if holders["top_holder_pct"] > 0.35:
            risk_pen += 0.6

        # Quote Jupiter pour price impact (honeypot light)
        j_quote = await get_quote_buy(mint, 0.2, slippage_bps=200)
        tradable, impact_bps = await honeypot_simulation(j_quote)

        ctx = Context(
            token_id=0,  # remplacé par id DB après upsert
            buys_smart_sol_5m=feats["buys_smart_sol_5m"],
            unique_smart_buyers_5m=feats["uniq_smart_5m"],
            ret_1m=feats["ret_1m"],
            ret_5m=feats["ret_5m"],
            liquidity_usd= j_quote.get("data", [{}])[0].get("outAmount", 0)/1e6 if j_quote.get("data") else 0.0,
            price_impact_1sol_bps=impact_bps or 0.0,
            risk_penalties=risk_pen
        )

        score, reason = strength(ctx)
        if score < 1.0 or not tradable:
            continue

        async with SessionLocal() as s:
            # upsert token
            q = await s.execute(Token.__table__.select().where(Token.mint==mint))
            row = q.mappings().first()
            if row:
                token_id = row["id"]
            else:
                res = await s.execute(Token.__table__.insert().values(mint=mint, flags={}).returning(Token.id))
                token_id = res.scalar_one()
            s.add(Signal(token_id=token_id, ts_ms=now_ms(), score=score, reason=reason | {"mint": mint}))
            await s.commit()

        await bus.publish(STREAM_SIGNALS, {"token_mint": mint, "score": score, "reason": reason})
        log.info("signal_real", mint=mint, score=round(score,2))
