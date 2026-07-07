from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from dotenv import load_dotenv
import sqlite3
from google.adk.tools import ToolContext
import os
from google.adk.tools import FunctionTool
from campus_nest.models.general_response import GeneralResponse


load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")


retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)

DB_PATH = "auth/campusnest.db"

# ------------------------------------------------------------
# 🔧 DB Helper
# ------------------------------------------------------------
def get_connection():
    return sqlite3.connect(DB_PATH)


# ------------------------------------------------------------
# 🔒 PRIVATE DATA HELPERS (Student-scoped)
# ------------------------------------------------------------

def get_student_id(tool_context: ToolContext):
    student_id = tool_context.state.get("student_id")
    if not student_id:
        return None, {"message": "User not authenticated. Please login again."}
    return student_id, None


def get_student_financial_history(tool_context: ToolContext):
    student_id, error = get_student_id(tool_context)
    if error:
        return error

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            record_id, student_id, fee_type, reason, amount,
            payment_status, issued_by, issued_date,
            payment_date, due_date, remarks
        FROM student_finances
        WHERE student_id = ?
        ORDER BY issued_date DESC
    """, (student_id,))

    rows = cursor.fetchall()
    conn.close()

    return {
        "financial_records": [
            {
                "record_id": r[0],
                "student_id": r[1],
                "fee_type": r[2],
                "reason": r[3],
                "amount": r[4],
                "payment_status": r[5],
                "issued_by": r[6],
                "issued_date": r[7],
                "payment_date": r[8],
                "due_date": r[9],
                "remarks": r[10],
            }
            for r in rows
        ],
        "message": "Financial history retrieved successfully."
    }


def get_student_incident_history(tool_context: ToolContext):
    student_id, error = get_student_id(tool_context)
    if error:
        return error

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ir.incident_id,
            s.name,
            ir.room_number,
            ir.category,
            ir.priority,
            ir.summary,
            ir.status,
            ir.created_timestamp,
            ir.assigned_personnel
        FROM incident_reports ir
        JOIN students s ON ir.reported_by = s.student_id
        WHERE ir.reported_by = ?
        ORDER BY ir.created_timestamp DESC
    """, (student_id,))

    rows = cursor.fetchall()
    conn.close()

    return {
        "incident_history": [
            {
                "incident_id": r[0],
                "student_name": r[1],
                "room_number": r[2],
                "category": r[3],
                "priority": r[4],
                "summary": r[5],
                "status": r[6],
                "created_timestamp": r[7],
                "assigned_personnel": r[8],
            }
            for r in rows
        ],
        "message": "Incident history retrieved successfully."
    }


def get_student_leave_history(tool_context: ToolContext):
    student_id, error = get_student_id(tool_context)
    if error:
        return error

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            application_id, student_id, leave_type,
            start_date, end_date, status,
            warden_remarks, timestamp
        FROM leave_requests
        WHERE student_id = ?
        ORDER BY timestamp DESC
    """, (student_id,))

    rows = cursor.fetchall()
    conn.close()

    return {
        "leave_history": [
            {
                "application_id": r[0],
                "student_id": r[1],
                "leave_type": r[2],
                "start_date": r[3],
                "end_date": r[4],
                "status": r[5],
                "warden_remarks": r[6],
                "timestamp": r[7],
            }
            for r in rows
        ],
        "message": "Leave history retrieved successfully."
    }


# ------------------------------------------------------------
# 📖 PUBLIC DATA HELPERS (No restrictions)
# ------------------------------------------------------------

def get_hostel_rules():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            rule_id,
            title,
            description
        FROM hostel_rules
        ORDER BY rule_id
    """)

    rows = cursor.fetchall()

    conn.close()

    return {
        "hostel_rules": [
            {
                "rule_id": r[0],
                "title": r[1],
                "description": r[2]
            }
            for r in rows
        ],
        "message": "Hostel rules retrieved successfully."
    }


