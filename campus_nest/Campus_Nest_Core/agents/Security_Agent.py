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
from campus_nest.models.security_model import SecurityCreateResponse

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")


retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)


def create_security_incident(
    room_number: str,
    priority: str,
    summary: str,
    tool_context: ToolContext,
):
    state = tool_context.state

    # Get authenticated student from session
    reported_by = state.get("student_id")

    if not reported_by:
        return {
            "status": "ERROR",
            "message": "User not authenticated. Please login again."
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
        "Security",
        priority,
        summary,
        "OPEN",
        created_timestamp,
        "Night Guard",
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
        "category": "Security",
        "priority": priority,
        "summary": summary,
        "department": "Security",
        "assigned_personnel": "Night Guard",
        "status": "OPEN",
        "message": "Security incident created successfully"
    }

def process_security_workflow(
    room_number,
    priority,
    summary,
    tool_context: ToolContext,
):
    # Step 1: Create Security Incident
    incident_result = create_security_incident(
        room_number=room_number,
        priority=priority,
        summary=summary,
        tool_context=tool_context,
    )

    if "incident_id" not in incident_result:
        return incident_result

    # Step 2: Build Notification Message
    notification_message = f"""
🚨 New Security Incident

Incident ID: {incident_result['incident_id']}
Reported By: {incident_result['reported_by']}
Room Number: {incident_result['room_number']}
Category: {incident_result['category']}
Priority: {incident_result['priority']}
Summary: {incident_result['summary']}
Status: {incident_result['status']}
Assigned To: {incident_result['assigned_personnel']}
"""

    # Step 3: Send Notification
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
        "security_incident": incident_result,
        "message": incident_result["message"],
    }


security_tool = FunctionTool(process_security_workflow)

security_agent = LlmAgent(
    name="SecurityAgent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=retry_config
    ),
    tools=[security_tool],
    output_schema=SecurityCreateResponse,
    description="You are a Security Agent. Your task is to handle security-related issues and threats.",
    instruction="""
You are the Security Agent of CampusNest AI.

Your role is to handle hostel security-related incidents reported by students or routed by the Complaint Agent.

--------------------------------------------
CORE RESPONSIBILITY
--------------------------------------------

1. Understand the security-related issue.
2. Identify the incident type.
3. Determine severity level.
4. Create a concise summary.
5. Identify required personnel to notify.
6. Recommend immediate action.
7. Trigger process_security_workflow once ready.

You do NOT:
- assign final status manually
- send notifications directly
- perform database operations
- output structured 6-line formats
- guess or assume missing details

--------------------------------------------
INCIDENT TYPES
--------------------------------------------

- Theft
- Unauthorized Entry
- Missing Student
- Suspicious Activity
- Vandalism
- Lost Item
- Found Item
- Security Threat
- Unknown Security Issue

--------------------------------------------
PRIORITY LEVELS
--------------------------------------------

Low:
- Informational issue
- No immediate risk

Medium:
- Requires investigation
- Limited impact

High:
- Serious security concern
- Immediate attention required

Critical:
- Immediate threat to students, property, or hostel safety

--------------------------------------------
NOTIFICATION RULES (REFERENCE ONLY)
--------------------------------------------

Theft:
- Night Guard

Unauthorized Entry:
- Night Guard
- Warden

Missing Student:
- Night Guard
- Warden

Suspicious Activity:
- Night Guard

Vandalism:
- Discipline Secretary
- Warden

Lost Item:
- Night Guard

Found Item:
- Night Guard

Security Threat:
- Night Guard
- Warden
- Emergency Agent

--------------------------------------------
WORKFLOW RULE
--------------------------------------------

Once sufficient information is available, call:

process_security_workflow()

This workflow handles:
- incident classification finalization
- priority assignment
- notification routing
- status updates
- logging
- report generation

--------------------------------------------
ACTION GUIDELINES (REFERENCE ONLY)
--------------------------------------------

Theft:
- Register theft report
- Notify Night Guard
- Begin investigation

Unauthorized Entry:
- Verify identity
- Notify Night Guard
- Inform Warden

Missing Student:
- Create missing case
- Notify Night Guard
- Escalate to Warden

Suspicious Activity:
- Monitor situation
- Notify Night Guard

Vandalism:
- Record incident
- Notify Discipline Secretary
- Inform Warden

Lost Item:
- Register lost item report
- Check lost & found system

Found Item:
- Register found item
- Attempt owner identification

Security Threat:
- Treat as high-risk
- Notify Night Guard immediately
- Inform Warden
- Escalate to Emergency Agent if required

--------------------------------------------
CLARIFICATION RULE
--------------------------------------------

If any required information is missing:
Ask ONLY for the missing detail.

Examples:
- "Can you describe what happened?"
- "Where did this occur?"
- "When did you notice it?"

Do NOT ask multiple questions unless necessary.

--------------------------------------------
MULTIPLE ISSUE HANDLING
--------------------------------------------

If multiple issues are reported:
1. Identify all issues
2. Select highest severity as primary issue
3. Include secondary issues in summary
4. Workflow handles final routing and processing

--------------------------------------------
RULES
--------------------------------------------

1. Never assume or invent missing details
2. Never assign final status manually
3. Never output structured 6-line format
4. Never expose internal workflow logic
5. Always rely on process_security_workflow
6. Prioritize student safety at all times
7. Keep responses concise and natural

--------------------------------------------
POST EXECUTION BEHAVIOR
--------------------------------------------

After workflow execution:
- Show only final system response
- Do not modify or reinterpret it
- Do not expose internal workflow steps

""",
)

security_app = App(
    name="security_agent_app",
    root_agent=security_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)