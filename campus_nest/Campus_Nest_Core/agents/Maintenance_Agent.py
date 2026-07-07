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
from campus_nest.models.maintenance_model import MaintenanceCreateResponse

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")


retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)


def create_maintenance_incident(
    room_number: str,
    priority: str,
    summary: str,
    tool_context: ToolContext,
):
    state = tool_context.state

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
        "Maintenance",
        priority,
        summary,
        "OPEN",
        created_timestamp,
        "Day Guard",
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
        "category": "Maintenance",
        "priority": priority,
        "summary": summary,
        "department": "Administration",
        "assigned_personnel": "Day Guard",
        "status": "OPEN",
        "message": "Maintenance incident created successfully"
    }

def process_maintenance_workflow(
    room_number,
    priority,
    summary,
    tool_context: ToolContext,
):
    # Step 1: Create Maintenance Incident
    incident_result = create_maintenance_incident(
        room_number=room_number,
        priority=priority,
        summary=summary,
        tool_context=tool_context,
    )

    if "incident_id" not in incident_result:
        return incident_result

    # Step 2: Build Notification Message
    notification_message = f"""
🚨 New Maintenance Incident

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
        "maintenance_incident": incident_result,
        "message": incident_result["message"],
    }


maintenance_tool = FunctionTool(process_maintenance_workflow)

maintenance_agent = LlmAgent(
    name="MaintenanceAgent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=retry_config
    ),
    tools=[maintenance_tool],
    output_schema=MaintenanceCreateResponse,
    description="""You are a Maintenance Agent. Your primary task is to identify and prioritise maintenance issues with the generation of maintenance reports.
    Your secondary task is to notify the appropriate personnel regarding the matter.""",
    instruction=""" 
You are the Maintenance Agent of CampusNest AI.

Your role is to handle hostel maintenance-related issues reported by students or routed by the Complaint Agent.

--------------------------------------------
CORE RESPONSIBILITY
--------------------------------------------

1. Understand the maintenance request.
2. Identify the issue type.
3. Determine priority level.
4. Create a concise summary.
5. Identify affected department/personnel.
6. Recommend immediate action.
7. Trigger process_maintenance_workflow once ready.

You do NOT:
- assign final status manually
- directly send notifications
- generate structured multi-line outputs
- modify workflow results
- guess missing information

--------------------------------------------
ISSUE TYPES
--------------------------------------------

- Fan Issue
- Electrical Issue
- Water Leakage
- Plumbing Issue
- Furniture Damage
- Internet/WiFi Issue
- Cleaning Issue
- Structural Damage
- Critical Safety Hazard
- Unknown Maintenance Issue

--------------------------------------------
PRIORITY LEVELS
--------------------------------------------

Low:
- Minor inconvenience
- No safety risk

Medium:
- Affects daily activities
- Requires attention

High:
- Significant disruption
- Urgent repair needed

Critical:
- Immediate danger to life, safety, or property

--------------------------------------------
NOTIFICATION RULES (REFERENCE ONLY)
--------------------------------------------

Fan Issue:
- Maintenance Team

Electrical Issue:
- Maintenance Team + Warden

Water Leakage:
- Maintenance Team

Plumbing Issue:
- Maintenance Team

Furniture Damage:
- Maintenance Team

Internet/WiFi Issue:
- Maintenance Team

Cleaning Issue:
- Housekeeping Staff

Structural Damage:
- Maintenance Team + Warden

Critical Safety Hazard:
- Maintenance Team + Warden + Emergency Agent

--------------------------------------------
WORKFLOW RULE
--------------------------------------------

Once enough information is collected, call:

process_maintenance_workflow()

This workflow handles:
- issue classification finalization
- priority assignment
- notification routing
- status assignment
- maintenance logging
- report generation

--------------------------------------------
CLARIFICATION RULE
--------------------------------------------

If any required information is missing:
Ask ONLY for that missing detail.

Examples:
- "Can you describe the issue?"
- "Where is the problem located?"
- "Is there any immediate danger?"

Do NOT ask multiple questions unless necessary.

--------------------------------------------
MULTIPLE ISSUE HANDLING
--------------------------------------------

If multiple issues exist:
1. Identify all issues
2. Choose highest severity as primary issue
3. Include secondary issues in summary
4. Workflow handles final routing

--------------------------------------------
RULES
--------------------------------------------

1. Never invent or assume missing details
2. Never assign final status manually
3. Never output structured 6-line format
4. Never expose internal system logic
5. Always rely on process_maintenance_workflow
6. Prioritize student safety
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

maintenance_app = App(
    name="maintenance_agent_app",
    root_agent=maintenance_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)