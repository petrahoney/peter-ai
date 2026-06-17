"""
analytics_service.py - Analytics & reporting service
"""

from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, timedelta
from backend.analytics_models import UsageMetricModel, UsageMetric, UserStats, WorkspaceStats
from core.database_bridge import get_bridge

db = get_bridge()

class AnalyticsService:
    """Track and report analytics"""
    
    def __init__(self):
        self.db = db
    
    async def track_usage(self, metric: UsageMetric) -> Tuple[bool, str]:
        """Track user usage metric"""
        try:
            m = UsageMetricModel(metric.user_id, metric.workspace_id, metric.metric_type, metric.value, metric.metadata)
            await self.db.db.usage_metrics.insert_one(m.to_dict())
            return True, "Metric tracked"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    async def get_user_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user statistics"""
        try:
            # Get or create stats
            stats = await self.db.db.user_stats.find_one({"user_id": user_id})
            
            if not stats:
                # Create new stats
                s = UserStats(user_id)
                await self.db.db.user_stats.insert_one(s.to_dict())
                stats = s.to_dict()
            
            # Get last 30 days metrics
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            metrics = await self.db.db.usage_metrics.find({
                "user_id": user_id,
                "created_at": {"$gte": thirty_days_ago}
            }).to_list(1000)
            
            # Calculate totals
            api_calls = sum(1 for m in metrics if m['metric_type'] == 'api_call')
            llm_queries = sum(1 for m in metrics if m['metric_type'] == 'llm_query')
            chat_messages = sum(1 for m in metrics if m['metric_type'] == 'chat_message')
            total_cost = sum(m.get('metadata', {}).get('cost', 0) for m in metrics)
            
            return {
                "user_id": user_id,
                "api_calls_30d": api_calls,
                "llm_queries_30d": llm_queries,
                "chat_messages_30d": chat_messages,
                "total_cost_30d": total_cost,
                "stats": stats
            }
        except Exception as e:
            return None
    
    async def get_workspace_stats(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace statistics"""
        try:
            # Get or create stats
            stats = await self.db.db.workspace_stats.find_one({"workspace_id": workspace_id})
            
            if not stats:
                s = WorkspaceStats(workspace_id)
                await self.db.db.workspace_stats.insert_one(s.to_dict())
                stats = s.to_dict()
            
            # Get team members
            teams = await self.db.db.teams.find({"workspace_id": workspace_id}).to_list(100)
            member_ids = set()
            for team in teams:
                for member in team.get('members', []):
                    member_ids.add(member['user_id'])
            
            # Get workspace metrics
            metrics = await self.db.db.usage_metrics.find({
                "workspace_id": workspace_id
            }).to_list(1000)
            
            return {
                "workspace_id": workspace_id,
                "member_count": len(member_ids),
                "team_count": len(teams),
                "total_messages": sum(1 for m in metrics if m['metric_type'] == 'chat_message'),
                "total_cost": sum(m.get('metadata', {}).get('cost', 0) for m in metrics),
                "stats": stats
            }
        except Exception as e:
            return None
    
    async def get_daily_stats(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily breakdown for last N days"""
        daily_stats = {}
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).date()
            date_str = date.isoformat()
            daily_stats[date_str] = {
                "date": date_str,
                "api_calls": 0,
                "llm_queries": 0,
                "messages": 0,
                "cost": 0.0
            }
        
        # Get metrics for period
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        metrics = await self.db.db.usage_metrics.find({
            "user_id": user_id,
            "created_at": {"$gte": start_date}
        }).to_list(5000)
        
        # Aggregate by day
        for metric in metrics:
            date_str = metric['created_at'][:10]
            if date_str in daily_stats:
                if metric['metric_type'] == 'api_call':
                    daily_stats[date_str]['api_calls'] += 1
                elif metric['metric_type'] == 'llm_query':
                    daily_stats[date_str]['llm_queries'] += 1
                elif metric['metric_type'] == 'chat_message':
                    daily_stats[date_str]['messages'] += 1
                
                daily_stats[date_str]['cost'] += metric.get('metadata', {}).get('cost', 0)
        
        return list(daily_stats.values())

# Global instance
_analytics_service: Optional[AnalyticsService] = None

def get_analytics_service() -> AnalyticsService:
    """Get analytics service"""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service

def init_analytics_service() -> AnalyticsService:
    """Initialize analytics service"""
    global _analytics_service
    _analytics_service = AnalyticsService()
    return _analytics_service