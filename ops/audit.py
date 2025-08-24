# ops/audit.py
import json, time, os, aiofiles, hashlib

AUDIT_DIR = os.getenv("AUDIT_DIR","./audit")

async def append_audit(event: dict):
    os.makedirs(AUDIT_DIR, exist_ok=True)
    ts = int(time.time()*1000)
    fn = os.path.join(AUDIT_DIR, f"{ts}-{hashlib.sha1(json.dumps(event, sort_keys=True).encode()).hexdigest()}.jsonl")
    async with aiofiles.open(fn, "w") as f:
        await f.write(json.dumps(event, separators=(",",":"))+"\n")
