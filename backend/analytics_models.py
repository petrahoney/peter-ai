"""
analytics_models.py - Analytics & usage tracking models
"""

from typing import Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

class UsageMetric(BaseModel):
    """Usage metric request"""
    user_id: str
    workspace_id: str
    metric_type: str  # api_call, llm_query, chat_message
    value: float = 1.0
    metadata: Optional[dict] = None

class UsageResponse(BaseModel):
    """Usage response"""
    id: str
    user_id: str
    workspace_id: str
    metric_type: str
    value: float
    created_at: str

class UsageMetricModel:
    """Usage metric document"""
    
    def __init__(self, user_id: str, workspace_id: str, metric_type: str, value: float = 1.0, metadata: dict = None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.workspace_id = workspace_id
        self.metric_type = metric_type
        self.value = value
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "_id": self.id,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "metric_type": self.metric_type,
            "value": self.value,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

class UserStats:
    """User statistics aggregation"""
    
    def __init__(self, user_id: str):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.total_api_calls = 0
        self.total_llm_queries = 0
        self.total_chat_messages = 0
        self.total_cost = 0.0
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "_id": self.id,
            "user_id": self.user_id,
            "total_api_calls": self.total_api_calls,
            "total_llm_queries": self.total_llm_queries,
            "total_chat_messages": self.total_chat_messages,
            "total_cost": self.total_cost,
            "updated_at": self.updated_at,
        }

class WorkspaceStats:
    """Workspace statistics"""
    
    def __init__(self, workspace_id: str):
        self.id = str(uuid.uuid4())
        self.workspace_id = workspace_id
        self.member_count = 0
        self.total_messages = 0
        self.total_cost = 0.0
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "_id": self.id,
            "workspace_id": self.workspace_id,
            "member_count": self.member_count,
            "total_messages": self.total_messages,
            "total_cost": self.total_cost,
            "updated_at": self.updated_at,
        }