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
from campus_nest.models.discipline_model import DisciplineCreateResponse

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")


retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)


def create_discipline_incident(
    room_number: str,
    priority: str,
    summary: str,
    tool_context: ToolContext
):
    state = tool_context.state

    # Get student ID from session memory
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
        "Discipline",
        priority,
        summary,
        "OPEN",
        created_timestamp,
        "Discipline Secretary",
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
        "category": "Discipline",
        "priority": priority,
        "summary": summary,
        "department": "Discipline",
        "assigned_personnel": "Discipline Secretary",
        "status": "OPEN",
        "message": "Discipline incident created successfully"
    }

def process_discipline_workflow(
    room_number,
    priority,
    summary,
    tool_context: ToolContext,
):
    # Step 1: Create Discipline Incident
    incident_result = create_discipline_incident(
        room_number=room_number,
        priority=priority,
        summary=summary,
        tool_context=tool_context
    )

    if "incident_id" not in incident_result:
        return incident_result

    # Step 2: Build Notification Message
    notification_message = f"""
🚨 New Discipline Incident

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
    "discipline_incident": incident_result,
    "message": incident_result["message"],
}

discipline_tool = FunctionTool(process_discipline_workflow)

discipline_agent = LlmAgent(
    name="DisciplineAgent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=retry_config
    ),
    tools=[discipline_tool],
    output_schema=DisciplineCreateResponse,
    description="You are a discipline agent. Your task is to handle discipline-related issues and complaints.",
    instruction="""
You are the Discipline Agent of CampusNest AI.

Your job is to collect all required information and trigger the workflow.

Required fields:
- reported_by
- room_number
- priority
- summary

Behavior:

1. If any field is missing → ask ONLY for that field.
2. If all fields are available → call process_discipline_workflow.
3. Do NOT classify incident types.
4. Do NOT decide actions or status.
5. Do NOT generate structured outputs.

After workflow execution:
- Show only final response returned by system
- Do not modify it

Behavior:

1. If any field is missing → ask ONLY for that field.
2. If all fields are available → call process_discipline_workflow.
3. Do NOT classify incident types.
4. Do NOT decide actions or status.
5. Do NOT generate structured outputs.

After workflow execution:
Return the tool result exactly as received.
Do not modify, summarize, or reformat it.

""",
)

discipline_app = App(
    name="discipline_agent_app",
    root_agent=discipline_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)