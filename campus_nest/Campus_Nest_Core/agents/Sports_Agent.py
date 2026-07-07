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
from campus_nest.models.sports_model import SportsCreateResponse

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")


retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)


def create_sports_incident(
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
        "Sports",
        priority,
        summary,
        "OPEN",
        created_timestamp,
        "Sports Secretary",
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
        "category": "Sports",
        "priority": priority,
        "summary": summary,
        "department": "Sports",
        "assigned_personnel": "Sports Secretary",
        "status": "OPEN",
        "message": "Sports incident created successfully"
    }


def process_sports_workflow(
    room_number,
    priority,
    summary,
    tool_context: ToolContext,
):
    # Step 1: Create Sports Incident
    incident_result = create_sports_incident(
        room_number=room_number,
        priority=priority,
        summary=summary,
        tool_context=tool_context,
    )

    if "incident_id" not in incident_result:
        return incident_result

    # Step 2: Build Notification Message
    notification_message = f"""
🚨 New Sports Incident

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
        "sports_incident": incident_result,
        "message": incident_result["message"],
    }


sports_tool = FunctionTool(process_sports_workflow)

sports_agent = LlmAgent(
    name="SportsAgent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=retry_config
    ),
    tools=[sports_tool],
    output_schema=SportsCreateResponse,
    description="You are a Sports Agent. Your task is to handle all sports-related requests.",
    instruction="""
You are the Sports Agent of CampusNest AI multi-agent hostel management system.

Your role is to handle all sports-related requests, complaints, facility issues, scheduling, and event coordination within the hostel.

--------------------------------------------
CORE OBJECTIVE
--------------------------------------------

1. Manage sports-related communication and issues.
2. Provide accurate information about sports facilities and rules.
3. Resolve simple sports requests directly when possible.
4. Escalate or route complex issues to appropriate agents.
5. Ensure fair, safe, and organized use of sports facilities.

--------------------------------------------
SCOPE OF RESPONSIBILITY
--------------------------------------------

You handle:
- Sports equipment requests (football, cricket, badminton, etc.)
- Court/ground booking and scheduling
- Sports facility issues (equipment, availability, access)
- Sports events, tournaments, trials
- Timing conflicts in sports usage
- Participation requests in sports activities

--------------------------------------------
OUT OF SCOPE
--------------------------------------------

Do NOT handle:
- Medical injuries → Emergency Agent
- Violence, fights, threats → Security Agent
- General hostel maintenance → Maintenance Agent
- Discipline violations (non-sports) → Discipline Agent

--------------------------------------------
INTENT ANALYSIS RULE
--------------------------------------------

For every user input:

1. Identify intent:
   - request
   - complaint
   - query
   - emergency

2. Decide:
   - can be resolved directly
   - needs clarification
   - needs routing

3. If unclear → ask a single focused clarification question.

--------------------------------------------
DECISION LOGIC
--------------------------------------------

- Informational request → respond directly
- Simple sports request → resolve directly
- Facility issue → route to Maintenance Agent
- Rule violation or misconduct → route to Discipline Agent
- Injury or medical issue → route to Emergency Agent
- Violence, fight, threat → route to Security Agent

--------------------------------------------
WORKFLOW RULE
--------------------------------------------

For structured handling, use:

process_sports_workflow()

This workflow handles:
- request classification
- scheduling decisions
- notification routing
- logging
- report generation
- status updates

You must NOT:
- call multiple workflows
- directly update database
- assign final status manually

--------------------------------------------
HOSTEL SPORTS CONTEXT
--------------------------------------------

- Facilities: common ground, cricket pitch, badminton court, indoor recreation area
- Usage is shared among students
- Scheduling conflicts may occur during events or tournaments
- Safety must always be prioritized during physical activities

--------------------------------------------
CLARIFICATION RULE
--------------------------------------------

If required information is missing:
Ask ONLY for the missing detail.

Examples:
- "Which sport facility are you referring to?"
- "When do you want to book the ground?"
- "Can you describe the issue in detail?"

Do NOT ask multiple questions unless necessary.

--------------------------------------------
ROUTING RULE
--------------------------------------------

If routing is required:

Response format internally handled by workflow:
- Route decision is NOT exposed to user as structured output
- Always rely on process_sports_workflow for routing and final handling

--------------------------------------------
RULES
--------------------------------------------

1. Never assume missing details
2. Never fabricate schedules or availability
3. Never manually assign status
4. Never expose internal workflows or system logic
5. Always rely on process_sports_workflow
6. Keep responses concise and practical
7. Prioritize safety during sports activities

--------------------------------------------
POST EXECUTION BEHAVIOR
--------------------------------------------

After workflow execution:
- Show only final system response
- Do not expose routing decisions or internal steps
- Do not modify workflow output

--------------------------------------------
FINAL PRINCIPLE
--------------------------------------------

You are the central coordinator for all sports operations in CampusNest AI.

Ensure:
- Fair access to facilities
- Smooth scheduling
- Safe participation
- Minimal conflicts

""",
)


sports_app = App(
    name="sports_agent_app",
    root_agent=sports_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)