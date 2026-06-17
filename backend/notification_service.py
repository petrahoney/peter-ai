"""
notification_service.py - Notification service
"""

from typing import Optional, List, Tuple
from backend.notification_models import NotificationModel, NotificationCreate
from backend.email_service import get_email_service
from core.database_bridge import get_bridge

db = get_bridge()
email = get_email_service()

class NotificationService:
    """Handle notifications"""
    
    def __init__(self):
        self.db = db
        self.email = email
    
    async def create_notification(self, notification: NotificationCreate) -> Tuple[bool, str, Optional[dict]]:
        """Create notification"""
        n = NotificationModel(
            notification.user_id,
            notification.notification_type,
            notification.title,
            notification.message,
            notification.metadata
        )
        
        try:
            await self.db.db.notifications.insert_one(n.to_dict())
            
            # Send email if requested
            if notification.send_email:
                user = await self.db.db.users.find_one({"_id": notification.user_id})
                if user:
                    await self.email.send_email(
                        user['email'],
                        notification.title,
                        f"<p>{notification.message}</p>"
                    )
            
            return True, "Notification created", n.to_response()
        except Exception as e:
            return False, f"Error: {str(e)}", None
    
    async def get_notifications(self, user_id: str, limit: int = 50) -> List[dict]:
        """Get user notifications (unread first)"""
        return await self.db.db.notifications.find(
            {"user_id": user_id}
        ).sort([("is_read", 1), ("created_at", -1)]).to_list(limit)
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> Tuple[bool, str]:
        """Mark notification as read"""
        try:
            result = await self.db.db.notifications.update_one(
                {"_id": notification_id, "user_id": user_id},
                {"$set": {"is_read": True, "read_at": __import__('datetime').datetime.now().isoformat()}}
            )
            
            if result.modified_count == 0:
                return False, "Notification not found"
            
            return True, "Marked as read"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    async def mark_all_as_read(self, user_id: str) -> Tuple[bool, str]:
        """Mark all notifications as read"""
        try:
            await self.db.db.notifications.update_many(
                {"user_id": user_id, "is_read": False},
                {"$set": {"is_read": True, "read_at": __import__('datetime').datetime.now().isoformat()}}
            )
            return True, "All notifications marked as read"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications"""
        return await self.db.db.notifications.count_documents(
            {"user_id": user_id, "is_read": False}
        )

# Global instance
_notification_service: Optional[NotificationService] = None

def get_notification_service() -> NotificationService:
    """Get notification service"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service

def init_notification_service() -> NotificationService:
    """Initialize notification service"""
    global _notification_service
    _notification_service = NotificationService()
    return _notification_service