def get_mess_info():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            info_id,
            title,
            description
        FROM mess_knowledge_base
        ORDER BY info_id
    """)

    rows = cursor.fetchall()

    conn.close()

    return {
        "mess_info": [
            {
                "info_id": r[0],
                "title": r[1],
                "description": r[2]
            }
            for r in rows
        ],
        "message": "Mess information retrieved successfully."
    }


def get_maintenance_info():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            info_id,
            title,
            description
        FROM maintenance_knowledge_base
        ORDER BY info_id
    """)

    rows = cursor.fetchall()

    conn.close()

    return {
        "maintenance_info": [
            {
                "info_id": r[0],
                "title": r[1],
                "description": r[2]
            }
            for r in rows
        ],
        "message": "Maintenance information retrieved successfully."
    }

def get_administrative_info():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            info_id,
            title,
            description
        FROM administrative_info
        ORDER BY info_id
    """)

    rows = cursor.fetchall()

    conn.close()

    return {
        "administrative_info": [
            {
                "info_id": r[0],
                "title": r[1],
                "description": r[2]
            }
            for r in rows
        ],
        "message": "Administrative information retrieved successfully."
    }

def get_emergency_info():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            info_id,
            title,
            description
        FROM emergency_knowledge_base
        ORDER BY info_id
    """)

    rows = cursor.fetchall()

    conn.close()

    return {
        "emergency_info": [
            {
                "info_id": r[0],
                "title": r[1],
                "description": r[2]
            }
            for r in rows
        ],
        "message": "Emergency information retrieved successfully."
    }


def get_hostel_facilities():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            facility_id,
            facility_name,
            description
        FROM hostel_facilities
        ORDER BY facility_id
    """)

    rows = cursor.fetchall()

    conn.close()

    return {
        "facilities": [
            {
                "facility_id": r[0],
                "title": r[1],          # Keep "title" for frontend consistency
                "description": r[2]
            }
            for r in rows
        ],
        "message": "Hostel facilities retrieved successfully."
    }


def get_personnel_directory():
    print("get_personnel_directory() tool called")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            role,
            department,
            contact_id,
            availability_status,
            duty_shift,
            phone_number
        FROM personnel
        ORDER BY role
    """)

    rows = cursor.fetchall()

    conn.close()

    return {
        "personnel": [
            {
                "id": r[0],
                "name": r[1],
                "role": r[2],
                "department": r[3],
                "contact_id": r[4],
                "availability": r[5],      # Keep existing frontend key
                "shift": r[6],             # Keep existing frontend key
                "contact_number": r[7]     # Keep existing frontend key
            }
            for r in rows
        ],
        "message": "Personnel directory retrieved successfully."
    }

# ------------------------------------------------------------
# 🔒 PRIVATE STUDENT TOOLS
# ------------------------------------------------------------

financial_tool = FunctionTool(get_student_financial_history)

incident_tool = FunctionTool(get_student_incident_history)

leave_tool = FunctionTool(get_student_leave_history)


# ------------------------------------------------------------
# 📖 PUBLIC KNOWLEDGE BASE TOOLS
# ------------------------------------------------------------

hostel_rules_tool = FunctionTool(get_hostel_rules)

mess_tool = FunctionTool(get_mess_info)

maintenance_tool = FunctionTool(get_maintenance_info)

emergency_tool = FunctionTool(get_emergency_info)

facilities_tool = FunctionTool(get_hostel_facilities)

personnel_tool = FunctionTool(get_personnel_directory)

administrative_tool = FunctionTool(get_administrative_info)



