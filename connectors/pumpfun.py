# connectors/pumpfun.py
import json
from typing import Optional, Tuple

PUMPFUN_PROGRAM = "GPvJk...REPLACE"  # ProgramId réel pump.fun

# Minimal decoder: repère init mint / buy events depuis logs
def parse_pumpfun_logs(result: dict) -> Optional[dict]:
    # result: {"value": {"signature": "...", "logs": [...], "context": {"slot": ...}, "err": None}}
    val = result.get("value", {})
    logs = val.get("logs") or []
    sig = val.get("signature")
    slot = result.get("context", {}).get("slot")

    # Heuristique: les logs contiennent souvent "Initialize", "Create", "Buy"
    kind = None
    for l in logs:
        if "Initialize" in l or "create" in l.lower():
            kind = "MINT_INIT"
            break
        if "Buy" in l or "swap" in l.lower():
            kind = "BUY"
            # on laisse continuer pour extraire infos
    if not kind:
        return None

    # Extraction adresse mint depuis un log b58 (si présent)
    mint = None
    for l in logs:
        if "mint:" in l.lower():
            mint = l.split()[-1].strip()
            break

    return {
        "source": "pumpfun",
        "signature": sig,
        "slot": slot,
        "kind": kind,
        "mint": mint
    }
