from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.apps import ResumabilityConfig, App
from google.adk.tools import FunctionTool
from google.genai import types
from .notification_tools import send_notification
from .Report_Generator_Agent import generate_leave_report
from datetime import datetime
import sqlite3
from dotenv import load_dotenv
import os
from campus_nest.models.leave_model import LeaveCreateResponse

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)  

def create_leave_request(
    student_id: str,
    leave_type: str,
    start_date: str,
    end_date: str,
    reason: str
):
    conn = sqlite3.connect("auth/campusnest.db")
    cursor = conn.cursor()

    cursor.execute("""
     SELECT name
     FROM students
     WHERE student_id = ?
    """, (student_id,))

    result = cursor.fetchone()

    if result is None:
        conn.close()
        return {
            "status": "failed",
            "message": "Student not found."
        }

    student_name = result[0]

    cursor.execute("SELECT COUNT(*) FROM leave_requests")
    count = cursor.fetchone()[0] + 1

    application_id = f"APP{count:03d}"

    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    cursor.execute("""
        INSERT INTO leave_requests (
            application_id,
            student_id,
            leave_type,
            reason,
            start_date,
            end_date,
            status,
            warden_remarks,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        application_id,
        student_id,
        leave_type, 
        reason,
        start_date,
        end_date,
        "PENDING",
        "",
        timestamp
    ))

    conn.commit()
    conn.close()

    return {
        "application_id": application_id,
        "student_id": student_id,
        "student_name": student_name,
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason,
        "department": "Administration",
        "status": "PENDING",
        "message": "Leave request created successfully"
    }

def process_leave_workflow(
    student_id,
    leave_type,
    start_date,
    end_date,
    reason,
):
     # Step 1: Create leave request
    leave_result = create_leave_request(
        student_id=student_id,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
    )

    if "application_id" not in leave_result:
        return leave_result

    # Step 2: Build notification message
    notification_message = f"""
🚨 New Leave Request

Application ID: {leave_result['application_id']}
Student ID: {leave_result['student_id']}
Leave Type: {leave_result['leave_type']}
Start Date: {leave_result['start_date']}
End Date: {leave_result['end_date']}
Reason: {leave_result['reason']}
Status: {leave_result['status']}
"""
        # Step 3: Send notification
    notification_result = send_notification(
        incident_id=leave_result["application_id"],
        department=leave_result["department"],
        message=notification_message,
    )
        # Step 4: Generate report
    report = generate_leave_report(
        application_id=leave_result["application_id"]
    )

    # Step 5: Return complete workflow result
    return {
        "leave_request": leave_result,
        "message": leave_result["message"],
    }

leave_tool = FunctionTool(process_leave_workflow)

leave_agent = LlmAgent(
    name="LeaveAgent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=retry_config
    ),
    tools=[
        leave_tool,
    ],
    output_schema=LeaveCreateResponse,
    description="""Handles student leave applications for CampusNest AI.""",
    instruction="""
You are the Leave Agent of CampusNest AI.

Your sole responsibility is LEAVE REQUEST PROCESSING.

Responsibilities:

1. Collect leave information
2. Identify: student_id, leave_type, start_date, end_date, reason
3. Validate information
4. Ask follow-ups if needed
5. Use create_leave_request when all required information has been collected.
6. Never approve/reject (only submit)

Leave Types:
- HOME_VISIT
- MEDICAL
- EMERGENCY
- ACADEMIC
- PERSONAL
- OTHER

--------------------------------------------
INFORMATION COLLECTION
--------------------------------------------

Collect ONLY from user input.
Never invent information.

If information is incomplete:
Ask SPECIFIC questions:

Missing student_id:
"What's your student ID?"

Missing dates:
"When do you want to start your leave?"
"When will you return?"

Missing reason:
"What's the reason for your leave?"

--------------------------------------------
RULES
--------------------------------------------

1. Never invent information
2. Never skip required fields
3. Verify dates are valid
4. Ask for clarification if confused
5. Always output Application ID
6. Do not approve/reject (only submit)
7. Never call create_leave_request.
8. Always call process_leave_workflow.

process_leave_workflow performs:
- Leave creation
- Notification
- Report generation

Do not perform these actions individually.

"""
)

leave_app = App(
    name="leave_agent_app",
    root_agent=leave_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)