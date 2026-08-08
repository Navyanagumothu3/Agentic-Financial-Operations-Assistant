export default function AgentTrace({ trace }) {
  if (!trace?.length) return null;
  const agents = ['Router', 'Support', 'Payment', 'Fraud', 'Internal Ops', 'Decision', 'Self-Check', 'Approval', 'Audit'];

  return (
    <div className="panel agent-trace">
      <h3>Agent Pipeline</h3>
      <div className="pipeline">
        {trace.map((step, i) => (
          <div key={i} className="pipeline-step">
            <div className="step-dot" />
            <div className="step-content">
              <strong>{step.agent}</strong>
              <p>{step.summary}</p>
            </div>
          </div>
        ))}
      </div>
      <div className="pipeline-legend">
        {agents.map((a) => (
          <span key={a} className="legend-item">{a}</span>
        ))}
      </div>
    </div>
  );
}
