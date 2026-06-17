import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio, json, uuid
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('.env.production')

PORT = int(os.getenv("DASHBOARD_PORT", "9000"))
HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
USER_NAME = os.getenv("USER_NAME", "Tjerlang")

from core.database_bridge import init_bridge
from backend.ai_router import get_router
from backend.llm_client import get_llm_client

db = init_bridge(mongo_url=os.getenv("MONGO_URL"))
router = get_router()
llm = get_llm_client()

app = FastAPI(title="PETER AI Bridge", version="2.3-v4.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Manager:
    def __init__(self):
        self.active = []
    async def connect(self, ws): 
        await ws.accept()
        self.active.append(ws)
    def disconnect(self, ws): 
        self.active.remove(ws) if ws in self.active else None
    async def broadcast(self, msg): 
        for ws in self.active:
            try: await ws.send_json(msg)
            except: pass

manager = Manager()

@app.get("/")
async def home():
    html = Path("web/dashboard.html")
    return FileResponse(html) if html.exists() else HTMLResponse("<h1>PETER AI</h1>")

@app.get("/api/health")
async def health():
    return await db.health_check()

@app.get("/api/status")
async def status():
    health = await db.health_check()
    return {"status": "online", "user": USER_NAME, "version": "2.3-v4.0", "database": health}

@app.get("/api/sessions")
async def list_sessions():
    sessions = await db.list_sessions(50)
    return {"count": len(sessions), "sessions": [{"id": s.get("id") or s.get("_id"), "user": s.get("user"), "created_at": s.get("created_at")} for s in sessions]}

@app.get("/api/sessions/{sid}/messages")
async def get_messages(sid: str):
    msgs = await db.get_messages(sid, 100)
    return {"session_id": sid, "count": len(msgs), "messages": [{"id": m.get("id") or m.get("_id"), "role": m.get("role"), "content": m.get("content"), "created_at": m.get("created_at")} for m in msgs]}

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await manager.connect(ws)
    sid = str(uuid.uuid4())
    
    await db.save_session(sid, {"id": sid, "user": USER_NAME, "created_at": datetime.now().isoformat(), "version": "2.3-v4.0"})
    await ws.send_json({"type": "connected", "message": f"Halo {USER_NAME}! PETER AI siap.", "session_id": sid})
    
    try:
        while True:
            data = json.loads(await ws.receive_text())
            if data.get("type") == "chat":
                user_msg_id = str(uuid.uuid4())
                query = data.get("message", "")
                
                await db.save_message(sid, {"id": user_msg_id, "role": "user", "content": query, "created_at": datetime.now().isoformat()})
                
                try:
                    # Route query
                    route_info = router.route_query(query)
                    tier = route_info['tier']
                    model = route_info['model']
                    provider = route_info['provider']
                    
                    # Call LLM
                    llm_result = await llm.call(provider, query, max_tokens=200)
                    
                    # Calculate cost
                    input_tokens = llm_result.get('input_tokens', len(query.split()))
                    output_tokens = llm_result.get('output_tokens', 50)
                    cost = router.calculate_cost(router.classify_query(query), input_tokens, output_tokens)
                    
                    # Format response
                    if llm_result['success']:
                        response = f"[{tier.upper()} | {model}]\n{llm_result['response']}\n\n💰 Cost: ${cost['total_cost']:.6f}"
                    else:
                        response = f"[{tier.upper()} | {model}]\n{llm_result['response']}\n💰 Cost: ${cost['total_cost']:.6f}"
                
                except Exception as e:
                    response = f"Error: {str(e)}"
                
                ai_msg_id = str(uuid.uuid4())
                await db.save_message(sid, {"id": ai_msg_id, "role": "assistant", "content": response, "created_at": datetime.now().isoformat()})
                
                await manager.broadcast({"type": "response", "message": response, "time": datetime.now().strftime("%H:%M:%S"), "message_id": ai_msg_id, "session_id": sid})
            
            elif data.get("type") == "ping":
                await ws.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(ws)

if __name__ == "__main__":
    import uvicorn
    print(f"\n{'='*60}\n🚀 PETER AI v2.3-v4.0 (Bridge + AIRouter + LLM)\n{'='*60}\n📍 http://{HOST}:{PORT}\n{'='*60}\n")
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")