# risk/engine.py
import httpx, base64
from typing import Tuple
from connectors.helius_tx import get_account_info
from config import settings

TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"

async def spl_mint_risk(mint: str) -> dict:
    info = await get_account_info(mint)
    parsed = (info or {}).get("value", {}).get("data", {}).get("parsed", {})
    mint_info = parsed.get("info", {})
    freeze = mint_info.get("freezeAuthority")
    mint_auth = mint_info.get("mintAuthority")
    supply = int(mint_info.get("supply", "0"))
    decimals = int(mint_info.get("decimals", 0))
    return {
        "freeze_active": freeze is not None,
        "mint_active": mint_auth is not None,
        "supply": supply,
        "decimals": decimals,
    }

async def top_holders_heuristic(mint: str) -> dict:
    # Simple, à remplacer par un indexeur: on ne fait qu'un placeholder champ
    # Idéalement: Flipside query: top holders %, dev wallet concentration
    return {"top_holder_pct": 0.28, "top5_pct": 0.63}

async def honeypot_simulation(jupiter_quote: dict) -> Tuple[bool, float]:
    # On valide que la route existe et slippage estimé raisonnable
    routes = jupiter_quote.get("data") or []
    if not routes:
        return False, 10000
    best = routes[0]
    est_bps = best.get("priceImpactPct", 0) * 10000
    return True, est_bps
