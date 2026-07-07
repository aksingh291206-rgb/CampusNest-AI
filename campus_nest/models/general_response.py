from pydantic import BaseModel, Field


class HostelRule(BaseModel):
    rule_id: str
    title: str
    description: str


class PersonnelRecord(BaseModel):
    id: int
    name: str
    role: str
    department: str
    contact_id: str
    availability: str
    shift: str
    contact_number: str


class MessInfo(BaseModel):
    info_id: str
    title: str
    description: str


class MaintenanceInfo(BaseModel):
    info_id: str
    title: str
    description: str


class EmergencyInfo(BaseModel):
    info_id: str
    title: str
    description: str


class Facility(BaseModel):
    facility_id: str
    title: str
    description: str


class AdministrativeInfo(BaseModel):
    info_id: str
    title: str
    description: str


class GeneralResponse(BaseModel):

    hostel_rules: list[HostelRule] = Field(default_factory=list)

    personnel: list[PersonnelRecord] = Field(default_factory=list)

    mess_info: list[MessInfo] = Field(default_factory=list)

    maintenance_info: list[MaintenanceInfo] = Field(default_factory=list)

    emergency_info: list[EmergencyInfo] = Field(default_factory=list)

    facilities: list[Facility] = Field(default_factory=list)

    administrative_info: list[AdministrativeInfo] = Field(default_factory=list)

    message: str