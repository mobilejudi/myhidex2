# ops/health.py
import asyncio, redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncEngine
from fastapi import APIRouter
from storage.db import engine
from config import settings

router = APIRouter(prefix="/ops", tags=["ops"])

@router.get("/ping")
async def ping():
    return {"ok": True}

@router.get("/readiness")
async def readiness():
    r = redis.from_url(settings.REDIS_URL)
    await r.ping()
    async with engine.connect() as conn:
        await conn.execute("SELECT 1")
    return {"ready": True}
