function LeaveCard({ leave, message }) {
    return (
        <div className="space-y-2">

            <h3 className="text-cyan-400 font-bold text-lg">
                📄 Leave Request
            </h3>

            <div>
                <strong>Application ID:</strong> {leave.application_id}
            </div>

            <div>
                <strong>Student:</strong> {leave.student_name}
            </div>

            <div>
                <strong>Leave Type:</strong> {leave.leave_type}
            </div>

            <div>
                <strong>Start Date:</strong> {leave.start_date}
            </div>

            <div>
                <strong>End Date:</strong> {leave.end_date}
            </div>

            <div>
                <strong>Status:</strong> {leave.status}
            </div>

            <hr className="border-slate-600" />

            <div>{message}</div>

        </div>
    );
}

export default LeaveCard;