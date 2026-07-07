from typing import Optional
from pydantic import BaseModel
from pydantic import BaseModel, Field


class LeaveTracking(BaseModel):
    application_id: str
    student_id: str
    student_name: str
    leave_type: str
    start_date: str
    end_date: str
    status: str
    warden_remarks: Optional[str] = None
    timestamp: Optional[str] = None


class IncidentTracking(BaseModel):
    incident_id: str
    reported_by: str
    student_name: str
    room_number: str
    category: str
    priority: str
    summary: str
    status: str
    created_timestamp: str
    assigned_personnel: str
    resolution_notes: Optional[str] = None
    closed_timestamp: Optional[str] = None


class FinancialRecord(BaseModel):
    record_id: str
    student_id: str
    student_name: str
    fee_type: str
    reason: str
    amount: float
    payment_status: str
    issued_by: str
    issued_date: str
    payment_date: Optional[str] = None
    due_date: str
    remarks: Optional[str] = None


class LostFoundTracking(BaseModel):
    item_id: str
    item_name: str
    description: str
    location_found: str
    date_found: str
    claimed_status: str
    owner_details: Optional[str] = None


class NotificationTracking(BaseModel):
    notification_id: str
    incident_id: str
    recipient_name: str
    recipient_role: str
    phone_number: str
    message: str
    timestamp: str
    delivery_status: str

class IncidentHistoryRecord(BaseModel):
    incident_id: str
    student_id: str
    student_name: str
    room_number: str
    category: str
    priority: str
    summary: str
    status: str
    created_timestamp: str
    assigned_personnel: str

class TrackingResponse(BaseModel):

    leave_tracking: Optional[LeaveTracking] = None

    incident_tracking: Optional[IncidentTracking] = None

    financial_record: Optional[FinancialRecord] = None

    financial_records: list[FinancialRecord] = Field(default_factory=list)

    lost_found_tracking: Optional[LostFoundTracking] = None

    notification_tracking: Optional[NotificationTracking] = None

    leave_history: list[LeaveTracking] = Field(default_factory=list)

    incident_history: list[IncidentHistoryRecord] = Field(default_factory=list)

    message: str