from google.adk.agents import LlmAgent               
from google.adk.apps import App
from google.adk.apps import ResumabilityConfig
from google.adk.models import Gemini
from google.adk.tools import FunctionTool
from google.genai import types
import sqlite3
from dotenv import load_dotenv
import os
from google.adk.tools import ToolContext
from campus_nest.models.tracking_model import TrackingResponse

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)

def track_incident_report(incident_id: str):

    conn = sqlite3.connect("auth/campusnest.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ir.incident_id,
            ir.reported_by,
            s.name,
            ir.room_number,
            ir.category,
            ir.priority,
            ir.summary,
            ir.status,
            ir.created_timestamp,
            ir.assigned_personnel,
            ir.resolution_notes,
            ir.closed_timestamp
        FROM incident_reports ir
        JOIN students s
            ON ir.reported_by = s.student_id
        WHERE ir.incident_id = ?
    """, (incident_id,))    

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return {
            "success": False,
            "message": "Incident not found."
        }

    return {
    "incident_tracking": {
        "incident_id": result[0],
        "reported_by": result[1],
        "student_name": result[2],
        "room_number": result[3],
        "category": result[4],
        "priority": result[5],
        "summary": result[6],
        "status": result[7],
        "created_timestamp": result[8],
        "assigned_personnel": result[9],
        "resolution_notes": result[10],
        "closed_timestamp": result[11]
    },
    "message": "Incident found successfully."
}

def track_financial_record(record_id: str):

    conn = sqlite3.connect("auth/campusnest.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sf.record_id,
            sf.student_id,
            s.name,
            sf.fee_type,
            sf.reason,
            sf.amount,
            sf.payment_status,
            sf.issued_by,
            sf.issued_date,
            sf.payment_date,
            sf.due_date,
            sf.remarks
        FROM student_finances sf
        JOIN students s
            ON sf.student_id = s.student_id
        WHERE sf.record_id = ?
    """, (record_id,))

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return {
            "message": "Financial record not found."
        }

    return {
        "financial_record": {
            "record_id": result[0],
            "student_id": result[1],
            "student_name": result[2],
            "fee_type": result[3],
            "reason": result[4],
            "amount": result[5],
            "payment_status": result[6],
            "issued_by": result[7],
            "issued_date": result[8],
            "payment_date": result[9],
            "due_date": result[10],
            "remarks": result[11]
        },
        "message": "Financial record found successfully."
    }

def get_student_financial_history(
    tool_context: ToolContext,
):
    state = tool_context.state

    student_id = state.get("student_id")

    if not student_id:
        return {
            "message": "User not authenticated. Please login again."
        }

    conn = sqlite3.connect("auth/campusnest.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sf.record_id,
            sf.student_id,
            s.name,
            sf.fee_type,
            sf.reason,
            sf.amount,
            sf.payment_status,
            sf.issued_by,
            sf.issued_date,
            sf.payment_date,
            sf.due_date,
            sf.remarks
        FROM student_finances sf
        JOIN students s
            ON sf.student_id = s.student_id
        WHERE sf.student_id = ?
        ORDER BY sf.issued_date DESC
    """, (student_id,))

    results = cursor.fetchall()

    conn.close()

    if not results:
        return {
            "message": "Financial records not found."
        }

    financial_records = []

    for row in results:
        financial_records.append({
            "record_id": row[0],
            "student_id": row[1],
            "student_name": row[2],
            "fee_type": row[3],
            "reason": row[4],
            "amount": row[5],
            "payment_status": row[6],
            "issued_by": row[7],
            "issued_date": row[8],
            "payment_date": row[9],
            "due_date": row[10],
            "remarks": row[11]
        })

    return {
        "financial_records": financial_records,
        "message": "Financial history retrieved successfully."
    }

def track_lost_found_item(item_id: str):

    conn = sqlite3.connect("auth/campusnest.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            item_id,
            item_name,
            description,
            location_found,
            date_found,
            claimed_status,
            owner_details
        FROM lost_found
        WHERE item_id = ?
    """, (item_id,))

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return {
            "success": False,
            "message": "Item not found."
        }

    return {
        "success": True,
        "item_id": result[0],
        "item_name": result[1],
        "description": result[2],
        "location_found": result[3],
        "date_found": result[4],
        "claimed_status": result[5],
        "owner_details": result[6]
    }


def track_notification(notification_id: str):

    conn = sqlite3.connect("auth/campusnest.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            notification_id,
            incident_id,
            recipient_name,
            recipient_role,
            phone_number,
            message,
            timestamp,
            delivery_status
        FROM notification_logs
        WHERE notification_id = ?
    """, (notification_id,))

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return {
            "success": False,
            "message": "Notification not found."
        }

    return {
        "success": True,
        "notification_id": result[0],
        "incident_id": result[1],
        "recipient_name": result[2],
        "recipient_role": result[3],
        "phone_number": result[4],
        "message": result[5],
        "timestamp": result[6],
        "delivery_status": result[7]
    }


def track_leave_request(application_id: str):

    conn = sqlite3.connect("auth/campusnest.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            lr.application_id,
            lr.student_id,
            s.name,
            lr.leave_type,
            lr.start_date,
            lr.end_date,
            lr.status,
            lr.warden_remarks,
            lr.timestamp
        FROM leave_requests lr
        JOIN students s
            ON lr.student_id = s.student_id
        WHERE lr.application_id = ?
    """, (application_id,))

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return {
            "message": "Application not found."
        }

    return {
        "leave_tracking": {
            "application_id": result[0],
            "student_id": result[1],
            "student_name": result[2],
            "leave_type": result[3],
            "start_date": result[4],
            "end_date": result[5],
            "status": result[6],
            "warden_remarks": result[7],
            "timestamp": result[8]
        },
        "message": "Leave request found successfully."
    }

