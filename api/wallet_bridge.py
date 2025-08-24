# api/wallet_bridge.py
from fastapi import APIRouter, HTTPException
import httpx, base64
from config import settings

router = APIRouter(prefix="/trade", tags=["trade"])

@router.post("/prepare-buy")
async def prepare_buy(mint: str, user_pubkey: str, amount_sol: float, slippage_bps: int = 150):
    # Quote
    amt = int(amount_sol * 1_000_000_000)
    async with httpx.AsyncClient(timeout=15) as cx:
        q = await cx.get(f"{settings.JUPITER_BASE}/v6/quote", params={
            "inputMint": "So11111111111111111111111111111111111111112",
            "outputMint": mint,
            "amount": amt,
            "slippageBps": slippage_bps,
            "onlyDirectRoutes": False
        })
        q.raise_for_status()
        route = q.json()
        sw = await cx.post(settings.JUPITER_SWAP, json={
            "quoteResponse": route,
            "userPublicKey": user_pubkey,
            "wrapAndUnwrapSol": True,
            "useSharedAccounts": True,
            "dynamicComputeUnitLimit": True,
            "prioritizationFeeLamports": "auto",
            "asLegacyTransaction": False
        })
        sw.raise_for_status()
        j = sw.json()
        return {"swapTransaction": j["swapTransaction"]}

@router.post("/submit")
async def submit(signed_tx_b64: str):
    async with httpx.AsyncClient(timeout=15) as cx:
        r = await cx.post(settings.HELIUS_HTTP, json={
            "jsonrpc":"2.0","id":1,"method":"sendRawTransaction",
            "params":[signed_tx_b64, {"skipPreflight": False}]
        })
        r.raise_for_status()
        return {"signature": r.json()["result"]}
