# api/obs.py
import time, uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter

HTTP_REQS = Counter("http_requests_total", "HTTP requests", ["method","path","code"])
HTTP_LATENCY = Histogram("http_request_seconds", "Latency", ["method","path"])
WS_CONN = Counter("ws_connections_total", "WebSocket connections", ["endpoint"])

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start = time.perf_counter()
        cid = request.headers.get("x-correlation-id") or str(uuid.uuid4())
        request.state.correlation_id = cid
        response: Response = await call_next(request)
        dur = time.perf_counter() - start
        HTTP_REQS.labels(request.method, request.url.path, response.status_code).inc()
        HTTP_LATENCY.labels(request.method, request.url.path).observe(dur)
        response.headers["x-correlation-id"] = cid
        return response

router = APIRouter()

@router.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
