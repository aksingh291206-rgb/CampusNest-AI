from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.apps import ResumabilityConfig
from google.adk.models import Gemini
from google.genai import types
from dotenv import load_dotenv
from .notification_tools import send_notification
from .Report_Generator_Agent import generate_lost_found_report
from google.adk.tools import FunctionTool
import os
import sqlite3

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")


retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)

def create_lost_found_item(
    item_name: str,
    description: str,
    location_found: str,
    date_found: str
):
    conn = sqlite3.connect("auth/campusnest.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM lost_found")
    count = cursor.fetchone()[0] + 1

    item_id = f"ITEM{count:03d}"

    cursor.execute("""
        INSERT INTO lost_found (
            item_id,
            item_name,
            description,
            location_found,
            date_found,
            claimed_status,
            owner_details
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        item_id,
        item_name,
        description,
        location_found,
        date_found,
        "UNCLAIMED",
        ""
    ))

    conn.commit()
    conn.close()

    return {
        "item_id": item_id,
        "item_name": item_name,
        "description": description,
        "location_found": location_found,
        "date_found": date_found,
        "claimed_status": "UNCLAIMED",
        "owner_details": "",
        "department": "Administration",
        "assigned_personnel": "Warden",
        "message": "Lost & Found item registered successfully"
    }


def process_lost_found_workflow(
    item_name,
    description,
    location_found,
    date_found,
):
    # Step 1: Register Lost Item
    item_result = create_lost_found_item(
        item_name=item_name,
        description=description,
        location_found=location_found,
        date_found=date_found,
    )

    if "item_id" not in item_result:
        return item_result

    # Step 2: Build Notification Message
    notification_message = f"""
📦 New Lost & Found Item

Item ID: {item_result['item_id']}
Item Name: {item_result['item_name']}
Description: {item_result['description']}
Location Found: {item_result['location_found']}
Date Found: {item_result['date_found']}
Status: {item_result['claimed_status']}
Assigned To: {item_result['assigned_personnel']}
"""

    # Step 3: Send Notification
    notification_result = send_notification(
        incident_id=item_result["item_id"],
        department=item_result["department"],
        message=notification_message,
    )

    # Step 4: Generate Report
    report = generate_lost_found_report(
        item_id=item_result["item_id"]
    )

    # Step 5: Return Complete Workflow Result
    return {
        "lost_found": item_result,
        "notification": notification_result,
        "report": report,
    }


lost_found_tool = FunctionTool(process_lost_found_workflow)

Lost_and_Found_agent = LlmAgent(
    name="Lost_and_Found_agent",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=retry_config
    ),
    tools=[lost_found_tool],
    description="""   """,
    instruction="""
You are the Lost & Found Agent of CampusNest AI.

Your sole responsibility is handling LOST & FOUND requests.

----------------------------------------------------
CORE RESPONSIBILITIES
----------------------------------------------------

You handle TWO situations:

1. Registering FOUND items.
2. Assisting students who have LOST an item.

----------------------------------------------------
CASE 1 : USER FOUND AN ITEM
----------------------------------------------------

If the user has FOUND an item:

• Collect all required information.
• Validate that no required information is missing.
• Ask only for missing fields.
• Once complete, call:

process_lost_found_workflow()

This workflow will:

• Register the item
• Generate an Item ID
• Notify the Warden
• Generate a Lost & Found report
• Mark the item as UNCLAIMED

Required information:

- item_name
- description
- location_found
- date_found

Ask only for missing information.

Examples:

"What item was found?"

"Can you briefly describe the item?"

"Where was the item found?"

"When was the item found?"

Never assume missing information.

----------------------------------------------------
CASE 2 : USER LOST AN ITEM
----------------------------------------------------

If the user reports that they LOST an item:

Do NOT register a new Lost & Found entry.

Instead:

1. Ask the user to describe the lost item if necessary.

2. Explain that CampusNest maintains a registry of FOUND items.

3. Inform the user that if a matching item has already been submitted, they should contact the Hostel Warden for ownership verification.

4. Explain that after successful verification, the Warden will update the item status to CLAIMED.

Do NOT promise that a matching item exists.

Do NOT invent search results.

Do NOT create a database entry for lost items.

----------------------------------------------------
WORKFLOW RULES
----------------------------------------------------

Call process_lost_found_workflow() ONLY when registering a FOUND item.

Never call it for a LOST item.

----------------------------------------------------
RULES
----------------------------------------------------

1. Never invent information.

2. Never assume missing details.

3. Never expose database logic.

4. Never expose internal functions.

5. Never modify workflow output.

6. Never claim an item has been found unless explicitly confirmed.

7. Never create a Lost Item database record.

----------------------------------------------------
POST EXECUTION RESPONSE
----------------------------------------------------

After successful registration of a FOUND item, respond only with:

✓ Lost & Found item registered successfully.

Item ID: <item_id>

Item Name: <item_name>

Location Found:
<location_found>

Date Found:
<date_found>

Current Status:
UNCLAIMED

The Warden has been notified.

A Lost & Found report has been generated for your records.

Do not display JSON.

Do not display workflow steps.

Do not display internal function names.
""",
)

Lost_and_Found_app = App(
    name="lost_and_found_agent_app",
    root_agent=Lost_and_Found_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)
    