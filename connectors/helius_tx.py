# connectors/helius_tx.py
import httpx
from config import settings

async def get_tx(signature: str) -> dict | None:
    # Utilise Helius Enhanced getTransaction
    payload = {
        "jsonrpc": "2.0", "id": 1, "method": "getTransaction",
        "params": [signature, {"maxSupportedTransactionVersion": 0}]
    }
    async with httpx.AsyncClient(timeout=15) as cx:
        r = await cx.post(settings.HELIUS_HTTP, json=payload)
        r.raise_for_status()
        j = r.json()
        return j.get("result")

async def get_account_info(account: str) -> dict | None:
    payload = {"jsonrpc":"2.0","id":1,"method":"getAccountInfo",
               "params":[account,{"encoding":"jsonParsed"}]}
    async with httpx.AsyncClient(timeout=15) as cx:
        r = await cx.post(settings.HELIUS_HTTP, json=payload)
        r.raise_for_status()
        return r.json().get("result")
