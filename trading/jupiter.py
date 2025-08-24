import httpx, structlog, base64, json, asyncio
from config import settings

log = structlog.get_logger("jupiter")

async def get_quote_buy(mint: str, amount_sol: float, slippage_bps: int = 150):
    amt = int(amount_sol * 1_000_000_000)  # lamports
    params = {
        "inputMint": "So11111111111111111111111111111111111111112",
        "outputMint": mint,
        "amount": amt,
        "slippageBps": slippage_bps,
        "onlyDirectRoutes": False
    }
    async with httpx.AsyncClient(timeout=10) as cx:
        r = await cx.get(f"{settings.JUPITER_BASE}/v6/quote", params=params)
        r.raise_for_status()
        return r.json()

async def swap(route: dict, user_pubkey: str, payer_signer: callable):
    # Build transaction
    async with httpx.AsyncClient(timeout=20) as cx:
        r = await cx.post(settings.JUPITER_SWAP, json={
            "quoteResponse": route,
            "userPublicKey": user_pubkey,
            "wrapAndUnwrapSol": True,
            "useSharedAccounts": True,
            "dynamicComputeUnitLimit": True,
            "prioritizationFeeLamports": "auto",
        })
        r.raise_for_status()
        j = r.json()
        tx_b64 = j["swapTransaction"]
        tx_bytes = base64.b64decode(tx_b64)
        # signer fourni par wallet.py
        signed = await payer_signer(tx_bytes)
        # envoyer via RPC HTTP (Helius)
        submit = await cx.post(settings.HELIUS_HTTP, json={
            "jsonrpc": "2.0", "id": 1, "method": "sendRawTransaction",
            "params": [base64.b64encode(signed).decode(), {"skipPreflight": False}]
        })
        submit.raise_for_status()
        sig = submit.json()["result"]
        log.info("swap_submitted", sig=sig)
        return sig
