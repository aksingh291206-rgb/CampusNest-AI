function IncidentHistoryTable({ history }) {
    return (
        <div className="space-y-4">

            <h2 className="text-xl font-bold text-cyan-400">
                My Incident History
            </h2>

            <div className="overflow-x-auto">
                <table className="min-w-full border border-slate-700 text-left">

                    <thead className="bg-slate-800 text-cyan-300">
                        <tr>
                            <th className="p-3">Incident ID</th>
                            <th className="p-3">Category</th>
                            <th className="p-3">Priority</th>
                            <th className="p-3">Status</th>
                            <th className="p-3">Assigned To</th>
                            <th className="p-3">Created</th>
                        </tr>
                    </thead>

                    <tbody>
                        {history.map((incident) => (
                            <tr
                                key={incident.incident_id}
                                className="border-t border-slate-700"
                            >
                                <td className="p-3">{incident.incident_id}</td>
                                <td className="p-3">{incident.category}</td>
                                <td className="p-3">{incident.priority}</td>
                                <td className="p-3">{incident.status}</td>
                                <td className="p-3">{incident.assigned_personnel}</td>
                                <td className="p-3">{incident.created_timestamp}</td>
                            </tr>
                        ))}
                    </tbody>

                </table>
            </div>

        </div>
    );
}

export default IncidentHistoryTable;