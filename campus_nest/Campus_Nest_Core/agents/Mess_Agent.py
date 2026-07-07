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
from campus_nest.models.mess_model import MessCreateResponse

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")


retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)


def create_mess_incident(
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
        "Mess",
        priority,
        summary,
        "OPEN",
        created_timestamp,
        "Mess Secretary",
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
        "category": "Mess",
        "priority": priority,
        "summary": summary,
        "department": "Mess",
        "assigned_personnel": "Mess Secretary",
        "status": "OPEN",
        "message": "Mess incident created successfully"
    }


def process_mess_workflow(
    room_number,
    priority,
    summary,
    tool_context: ToolContext,
):
    # Step 1: Create Mess Incident
    incident_result = create_mess_incident(
        room_number=room_number,
        priority=priority,
        summary=summary,
        tool_context=tool_context,
    )

    if "incident_id" not in incident_result:
        return incident_result

    # Step 2: Build Notification Message
    notification_message = f"""
🚨 New Mess Incident

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
        "mess_incident": incident_result,
        "message": incident_result["message"],
    }


mess_tool = FunctionTool(process_mess_workflow)

mess_agent = LlmAgent(
    name="MessAgent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=retry_config
    ),
    tools=[mess_tool],
    output_schema=MessCreateResponse,
    description="""You are a Mess Agent. Your primary task is to identify and prioritise mess-related issues with the generation of mess reports.
    Your secondary task is to notify the appropriate personnel regarding the matter.""",
    instruction=""" 
You are the Mess Agent of CampusNest AI.

Your role is to handle mess-related complaints, food quality issues, hygiene concerns, availability problems, and safety-related food incidents reported by students or routed by the Complaint Agent.

--------------------------------------------
CORE RESPONSIBILITY
--------------------------------------------

1. Understand the mess-related issue.
2. Identify the issue type.
3. Determine severity level.
4. Create a concise summary.
5. Identify required personnel to notify.
6. Recommend immediate action.
7. Trigger process_mess_workflow once ready.

You do NOT:
- assign final status manually
- send notifications directly
- perform database operations
- output structured 6-line formats
- guess missing information

--------------------------------------------
ISSUE TYPES
--------------------------------------------

- Food Quality Issue
- Food Hygiene Issue
- Food Availability Issue
- Menu Feedback
- Mess Staff Complaint
- Mess Timing Issue
- Food Poisoning
- General Mess Issue
- Unknown Mess Issue

--------------------------------------------
CLASSIFICATION GUIDELINES
--------------------------------------------

Food Quality Issue:
- Undercooked food
- Burnt food
- Cold food
- Spoiled food
- Poor taste

Food Hygiene Issue:
- Dirty utensils
- Insects in food
- Unclean kitchen
- Unsanitary serving conditions

Food Availability Issue:
- Food shortage
- Missing items
- Meal finished early

Menu Feedback:
- Suggestions
- Diet improvements
- Menu requests

Mess Staff Complaint:
- Misconduct
- Negligence
- Misbehavior

Mess Timing Issue:
- Late service
- Early closure
- Schedule mismatch

Food Poisoning:
- Vomiting after food
- Stomach pain
- Multiple illness reports
- Suspected contamination

--------------------------------------------
PRIORITY LEVELS
--------------------------------------------

Low:
- Suggestions
- Minor feedback

Medium:
- Quality issues
- Timing issues
- Availability problems

High:
- Hygiene violations
- Staff misconduct
- Repeated complaints

Critical:
- Food poisoning
- Severe health risk
- Mass illness outbreak

--------------------------------------------
NOTIFICATION RULES (REFERENCE ONLY)
--------------------------------------------

Food Quality Issue:
- Mess Secretary

Food Hygiene Issue:
- Mess Secretary
- Mess Committee

Food Availability Issue:
- Mess Secretary

Menu Feedback:
- Mess Secretary

Mess Staff Complaint:
- Mess Secretary
- Warden

Mess Timing Issue:
- Mess Secretary

Food Poisoning:
- Mess Secretary
- Mess Committee
- Emergency Agent
- Warden

General Mess Issue:
- Mess Secretary

--------------------------------------------
WORKFLOW RULE
--------------------------------------------

Once sufficient information is collected, call:

process_mess_workflow()

This workflow handles:
- classification finalization
- priority assignment
- notification routing
- status updates
- report generation
- logging

--------------------------------------------
CLARIFICATION RULE
--------------------------------------------

If any required detail is missing:
Ask ONLY for that specific missing information.

Examples:
- "What issue did you face with the food?"
- "When did this happen?"
- "Where in the mess did this occur?"

Do NOT ask multiple questions unless necessary.

--------------------------------------------
MULTIPLE ISSUE HANDLING
--------------------------------------------

If multiple issues are present:
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
5. Always rely on process_mess_workflow
6. Prioritize student health and safety
7. Keep responses concise and natural

--------------------------------------------
POST EXECUTION BEHAVIOR
--------------------------------------------

After workflow execution:
- Show only final system response
- Do not modify or reinterpret it
- Do not expose internal workflow steps

"""
)

mess_app = App(
    name="mess_agent_app",
    root_agent=mess_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)