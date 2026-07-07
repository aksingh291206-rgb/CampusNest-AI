import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

TWILIO_WHATSAPP_TO = os.getenv("TWILIO_WHATSAPP_TO")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")

DB_PATH = "auth/campusnest.db"
    

def _format_whatsapp_number(number: str):
    if not number:
        return None

    number = number.strip()
    if number.startswith("whatsapp:"):
        return number
    if number.startswith("+"):
        return f"whatsapp:{number}"

    digits = "".join(ch for ch in number if ch.isdigit())
    if digits:
        return f"whatsapp:+{digits}"

    return None


def _send_whatsapp_message(phone_number: str, message: str):
    formatted_phone = _format_whatsapp_number(phone_number) or TWILIO_WHATSAPP_TO
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    msg = client.messages.create(
        body=message,
        from_=TWILIO_WHATSAPP_FROM,
        to=formatted_phone
    )
    return msg.sid


def generate_notification_id():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT notification_id
        FROM notification_logs
        ORDER BY notification_id DESC
        LIMIT 1
        """
    )

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return "NOT001"

    last_id = result[0]

    number = int(last_id.replace("NOT", ""))

    return f"NOT{number + 1:03d}"

def get_personnel_by_department(department: str):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            name,
            role,
            phone_number,
            id
        FROM personnel
        WHERE department = ?
        LIMIT 1
        """,
        (department,)
    )

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return {
            "success": False,
            "message": f"No personnel found for department: {department}"
        }

    return {
        "success": True,
        "name": result[0],
        "role": result[1],
        "phone_number": result[2],
        "id": result[3]
    }

def create_notification_log(
    incident_id: str,
    recipient_name: str,
    recipient_role: str,
    phone_number: str,
    message: str,
    delivery_status: str
    ):

    notification_id = generate_notification_id()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO notification_logs (
            notification_id,
            incident_id,
            recipient_name,
            recipient_role,
            phone_number,
            message,
            timestamp,
            delivery_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            notification_id,
            incident_id,
            recipient_name,
            recipient_role,
            phone_number,
            message,
            datetime.now().isoformat(),
            delivery_status
        )
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "notification_id": notification_id,
        "delivery_status": delivery_status
    }

def send_notification(
    incident_id: str,
    department: str,
    message: str
    ):

    authority = get_personnel_by_department(department)

    if not authority["success"]:
        return authority

    recipient_name = authority["name"]
    recipient_role = authority["role"]
    recipient_phone = _format_whatsapp_number(authority.get("phone_number")) or TWILIO_WHATSAPP_TO

    try:
        message_sid = _send_whatsapp_message(recipient_phone, message)
        delivery_status = "SENT"
    except Exception as exc:
        delivery_status = f"FAILED: {exc}"
        message_sid = None

    log_result = create_notification_log(
        incident_id=incident_id,
        recipient_name=recipient_name,
        recipient_role=recipient_role,
        phone_number=recipient_phone,
        message=message,
        delivery_status=delivery_status
    )

    result = {
        "success": delivery_status == "SENT",
        "notification_id": log_result["notification_id"],
        "recipient_name": recipient_name,
        "recipient_role": recipient_role,
        "phone_number": recipient_phone,
        "delivery_status": delivery_status
    }
    if message_sid:
        result["message_sid"] = message_sid

    return result
