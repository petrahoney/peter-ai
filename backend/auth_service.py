"""
auth_service.py - Authentication service logic
"""

from typing import Optional, Tuple
from backend.auth_models import UserModel, SubscriptionModel, UserRegister, UserLogin
from backend.auth_utils import hash_password, verify_password, create_access_token, get_user_id_from_token
from core.database_bridge import get_bridge

db = get_bridge()

class AuthService:
    """Handle all authentication operations"""
    
    def __init__(self):
        self.db = db
    
    async def register_user(self, reg: UserRegister) -> Tuple[bool, str, Optional[UserModel]]:
        """Register new user"""
        
        # Check if user exists
        existing = await self.db.db.users.find_one({"email": reg.email})
        if existing:
            return False, "Email already registered", None
        
        existing_username = await self.db.db.users.find_one({"username": reg.username})
        if existing_username:
            return False, "Username already taken", None
        
        # Create user
        user = UserModel(
            email=reg.email,
            username=reg.username,
            password_hash=hash_password(reg.password),
            full_name=reg.full_name
        )
        
        # Save to DB
        await self.db.db.users.insert_one(user.to_dict())
        
        # Create free subscription
        sub = SubscriptionModel(user.id, tier="free")
        await self.db.db.subscriptions.insert_one(sub.to_dict())
        
        return True, "User registered successfully", user
    
    async def login_user(self, login: UserLogin) -> Tuple[bool, str, Optional[dict]]:
        """Login user and return token"""
        
        # Find user
        user_doc = await self.db.db.users.find_one({"email": login.email})
        if not user_doc:
            return False, "Invalid email or password", None
        
        # Verify password
        if not verify_password(login.password, user_doc['password_hash']):
            return False, "Invalid email or password", None
        
        # Check if active
        if not user_doc.get('is_active', True):
            return False, "User account is disabled", None
        
        # Create token
        token = create_access_token(user_doc['_id'], user_doc['email'])
        
        # Get subscription tier
        sub = await self.db.db.subscriptions.find_one({"user_id": user_doc['_id']})
        tier = sub.get('tier', 'free') if sub else 'free'
        
        return True, "Login successful", {
            "access_token": token,
            "user_id": user_doc['_id'],
            "email": user_doc['email'],
            "username": user_doc['username'],
            "tier": tier
        }
    
    async def verify_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """Verify token and return user_id"""
        user_id = get_user_id_from_token(token)
        if not user_id:
            return False, None
        
        # Check if user still exists and active
        user = await self.db.db.users.find_one({"_id": user_id})
        if not user or not user.get('is_active', True):
            return False, None
        
        return True, user_id
    
    async def get_user(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        return await self.db.db.users.find_one({"_id": user_id})
    
    async def get_user_subscription(self, user_id: str) -> Optional[dict]:
        """Get user subscription"""
        return await self.db.db.subscriptions.find_one({"user_id": user_id})

# Global instance
_auth_service: Optional[AuthService] = None

def get_auth_service() -> AuthService:
    """Get auth service"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service

def init_auth_service() -> AuthService:
    """Initialize auth service"""
    global _auth_service
    _auth_service = AuthService()
    return _auth_service