import sqlite3
import hashlib

from google.adk.tools import ToolContext


def verify_credentials(
    student_id: str,
    password: str,
    tool_context: ToolContext,
) -> dict:

    print("verify_credentials called")
    print(student_id)
    print(password)

    state = tool_context.state

    # Initialize session state
    state.setdefault("authenticated", False)
    state.setdefault("student_id", None)
    state.setdefault("student_name", None)
    state.setdefault("room_number", None)
    state.setdefault("auth_attempts", 0)

    # Already authenticated
    if state["authenticated"]:
        return {
            "status": "ALREADY_AUTHENTICATED",
            "student_id": state["student_id"],
            "student_name": state["student_name"],
            "room_number": state["room_number"],
        }

    # Lock after 3 failed attempts
    if state["auth_attempts"] >= 3:
        return {
            "status": "LOCKED",
            "message": "Too many failed login attempts. Please try again later.",
        }

    conn = sqlite3.connect("auth/campusnest.db")
    cursor = conn.cursor()

    # Fetch password hash
    cursor.execute("""
        SELECT password_hash
        FROM student_auth
        WHERE student_id = ?
    """, (student_id,))

    auth_row = cursor.fetchone()

    if auth_row is None:
        conn.close()
        state["auth_attempts"] += 1

        return {
            "status": "AUTH_FAILED",
            "message": "Invalid Student ID or Password.",
        }

    stored_hash = auth_row[0]
    entered_hash = hashlib.sha256(password.encode()).hexdigest()

    if entered_hash != stored_hash:
        conn.close()
        state["auth_attempts"] += 1

        return {
            "status": "AUTH_FAILED",
            "message": "Invalid Student ID or Password.",
        }

    # Fetch student details
    cursor.execute("""
        SELECT
            student_id,
            name,
            room_number
        FROM students
        WHERE student_id = ?
    """, (student_id,))

    student = cursor.fetchone()

    conn.close()

    if student is None:
        return {
            "status": "AUTH_FAILED",
            "message": "Student record not found.",
        }

    # Store session memory
    state["authenticated"] = True
    state["student_id"] = student[0]
    state["student_name"] = student[1]
    state["room_number"] = student[2]
    state["auth_attempts"] = 0

    return {
        "status": "AUTH_SUCCESS",
        "student_id": student[0],
        "student_name": student[1],
        "room_number": student[2],
    }