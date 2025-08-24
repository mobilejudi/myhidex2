import asyncio
from bus.events import bus, STREAM_SIGNALS
from config import settings
from telegram import Bot

async def run_bot():
    if not settings.TG_TOKEN or not settings.TG_CHAT_ID:
        return
    bot = Bot(token=settings.TG_TOKEN)
    async for _, ev in bus.consume(STREAM_SIGNALS, "tg", "tg-1"):
        msg = (
          f"Signal {ev.get('token_mint','?')} "
          f"score={ev['score']:.2f} | "
          f"smart_5m={ev['reason'].get('inputs',{}).get('buys_smart_sol_5m',0):.2f} SOL | "
          f"risk={ev['reason'].get('risk',0):.2f}"
        )
        await bot.send_message(chat_id=settings.TG_CHAT_ID, text=msg)
