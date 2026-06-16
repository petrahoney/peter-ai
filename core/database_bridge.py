"""
database_bridge.py
Dual-persistence layer: File-based (v2.3) + MongoDB (v4.0)
"""

import json
import os
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)

class DataBridge:
    """Manages dual persistence to file system and MongoDB"""
    
    def __init__(self, mongo_url: Optional[str] = None):
        self.sessions_dir = Path("data/sessions")
        self.messages_dir = Path("data/messages")
        self.memories_dir = Path("data/memories")
        
        for d in [self.sessions_dir, self.messages_dir, self.memories_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        self.mongo_ready = False
        self.mongo_url = mongo_url
        self.mongo_client = None
        self.db = None
        
        if mongo_url:
            try:
                self.mongo_client = AsyncIOMotorClient(mongo_url)
                self.db_name = "peter_ai_dev"
                self.db = self.mongo_client[self.db_name]
                self.mongo_ready = True
                logger.info("✅ MongoDB bridge initialized")
            except Exception as e:
                logger.warning(f"⚠️ MongoDB initialization failed: {e}")
                self.mongo_ready = False
    
    async def save_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Save session to file + MongoDB"""
        success = False
        
        try:
            session_file = self.sessions_dir / f"{session_id}.json"
            with open(session_file, 'w') as f:
                json.dump({**data, "_saved_at": datetime.now().isoformat()}, f, indent=2)
            success = True
            logger.debug(f"📄 Session saved to file: {session_id}")
        except Exception as e:
            logger.error(f"❌ File save failed: {e}")
        
        if self.mongo_ready:
            try:
                await self.db.sessions.insert_one({
                    "_id": session_id,
                    **data,
                    "created_at": datetime.now().isoformat()
                })
                logger.debug(f"🔵 Session saved to MongoDB: {session_id}")
            except Exception as e:
                logger.warning(f"⚠️ MongoDB save failed: {e}")
        
        return success
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session from MongoDB or file"""
        if self.mongo_ready:
            try:
                doc = await self.db.sessions.find_one({"_id": session_id})
                if doc:
                    return doc
            except Exception as e:
                logger.warning(f"⚠️ MongoDB read failed: {e}")
        
        session_file = self.sessions_dir / f"{session_id}.json"
        if session_file.exists():
            try:
                with open(session_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ File read failed: {e}")
        
        return None
    
    async def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent sessions"""
        if self.mongo_ready:
            try:
                sessions = []
                async for doc in self.db.sessions.find().sort("created_at", -1).limit(limit):
                    sessions.append(doc)
                return sessions
            except Exception as e:
                logger.warning(f"⚠️ MongoDB list failed: {e}")
        
        sessions = []
        for f in sorted(self.sessions_dir.glob("*.json"), 
                       key=lambda x: x.stat().st_mtime, 
                       reverse=True)[:limit]:
            try:
                with open(f, 'r') as file:
                    sessions.append(json.load(file))
            except:
                pass
        return sessions
    
    async def save_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """Save message to file + MongoDB"""
        success = False
        
        try:
            msg_dir = self.messages_dir / session_id
            msg_dir.mkdir(parents=True, exist_ok=True)
            msg_file = msg_dir / f"{message.get('id', 'unknown')}.json"
            with open(msg_file, 'w') as f:
                json.dump({**message, "_saved_at": datetime.now().isoformat()}, f, indent=2)
            success = True
            logger.debug(f"📄 Message saved to file: {message.get('id')}")
        except Exception as e:
            logger.error(f"❌ Message file save failed: {e}")
        
        if self.mongo_ready:
            try:
                await self.db.messages.insert_one({
                    "_id": message.get("id"),
                    "session_id": session_id,
                    **message,
                    "created_at": datetime.now().isoformat()
                })
                logger.debug(f"🔵 Message saved to MongoDB: {message.get('id')}")
            except Exception as e:
                logger.warning(f"⚠️ MongoDB message save failed: {e}")
        
        return success
    
    async def get_messages(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages for a session"""
        if self.mongo_ready:
            try:
                messages = []
                async for doc in self.db.messages.find(
                    {"session_id": session_id}
                ).sort("created_at", 1).limit(limit):
                    messages.append(doc)
                return messages
            except Exception as e:
                logger.warning(f"⚠️ MongoDB messages read failed: {e}")
        
        messages = []
        msg_dir = self.messages_dir / session_id
        if msg_dir.exists():
            for f in sorted(msg_dir.glob("*.json")):
                try:
                    with open(f, 'r') as file:
                        messages.append(json.load(file))
                except:
                    pass
        return messages[:limit]
    
    async def save_memory(self, memory: Dict[str, Any]) -> bool:
        """Save memory"""
        success = False
        
        try:
            mem_file = self.memories_dir / f"{memory.get('id', 'unknown')}.json"
            with open(mem_file, 'w') as f:
                json.dump(memory, f, indent=2)
            success = True
        except Exception as e:
            logger.error(f"❌ Memory file save failed: {e}")
        
        if self.mongo_ready:
            try:
                await self.db.memories.insert_one(memory)
            except Exception as e:
                logger.warning(f"⚠️ MongoDB memory save failed: {e}")
        
        return success
    
    async def health_check(self) -> Dict[str, Any]:
        """Check bridge health status"""
        mongo_ok = False
        file_ok = Path(self.sessions_dir).exists()
        
        if self.mongo_ready:
            try:
                await self.db.command("ping")
                mongo_ok = True
            except:
                mongo_ok = False
        
        if mongo_ok and file_ok:
            status = "healthy"
        elif mongo_ok or file_ok:
            status = "degraded"
        else:
            status = "critical"
        
        return {
            "mongo": mongo_ok,
            "file": file_ok,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }

def get_bridge() -> DataBridge:
    """Get global bridge instance"""
    from dotenv import load_dotenv
    load_dotenv('.env.production')
    mongo_url = os.getenv("MONGO_URL")
    return DataBridge(mongo_url=mongo_url)

def init_bridge(mongo_url: Optional[str] = None) -> DataBridge:
    """Initialize bridge at startup"""
    return DataBridge(mongo_url=mongo_url)