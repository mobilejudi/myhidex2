import asyncio, uvicorn
from workers.ingestor import run as run_ingestor
from signals.engine import run as run_signals
from bots.telegram_bot import run as run_bot

async def main():
    # Lancer API
    config = uvicorn.Config("api.main:app", host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    # Lancer workers concurrents
    await asyncio.gather(
        server.serve(),
        run_ingestor(),
        run_signals(),
        run_bot(),
    )

if __name__ == "__main__":
    asyncio.run(main())
