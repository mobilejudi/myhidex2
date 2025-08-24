from dataclasses import dataclass
from typing import Dict, Any
import math, time

@dataclass
class Context:
    token_id: int
    buys_smart_sol_5m: float
    unique_smart_buyers_5m: int
    ret_1m: float
    ret_5m: float
    liquidity_usd: float
    price_impact_1sol_bps: float
    risk_penalties: float  # 0..2

def strength(ctx: Context) -> tuple[float, Dict[str, Any]]:
    smart = min(3.0, math.log10(ctx.buys_smart_sol_5m + 1.0) + 0.2*ctx.unique_smart_buyers_5m)
    momentum = max(0.0, 0.8*ctx.ret_1m + 0.2*ctx.ret_5m)  # très simple, à affiner
    liquidity_q = min(3.0, 0.002 * ctx.liquidity_usd - 0.001 * ctx.price_impact_1sol_bps)
    risk = max(0.0, 3.0 - ctx.risk_penalties)

    score = 0.4*smart + 0.25*momentum + 0.2*liquidity_q + 0.15*risk
    score = max(0.0, min(3.0, score))

    reason = {
        "smart": smart, "momentum": momentum, "liq": liquidity_q, "risk": risk,
        "inputs": ctx.__dict__
    }
    return score, reason