def get_student_leave_history(
    tool_context: ToolContext,
):
    state = tool_context.state

    student_id = state.get("student_id")

    if not student_id:
        return {
            "message": "User not authenticated. Please login again."
        }

    conn = sqlite3.connect("auth/campusnest.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            lr.application_id,
            lr.student_id,
            s.name,
            lr.leave_type,
            lr.start_date,
            lr.end_date,
            lr.status,
            lr.warden_remarks,
            lr.timestamp
        FROM leave_requests lr
        JOIN students s
            ON lr.student_id = s.student_id
        WHERE lr.student_id = ?
        ORDER BY lr.timestamp DESC
    """, (student_id,))

    results = cursor.fetchall()

    conn.close()

    if not results:
        return {
            "message": "No leave history found."
        }

    leave_history = []

    for row in results:
        leave_history.append({
            "application_id": row[0],
            "student_id": row[1],
            "student_name": row[2],
            "leave_type": row[3],
            "start_date": row[4],
            "end_date": row[5],
            "status": row[6],
            "warden_remarks": row[7],
            "timestamp": row[8]
        })

    return {
        "leave_history": leave_history,
        "message": "Leave history retrieved successfully."
    }

def get_student_incident_history(
    tool_context: ToolContext,
):
    state = tool_context.state
    student_id = state.get("student_id")

    if not student_id:
        return {
            "message": "User not authenticated. Please login again.",
            "incident_history": []
        }

    conn = sqlite3.connect("auth/campusnest.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ir.incident_id,
            s.student_id,
            s.name,
            ir.room_number,
            ir.category,
            ir.priority,
            ir.summary,
            ir.status,
            ir.created_timestamp,
            ir.assigned_personnel
        FROM incident_reports ir
        JOIN students s
            ON ir.reported_by = s.student_id
        WHERE ir.reported_by = ?
        ORDER BY ir.created_timestamp DESC
    """, (student_id,))

    results = cursor.fetchall()
    conn.close()

    if not results:
        return {
            "message": "No incident history found.",
            "incident_history": []
        }

    incident_history = []

    for row in results:
        incident_history.append({
            "incident_id": row[0],
            "student_id": row[1],
            "student_name": row[2],
            "room_number": row[3],
            "category": row[4],
            "priority": row[5],
            "summary": row[6],
            "status": row[7],
            "created_timestamp": row[8],
            "assigned_personnel": row[9]
        })

    return {
        "incident_history": incident_history,
        "message": "Here is your incident history."
    }

track_agent = LlmAgent(
    name="TrackAgent",


    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=retry_config
    ),

    tools=[
        FunctionTool(track_leave_request),
        FunctionTool(get_student_leave_history),
        FunctionTool(track_financial_record),
        FunctionTool(track_lost_found_item),
        FunctionTool(track_notification),
        FunctionTool(get_student_financial_history),
        FunctionTool(track_incident_report),
        FunctionTool(get_student_incident_history),
    ],
    output_schema=TrackingResponse,
    description="""
    Tracks leave requests, incident reports, financial status,
    lost & found items, notification delivery, and student leave history.
    """,

instruction="""
You are the Track Agent of CampusNest AI.

Your sole responsibility is STATUS TRACKING.

------------------------------------------------------------
RESPONSIBILITIES
------------------------------------------------------------

1. Track leave requests (single + history)
2. Track incident reports (single + history)
3. Track student financial records (single + history)
4. Track Lost & Found items
5. Track notification delivery

------------------------------------------------------------
AVAILABLE TOOLS
------------------------------------------------------------

- track_leave_request()
- get_student_leave_history()
- track_incident_report()
- get_student_incident_history()
- track_financial_record()
- get_student_financial_history()
- track_lost_found_item()
- track_notification()

------------------------------------------------------------
TOOL SELECTION RULES
------------------------------------------------------------

LEAVE TRACKING
- Use track_leave_request() for a SINGLE application (APPxxx)
- Use get_student_leave_history() for ALL leave records

------------------------------------------------------------

INCIDENT TRACKING
- Use track_incident_report() ONLY when Incident ID (INCxxx) is provided
- Use get_student_incident_history() when no Incident ID is provided

Examples:
- Track INC011 → track_incident_report()
- Show my incidents → get_student_incident_history()

------------------------------------------------------------

FINANCIAL TRACKING
- Use track_financial_record() for a SINGLE record (RECxxx)
- Use get_student_financial_history() for ALL financial records

------------------------------------------------------------

LOST & FOUND
- Use track_lost_found_item() only with Item ID (ITEMxxx)

------------------------------------------------------------

NOTIFICATION TRACKING
- Use track_notification() only with Notification ID (NOTxxx)

------------------------------------------------------------
GENERAL RULES
------------------------------------------------------------

1. Always choose the most specific tool first.
2. If no ID is provided, prefer history tools.
3. Never ask for ID if history tool is available.
4. All student-specific history tools use authenticated student_id automatically.
5. Always return structured results clearly.

------------------------------------------------------------
VALID STATUS VALUES
------------------------------------------------------------

Leave Requests:
- PENDING, APPROVED, REJECTED

Incident Reports:
- OPEN, CLOSED

Lost & Found:
- UNCLAIMED, CLAIMED

Notification Logs:
- SENT, DELIVERED, APPROVED, REJECTED, RESOLVED, FAILED

"""
)

track_app = App(
    name="track_agent_app",
    root_agent=track_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)