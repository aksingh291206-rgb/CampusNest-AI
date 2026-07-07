function IncidentCard({ incident, message }) {

    const statusColor =
        incident.status === "OPEN"
            ? "text-red-400"
            : "text-green-400";

    const priorityColor =
        incident.priority.toLowerCase() === "critical"
            ? "text-red-400"
            : incident.priority.toLowerCase() === "high"
            ? "text-orange-400"
            : "text-yellow-400";

    return (
        <div className="bg-slate-900 border border-cyan-700 rounded-xl p-5 space-y-4">

            <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold text-cyan-300">
                    🚨 {incident.category}
                </h2>

                <span className={statusColor}>
                    {incident.status}
                </span>
            </div>

            <div className="grid grid-cols-2 gap-3 text-sm">

                <div>
                    <span className="text-gray-400">Incident ID</span>
                    <div>{incident.incident_id}</div>
                </div>

                <div>
                    <span className="text-gray-400">Student</span>
                    <div>{incident.student_name}</div>
                </div>

                <div>
                    <span className="text-gray-400">Room</span>
                    <div>{incident.room_number}</div>
                </div>

                <div>
                    <span className="text-gray-400">Priority</span>
                    <div className={priorityColor}>
                        {incident.priority}
                    </div>
                </div>

                <div className="col-span-2">
                    <span className="text-gray-400">Assigned To</span>
                    <div>{incident.assigned_personnel}</div>
                </div>

            </div>

            <div className="border-t border-slate-700 pt-3">

                <div className="text-gray-400 mb-1">
                    Assistant Message
                </div>

                <div className="text-cyan-100">
                    {message}
                </div>

            </div>

        </div>
    );
}

export default IncidentCard;