# ops/scheduler.py
import asyncio, time, structlog
from trading.policy import policy_state

log = structlog.get_logger("scheduler")

async def run_scheduler():
    while True:
        # Reset des compteurs quotidiens à 00:00 UTC
        now = time.gmtime()
        if now.tm_hour == 0 and now.tm_min < 2:
            policy_state.day_used_sol = 0.0
            log.info("policy_reset_daily")
            await asyncio.sleep(120)
        await asyncio.sleep(10)
