import sqlite3

def approve_leave_request(
    application_id: str,
    remarks: str = "Approved by Warden"
    ):

    conn = sqlite3.connect("auth/campusnest.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE leave_requests
        SET
            status = ?,
            warden_remarks = ?
        WHERE application_id = ?
        """,
        (
            "APPROVED",
            remarks,
            application_id
        )
    )

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return {
            "success": False,
            "message": f"Application {application_id} not found."
        }

    conn.close()

    return {
        "success": True,
        "application_id": application_id,
        "status": "APPROVED",
        "message": "Leave request approved successfully."
    }

def reject_leave_request(
        application_id: str,
        remarks: str
        ):

    conn = sqlite3.connect("auth/campusnest.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE leave_requests
        SET
            status = ?,
            warden_remarks = ?
        WHERE application_id = ?
        """,
        (
            "REJECTED",
            remarks,
            application_id
        )
    )

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return {
            "success": False,
            "message": f"Application {application_id} not found."
        }

    conn.close()

    return {
        "success": True,
        "application_id": application_id,
        "status": "REJECTED",
        "message": "Leave request rejected successfully."
    }