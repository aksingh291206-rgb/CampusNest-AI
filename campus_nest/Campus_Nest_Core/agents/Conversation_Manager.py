"""
Conversation Manager - Handles conversation flow, graceful closing, and seamless transitions
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from state.session_state import get_session

class ConversationManager:
    """
    Manages conversation flow including:
    - Multi-intent detection and handling
    - Seamless agent transitions
    - Graceful conversation closing
    - Context preservation
    """
    
    # Keywords indicating conversation exit
    EXIT_KEYWORDS = [
        "exit", "quit", "bye", "goodbye", "logout", "done", "close",
        "finish", "end", "thank you", "thanks", "that's all", "nothing else",
        "no more", "no thanks", "not needed", "no help needed"
    ]
    
    # Multi-intent patterns (combined requests)
    MULTI_INTENT_PATTERNS = {
        "complaint_and_track": ["complaint", "track"],
        "maintenance_and_mess": ["maintenance", "mess"],
        "emergency_and_notification": ["emergency", "urgent"],
        "leave_and_notification": ["leave", "not available"],
    }
    
    def __init__(self):
        self.session = get_session()
        self.conversation_active = True
        self.pending_actions: List[Dict[str, Any]] = []
        
    def detect_exit_intent(self, user_input: str) -> bool:
        """
        Detect if user wants to exit the conversation
        
        Args:
            user_input: User's message
            
        Returns:
            True if exit intent detected, False otherwise
        """
        lower_input = user_input.lower().strip()
        
        # Check for exit keywords
        for keyword in self.EXIT_KEYWORDS:
            if keyword in lower_input:
                return True
        
        return False
    
    def detect_multiple_intents(self, user_input: str) -> List[Dict[str, str]]:
        """
        Detect multiple intents in a single user message
        
        Args:
            user_input: User's message
            
        Returns:
            List of detected intents with their types
        """
        intents = []
        lower_input = user_input.lower()
        
        # Keywords for different intent types
        intent_keywords = {
            "complaint": ["complain", "issue", "problem", "complaint", "report", "lodge"],
            "leave": ["leave", "vacation", "break", "absent", "going home", "not available"],
            "track": ["track", "status", "update", "where", "what happened"],
            "maintenance": ["maintenance", "repair", "fix", "broken", "damage", "maintenance issue"],
            "mess": ["mess", "food", "dining", "complaint about mess"],
            "emergency": ["emergency", "urgent", "immediately", "help", "danger", "accident"],
            "security": ["security", "unsafe", "threat", "suspicious"],
            "discipline": ["discipline", "conduct", "violation"],
            "sports": ["sports", "event", "tournament", "participation"],
            "general": ["hostel", "information", "how", "where", "when"],
        }
        
        for intent_type, keywords in intent_keywords.items():
            for keyword in keywords:
                if keyword in lower_input:
                    intents.append({
                        "type": intent_type,
                        "keyword": keyword,
                        "confidence": "high" if lower_input.count(keyword) > 1 else "medium"
                    })
                    break  # Add each intent type only once
        
        return intents
    
    def handle_multiple_intents(self, intents: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Handle multiple intents by creating a workflow plan
        
        Args:
            intents: List of detected intents
            
        Returns:
            Workflow plan for handling multiple intents
        """
        if len(intents) <= 1:
            return {
                "multi_intent": False,
                "workflow": []
            }
        
        # Sort intents by confidence and type priority
        intent_priority = {
            "emergency": 0,
            "complaint": 1,
            "leave": 2,
            "track": 3,
            "maintenance": 4,
            "mess": 4,
            "security": 4,
            "discipline": 4,
            "sports": 5,
            "general": 6
        }
        
        sorted_intents = sorted(
            intents,
            key=lambda x: (intent_priority.get(x["type"], 99))
        )
        
        # Create workflow plan
        workflow = []
        agent_mapping = {
            "complaint": "ComplaintAgent",
            "leave": "LeaveAgent",
            "track": "TrackAgent",
            "maintenance": "MaintenanceAgent",
            "mess": "MessAgent",
            "emergency": "EmergencyAgent",
            "security": "SecurityAgent",
            "discipline": "DisciplineAgent",
            "sports": "SportsAgent",
            "general": "GeneralAgent",
        }
        
        for intent in sorted_intents:
            workflow.append({
                "step": len(workflow) + 1,
                "intent_type": intent["type"],
                "target_agent": agent_mapping.get(intent["type"], "RoutingAgent"),
                "status": "pending"
            })
        
        # Only add notification and report generation if there is at least one domain intent
        # General and tracking-only workflows should not trigger the notification/report stages.
        has_domain_intent = any(
            intent["type"] not in ("general", "track")
            for intent in sorted_intents
        )
        if has_domain_intent:
            workflow.append({
                "step": len(workflow) + 1,
                "intent_type": "notification",
                "target_agent": "NotificationAgent",
                "status": "pending"
            })
            
            workflow.append({
                "step": len(workflow) + 1,
                "intent_type": "report",
                "target_agent": "ReportGeneratorAgent",
                "status": "pending"
            })
        
        return {
            "multi_intent": True,
            "intent_count": len(intents),
            "intents": sorted_intents,
            "workflow": workflow
        }
    
    def create_seamless_transition(
        self,
        from_agent: str,
        to_agent: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a seamless transition from one agent to another
        
        Args:
            from_agent: Name of current agent
            to_agent: Name of target agent
            context: Current conversation context
            
        Returns:
            Transition information with hidden routing details
        """
        # Record agent transition
        self.session.conversation_context.add_agent_visit(to_agent)
        
        # Create transition message that's transparent to user
        transition_data = {
            "seamless": True,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "internal_message": f"Transferring to {to_agent} to continue assistance.",
            "user_friendly_message": self._get_user_friendly_transition(from_agent, to_agent)
        }
        
        return transition_data
    
    def _get_user_friendly_transition(self, from_agent: str, to_agent: str) -> str:
        """
        Generate user-friendly transition messages
        """
        transition_messages = {
            ("CampusNestOrchestrator", "ComplaintAgent"): "I'll help you file a complaint. Let me gather the details.",
            ("CampusNestOrchestrator", "LeaveAgent"): "I'll assist you with your leave application. Let me get the required information.",
            ("CampusNestOrchestrator", "TrackAgent"): "Let me check the status of your request for you.",
            ("ComplaintAgent", "NotificationAgent"): "Great! I'm notifying the concerned authorities about your complaint.",
            ("NotificationAgent", "ReportGeneratorAgent"): "Now I'll generate a complete report for your records.",
            ("ReportGeneratorAgent", "CampusNestOrchestrator"): "Your request has been processed. Is there anything else I can help you with?",
        }
        
        default = f"Connecting you to the right team to assist you further."
        return transition_messages.get((from_agent, to_agent), default)
    
    def handle_graceful_exit(self) -> Dict[str, Any]:
        """
        Handle graceful conversation closing
        
        Returns:
            Exit summary and session information
        """
        session_summary = self.session.end_session()
        
        # Create exit message
        exit_data = {
            "graceful_exit": True,
            "farewell_message": self._get_farewell_message(session_summary),
            "session_summary": session_summary,
            "next_steps": self._get_next_steps(session_summary)
        }
        
        return exit_data
    
    def _get_farewell_message(self, session_summary: Dict[str, Any]) -> str:
        """Generate a personalized farewell message"""
        completed = session_summary.get("completed_requests", 0)
        
        if completed == 0:
            return "Thank you for using CampusNest AI. Have a great day! 😊"
        elif completed == 1:
            return f"Thank you! Your request has been processed and the relevant authorities have been notified. Have a great day! 😊"
        else:
            return f"Thank you! We've processed {completed} of your requests and notified the relevant teams. Have a great day! 😊"
    
    def _get_next_steps(self, session_summary: Dict[str, Any]) -> List[str]:
        """Generate next steps for the user"""
        next_steps = []
        
        completed = session_summary.get("completed_requests", 0)
        pending = session_summary.get("pending_requests", 0)
        
        if completed > 0:
            next_steps.append("📋 Your request(s) have been logged in the system")
            next_steps.append("📧 You will receive updates via notifications")
            next_steps.append("📱 Check your messages for response from authorities")
        
        if pending > 0:
            next_steps.append(f"⏳ You have {pending} pending request(s)")
        
        next_steps.extend([
            "🔄 You can log back in anytime to check status",
            "💬 Feel free to reach out if you need further assistance"
        ])
        
        return next_steps
    
    def track_request(self, request: Dict[str, Any]) -> None:
        """Track a user request"""
        self.session.conversation_context.set_current_request(request)
        self.session.add_pending_request(request)
    
    def mark_request_complete(self, request_id: str) -> None:
        """Mark a request as completed"""
        # Remove from pending
        self.session.pending_requests = [
            r for r in self.session.pending_requests
            if r.get("request_id") != request_id
        ]
        
        # Add to completed
        self.session.add_completed_request({"request_id": request_id})
    
    def get_conversation_status(self) -> Dict[str, Any]:
        """Get current conversation status"""
        return {
            "active": self.conversation_active,
            "session_summary": self.session.get_session_summary(),
            "pending_actions": self.pending_actions,
            "conversation_context": self.session.conversation_context.get_context_summary()
        }
    
    def is_conversation_active(self) -> bool:
        """Check if conversation is still active"""
        return self.conversation_active and self.session.is_active


# Global conversation manager instance
_conversation_manager: Optional[ConversationManager] = None

def get_conversation_manager() -> ConversationManager:
    """Get or create the global conversation manager instance"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager

def reset_conversation_manager() -> None:
    """Reset the global conversation manager"""
    global _conversation_manager
    _conversation_manager = ConversationManager()
