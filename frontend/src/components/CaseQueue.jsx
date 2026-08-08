export default function CaseQueue({ cases, selected, onSelect }) {
  return (
    <div className="panel case-queue">
      <h3>Case Queue <span className="count">{cases.length}</span></h3>
      {cases.length === 0 ? (
        <p className="empty">No cases yet. Start a conversation with FinOps Assistant.</p>
      ) : (
        <ul>
          {cases.map((c) => (
            <li
              key={c.case_id}
              className={`case-item ${selected?.case_id === c.case_id ? 'selected' : ''}`}
              onClick={() => onSelect(c)}
            >
              <div className="case-top">
                <strong>{c.case_id}</strong>
                <span className={`badge ${c.decision}`}>{c.decision}</span>
              </div>
              <div className="case-meta">{c.request_type} · ₹{c.amount?.toLocaleString('en-IN') || 0}</div>
              <div className="case-meta muted">{c.customer_id} · {c.approval_status}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
