# connectors/raydium.py
from typing import Optional

RAYDIUM_CP_PROGRAM = "EoTcj6..."  # AMM v4/v5
RAYDIUM_CLMM_PROGRAM = "CAMMCg..."  # CLMM
TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"  # SPL token

def parse_raydium_logs(result: dict) -> Optional[dict]:
    val = result.get("value", {})
    logs = val.get("logs") or []
    sig = val.get("signature")
    slot = result.get("slot") or result.get("context", {}).get("slot")

    # Identify swap by log message
    is_swap = any("swap" in l.lower() for l in logs)
    if not is_swap:
        return None

    # Heuristique: extraire mint via "mint" mot-clé (sera amélioré avec getTransaction)
    mint = None
    for l in logs:
        if "mint:" in l.lower():
            mint = l.split()[-1].strip()
            break

    return {
        "source": "raydium",
        "signature": sig,
        "slot": slot,
        "kind": "SWAP",
        "mint": mint
    }
