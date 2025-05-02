#!/usr/bin/env python3
# calvin_core/main.py

import os
import sys
import logging
import threading
import importlib.util
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
import uvicorn

# ─── CONFIG ────────────────────────────────────────────────────────────────────
HOST      = os.getenv("CALVIN_CORE_HOST", "0.0.0.0")
PORT      = int(os.getenv("CALVIN_CORE_PORT", 8000))
API_TOKEN = os.getenv("CALVIN_CORE_TOKEN", "changeme")  # change in production

# ─── LOGGING ───────────────────────────────────────────────────────────────────
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.info("Logging initialized.")

# ─── MEMORY STORE (stub) ───────────────────────────────────────────────────────
class MemoryStore:
    def __init__(self):
        self.logs = []

    def log(self, tag: str, data: Any):
        entry = {"tag": tag, "data": data}
        self.logs.append(entry)
        logging.debug(f"Memory log: {entry}")

memory = MemoryStore()

# ─── PLUGIN LOADER (stub) ──────────────────────────────────────────────────────
plugins: Dict[str, Any] = {}

def load_plugins():
    plugins_dir = Path(__file__).parent.parent / "plugins"
    logging.info(f"🔍 Loading plugins from {plugins_dir}")
    if not plugins_dir.exists():
        logging.warning("No plugins/ folder found.")
        return

    for file in plugins_dir.glob("*.py"):
        if file.stem.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(file.stem, str(file))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore
            plugins[file.stem] = module
            logging.info(f"✅ Loaded plugin: {file.stem}")
        except Exception as e:
            logging.error(f"❌ Failed to load plugin {file.stem}: {e}")

# ─── NODE REGISTRY (stub) ──────────────────────────────────────────────────────
nodes: Dict[str, Dict[str, Any]] = {}

# ─── Pydantic Models ───────────────────────────────────────────────────────────
class CommandRequest(BaseModel):
    cmd: str

class NodeRegistration(BaseModel):
    node_id: str
    info: Dict[str, Any] = {}

# ─── FASTAPI APP ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Calvin Core",
    description="Modular, local-first AI core with plugin & node orchestration",
    version="0.1.0"
)

# ─── SECURITY DEPENDENCY ───────────────────────────────────────────────────────
async def verify_token(request: Request):
    token = request.headers.get("X-API-Token", "")
    if token != API_TOKEN:
        logging.warning("Invalid API token attempt.")
        raise HTTPException(status_code=401, detail="Invalid API Token")

# ─── STARTUP EVENT ─────────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    setup_logging()
    logging.info("🛠️  Calvin Core booting up…")
    load_plugins()
    logging.info(f"🔗 {len(plugins)} plugin(s) loaded.")
    logging.info("🚀 Startup complete. API docs at /docs")

# ─── ROUTES ────────────────────────────────────────────────────────────────────
@app.get("/status", dependencies=[Depends(verify_token)])
async def status():
    return {
        "status": "running",
        "nodes_connected": len(nodes),
        "plugins_loaded": list(plugins.keys()),
    }

@app.post("/command", dependencies=[Depends(verify_token)])
async def command(req: CommandRequest):
    logging.info(f"📥 API command received: {req.cmd}")
    memory.log("command", req.cmd)
    # TODO: dispatch to plugin or internal handler
    result = f"Processed: {req.cmd}"
    return {"result": result}

@app.post("/node_sync", dependencies=[Depends(verify_token)])
async def node_sync(reg: NodeRegistration):
    logging.info(f"📡 Node registered: {reg.node_id} → {reg.info}")
    nodes[reg.node_id] = reg.info
    return {"status": "ok", "node_id": reg.node_id}

# ─── CLI OVERRIDE LOOP ─────────────────────────────────────────────────────────
def start_cli_loop():
    logging.info("🖥️  Entering CLI loop. Type 'exit' or 'quit' to stop.")
    try:
        while True:
            cmd = input("Calvin> ").strip()
            if cmd.lower() in ("exit", "quit"):
                logging.info("🛑 CLI requested shutdown.")
                break
            logging.info(f"🖱️  CLI command: {cmd}")
            # TODO: dispatch to core logic
    except (EOFError, KeyboardInterrupt):
        logging.info("🛑 CLI interrupted.")
    finally:
        sys.exit(0)

# ─── MAIN ENTRY ────────────────────────────────────────────────────────────────
def main():
    # Run FastAPI/uvicorn in background
    server = threading.Thread(
        target=lambda: uvicorn.run(app, host=HOST, port=PORT, log_level="info"),
        daemon=True
    )
    server.start()
    logging.info(f"🔌 Server thread started on {HOST}:{PORT}")
    # Hand control to CLI
    start_cli_loop()

if __name__ == "__main__":
    main()
