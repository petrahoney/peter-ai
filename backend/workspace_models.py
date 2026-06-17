"""
workspace_models.py - Workspace & Team models
"""

from typing import Optional, List
from pydantic import BaseModel
import uuid
from datetime import datetime

# ===== REQUEST/RESPONSE MODELS =====

class WorkspaceCreate(BaseModel):
    """Create workspace request"""
    name: str
    description: Optional[str] = None

class WorkspaceResponse(BaseModel):
    """Workspace response"""
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    created_at: str

class TeamCreate(BaseModel):
    """Create team request"""
    workspace_id: str
    name: str
    description: Optional[str] = None

class TeamResponse(BaseModel):
    """Team response"""
    id: str
    workspace_id: str
    name: str
    description: Optional[str]
    owner_id: str
    member_count: int
    created_at: str

class TeamMemberAdd(BaseModel):
    """Add team member request"""
    team_id: str
    user_id: str
    role: str = "member"  # owner, admin, member, guest

# ===== DATABASE MODELS =====

class WorkspaceModel:
    """Workspace document"""
    
    def __init__(self, name: str, owner_id: str, description: str = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description or ""
        self.owner_id = owner_id
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "_id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    def to_response(self):
        return WorkspaceResponse(
            id=self.id,
            name=self.name,
            description=self.description,
            owner_id=self.owner_id,
            created_at=self.created_at
        )

class TeamModel:
    """Team document"""
    
    def __init__(self, workspace_id: str, name: str, owner_id: str, description: str = None):
        self.id = str(uuid.uuid4())
        self.workspace_id = workspace_id
        self.name = name
        self.description = description or ""
        self.owner_id = owner_id
        self.members = [{"user_id": owner_id, "role": "owner"}]
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "_id": self.id,
            "workspace_id": self.workspace_id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "members": self.members,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    def to_response(self):
        return TeamResponse(
            id=self.id,
            workspace_id=self.workspace_id,
            name=self.name,
            description=self.description,
            owner_id=self.owner_id,
            member_count=len(self.members),
            created_at=self.created_at
        )

class ResourceShare:
    """Resource sharing model"""
    
    def __init__(self, resource_type: str, resource_id: str, shared_by: str, shared_with: str, permission: str = "view"):
        self.id = str(uuid.uuid4())
        self.resource_type = resource_type  # session, memory, script
        self.resource_id = resource_id
        self.shared_by = shared_by
        self.shared_with = shared_with  # user_id or team_id
        self.permission = permission  # view, edit, admin
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "_id": self.id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "shared_by": self.shared_by,
            "shared_with": self.shared_with,
            "permission": self.permission,
            "created_at": self.created_at,
        }