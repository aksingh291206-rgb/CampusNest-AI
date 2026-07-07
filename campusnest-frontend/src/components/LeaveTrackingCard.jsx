function LeaveTrackingCard({ tracking, message }) {
    return (
        <div className="space-y-3 rounded-xl bg-slate-800 p-5 text-white">

            <h3 className="text-xl font-bold text-cyan-400">
                Leave Request Status
            </h3>

            <div>
                <strong>Application ID:</strong> {tracking.application_id}
            </div>

            <div>
                <strong>Student ID:</strong> {tracking.student_id}
            </div>

            <div>
                <strong>Student Name:</strong> {tracking.student_name}
            </div>

            <div>
                <strong>Leave Type:</strong> {tracking.leave_type}
            </div>

            <div>
                <strong>Start Date:</strong> {tracking.start_date}
            </div>

            <div>
                <strong>End Date:</strong> {tracking.end_date}
            </div>

            <div>
                <strong>Status:</strong> {tracking.status}
            </div>

            <div>
                <strong>Submitted On:</strong> {tracking.timestamp}
            </div>

            {message && (
                <div className="mt-4 rounded-lg bg-cyan-900/30 p-3 text-cyan-300">
                    {message}
                </div>
            )}

        </div>
    );
}

export default LeaveTrackingCard;