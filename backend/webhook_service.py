"""
webhook_service.py - Webhook service
"""

from typing import Optional, List, Tuple
import httpx
import asyncio
from backend.webhook_models import WebhookModel, WebhookCreate, WebhookLog
from core.database_bridge import get_bridge

db = get_bridge()

class WebhookService:
    """Handle webhooks"""
    
    def __init__(self):
        self.db = db
    
    async def create_webhook(self, webhook: WebhookCreate, user_id: str) -> Tuple[bool, str, Optional[dict]]:
        """Create webhook"""
        w = WebhookModel(webhook.workspace_id, webhook.url, webhook.events)
        
        try:
            await self.db.db.webhooks.insert_one(w.to_dict())
            return True, "Webhook created", w.to_response()
        except Exception as e:
            return False, f"Error: {str(e)}", None
    
    async def get_workspace_webhooks(self, workspace_id: str) -> List[dict]:
        """Get webhooks for workspace"""
        return await self.db.db.webhooks.find(
            {"workspace_id": workspace_id}
        ).to_list(100)
    
    async def trigger_webhook(self, event: str, workspace_id: str, data: dict) -> Tuple[bool, str]:
        """Trigger webhooks for event"""
        webhooks = await self.db.db.webhooks.find({
            "workspace_id": workspace_id,
            "events": event,
            "active": True
        }).to_list(100)
        
        for webhook in webhooks:
            asyncio.create_task(self._send_webhook(webhook, event, data))
        
        return True, f"Triggered {len(webhooks)} webhooks"
    
    async def _send_webhook(self, webhook: dict, event: str, data: dict):
        """Send webhook (async)"""
        import time
        start_time = time.time()
        
        payload = {
            "event": event,
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "data": data
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(webhook['url'], json=payload)
                response_time = time.time() - start_time
                
                # Log delivery
                log = WebhookLog(webhook['_id'], event, response.status_code, response_time)
                await self.db.db.webhook_logs.insert_one(log.to_dict())
                
                # Update webhook stats
                await self.db.db.webhooks.update_one(
                    {"_id": webhook['_id']},
                    {
                        "$set": {"last_triggered": __import__('datetime').datetime.now().isoformat()},
                        "$inc": {"trigger_count": 1}
                    }
                )
        except Exception as e:
            # Log error
            log = WebhookLog(webhook['_id'], event, 0, 0)
            await self.db.db.webhook_logs.insert_one(log.to_dict())
    
    async def get_webhook_logs(self, webhook_id: str, limit: int = 100) -> List[dict]:
        """Get webhook delivery logs"""
        return await self.db.db.webhook_logs.find(
            {"webhook_id": webhook_id}
        ).sort("created_at", -1).to_list(limit)
    
    async def test_webhook(self, webhook_id: str) -> Tuple[bool, str]:
        """Test webhook delivery"""
        webhook = await self.db.db.webhooks.find_one({"_id": webhook_id})
        
        if not webhook:
            return False, "Webhook not found"
        
        test_data = {
            "test": True,
            "message": "This is a test webhook"
        }
        
        success, message = await self._send_webhook(webhook, "test.event", test_data)
        
        return True, "Test webhook sent"

# Global instance
_webhook_service: Optional[WebhookService] = None

def get_webhook_service() -> WebhookService:
    """Get webhook service"""
    global _webhook_service
    if _webhook_service is None:
        _webhook_service = WebhookService()
    return _webhook_service

def init_webhook_service() -> WebhookService:
    """Initialize webhook service"""
    global _webhook_service
    _webhook_service = WebhookService()
    return _webhook_service