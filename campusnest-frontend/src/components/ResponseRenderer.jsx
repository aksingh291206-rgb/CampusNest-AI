import IncidentCard from "./IncidentCard";
import LeaveCard from "./LeaveCard";
import FinanceTable from "./FinanceTable";
import LeaveHistoryTable from "./LeaveHistoryTable";
import LeaveTrackingCard from "./LeaveTrackingCard";
import IncidentTrackingCard from "./IncidentTrackingCard";
import IncidentHistoryTable from "./IncidentHistoryTable";
import KnowledgeTable from "./KnowledgeTable";
import PersonnelTable from "./PersonnelTable";

function ResponseRenderer({ data }) {
    if (!data) {
        return null;
    }

    // ============================
    // Incident Cards
    // ============================
    const incident =
        data.emergency_incident ||
        data.discipline_incident ||
        data.maintenance_incident ||
        data.security_incident ||
        data.mess_incident ||
        data.sports_incident;

    if (incident) {
        return (
            <IncidentCard
                incident={incident}
                message={data.message}
            />
        );
    }

    // ============================
    // Leave Request
    // ============================
    if (data.leave_request) {
        return (
            <LeaveCard
                leave={data.leave_request}
                message={data.message}
            />
        );
    }

    // ============================
    // Leave Tracking
    // ============================
    if (data.leave_tracking) {
        return (
            <LeaveTrackingCard
                tracking={data.leave_tracking}
                message={data.message}
            />
        );
    }

    // ============================
    // Incident Tracking
    // ============================
    if (data.incident_tracking) {
        return (
            <IncidentTrackingCard
                tracking={data.incident_tracking}
                message={data.message}
            />
        );
    }

    // ============================
    // Financial Records
    // ============================
    if (data.financial_records?.length > 0) {
        return (
            <FinanceTable
                records={data.financial_records}
            />
        );
    }

    // ============================
    // Leave History
    // ============================
    if (data.leave_history?.length > 0) {
        return (
            <LeaveHistoryTable
                history={data.leave_history}
            />
        );
    }

    // ============================
    // Incident History
    // ============================
    if (data.incident_history?.length > 0) {
        return (
            <IncidentHistoryTable
                history={data.incident_history}
            />
        );
    }

    // ============================
    // Hostel Rules
    // ============================
    if (data.hostel_rules?.length > 0) {
        return (
            <KnowledgeTable
                title="Hostel Rules"
                data={data.hostel_rules}
            />
        );
    }

    // ============================
    // Mess Information
    // ============================
    if (data.mess_info?.length > 0) {
        return (
            <KnowledgeTable
                title="Mess Information"
                data={data.mess_info}
            />
        );
    }

    // ============================
    // Maintenance Information
    // ============================
    if (data.maintenance_info?.length > 0) {
        return (
            <KnowledgeTable
                title="Maintenance Information"
                data={data.maintenance_info}
            />
        );
    }

    // ============================
    // Emergency Information
    // ============================
    if (data.emergency_info?.length > 0) {
        return (
            <KnowledgeTable
                title="Emergency Information"
                data={data.emergency_info}
            />
        );
    }

    // ============================
    // Hostel Facilities
    // ============================
    if (data.facilities?.length > 0) {
        return (
            <KnowledgeTable
                title="Hostel Facilities"
                data={data.facilities}
            />
        );
    }

    // ============================
    // Administrative Information
    // ============================
    if (data.administrative_info?.length > 0) {
        return (
            <KnowledgeTable
                title="Administrative Information"
                data={data.administrative_info}
            />
        );
    }

    // ============================
    // Personnel Directory
    // ============================
    if (data.personnel?.length > 0) {
        return (
            <PersonnelTable
                personnel={data.personnel}
            />
        );
    }

    // ============================
    // Default Response
    // ============================
    return (
        <div className="whitespace-pre-wrap">
            {data.message || "No response available."}
        </div>
    );
}

export default ResponseRenderer;