function LeaveHistoryTable({ history }) {
    return (
        <div className="overflow-x-auto">

            <h3 className="text-cyan-300 text-lg font-bold mb-3">
                📄 Leave History
            </h3>

            <table className="min-w-full border border-slate-700 text-sm">

                <thead className="bg-slate-800 text-cyan-300">
                    <tr>
                        <th className="border p-2">Application ID</th>
                        <th className="border p-2">Leave Type</th>
                        <th className="border p-2">Start</th>
                        <th className="border p-2">End</th>
                        <th className="border p-2">Status</th>
                    </tr>
                </thead>

                <tbody>

                    {history.map((leave) => (

                        <tr key={leave.application_id}>

                            <td className="border p-2">
                                {leave.application_id}
                            </td>

                            <td className="border p-2">
                                {leave.leave_type}
                            </td>

                            <td className="border p-2">
                                {leave.start_date}
                            </td>

                            <td className="border p-2">
                                {leave.end_date}
                            </td>

                            <td className="border p-2">
                                {leave.status}
                            </td>

                        </tr>

                    ))}

                </tbody>

            </table>

        </div>
    );
}

export default LeaveHistoryTable;