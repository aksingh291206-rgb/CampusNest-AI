# state/session_state.py
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

class ConversationContext:
    """Tracks conversation context and history"""
    def __init__(self):
        self.intents: List[Dict[str, Any]] = []
        self.current_request: Optional[Dict[str, Any]] = None
        self.previous_requests: List[Dict[str, Any]] = []
        self.conversation_start_time: datetime = datetime.now()
        self.last_interaction_time: datetime = datetime.now()
        self.agent_history: List[str] = []
        
    def add_intent(self, intent: Dict[str, Any]) -> None:
        """Add a new intent to the conversation"""
        self.intents.append({
            **intent,
            'timestamp': datetime.now().isoformat()
        })
        self.last_interaction_time = datetime.now()
    
    def set_current_request(self, request: Dict[str, Any]) -> None:
        """Set the current request being processed"""
        if self.current_request:
            self.previous_requests.append(self.current_request)
        self.current_request = {
            **request,
            'timestamp': datetime.now().isoformat()
        }
        self.last_interaction_time = datetime.now()
    
    def add_agent_visit(self, agent_name: str) -> None:
        """Track which agents were visited"""
        self.agent_history.append(agent_name)
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of conversation context"""
        return {
            'total_intents': len(self.intents),
            'current_request': self.current_request,
            'previous_requests': self.previous_requests,
            'agent_history': self.agent_history,
            'conversation_duration': str(datetime.now() - self.conversation_start_time),
            'recent_agents': self.agent_history[-3:] if self.agent_history else []
        }
    
    def clear(self) -> None:
        """Clear conversation context"""
        self.intents.clear()
        self.current_request = None
        self.previous_requests.clear()
        self.agent_history.clear()
        self.conversation_start_time = datetime.now()

class SessionState:
    """Enhanced session state with persistent conversation context"""
    def __init__(self):
        # Authentication state
        self.authenticated = False
        self.auth_attempts = 0
        self.student_id = None
        
        # Conversation context
        self.conversation_context = ConversationContext()
        
        # Session metadata
        self.session_id = None
        self.session_start_time = datetime.now()
        self.is_active = True
        
        # Multi-request tracking
        self.completed_requests: List[Dict[str, Any]] = []
        self.pending_requests: List[Dict[str, Any]] = []
        
        # User preferences
        self.notification_enabled = True
        self.report_generation_enabled = True
        
    def start_session(self, session_id: str, student_id: str) -> None:
        """Initialize a new session"""
        self.session_id = session_id
        self.student_id = student_id
        self.authenticated = True
        self.session_start_time = datetime.now()
        self.is_active = True
    
    def end_session(self) -> Dict[str, Any]:
        """End the session and return session summary"""
        self.is_active = False
        session_duration = datetime.now() - self.session_start_time
        return {
            'session_id': self.session_id,
            'student_id': self.student_id,
            'duration': str(session_duration),
            'total_requests': len(self.completed_requests),
            'pending_requests': len(self.pending_requests),
            'conversation_context': self.conversation_context.get_context_summary()
        }
    
    def add_completed_request(self, request: Dict[str, Any]) -> None:
        """Mark a request as completed"""
        self.completed_requests.append({
            **request,
            'completed_at': datetime.now().isoformat()
        })
    
    def add_pending_request(self, request: Dict[str, Any]) -> None:
        """Add a pending request"""
        self.pending_requests.append({
            **request,
            'added_at': datetime.now().isoformat()
        })
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get complete session summary"""
        return {
            'session_id': self.session_id,
            'student_id': self.student_id,
            'authenticated': self.authenticated,
            'active': self.is_active,
            'session_duration': str(datetime.now() - self.session_start_time),
            'completed_requests': len(self.completed_requests),
            'pending_requests': len(self.pending_requests),
            'conversation_context': self.conversation_context.get_context_summary(),
            'auth_attempts': self.auth_attempts
        }
    
    def reset(self) -> None:
        """Reset session state"""
        self.authenticated = False
        self.auth_attempts = 0
        self.student_id = None
        self.session_id = None
        self.conversation_context.clear()
        self.completed_requests.clear()
        self.pending_requests.clear()
        self.is_active = False

# Global session instance
_session = SessionState()

def get_session() -> SessionState:
    """Get the global session instance"""
    return _session

def reset_session() -> None:
    """Reset the global session"""
    global _session
    _session.reset()
    _session = SessionState()