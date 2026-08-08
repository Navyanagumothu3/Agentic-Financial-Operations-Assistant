function renderMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/⚠️/g, '<span class="warn">⚠️</span>')
    .replace(/✅/g, '<span class="ok">✅</span>')
    .replace(/\n/g, '<br/>');
}

export default function ChatPanel({ messages, onSend, loading, scenarios, onScenario }) {
  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div className="avatar">🤖</div>
        <div>
          <h2>FinOps Assistant</h2>
          <p className="muted">Agentic financial operations copilot</p>
        </div>
        <div className="live-badge">Live</div>
      </div>

      <div className="scenarios">
        {scenarios.map((s) => (
          <button key={s.label} className="scenario-chip" onClick={() => onScenario(s.message)} disabled={loading}>
            {s.label}
          </button>
        ))}
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-msg">
            <p>Welcome to the Agentic Financial Operations Assistant.</p>
            <p className="muted">Ask me to process refunds, investigate fraud, or handle support cases. I orchestrate support, payment, fraud, and ops agents — with human approval for high-risk actions.</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`msg ${msg.role}`}>
            {msg.role === 'assistant' ? (
              <div dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }} />
            ) : (
              msg.content
            )}
            {msg.trace && (
              <div className="msg-trace">
                {msg.trace.map((t, j) => (
                  <span key={j} className="trace-chip">{t.agent}</span>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && <div className="msg assistant typing">Processing through agent pipeline…</div>}
      </div>

      <form
        className="chat-input"
        onSubmit={(e) => {
          e.preventDefault();
          const input = e.target.elements.message;
          if (input.value.trim()) {
            onSend(input.value.trim());
            input.value = '';
          }
        }}
      >
        <input name="message" placeholder="Describe the operation… e.g. Process refund ₹7500 for C1001" disabled={loading} />
        <button type="submit" disabled={loading}>Send</button>
      </form>
    </div>
  );
}
