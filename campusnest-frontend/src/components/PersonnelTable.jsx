function PersonnelTable({ personnel }) {
    return (
        <div className="space-y-4">

            <h2 className="text-xl font-bold text-cyan-400">
                Personnel Directory
            </h2>

            <div className="overflow-x-auto">

                <table className="min-w-full border border-slate-700 rounded-lg overflow-hidden">

                    <thead className="bg-slate-800">

                        <tr>

                            <th className="px-6 py-3 text-left border-b border-slate-700">
                                Name
                            </th>

                            <th className="px-6 py-3 text-left border-b border-slate-700">
                                Role
                            </th>

                            <th className="px-6 py-3 text-left border-b border-slate-700">
                                Department
                            </th>

                            <th className="px-6 py-3 text-left border-b border-slate-700">
                                Status
                            </th>

                            <th className="px-6 py-3 text-left border-b border-slate-700">
                                Shift
                            </th>

                            <th className="px-6 py-3 text-left border-b border-slate-700">
                                Contact
                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        {personnel.map((p, index) => (

                            <tr
                                key={index}
                                className="border-t border-slate-700 hover:bg-slate-800 transition-colors"
                            >

                                <td className="px-6 py-4">
                                    {p.name}
                                </td>

                                <td className="px-6 py-4">
                                    {p.role}
                                </td>

                                <td className="px-6 py-4">
                                    {p.department}
                                </td>

                                <td className="px-6 py-4">
                                    {p.availability}
                                </td>

                                <td className="px-6 py-4">
                                    {p.shift}
                                </td>

                                <td className="px-6 py-4">
                                    {p.contact_number}
                                </td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </div>

        </div>
    );
}

export default PersonnelTable;