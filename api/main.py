from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import ORJSONResponse
from storage.db import init_models, SessionLocal, Signal
from bus.events import bus, STREAM_SIGNALS
import asyncio, json
from api.wallet_bridge import router as trade_router
from api.obs import MetricsMiddleware, router as metrics_router
from ops.health import router as ops_router

app = FastAPI(default_response_class=ORJSONResponse)
app.add_middleware(MetricsMiddleware)
app.include_router(trade_router)
app.include_router(metrics_router)
app.include_router(ops_router)
subscribers: set[WebSocket] = set()

@app.on_event("startup")
async def _startup():
    await init_models()
    asyncio.create_task(_forward_signals())

async def _forward_signals():
    async for _, ev in bus.consume(STREAM_SIGNALS, "ws", "ws-1"):
        dead = []
        for ws in subscribers:
            try:
                await ws.send_json(ev)
            except Exception:
                dead.append(ws)
        for ws in dead:
            subscribers.discard(ws)

@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/signals")
async def list_signals(limit: int = 50):
    async with SessionLocal() as s:
        rows = (await s.execute(
            Signal.__table__.select().order_by(Signal.ts_ms.desc()).limit(limit)
        )).mappings().all()
        return [dict(r) for r in rows]

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    subscribers.add(ws)
    try:
        while True:
            await ws.receive_text()  # keepalive
    except WebSocketDisconnect:
        subscribers.discard(ws)
