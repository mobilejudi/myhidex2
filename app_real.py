# app_real.py
import asyncio, uvicorn
from api.main import app
from workers.ingestor_real import run as run_ingestor
from signals.engine_real import run as run_signals
from bots.telegram_bot import run as run_bot

async def main():
    server = uvicorn.Server(uvicorn.Config("api.main:app", host="0.0.0.0", port=8000))
    await asyncio.gather(
        server.serve(),
        run_ingestor(),
        run_signals(),
        run_bot(),
    )

if __name__ == "__main__":
    asyncio.run(main())
