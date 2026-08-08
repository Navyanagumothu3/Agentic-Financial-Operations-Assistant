export default function MetricsPanel({ metrics }) {
  if (!metrics) return null;
  const cost = metrics.cost || {};
  return (
    <div className="metrics-bar">
      <div className="metric"><span className="metric-val">{metrics.total_cases || 0}</span><span className="metric-label">Cases</span></div>
      <div className="metric"><span className="metric-val warn">{metrics.pending_approval || 0}</span><span className="metric-label">Pending HITL</span></div>
      <div className="metric"><span className="metric-val">{metrics.escalated || 0}</span><span className="metric-label">Escalated</span></div>
      <div className="metric"><span className="metric-val ok">{metrics.auto_approved || 0}</span><span className="metric-label">Auto-approved</span></div>
      <div className="metric"><span className="metric-val">${cost.avg_cost_per_decision_usd?.toFixed(6) || '0'}</span><span className="metric-label">Cost/decision</span></div>
    </div>
  );
}
