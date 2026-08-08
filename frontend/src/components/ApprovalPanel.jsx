import { useState } from 'react';

export default function ApprovalPanel({ caseItem, onApprove }) {
  const [reviewer, setReviewer] = useState('ops_manager');
  const [loading, setLoading] = useState(false);

  if (!caseItem) {
    return (
      <div className="panel approval-panel">
        <h3>Human-in-the-Loop</h3>
        <p className="empty">Select a case requiring approval to review.</p>
      </div>
    );
  }

  const needsApproval = caseItem.approval_required && caseItem.approval_status === 'pending';

  return (
    <div className="panel approval-panel">
      <h3>Human-in-the-Loop</h3>
      <div className="detail-grid">
        <div><label>Case</label><span>{caseItem.case_id}</span></div>
        <div><label>Action</label><span>{caseItem.action}</span></div>
        <div><label>Amount</label><span>₹{caseItem.amount?.toLocaleString('en-IN')}</span></div>
        <div><label>Status</label><span className={`badge ${caseItem.approval_status}`}>{caseItem.approval_status}</span></div>
      </div>
      <div className="reason-box">
        <label>Reason</label>
        <p>{caseItem.reason}</p>
      </div>
      {caseItem.explanation && (
        <div className="reason-box">
          <label>Explanation</label>
          <p>{caseItem.explanation}</p>
        </div>
      )}

      {needsApproval ? (
        <div className="approval-actions">
          <input value={reviewer} onChange={(e) => setReviewer(e.target.value)} placeholder="Reviewer name" />
          <div className="btn-row">
            <button
              className="btn-approve"
              disabled={loading}
              onClick={async () => {
                setLoading(true);
                await onApprove(caseItem.case_id, true, reviewer);
                setLoading(false);
              }}
            >
              Approve
            </button>
            <button
              className="btn-reject"
              disabled={loading}
              onClick={async () => {
                setLoading(true);
                await onApprove(caseItem.case_id, false, reviewer);
                setLoading(false);
              }}
            >
              Reject
            </button>
          </div>
        </div>
      ) : (
        <p className="muted">{caseItem.approval_status === 'auto_approved' ? 'Auto-approved (low risk)' : `Reviewed by ${caseItem.reviewer || 'system'}`}</p>
      )}
    </div>
  );
}
