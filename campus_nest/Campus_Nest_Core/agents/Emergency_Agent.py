from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.apps import ResumabilityConfig
from google.adk.models import Gemini
from google.genai import types
from dotenv import load_dotenv
from .notification_tools import send_notification
from .Report_Generator_Agent import generate_incident_report
from google.adk.tools import FunctionTool
import os
import sqlite3
from datetime import datetime
from google.adk.tools import ToolContext
from campus_nest.models.emergency_model import EmergencyCreateResponse

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")


retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)

def create_emergency_incident(
    room_number: str,
    priority: str,
    summary: str,
    tool_context: ToolContext
):
    state = tool_context.state

    reported_by = state.get("student_id")

    if not reported_by:
        return {
            "status": "ERROR",
            "message": "User not authenticated. Emergency cannot be processed without login."
        }

    conn = sqlite3.connect("auth/campusnest.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM students
        WHERE student_id = ?
    """, (reported_by,))

    result = cursor.fetchone()

    if result is None:
        conn.close()
        return {
            "status": "ERROR",
            "message": "Student not found."
        }

    student_name = result[0]

    cursor.execute("SELECT COUNT(*) FROM incident_reports")
    count = cursor.fetchone()[0] + 1

    incident_id = f"INC{count:03d}"

    created_timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    cursor.execute("""
        INSERT INTO incident_reports (
            incident_id,
            reported_by,
            room_number,
            category,
            priority,
            summary,
            status,
            created_timestamp,
            assigned_personnel,
            resolution_notes,
            closed_timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        incident_id,
        reported_by,
        room_number,
        "Emergency",
        priority,
        summary,
        "OPEN",
        created_timestamp,
        "Warden",
        "",
        None
    ))

    conn.commit()
    conn.close()

    return {
        "incident_id": incident_id,
        "reported_by": reported_by,
        "student_name": student_name,
        "room_number": room_number,
        "category": "Emergency",
        "priority": priority,
        "summary": summary,
        "department": "Administration",
        "assigned_personnel": "Warden",
        "status": "OPEN",
        "message": "Emergency incident created successfully"
    }

def process_emergency_workflow(
    room_number,
    priority,
    summary,
    tool_context: ToolContext,
):
    # Step 1: Create Emergency Incident
    incident_result = create_emergency_incident(
        room_number=room_number,
        priority=priority,
        summary=summary,
        tool_context=tool_context
    )

    if "incident_id" not in incident_result:
        return incident_result

    # Step 2: Build Notification Message
    notification_message = f"""
🚨 EMERGENCY ALERT

Incident ID: {incident_result['incident_id']}
Reported By: {incident_result['reported_by']}
Room Number: {incident_result['room_number']}
Category: {incident_result['category']}
Priority: {incident_result['priority']}
Summary: {incident_result['summary']}
Status: {incident_result['status']}
Assigned To: {incident_result['assigned_personnel']}
"""

    # Step 3: Send Notification to Warden
    notification_result = send_notification(
        incident_id=incident_result["incident_id"],
        department=incident_result["department"],
        message=notification_message,
    )

    # Step 4: Generate Report
    report = generate_incident_report(
        incident_id=incident_result["incident_id"]
    )

    # Step 5: Return Complete Workflow Result
    return {
        "emergency_incident": incident_result,
        "message": incident_result["message"],
    }

emergency_tool = FunctionTool(process_emergency_workflow)

emergency_agent = LlmAgent(
    name="EmergencyAgent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=retry_config
    ),
    tools=[emergency_tool],
    output_schema=EmergencyCreateResponse,
    description="""You are an Emergency Agent. Your task is to handle emergency situations that have already been identified by the Complaint Agent.
    Your primary and secondary task is to assign degree of severity to an emergency situation and notifying appropriate personnel regarding the matter,respectively.""",
    instruction="""
You are the Emergency Agent of CampusNest AI.

Your role is ONLY to classify an emergency and trigger the emergency workflow system. You do NOT execute actions yourself.

--------------------------------------------
CORE RESPONSIBILITY
--------------------------------------------

1. Understand the emergency situation.
2. Identify the most appropriate emergency type.
3. Collect missing critical details if required.
4. Trigger the emergency workflow function once enough information is available.

You do NOT decide final actions manually.
You do NOT send notifications directly.
You do NOT format structured outputs like reports.

--------------------------------------------
EMERGENCY TYPES
--------------------------------------------

- Medical Emergency
- Fire Emergency
- Electrical Hazard
- Security Threat
- Violence
- Unknown Emergency

--------------------------------------------
NOTIFICATION RULES (REFERENCE ONLY)
--------------------------------------------

All emergencies MUST always notify:
- Night Guard (first responder)

Additional escalation:

Medical Emergency:
- Night Guard → Warden

Fire Emergency:
- Night Guard → Warden → Maintenance Team

Electrical Hazard:
- Night Guard → Warden → Maintenance Team

Violence:
- Night Guard → Discipline Secretary → Warden

Security Threat:
- Night Guard → Warden → Security Team

--------------------------------------------
WORKFLOW RULE
--------------------------------------------

Once sufficient information is available, call:

process_emergency_workflow()

This function handles:
- classification finalization
- notification routing
- action generation
- status assignment
- logging

--------------------------------------------
CLARIFICATION RULE
--------------------------------------------

If important information is missing:
Ask short, direct follow-up questions such as:
- "Can you describe what is happening?"
- "Is anyone injured?"
- "Where exactly is this happening?"

Do NOT assume missing details.

--------------------------------------------
OUTPUT RULES
--------------------------------------------

1. Do NOT output structured formats like:
   emergency_type:
   notify:
   action:
   status:

2. Do NOT include markdown, bullets, or lists.

3. Do NOT invent emergency types or severity.

4. Always rely on provided information.

--------------------------------------------
BEHAVIOR AFTER EXECUTION
--------------------------------------------

After workflow execution:
- Present only the final system response
- Do not modify or reinterpret results
- Do not expose internal routing or logic

""",
)

emergency_app = App(
    name="emergency_agent_app",
    root_agent=emergency_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)
    