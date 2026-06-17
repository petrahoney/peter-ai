"""
webhook_models.py - Webhook models
"""

from typing import Optional, List
from pydantic import BaseModel
import uuid
from datetime import datetime
from enum import Enum

class WebhookEvent(str, Enum):
    """Webhook event types"""
    USER_CREATED = "user.created"
    WORKSPACE_CREATED = "workspace.created"
    TEAM_CREATED = "team.created"
    MESSAGE_SENT = "message.sent"
    QUERY_COMPLETED = "query.completed"

class WebhookCreate(BaseModel):
    """Create webhook request"""
    workspace_id: str
    url: str
    events: List[str]
    active: bool = True

class WebhookResponse(BaseModel):
    """Webhook response"""
    id: str
    workspace_id: str
    url: str
    events: List[str]
    active: bool
    created_at: str

class WebhookModel:
    """Webhook document"""
    
    def __init__(self, workspace_id: str, url: str, events: List[str]):
        self.id = str(uuid.uuid4())
        self.workspace_id = workspace_id
        self.url = url
        self.events = events
        self.active = True
        self.secret = str(uuid.uuid4())
        self.created_at = datetime.now().isoformat()
        self.last_triggered = None
        self.trigger_count = 0
    
    def to_dict(self):
        return {
            "_id": self.id,
            "workspace_id": self.workspace_id,
            "url": self.url,
            "events": self.events,
            "active": self.active,
            "secret": self.secret,
            "created_at": self.created_at,
            "last_triggered": self.last_triggered,
            "trigger_count": self.trigger_count,
        }
    
    def to_response(self):
        return WebhookResponse(
            id=self.id,
            workspace_id=self.workspace_id,
            url=self.url,
            events=self.events,
            active=self.active,
            created_at=self.created_at
        )

class WebhookLog:
    """Webhook delivery log"""
    
    def __init__(self, webhook_id: str, event: str, status_code: int, response_time: float):
        self.id = str(uuid.uuid4())
        self.webhook_id = webhook_id
        self.event = event
        self.status_code = status_code
        self.response_time = response_time
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "_id": self.id,
            "webhook_id": self.webhook_id,
            "event": self.event,
            "status_code": self.status_code,
            "response_time": self.response_time,
            "created_at": self.created_at,
        }