general_agent = Agent(
    name="GeneralAgent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=retry_config
    ),
    tools=[
    financial_tool,
    incident_tool,
    leave_tool,
    hostel_rules_tool,
    mess_tool,
    maintenance_tool,
    emergency_tool,
    facilities_tool,
    personnel_tool,
    administrative_tool,
    ],
    output_schema=GeneralResponse,

    description="You are a General Agent. Your task is to assist with general inquiries.",
    instruction="""
You are the General Agent of CampusNest AI, acting as both a Greeter (front desk welcome assistant) and a Receptionist (information router and retrieval agent).

Your role is to warmly welcome users, understand their intent, and route every request to the correct tool. You NEVER fabricate information and NEVER answer without tools when a tool exists.

You are the first point of contact inside CampusNest AI.

🌟 CORE PERSONALITIES
👋 Greeter Role
Welcome users politely on first interaction or when context is new.
Maintain a calm, helpful, hostel-front-desk tone.
Acknowledge user intent before taking action.
Keep greetings short and natural.

Example behavior:

“Welcome to CampusNest. How can I help you today?”
“Sure, I can help you with that.”
🧭 Receptionist Role
Understand user intent and route it to the correct tool.
Clarify briefly if the request is ambiguous.
Act as a smart switchboard between user and hostel systems.

You do NOT answer directly if a tool exists.

🚨 CORE RULES (UNCHANGED)
NEVER invent information.
NEVER fabricate database records.
NEVER answer from memory when a tool exists.
ALWAYS use the appropriate tool.
NEVER write SQL.
NEVER manually construct structured data.
ONLY return tool-generated information.
🔐 AUTHENTICATION RULES
Use session state to identify authenticated student.
Never ask for another student’s ID.
If not authenticated:
Politely ask user to login again before proceeding.
🧾 PRIVATE DATA RULES

Private tools (authenticated only):

get_student_financial_history()
get_student_leave_history()
get_student_incident_history()

Never expose another student’s data.

🌍 PUBLIC INFORMATION (TOOL DRIVEN)

Always use tools for:

Hostel Rules → get_hostel_rules()
Personnel Directory → get_personnel_directory()
Hostel Facilities → get_hostel_facilities()
Mess Information → get_mess_info()
Maintenance Information → get_maintenance_info()
Emergency Information → get_emergency_info()

Never answer from memory.

🧠 TOOL SELECTION RULES
📌 Hostel Rules

Trigger keywords:

rules, curfew, visitor policy, regulations, hostel policies, anti-ragging, mess rules, internet rules

→ ALWAYS call:
get_hostel_rules()

👥 Personnel Directory

Keywords:

staff, warden, guards, mess secretary, contacts, administration

→ ALWAYS call:
get_personnel_directory()

🏠 Facilities

Keywords:

facilities, amenities, WiFi, sports, recreation, services

→ ALWAYS call:
get_hostel_facilities()

🍽 Mess Info

Keywords:

mess, food, menu, breakfast, lunch, dinner, mess complaint, timings

→ ALWAYS call:
get_mess_info()

🔧 Maintenance

Keywords:

repair, plumbing, electrician, complaint, maintenance

→ ALWAYS call:
get_maintenance_info()

🚨 Emergency

Keywords:

emergency, ambulance, hospital, fire, evacuation

→ ALWAYS call:
get_emergency_info()

💰 Student Financial Data

Keywords:

my fees, dues, payments, balance, fines

→ ALWAYS call:
get_student_financial_history()

🧾 Leave Data

Keywords:

my leave, leave history, leave requests

→ ALWAYS call:
get_student_leave_history()

📄 Incident Data

Keywords:

my complaints, incidents, incident history

→ ALWAYS call:
get_student_incident_history()

📋 LIST / SHOW ALL RULE

If user asks:

list all
show all
display all
complete list
full information

👉 ALWAYS call the relevant tool directly.

Never summarize from memory.

🧭 RECEPTIONIST BEHAVIOR FLOW

When a user sends a message:

👋 If first interaction → greet briefly
🧠 Understand intent
🧭 Route to correct tool
📦 Return only tool output
💬 Add minimal human-friendly framing ONLY if needed
❓ AMBIGUITY RULE

If request is unclear:

Ask a short clarification question
Do NOT guess
🚫 STRICT PROHIBITIONS
No hallucination
No SQL
No direct DB access
No fabricated structured responses
No cross-student data leaks
🎯 FINAL PRINCIPLE

You are a front desk receptionist powered by tools, not a knowledge model.

Your job is:

Welcome the user 👋
Understand intent 🧭
Call the right tool 🧠
Present tool output clearly 📦

Nothing more. Nothing less.

""")