from pydantic import BaseModel


class LeaveRequest(BaseModel):
    application_id: str
    student_id: str
    student_name: str
    leave_type: str
    start_date: str
    end_date: str
    reason: str
    department: str
    status: str


class LeaveCreateResponse(BaseModel):
    leave_request: LeaveRequest
    message: str