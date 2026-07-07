"""
Context Preservation Utility
Handles context preservation across agent transitions
"""
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

class ContextPreserver:
    """
    Preserves and manages context across agent transitions
    to ensure seamless conversation flow
    """
    
    def __init__(self):
        self.context_stack: List[Dict[str, Any]] = []
        self.current_context: Optional[Dict[str, Any]] = None
        
    def save_context(self, agent_name: str, context_data: Dict[str, Any]) -> None:
        """
        Save context before transitioning to next agent
        
        Args:
            agent_name: Name of current agent
            context_data: Context to preserve
        """
        context_entry = {
            "agent": agent_name,
            "context": context_data,
            "timestamp": datetime.now().isoformat(),
            "preserved": True
        }
        
        if self.current_context:
            self.context_stack.append(self.current_context)
        
        self.current_context = context_entry
    
    def get_context(self, agent_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get context for a specific agent or current context
        
        Args:
            agent_name: Optional agent name to retrieve context for
            
        Returns:
            Context data or None
        """
        if agent_name and self.context_stack:
            for context in self.context_stack:
                if context.get("agent") == agent_name:
                    return context.get("context")
        
        return self.current_context.get("context") if self.current_context else None
    
    def restore_previous_context(self) -> Optional[Dict[str, Any]]:
        """
        Restore the previous context from stack
        
        Returns:
            Previous context or None
        """
        if self.context_stack:
            self.current_context = self.context_stack.pop()
            return self.current_context.get("context")
        return None
    
    def create_transition_context(
        self,
        from_agent: str,
        to_agent: str,
        user_data: Dict[str, Any],
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a complete context for agent transition
        
        Args:
            from_agent: Current agent
            to_agent: Target agent
            user_data: User information
            request_data: Request/incident data
            
        Returns:
            Complete transition context
        """
        return {
            "transition": {
                "from": from_agent,
                "to": to_agent,
                "timestamp": datetime.now().isoformat()
            },
            "user": user_data,
            "request": request_data,
            "history": [c.get("agent") for c in self.context_stack]
        }
    
    def clear(self) -> None:
        """Clear all preserved context"""
        self.context_stack.clear()
        self.current_context = None


class RequestTracker:
    """Tracks requests through the workflow"""
    
    def __init__(self):
        self.requests: Dict[str, Dict[str, Any]] = {}
        self.completed_requests: List[str] = []
        self.current_request_id: Optional[str] = None
    
    def create_request(
        self,
        request_id: str,
        request_type: str,
        user_id: str,
        request_data: Dict[str, Any]
    ) -> None:
        """Create a new request entry"""
        self.requests[request_id] = {
            "id": request_id,
            "type": request_type,
            "user_id": user_id,
            "data": request_data,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "agents_visited": [],
            "updates": []
        }
        self.current_request_id = request_id
    
    def add_agent_visit(self, request_id: str, agent_name: str) -> None:
        """Record an agent visit"""
        if request_id in self.requests:
            if agent_name not in self.requests[request_id]["agents_visited"]:
                self.requests[request_id]["agents_visited"].append(agent_name)
    
    def add_update(self, request_id: str, update_data: Dict[str, Any]) -> None:
        """Add an update to request"""
        if request_id in self.requests:
            self.requests[request_id]["updates"].append({
                "timestamp": datetime.now().isoformat(),
                "data": update_data
            })
    
    def mark_complete(self, request_id: str) -> None:
        """Mark request as completed"""
        if request_id in self.requests:
            self.requests[request_id]["status"] = "completed"
            self.requests[request_id]["completed_at"] = datetime.now().isoformat()
            self.completed_requests.append(request_id)
    
    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get request details"""
        return self.requests.get(request_id)
    
    def get_request_history(self, request_id: str) -> Dict[str, Any]:
        """Get complete request history"""
        request = self.requests.get(request_id)
        if request:
            return {
                "request_id": request_id,
                "type": request["type"],
                "status": request["status"],
                "agents_visited": request["agents_visited"],
                "updates": request["updates"],
                "timeline": {
                    "created": request.get("created_at"),
                    "completed": request.get("completed_at")
                }
            }
        return {}
    
    def clear(self) -> None:
        """Clear all requests"""
        self.requests.clear()
        self.completed_requests.clear()
        self.current_request_id = None


class ConversationFlow:
    """Manages the overall conversation flow and workflow"""
    
    def __init__(self):
        self.context_preserver = ContextPreserver()
        self.request_tracker = RequestTracker()
        self.workflow_complete = False
        self.multi_intent_count = 0
        self.completed_intents = 0
    
    def start_multi_intent_workflow(self, intent_count: int) -> None:
        """Initialize multi-intent workflow"""
        self.multi_intent_count = intent_count
        self.completed_intents = 0
        self.workflow_complete = False
    
    def complete_intent(self) -> None:
        """Mark one intent as completed"""
        self.completed_intents += 1
    
    def is_multi_intent_workflow_complete(self) -> bool:
        """Check if all intents are completed"""
        return self.completed_intents >= self.multi_intent_count
    
    def get_workflow_progress(self) -> Dict[str, Any]:
        """Get progress of current workflow"""
        return {
            "multi_intent": self.multi_intent_count > 1,
            "total_intents": self.multi_intent_count,
            "completed_intents": self.completed_intents,
            "progress_percentage": (self.completed_intents / max(self.multi_intent_count, 1)) * 100,
            "workflow_complete": self.is_multi_intent_workflow_complete()
        }
    
    def clear(self) -> None:
        """Clear workflow state"""
        self.context_preserver.clear()
        self.request_tracker.clear()
        self.workflow_complete = False
        self.multi_intent_count = 0
        self.completed_intents = 0


# Global instances
_context_preserver: Optional[ContextPreserver] = None
_request_tracker: Optional[RequestTracker] = None
_conversation_flow: Optional[ConversationFlow] = None


def get_context_preserver() -> ContextPreserver:
    """Get global context preserver instance"""
    global _context_preserver
    if _context_preserver is None:
        _context_preserver = ContextPreserver()
    return _context_preserver


def get_request_tracker() -> RequestTracker:
    """Get global request tracker instance"""
    global _request_tracker
    if _request_tracker is None:
        _request_tracker = RequestTracker()
    return _request_tracker


def get_conversation_flow() -> ConversationFlow:
    """Get global conversation flow instance"""
    global _conversation_flow
    if _conversation_flow is None:
        _conversation_flow = ConversationFlow()
    return _conversation_flow


def reset_context_preservation() -> None:
    """Reset all context preservation"""
    global _context_preserver, _request_tracker, _conversation_flow
    _context_preserver = ContextPreserver()
    _request_tracker = RequestTracker()
    _conversation_flow = ConversationFlow()
