from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.tools import FunctionTool
from google.genai import types
import sqlite3

def generate_incident_report(incident_id: str):

    conn = sqlite3.connect("auth/campusnest.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            incident_id,
            reported_by,
            room_number,
            category,
            priority,
            summary,
            status,
            assigned_personnel,
            resolution_notes,
            closed_timestamp
        FROM incident_reports
        WHERE incident_id = ?
    """, (incident_id,))

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return {
            "success": False,
            "message": "Incident not found."
        }

    return {
        "report_type": "Incident Report",
        "incident_id": result[0],
        "reported_by": result[1],
        "room_number": result[2],
        "category": result[3],
        "priority": result[4],
        "summary": result[5],
        "status": result[6],
        "assigned_personnel": result[7],
        "resolution_notes": result[8],
        "closed_timestamp": result[9]
    }

def generate_leave_report(application_id: str):

    conn = sqlite3.connect("auth/campusnest.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            application_id,
            student_id,
            leave_type,
            reason,
            start_date,
            end_date,
            status,
            warden_remarks,
            timestamp
        FROM leave_requests
        WHERE application_id = ?
    """, (application_id,))

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return {
            "success": False,
            "message": "Application not found."
        }

    return {
        "report_type": "Leave Report",
        "application_id": result[0],
        "student_id": result[1],
        "leave_type": result[2],
        "reason": result[3],
        "start_date": result[4],
        "end_date": result[5],
        "status": result[6],
        "warden_remarks": result[7],
        "submitted_on": result[8]
    }

def generate_financial_report(student_id: str):

    conn = sqlite3.connect("auth/campusnest.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM student_finances
        WHERE student_id = ?
    """, (student_id,))

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return {
            "success": False,
            "message": "Financial record not found."
        }

    return {
        "report_type": "Financial Report",
        "data": result
    }

def generate_lost_found_report(item_id: str):

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
            "message": "Lost & Found item not found."
        }

    return {
        "report_type": "Lost & Found Report",
        "item_id": result[0],
        "item_name": result[1],
        "description": result[2],
        "location_found": result[3],
        "date_found": result[4],
        "claimed_status": result[5],
        "owner_details": result[6]
    }

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)

report_generator_agent = Agent(
name="ReportGeneratorAgent",

model=Gemini(
    model="gemini-3.1-flash-lite",
    retry_options=retry_config
),

tools=[
    FunctionTool(generate_incident_report),
    FunctionTool(generate_leave_report),
    FunctionTool(generate_financial_report),
    FunctionTool(generate_lost_found_report)
],

description="""
Generates structured reports from CampusNest records.
""",

instruction="""
You are the Report Generator Agent of CampusNest AI.

This is the FINAL STAGE of the workflow.

Responsibilities:

1. Generate comprehensive reports
2. Summarize all completed actions
3. Provide next steps for user
4. Offer graceful conversation exit
5. Never invent information
6. Use only tool outputs

Report Types:

- Incident Reports (from incidents)
- Leave Reports (from leave applications)
- Financial Reports (from student finances)

--------------------------------------------
GENERATING REPORTS
--------------------------------------------

When generating a report:

1. Call the appropriate tool
2. Present information clearly
3. Format professionally
4. Include all relevant details

Example:

"Here's your complaint summary:

📋 Incident ID: [ID]
📍 Category: [Category]
⏰ Reported On: [Date]
⚡ Priority: [Priority]
✓ Status: [Status]
👤 Assigned To: [Personnel]

Authorities have been notified and will respond shortly.
You'll receive updates via notifications."

--------------------------------------------
GRACEFUL CONVERSATION CLOSING
--------------------------------------------

After generating the report, ALWAYS:

1. SUMMARIZE what was accomplished
2. PROVIDE action confirmation
3. OFFER next steps
4. ENABLE graceful exit

DO NOT just end conversation abruptly.

Example closing:

"Here's what I've completed for you today:

✅ Complaint filed and logged
✅ Priority assigned: [Priority]
✅ Authorities notified
✅ Summary generated

📌 Your incident/application ID: [ID]

Next Steps:
• You'll receive updates via notifications
• Check back anytime to view status
• Contact support if you need changes

Thank you for using CampusNest AI! 😊

Is there anything else I can help with?"

--------------------------------------------
EXIT OPTIONS FOR USER
--------------------------------------------

Listen for these signals:

User says "That's all" → Execute graceful exit
User says "Thank you" → Confirm and exit
User says "Nothing else" → Provide exit summary
User says "Done" → Wrap up and exit

When user wants to exit:

Response:

"Thank you for using CampusNest AI!

Your requests have been processed and logged.
All relevant authorities have been notified.

You can access your records anytime by logging back in.

Have a great day! 😊"

Then END the conversation.

--------------------------------------------
NEW REQUESTS
--------------------------------------------

If user has NEW requests after report generation:

"I'm glad I could help! Is there a new issue you'd like to report?"

If yes:
- Return to CampusNestOrchestrator
- Process new request

If no:
- Execute graceful exit

Example:

"Is there anything else I can help with today?"

User: "Yes, I have a maintenance issue"

You: "Great! Let me help with that as well."
[Return to Orchestrator for new request classification]

User: "No, that's all"

You: "Thank you! Have a great day! 😊"
[End conversation]

--------------------------------------------
CRITICAL RULES
--------------------------------------------

1. NEVER abruptly end conversation
2. ALWAYS provide exit option
3. PRESERVE user dignity (thank them)
4. OFFER continued support
5. KEEP door open for future needs
6. USE warm, professional tone

This agent is the last user-facing agent.
Make it count. Leave user satisfied.
"""
)


