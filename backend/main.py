from fastapi import FastAPI
from fastapi import Request
import sqlite3
from datetime import datetime
import re
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
from twilio.twiml.messaging_response import MessagingResponse
from fastapi.responses import Response
import requests

app = FastAPI()

# Allow your React app to access this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "CampusNest Backend is running!"
    }


@app.post("/login")
async def login():

    async with httpx.AsyncClient(timeout=30) as client:

        # Step 1: Create a new ADK session
        session_response = await client.post(
            "http://127.0.0.1:8000/apps/Campus_Nest_AI/users/user/sessions"
        )

        session = session_response.json()
        session_id = session["id"]

        print("New Session ID:", session_id)

        # Step 2: Send Hello
        payload = {
            "appName": "Campus_Nest_AI",
            "userId": "user",
            "sessionId": session_id,
            "newMessage": {
                "role": "user",
                "parts": [
                    {
                        "text": "Hello"
                    }
                ]
            },
            "streaming": False
        }

        run_response = await client.post(
        "http://127.0.0.1:8000/run_sse",
        json=payload,
        headers={
            "Accept": "text/event-stream"
        }
    )

    print("STATUS:", run_response.status_code)
    print("BODY:")
    print(run_response.text)

    response_text = run_response.text

    message = ""

    for line in response_text.splitlines():

        if line.startswith("data: "):

            try:
                data = json.loads(line[6:])

                if "content" in data:

                    parts = data["content"].get("parts", [])

                    if parts and "text" in parts[0]:

                        message = parts[0]["text"]
                        break

            except Exception:
                pass

    return {
        "sessionId": session_id,
        "message": message
    }

@app.post("/send-student-id")
async def send_student_id(data: dict):

    payload = {
        "appName": "Campus_Nest_AI",
        "userId": "user",
        "sessionId": data["sessionId"],
        "newMessage": {
            "role": "user",
            "parts": [
                {
                    "text": data["studentId"]
                }
            ]
        },
        "streaming": False
    }

    async with httpx.AsyncClient(timeout=30) as client:

        response = await client.post(
            "http://127.0.0.1:8000/run_sse",
            json=payload,
            headers={
                "Accept": "text/event-stream"
            }
        )

    response_text = response.text

    message = ""

    for line in response_text.splitlines():

        if line.startswith("data: "):

            try:
                data = json.loads(line[6:])

                if "content" in data:

                    parts = data["content"].get("parts", [])

                    if parts and "text" in parts[0]:

                        message = parts[0]["text"]
                        break

            except Exception:
                pass

    return {
        "message": message
    }

@app.post("/send-password")
async def send_password(data: dict):

    payload = {
        "appName": "Campus_Nest_AI",
        "userId": "user",
        "sessionId": data["sessionId"],
        "newMessage": {
            "role": "user",
            "parts": [
                {
                    "text": data["password"]
                }
            ]
        },
        "streaming": False
    }

    async with httpx.AsyncClient(timeout=30) as client:

        response = await client.post(
            "http://127.0.0.1:8000/run_sse",
            json=payload,
            headers={
                "Accept": "text/event-stream"
            }
        )

    response_text = response.text

    message = ""

    for line in response_text.splitlines():

        if line.startswith("data: "):

            try:
                data = json.loads(line[6:])

                if "content" in data:

                    parts = data["content"].get("parts", [])

                    if parts and "text" in parts[0]:

                        message = parts[0]["text"]
                        break

            except Exception:
                pass

    return {
        "message": message
    }

@app.post("/chat")
async def chat(data: dict):

    payload = {
        "appName": "Campus_Nest_AI",
        "userId": "user",
        "sessionId": data["sessionId"],
        "newMessage": {
            "role": "user",
            "parts": [
                {
                    "text": data["message"]
                }
            ]
        },
        "streaming": False
    }

    async with httpx.AsyncClient(timeout=30) as client:

        response = await client.post(
            "http://127.0.0.1:8000/run_sse",
            json=payload,
            headers={
                "Accept": "text/event-stream"
            }
        )

    response_text = response.text

    message = ""

    for line in response_text.splitlines():

        if not line.startswith("data: "):
            continue

        try:
            event = json.loads(line[6:])

            if "content" not in event:
                continue

            parts = event["content"].get("parts", [])

            if parts and "text" in parts[0]:
                message = parts[0]["text"]

        except Exception:
            continue
    
    print(type(message))
    print(message)
    
    # Try to convert JSON string returned by the LLM into a Python dict
    try:
        return json.loads(message)
    except json.JSONDecodeError:
        return {
            "message": message
        }
    
@app.post("/chat")
async def chat(data: dict):

    payload = {
        "appName": "Campus_Nest_AI",
        "userId": "user",
        "sessionId": data["sessionId"],
        "newMessage": {
            "role": "user",
            "parts": [
                {
                    "text": data["message"]
                }
            ]
        },
        "streaming": False
    }

    async with httpx.AsyncClient(timeout=120) as client:

        response = await client.post(
            "http://127.0.0.1:8000/run_sse",
            json=payload,
            headers={
                "Accept": "text/event-stream"
            }
        )

    response_text = response.text

    message = ""

    for line in response_text.splitlines():

        if line.startswith("data: "):

            try:

                event = json.loads(line[6:])

                if "content" in event:

                    parts = event["content"].get("parts", [])

                    if parts and "text" in parts[0]:

                        message = parts[0]["text"]

            except:
                pass

    try:
        parsed_message = json.loads(message)
        return parsed_message

    except json.JSONDecodeError:
        print(type(message))
        print(message)
        return {
            "message": message
        }
    
    

