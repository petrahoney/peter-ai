"""
workspace_service.py - Workspace & Team service logic
"""

from typing import Optional, List, Tuple
from backend.workspace_models import WorkspaceModel, TeamModel, ResourceShare
from backend.workspace_models import WorkspaceCreate, TeamCreate, TeamMemberAdd
from core.database_bridge import get_bridge

db = get_bridge()

class WorkspaceService:
    """Handle workspace & team operations"""
    
    def __init__(self):
        self.db = db
    
    # ===== WORKSPACE OPERATIONS =====
    
    async def create_workspace(self, workspace: WorkspaceCreate, user_id: str) -> Tuple[bool, str, Optional[dict]]:
        """Create new workspace"""
        ws = WorkspaceModel(workspace.name, user_id, workspace.description)
        
        try:
            await self.db.db.workspaces.insert_one(ws.to_dict())
            return True, "Workspace created", ws.to_response()
        except Exception as e:
            return False, f"Error creating workspace: {str(e)}", None
    
    async def get_workspace(self, workspace_id: str, user_id: str) -> Optional[dict]:
        """Get workspace (check if user has access)"""
        ws = await self.db.db.workspaces.find_one({"_id": workspace_id})
        
        if not ws:
            return None
        
        # Check access: owner or team member
        if ws['owner_id'] != user_id:
            # Check if user is in any team in this workspace
            team = await self.db.db.teams.find_one({
                "workspace_id": workspace_id,
                "members": {"$elemMatch": {"user_id": user_id}}
            })
            if not team:
                return None
        
        return ws
    
    async def list_user_workspaces(self, user_id: str) -> List[dict]:
        """List all workspaces user has access to"""
        # Own workspaces
        owned = await self.db.db.workspaces.find({"owner_id": user_id}).to_list(50)
        
        # Shared via teams
        teams = await self.db.db.teams.find({
            "members": {"$elemMatch": {"user_id": user_id}}
        }).to_list(50)
        
        workspace_ids = set([ws['_id'] for ws in owned])
        for team in teams:
            workspace_ids.add(team['workspace_id'])
        
        all_workspaces = list(owned)
        for ws_id in workspace_ids:
            if ws_id not in [w['_id'] for w in all_workspaces]:
                ws = await self.db.db.workspaces.find_one({"_id": ws_id})
                if ws:
                    all_workspaces.append(ws)
        
        return all_workspaces
    
    # ===== TEAM OPERATIONS =====
    
    async def create_team(self, team: TeamCreate, user_id: str) -> Tuple[bool, str, Optional[dict]]:
        """Create team in workspace"""
        # Check workspace access
        ws = await self.get_workspace(team.workspace_id, user_id)
        if not ws:
            return False, "Workspace not found or no access", None
        
        t = TeamModel(team.workspace_id, team.name, user_id, team.description)
        
        try:
            await self.db.db.teams.insert_one(t.to_dict())
            return True, "Team created", t.to_response()
        except Exception as e:
            return False, f"Error creating team: {str(e)}", None
    
    async def get_team(self, team_id: str, user_id: str) -> Optional[dict]:
        """Get team (check if user is member)"""
        team = await self.db.db.teams.find_one({"_id": team_id})
        
        if not team:
            return None
        
        # Check if user is member
        is_member = any(m['user_id'] == user_id for m in team.get('members', []))
        
        if not is_member:
            return None
        
        return team
    
    async def add_team_member(self, team_id: str, user_id: str, member_user_id: str, role: str = "member") -> Tuple[bool, str]:
        """Add member to team (must be team owner)"""
        team = await self.db.db.teams.find_one({"_id": team_id})
        
        if not team:
            return False, "Team not found"
        
        if team['owner_id'] != user_id:
            return False, "Only team owner can add members"
        
        # Check if already member
        if any(m['user_id'] == member_user_id for m in team.get('members', [])):
            return False, "User already in team"
        
        try:
            await self.db.db.teams.update_one(
                {"_id": team_id},
                {"$push": {"members": {"user_id": member_user_id, "role": role}}}
            )
            return True, "Member added"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    # ===== RESOURCE SHARING =====
    
    async def share_resource(self, resource_type: str, resource_id: str, 
                            shared_by: str, shared_with: str, permission: str = "view") -> Tuple[bool, str]:
        """Share resource with user or team"""
        share = ResourceShare(resource_type, resource_id, shared_by, shared_with, permission)
        
        try:
            await self.db.db.resource_shares.insert_one(share.to_dict())
            return True, "Resource shared"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    async def get_shared_resources(self, user_id: str, resource_type: str = None) -> List[dict]:
        """Get resources shared with user"""
        query = {"shared_with": user_id}
        if resource_type:
            query["resource_type"] = resource_type
        
        return await self.db.db.resource_shares.find(query).to_list(100)

# Global instance
_workspace_service: Optional[WorkspaceService] = None

def get_workspace_service() -> WorkspaceService:
    """Get workspace service"""
    global _workspace_service
    if _workspace_service is None:
        _workspace_service = WorkspaceService()
    return _workspace_service

def init_workspace_service() -> WorkspaceService:
    """Initialize workspace service"""
    global _workspace_service
    _workspace_service = WorkspaceService()
    return _workspace_service