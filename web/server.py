"""
web/server.py
FastAPI WebSocket Dashboard Server
"""

import sys
import os
sys.path.append("C:\\peter-ai")

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import asyncio
import json
from datetime import datetime
from config import DASHBOARD_PORT, USER_NAME

app = FastAPI(title="PETER AI Dashboard")


# ── WebSocket Manager ─────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, message: dict):
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


# ── Routes ───────────────────────────────────────
@app.get("/")
async def dashboard():
    html_path = "C:\\peter-ai\\web\\dashboard.html"
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return HTMLResponse("<h1>PETER AI Dashboard</h1><p>dashboard.html tidak ditemukan</p>")


@app.get("/api/status")
async def get_status():
    return {
        "status"   : "online",
        "user"     : USER_NAME,
        "time"     : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version"  : "2.0"
    }


@app.get("/api/files")
async def get_files():
    output_dir = "C:\\peter-ai\\data\\outputs"
    files = []
    if os.path.exists(output_dir):
        for f in os.listdir(output_dir):
            path = os.path.join(output_dir, f)
            files.append({
                "name": f,
                "size": os.path.getsize(path),
                "date": datetime.fromtimestamp(
                    os.path.getmtime(path)
                ).strftime("%Y-%m-%d %H:%M")
            })
    return {"files": files}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    await websocket.send_json({
        "type"   : "connected",
        "message": f"PETER AI Dashboard terhubung — Halo {USER_NAME}!"
    })
    try:
        while True:
            data = await websocket.receive_text()
            msg  = json.loads(data)

            if msg.get("type") == "chat":
                # Proses pesan chat
                from core.brain import PeterBrain
                brain    = PeterBrain()
                response = brain.think(msg.get("message", ""))
                await manager.broadcast({
                    "type"   : "response",
                    "message": response,
                    "time"   : datetime.now().strftime("%H:%M:%S")
                })

            elif msg.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)


def start_server():
    """Jalankan dashboard server"""
    import uvicorn
    print(f"\n[DASHBOARD] Server berjalan di http://localhost:{DASHBOARD_PORT}")
    print(f"[DASHBOARD] Buka browser dan akses URL di atas")
    uvicorn.run(
        app,
        host = "0.0.0.0",
        port = DASHBOARD_PORT,
        log_level = "warning"
    )


if __name__ == "__main__":
    start_server()