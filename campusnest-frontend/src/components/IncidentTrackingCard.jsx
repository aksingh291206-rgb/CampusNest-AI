function IncidentTrackingCard({ tracking, message }) {
    return (
        <div className="space-y-3 rounded-xl bg-slate-800 p-5 text-white">

            <h3 className="text-xl font-bold text-red-400">
                Incident Status
            </h3>

            <div>
                <strong>Incident ID:</strong> {tracking.incident_id}
            </div>

            <div>
                <strong>Reported By:</strong> {tracking.student_name}
            </div>

            <div>
                <strong>Room Number:</strong> {tracking.room_number}
            </div>

            <div>
                <strong>Category:</strong> {tracking.category}
            </div>

            <div>
                <strong>Priority:</strong> {tracking.priority}
            </div>

            <div>
                <strong>Status:</strong> {tracking.status}
            </div>

            <div>
                <strong>Assigned Personnel:</strong> {tracking.assigned_personnel}
            </div>

            <div>
                <strong>Created On:</strong> {tracking.created_timestamp}
            </div>

            <div>
                <strong>Resolution Notes:</strong>{" "}
                {tracking.resolution_notes || "Not available"}
            </div>

            {tracking.closed_timestamp && (
                <div>
                    <strong>Closed On:</strong> {tracking.closed_timestamp}
                </div>
            )}

            {message && (
                <div className="mt-4 rounded-lg bg-cyan-900/30 p-3 text-cyan-300">
                    {message}
                </div>
            )}

        </div>
    );
}

export default IncidentTrackingCard;