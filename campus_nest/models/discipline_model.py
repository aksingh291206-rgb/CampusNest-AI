from pydantic import BaseModel


class DisciplineIncident(BaseModel):
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


class DisciplineCreateResponse(BaseModel):
    discipline_incident: DisciplineIncident
    message: str