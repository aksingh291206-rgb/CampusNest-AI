from .Leave_Agent import create_leave_request
from .notification_tools import send_notification
from .Report_Generator_Agent import generate_leave_report

def process_leave_workflow(
    student_id: str,
    leave_type: str,
    start_date: str,
    end_date: str,
    reason: str,
):
    leave_result = create_leave_request(
    student_id=student_id,
    leave_type=leave_type,
    start_date=start_date,
    end_date=end_date,
    reason=reason,
)
    if "application_id" not in leave_result:
        return leave_result
    
    notification_message = f"""
🚨 New Leave Request

Application ID: {leave_result["application_id"]}
Student ID: {leave_result["student_id"]}
Leave Type: {leave_result["leave_type"]}
Start Date: {leave_result["start_date"]}
End Date: {leave_result["end_date"]}
Reason: {leave_result["reason"]}
Status: {leave_result["status"]}
"""
    notification_result = send_notification(
    incident_id=leave_result["application_id"],
    department=leave_result["department"],
    message=notification_message,
)
    if not notification_result["success"]:
        return {
            "leave_request": leave_result,
            "notification": notification_result,
        }
    
    report_result = generate_leave_report(
    leave_result["application_id"]
)
    return {
    "leave_request": leave_result,
    "notification": notification_result,
    "report": report_result,
}