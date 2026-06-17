"""
auth_models.py - User authentication models
"""

from datetime import datetime, timedelta
from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr

# ===== REQUEST/RESPONSE MODELS =====

class UserRegister(BaseModel):
    """User registration request"""
    email: str
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    """User login request"""
    email: str
    password: str

class UserResponse(BaseModel):
    """User response (no password)"""
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    created_at: str
    is_active: bool = True

class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ===== DATABASE MODELS =====

class UserModel:
    """User document for MongoDB"""
    
    def __init__(self, email: str, username: str, password_hash: str, full_name: str = None):
        self.id = str(uuid.uuid4())
        self.email = email
        self.username = username
        self.password_hash = password_hash
        self.full_name = full_name or ""
        self.is_active = True
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "_id": self.id,
            "email": self.email,
            "username": self.username,
            "password_hash": self.password_hash,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    def to_response(self):
        return UserResponse(
            id=self.id,
            email=self.email,
            username=self.username,
            full_name=self.full_name,
            created_at=self.created_at,
            is_active=self.is_active
        )

class SubscriptionModel:
    """Subscription/tier for user"""
    
    def __init__(self, user_id: str, tier: str = "free"):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.tier = tier  # free, pro, premium, enterprise
        self.status = "active"
        self.created_at = datetime.now().isoformat()
        self.expires_at = (datetime.now() + timedelta(days=365)).isoformat()
    
    def to_dict(self):
        return {
            "_id": self.id,
            "user_id": self.user_id,
            "tier": self.tier,
            "status": self.status,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
        }