export default function AuditLog({ entries }) {
  return (
    <div className="panel audit-log">
      <h3>Audit Trail</h3>
      {entries.length === 0 ? (
        <p className="empty">No audit entries yet.</p>
      ) : (
        <ul>
          {entries.slice(0, 15).map((e, i) => (
            <li key={i}>
              <span className="audit-time">{e.timestamp?.slice(11, 19) || ''}</span>
              <span className="audit-msg">{e.message || e.reason || JSON.stringify(e)}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
