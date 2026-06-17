"""
notification_models.py - Notification models
"""

from typing import Optional
from pydantic import BaseModel
import uuid
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    """Notification types"""
    WELCOME = "welcome"
    TEAM_INVITE = "team_invite"
    WORKSPACE_INVITE = "workspace_invite"
    USAGE_ALERT = "usage_alert"
    PAYMENT = "payment"
    SYSTEM = "system"

class NotificationCreate(BaseModel):
    """Create notification request"""
    user_id: str
    notification_type: NotificationType
    title: str
    message: str
    metadata: Optional[dict] = None
    send_email: bool = False

class NotificationResponse(BaseModel):
    """Notification response"""
    id: str
    user_id: str
    notification_type: str
    title: str
    message: str
    is_read: bool
    created_at: str

class NotificationModel:
    """Notification document"""
    
    def __init__(self, user_id: str, notification_type: str, title: str, message: str, metadata: dict = None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.notification_type = notification_type
        self.title = title
        self.message = message
        self.metadata = metadata or {}
        self.is_read = False
        self.created_at = datetime.now().isoformat()
        self.read_at = None
    
    def to_dict(self):
        return {
            "_id": self.id,
            "user_id": self.user_id,
            "notification_type": self.notification_type,
            "title": self.title,
            "message": self.message,
            "metadata": self.metadata,
            "is_read": self.is_read,
            "created_at": self.created_at,
            "read_at": self.read_at,
        }
    
    def to_response(self):
        return NotificationResponse(
            id=self.id,
            user_id=self.user_id,
            notification_type=self.notification_type,
            title=self.title,
            message=self.message,
            is_read=self.is_read,
            created_at=self.created_at
        )