def detect_action(text: str):

    text = text.lower()

    if any(word in text for word in ["approve", "approved", "accept"]):
        return "APPROVED"

    if any(word in text for word in ["reject", "rejected", "decline"]):
        return "REJECTED"

    if any(word in text for word in ["close", "closed", "resolve", "resolved", "fix"]):
        return "CLOSED"

    if any(word in text for word in ["claim", "claimed"]):
        return "CLAIMED"

    return None


def extract_reference_id(text: str):

    match = re.search(r"\b(INC\d+|APP\d+|ITEM\d+)\b", text, re.IGNORECASE)

    return match.group(1).upper() if match else None


@app.post("/whatsapp-webhook")
async def whatsapp_webhook(request: Request):

    form = await request.form()

    sender = form.get("From")
    message = form.get("Body", "")

    # 🧠 Safe cleanup (IMPORTANT FIX)
    message = (message or "").encode("utf-8", "ignore").decode("utf-8").strip()

    print("RAW MESSAGE RECEIVED:", message)

    ref_id = extract_reference_id(message)
    action = detect_action(message)

    print("PARSED REF ID:", ref_id)
    print("PARSED ACTION:", action)

    conn = sqlite3.connect("../auth/campusnest.db")
    cursor = conn.cursor()

    response_text = None

    # ====================================================
    # VALIDATION GATE (NO SILENT FAIL)
    # ====================================================

    if not ref_id or not action:
        response_text = "❌ Invalid command. Use: approve APP001 / reject APP001"

    # ====================================================
    # LEAVE REQUESTS
    # ====================================================

    elif ref_id.startswith("APP"):

        cursor.execute("""
            SELECT application_id, status
            FROM leave_requests
            WHERE application_id = ?
        """, (ref_id,))

        row = cursor.fetchone()
        print("DB RECORD FOUND:", row)

        if not row:
            response_text = f"❌ {ref_id} not found in system"

        else:

            if action == "APPROVED":

                cursor.execute("""
                    UPDATE leave_requests
                    SET status = ?,
                        warden_remarks = ?,
                        timestamp = ?
                    WHERE application_id = ?
                """, (
                    "APPROVED",
                    f"Approved via WhatsApp by {sender}",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ref_id
                ))

            elif action == "REJECTED":

                cursor.execute("""
                    UPDATE leave_requests
                    SET status = ?,
                        warden_remarks = ?,
                        timestamp = ?
                    WHERE application_id = ?
                """, (
                    "REJECTED",
                    f"Rejected via WhatsApp by {sender}",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ref_id
                ))

            conn.commit()
            print("ROWS AFFECTED:", cursor.rowcount)

            print("📢 Triggering Leave Request Agent")
            response_text = f"✅ {ref_id} has been {action}"

    # ====================================================
    # INCIDENT REPORTS
    # ====================================================

    elif ref_id.startswith("INC"):

        cursor.execute("""
            SELECT incident_id, status
            FROM incident_reports
            WHERE incident_id = ?
        """, (ref_id,))

        row = cursor.fetchone()

        if not row:
            response_text = f"❌ {ref_id} not found in system"

        else:

            if action == "CLOSED":

                cursor.execute("""
                    UPDATE incident_reports
                    SET status = ?,
                        resolution_notes = ?,
                        closed_timestamp = ?
                    WHERE incident_id = ?
                """, (
                    "CLOSED",
                    f"Closed via WhatsApp by {sender}",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ref_id
                ))

                conn.commit()

            print("📢 Triggering Incident Agent")
            response_text = f"✅ {ref_id} has been {action}"

    # ====================================================
    # LOST & FOUND
    # ====================================================

    elif ref_id.startswith("ITEM"):

        cursor.execute("""
            SELECT item_id, claimed_status
            FROM lost_found
            WHERE item_id = ?
        """, (ref_id,))

        row = cursor.fetchone()

        if not row:
            response_text = f"❌ {ref_id} not found in system"

        else:

            if action == "CLAIMED":

                cursor.execute("""
                    UPDATE lost_found
                    SET claimed_status = ?,
                        owner_details = ?
                    WHERE item_id = ?
                """, (
                    "CLAIMED",
                    f"Claimed via WhatsApp by {sender}",
                    ref_id
                ))

                conn.commit()

            print("📢 Triggering Lost & Found Agent")
            response_text = f"✅ {ref_id} has been {action}"

    conn.close()

    # ====================================================
    # WHATSAPP RESPONSE (GUARANTEED)
    # ====================================================

    from twilio.twiml.messaging_response import MessagingResponse
    from fastapi.responses import Response

    response = MessagingResponse()
    response.message(response_text)

    return Response(content=str(response), media_type="application/xml")

@app.post("/logout")
async def logout(data: dict):

    session_id = data["sessionId"]

    # TODO:
    # Clear the ADK session / authentication state here

    return {
        "message": "Logged out successfully."
    }