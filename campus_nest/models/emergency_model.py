from pydantic import BaseModel


class EmergencyIncident(BaseModel):
    incident_id: str
    reported_by: str
    student_name: str
    room_number: str
    category: str
    priority: str
    summary: str
    department: str
    assigned_personnel: str
    status: str


class EmergencyCreateResponse(BaseModel):
    emergency_incident: EmergencyIncident
    message: str