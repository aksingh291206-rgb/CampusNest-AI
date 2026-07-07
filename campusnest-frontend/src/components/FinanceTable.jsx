function FinanceTable({ records }) {
    return (
        <div className="overflow-x-auto">

            <table className="min-w-full border border-slate-700 text-sm">

                <thead className="bg-slate-800 text-cyan-300">
                    <tr>
                        <th className="p-2 border">Record ID</th>
                        <th className="p-2 border">Fee Type</th>
                        <th className="p-2 border">Amount</th>
                        <th className="p-2 border">Status</th>
                        <th className="p-2 border">Due Date</th>
                    </tr>
                </thead>

                <tbody>

                    {records.map((record) => (

                        <tr key={record.record_id} className="text-center">

                            <td className="border p-2">
                                {record.record_id}
                            </td>

                            <td className="border p-2">
                                {record.fee_type}
                            </td>

                            <td className="border p-2">
                                ₹{record.amount}
                            </td>

                            <td className="border p-2">
                                {record.payment_status}
                            </td>

                            <td className="border p-2">
                                {record.due_date}
                            </td>

                        </tr>

                    ))}

                </tbody>

            </table>

        </div>
    );
}

export default FinanceTable;