function TrackingCard({ tracking }) {
    return (
        <div className="space-y-2">

            <h3 className="text-yellow-400 font-bold text-lg">
                📌 Tracking Status
            </h3>

            <div>
                <strong>Reference ID:</strong> {tracking.reference_id}
            </div>

            <div>
                <strong>Category:</strong> {tracking.category}
            </div>

            <div>
                <strong>Status:</strong> {tracking.status}
            </div>

            <div>
                <strong>Assigned To:</strong> {tracking.assigned_personnel}
            </div>

            <div>
                <strong>Priority:</strong> {tracking.priority}
            </div>

            <div>
                <strong>Remarks:</strong> {tracking.remarks}
            </div>

        </div>
    );
}

export default TrackingCard;