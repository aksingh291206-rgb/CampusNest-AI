function KnowledgeTable({ title, data }) {
    return (
        <div className="space-y-4">

            <h2 className="text-xl font-bold text-cyan-400">
                {title}
            </h2>

            <div className="overflow-x-auto">
                <table className="min-w-full border border-slate-700">

                    <thead className="bg-slate-800">
                        <tr>
                            <th className="border border-slate-700 p-2">Title</th>
                            <th className="border border-slate-700 p-2">Description</th>
                        </tr>
                    </thead>

                    <tbody>
                        {data.map((item, index) => (
                            <tr key={index}>
                                <td className="border border-slate-700 p-2 font-semibold">
                                    {item.title}
                                </td>

                                <td className="border border-slate-700 p-2">
                                    {item.description}
                                </td>
                            </tr>
                        ))}
                    </tbody>

                </table>
            </div>

        </div>
    );
}

export default KnowledgeTable;