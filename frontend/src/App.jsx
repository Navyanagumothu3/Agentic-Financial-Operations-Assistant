import { useEffect, useState, useRef } from 'react';
import { api } from './api';
import './App.css';

function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [userRole, setUserRole] = useState('customer'); // 'customer' or 'manager'
  const [activeTab, setActiveTab] = useState('dashboard');
  const [customerId, setCustomerId] = useState('C1001');
  const [password, setPassword] = useState('bank123');
  const [userInfo, setUserInfo] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [allCustomers, setAllCustomers] = useState([]);
  const [pendingApprovals, setPendingApprovals] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [metrics, setMetrics] = useState(null);

  // Floating AI Assistant Drawer State
  const [aiDrawerOpen, setAiDrawerOpen] = useState(false);
  const [aiFullScreen, setAiFullScreen] = useState(false);
  const [message, setMessage] = useState('');
  const [actionStatus, setActionStatus] = useState('');
  const [chatMessages, setChatMessages] = useState([
    {
      role: 'assistant',
      content: '👋 **Hello! I am your FinOps Assistant.**\nI can help process refunds, analyze transactions, investigate fraud, and manage account actions. Ask me anything below!',
    },
  ]);

  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [transferForm, setTransferForm] = useState({ from_account: 'A2001', to_account: 'A2002', amount: '1000', description: 'Transfer to savings' });

  const chatEndRef = useRef(null);

  useEffect(() => {
    if (aiDrawerOpen) {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages, actionLoading, aiDrawerOpen]);

  const loadDataForRole = async (role, id) => {
    setLoading(true);
    try {
      if (role === 'manager') {
        const [pendingRes, auditRes, metricsRes, customersRes] = await Promise.all([
          api.pendingApprovals(),
          api.audit(50),
          api.metrics(),
          api.customers(),
        ]);
        setPendingApprovals(pendingRes);
        setAuditLogs(auditRes);
        setMetrics(metricsRes);
        setAllCustomers(customersRes);
      } else {
        const [customerRes, accountsRes, txnsRes, analyticsRes] = await Promise.all([
          api.customer(id),
          api.accounts(id),
          api.transactions(id),
          api.analytics(id),
        ]);
        setUserInfo(customerRes);
        setAccounts(accountsRes);
        setTransactions(txnsRes);
        setAnalytics(analyticsRes);
      }
    } catch (err) {
      setActionStatus(`❌ Data load error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e, forceId, forcePwd) => {
    if (e) e.preventDefault();
    const loginId = forceId || customerId;
    const loginPwd = forcePwd || password;
    setLoading(true);
    try {
      const res = await api.login(loginId, loginPwd);
      setLoggedIn(res.authenticated);
      const role = res.role || (loginId.toUpperCase().startsWith('M') ? 'manager' : 'customer');
      setUserRole(role);
      setUserInfo(res.customer || res.user);
      setActiveTab(role === 'manager' ? 'manager' : 'dashboard');
      await loadDataForRole(role, loginId);
      setActionStatus(`Logged in successfully as ${role === 'manager' ? 'Ops Manager' : res.customer?.name || loginId}`);
    } catch (err) {
      setActionStatus(`Login failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setLoggedIn(false);
    setUserInfo(null);
    setActionStatus('Logged out successfully.');
  };

  const handleTransfer = async (e) => {
    e.preventDefault();
    if (!transferForm.amount || Number(transferForm.amount) <= 0) return;
    setActionLoading(true);
    try {
      const res = await api.transfer({
        customer_id: customerId,
        from_account: transferForm.from_account,
        to_account: transferForm.to_account,
        amount: Number(transferForm.amount),
        description: transferForm.description,
      });
      setActionStatus(`✅ ${res.message}\nDecision: ${res.decision} | Approval Status: ${res.approval_status}`);
      await loadDataForRole(userRole, customerId);
    } catch (err) {
      setActionStatus(`❌ Transfer failed: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleWithdraw = async () => {
    setActionLoading(true);
    const targetAccount = accounts[0]?.account_id || 'A2001';
    try {
      const res = await api.withdraw({ customer_id: customerId, account_id: targetAccount, amount: 5000 });
      setActionStatus(`✅ ${res.message}\nDecision: ${res.decision} | Approval Status: ${res.approval_status}`);
      await loadDataForRole(userRole, customerId);
    } catch (err) {
      setActionStatus(`❌ Withdrawal failed: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleApproveCase = async (caseId, approved) => {
    setActionLoading(true);
    try {
      const res = await api.approve(caseId, approved, userInfo?.name || 'Ops Manager');
      setActionStatus(`✅ Case ${caseId} ${res.status.toUpperCase()} by Manager.`);
      await loadDataForRole(userRole, customerId);
    } catch (err) {
      setActionStatus(`❌ Approval error: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleAskAgent = async (promptText) => {
    const query = (promptText || message).trim();
    if (!query) return;

    setChatMessages((prev) => [...prev, { role: 'user', content: query }]);
    setMessage('');
    setActionLoading(true);

    try {
      const res = await api.chat(query, 'default', userRole === 'customer' ? customerId : 'C1001');
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.reply,
          trace: res.agent_trace,
        },
      ]);
      await loadDataForRole(userRole, customerId);
    } catch (err) {
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `❌ Error communicating with agent: ${err.message}`,
        },
      ]);
    } finally {
      setActionLoading(false);
    }
  };

  const demoScenarios = [
    { label: "⚡ Duplicate UPI Refund ₹7,500", text: "Customer C1001 was charged twice ₹7500 for electricity. Process refund on account A2001." },
    { label: "✅ Small Auto-Refund ₹500", text: "Refund ₹500 to customer C1004 on account A5001 for failed transaction." },
    { label: "🚨 Fraud Hold ₹1,25,000", text: "Investigate suspicious IMPS of ₹125000 on account A4001 for customer C1003." },
  ];

  return (
    <div className="app">
      {/* Top Navbar */}
      <header className="topbar">
        <div className="brand">
          <span className="brand-icon">🏦</span>
          <div>
            <div className="brand-title">Banking Intelligence Suite</div>
            <div className="brand-sub">RBI-Ready Enterprise Agentic FinOps</div>
          </div>
        </div>

        {loggedIn && (
          <nav className="nav-tabs">
            {userRole === 'customer' ? (
              <>
                <button className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
                  📊 Dashboard
                </button>
                <button className={`nav-tab ${activeTab === 'transfers' ? 'active' : ''}`} onClick={() => setActiveTab('transfers')}>
                  💸 Transfers & Cash
                </button>
                <button className={`nav-tab ${activeTab === 'transactions' ? 'active' : ''}`} onClick={() => setActiveTab('transactions')}>
                  📜 Transactions
                </button>
              </>
            ) : (
              <>
                <button className={`nav-tab ${activeTab === 'manager' ? 'active' : ''}`} onClick={() => setActiveTab('manager')}>
                  🛡️ Manager HITL Hub
                  {pendingApprovals.length > 0 && <span className="nav-badge">{pendingApprovals.length}</span>}
                </button>
                <button className={`nav-tab ${activeTab === 'audit' ? 'active' : ''}`} onClick={() => setActiveTab('audit')}>
                  📈 Audit & AI Metrics
                </button>
                <button className={`nav-tab ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>
                  👥 Customer Directory
                </button>
              </>
            )}
          </nav>
        )}

        {loggedIn && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="user-pill">
              <div className="user-avatar">{userInfo?.name?.[0] || 'U'}</div>
              <div className="user-info">
                <span>{userInfo?.name}</span>
                <small>{userRole === 'manager' ? 'OPS MANAGER' : `${userInfo?.tier?.toUpperCase() || 'GOLD'} TIER`}</small>
              </div>
            </div>
            <button className="icon-btn" onClick={handleLogout} title="Logout" style={{ width: 'auto', padding: '6px 12px', fontSize: '0.8rem' }}>
              Sign Out
            </button>
          </div>
        )}
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        {!loggedIn ? (
          <div className="auth-container">
            <div className="auth-card">
              <h2>Role-Based Banking Login</h2>
              <p>Select your role to access Customer services or Manager governance.</p>

              <form onSubmit={(e) => handleLogin(e)} className="form-group">
                <div style={{ marginBottom: 12 }}>
                  <label>User / Customer ID</label>
                  <input value={customerId} onChange={(e) => setCustomerId(e.target.value)} placeholder="C1001 or M1001" />
                </div>
                <div style={{ marginBottom: 16 }}>
                  <label>Password</label>
                  <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
                </div>
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? 'Signing in…' : 'Sign In'}
                </button>
              </form>

              <div style={{ marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: 10, fontWeight: 600 }}>Quick One-Click Sign In:</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  <button
                    type="button"
                    className="scenario-btn"
                    style={{ background: 'rgba(59,130,246,0.15)', color: '#93c5fd', borderColor: 'rgba(59,130,246,0.3)', padding: 10 }}
                    onClick={() => { setCustomerId('C1001'); setPassword('bank123'); handleLogin(null, 'C1001', 'bank123'); }}
                  >
                    👤 <strong>Sign In as Customer</strong> (Priya Sharma - C1001)
                  </button>
                  <button
                    type="button"
                    className="scenario-btn"
                    style={{ background: 'rgba(245,158,11,0.15)', color: '#fcd34d', borderColor: 'rgba(245,158,11,0.3)', padding: 10 }}
                    onClick={() => { setCustomerId('M1001'); setPassword('admin123'); handleLogin(null, 'M1001', 'admin123'); }}
                  >
                    🛡️ <strong>Sign In as Ops Manager</strong> (HITL & Audit Governance - M1001)
                  </button>
                </div>
              </div>

              {actionStatus && <div className="status-alert">{actionStatus}</div>}
            </div>
          </div>
        ) : (
          <>
            {/* CUSTOMER TAB 1: DASHBOARD */}
            {userRole === 'customer' && activeTab === 'dashboard' && (
              <div>
                <section className="hero-card">
                  <div>
                    <div className="eyebrow">Customer Account Dashboard</div>
                    <h2>{userInfo?.name}</h2>
                    <p style={{ color: 'var(--text-muted)' }}>{userInfo?.email} · {userInfo?.region} · KYC Verified</p>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Net Balance</div>
                    <div className="hero-balance-val">
                      ₹{accounts.reduce((sum, acc) => sum + acc.balance, 0).toLocaleString('en-IN')}
                    </div>
                  </div>
                </section>

                <div className="grid-main">
                  <div>
                    <div className="card" style={{ marginBottom: 20 }}>
                      <div className="card-header">
                        <div className="card-title">💳 Linked Accounts</div>
                      </div>
                      {accounts.map((acc) => (
                        <div key={acc.account_id} className="account-item">
                          <div>
                            <strong>{acc.account_id}</strong>
                            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{acc.account_type} Account</div>
                          </div>
                          <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#38bdf8' }}>
                            ₹{acc.balance.toLocaleString('en-IN')}
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="card">
                      <div className="card-header">
                        <div className="card-title">📊 Agent Intelligence Signals</div>
                      </div>
                      {analytics && (
                        <div className="grid-3" style={{ textAlign: 'center' }}>
                          <div style={{ background: 'rgba(15,23,42,0.6)', padding: 14, borderRadius: 12 }}>
                            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff' }}>{analytics.transaction_count}</div>
                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Total Txns</div>
                          </div>
                          <div style={{ background: 'rgba(15,23,42,0.6)', padding: 14, borderRadius: 12 }}>
                            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f59e0b' }}>{analytics.duplicate_count}</div>
                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Duplicates</div>
                          </div>
                          <div style={{ background: 'rgba(15,23,42,0.6)', padding: 14, borderRadius: 12 }}>
                            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#10b981' }}>{analytics.high_value_transactions}</div>
                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>High-Value</div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <div>
                    <div className="card">
                      <div className="card-header">
                        <div className="card-title"> Recent Activity</div>
                      </div>
                      {transactions.slice(0, 5).map((tx) => (
                        <div key={tx.txn_id} className="txn-row">
                          <div>
                            <strong>{tx.merchant}</strong>
                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{tx.type} · {tx.status}</div>
                          </div>
                          <div className="txn-amount">₹{tx.amount.toLocaleString('en-IN')}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* CUSTOMER TAB 2: TRANSFERS & CASH WITHDRAWALS */}
            {userRole === 'customer' && activeTab === 'transfers' && (
              <div className="grid-2">
                <div className="card">
                  <div className="card-header">
                    <div className="card-title">💸 Internal & Domestic Transfer</div>
                  </div>
                  <form onSubmit={handleTransfer}>
                    <div className="form-group">
                      <label>From Account</label>
                      <select value={transferForm.from_account} onChange={(e) => setTransferForm({ ...transferForm, from_account: e.target.value })}>
                        {accounts.map((a) => (
                          <option key={a.account_id} value={a.account_id}>{a.account_id} ({a.account_type} - ₹{a.balance.toLocaleString('en-IN')})</option>
                        ))}
                      </select>
                    </div>
                    <div className="form-group">
                      <label>To Account / Beneficiary</label>
                      <input value={transferForm.to_account} onChange={(e) => setTransferForm({ ...transferForm, to_account: e.target.value })} placeholder="A2002" />
                    </div>
                    <div className="form-group">
                      <label>Amount (₹)</label>
                      <input type="number" value={transferForm.amount} onChange={(e) => setTransferForm({ ...transferForm, amount: e.target.value })} placeholder="1000" />
                    </div>
                    <div className="form-group">
                      <label>Transfer Description</label>
                      <input value={transferForm.description} onChange={(e) => setTransferForm({ ...transferForm, description: e.target.value })} placeholder="Fund transfer" />
                    </div>
                    <button type="submit" className="btn-primary" disabled={actionLoading}>
                      {actionLoading ? 'Processing Transfer…' : 'Execute Transfer'}
                    </button>
                  </form>
                </div>

                <div className="card">
                  <div className="card-header">
                    <div className="card-title">🏧 Instant ATM Cash Withdrawal</div>
                  </div>
                  <p style={{ color: 'var(--text-muted)', marginBottom: 20 }}>Withdraw cash instantly from your primary account A2001.</p>
                  <button className="btn-secondary" onClick={handleWithdraw} disabled={actionLoading}>
                    {actionLoading ? 'Processing Withdrawal…' : 'Withdraw ₹5,000 Cash'}
                  </button>

                  {actionStatus && <div className="status-alert">{actionStatus}</div>}
                </div>
              </div>
            )}

            {/* CUSTOMER TAB 3: TRANSACTIONS */}
            {userRole === 'customer' && activeTab === 'transactions' && (
              <div className="card">
                <div className="card-header">
                  <div className="card-title">📜 Complete Transaction History</div>
                </div>
                {transactions.map((tx) => (
                  <div key={tx.txn_id} className="txn-row">
                    <div>
                      <strong>{tx.merchant}</strong>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        ID: {tx.txn_id} · Ref: {tx.reference || 'N/A'} · {tx.timestamp}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div className="txn-amount">₹{tx.amount.toLocaleString('en-IN')}</div>
                      <div style={{ fontSize: '0.75rem', color: tx.status === 'completed' ? '#10b981' : '#f59e0b', fontWeight: 600 }}>
                        {tx.type} ({tx.status.toUpperCase()})
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* MANAGER TAB 1: HITL APPROVAL HUB */}
            {userRole === 'manager' && activeTab === 'manager' && (
              <div className="card">
                <div className="card-header">
                  <div className="card-title">🛡️ Manager Human-In-The-Loop (HITL) Governance Queue</div>
                </div>
                <p style={{ color: 'var(--text-muted)', marginBottom: 18 }}>
                  RBI Compliance Directive: High-risk refunds (&gt;₹1,000), fraud holds, and account escalations are queued here for manual manager review before final execution.
                </p>

                {pendingApprovals.length === 0 ? (
                  <div style={{ padding: 28, textAlign: 'center', background: 'rgba(15,23,42,0.6)', borderRadius: 12, color: 'var(--text-muted)' }}>
                    ✅ No pending cases in manager queue. All routine actions auto-approved by AI pipeline.
                  </div>
                ) : (
                  pendingApprovals.map((caseItem) => (
                    <div key={caseItem.case_id} className="approval-card">
                      <h4>⚠️ Pending Case {caseItem.case_id}</h4>
                      <div style={{ fontSize: '0.9rem', color: 'var(--text-main)', marginBottom: 6 }}>
                        <strong>Customer:</strong> {caseItem.customer_id} · <strong>Request:</strong> {caseItem.request_type?.toUpperCase()} · <strong>Amount:</strong> ₹{caseItem.amount?.toLocaleString('en-IN')} · <strong>Account:</strong> {caseItem.account_id}
                      </div>
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                        <strong>Policy Reason:</strong> {caseItem.reason}
                      </div>
                      <div className="approval-actions">
                        <button className="btn-approve" onClick={() => handleApproveCase(caseItem.case_id, true)} disabled={actionLoading}>
                          ✅ Approve Action
                        </button>
                        <button className="btn-reject" onClick={() => handleApproveCase(caseItem.case_id, false)} disabled={actionLoading}>
                          ❌ Reject Action
                        </button>
                      </div>
                    </div>
                  ))
                )}
                {actionStatus && <div className="status-alert">{actionStatus}</div>}
              </div>
            )}

            {/* MANAGER TAB 2: AUDIT & AI METRICS */}
            {userRole === 'manager' && activeTab === 'audit' && (
              <div className="grid-main">
                <div className="card">
                  <div className="card-header">
                    <div className="card-title">📈 System Operational Metrics</div>
                  </div>
                  {metrics && (
                    <div className="grid-3" style={{ textAlign: 'center', marginBottom: 20 }}>
                      <div style={{ background: 'rgba(15,23,42,0.6)', padding: 14, borderRadius: 12 }}>
                        <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>{metrics.total_cases}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Total Cases</div>
                      </div>
                      <div style={{ background: 'rgba(15,23,42,0.6)', padding: 14, borderRadius: 12 }}>
                        <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f59e0b' }}>{metrics.pending_approval}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Pending HITL</div>
                      </div>
                      <div style={{ background: 'rgba(15,23,42,0.6)', padding: 14, borderRadius: 12 }}>
                        <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#10b981' }}>{metrics.auto_approved}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Auto Approved</div>
                      </div>
                    </div>
                  )}
                  <div style={{ background: 'rgba(15,23,42,0.6)', padding: 14, borderRadius: 12, fontSize: '0.88rem' }}>
                    <strong>Avg Decision Cost:</strong> ~$0.000100 USD (Rule-based & Tiered LLM)
                  </div>
                </div>

                <div className="card">
                  <div className="card-header">
                    <div className="card-title">📜 Immutable Audit Log Trail</div>
                  </div>
                  <div style={{ maxHeight: 380, overflowY: 'auto' }}>
                    {auditLogs.map((log, idx) => (
                      <div key={idx} style={{ padding: '8px 0', borderBottom: '1px solid var(--border)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        <strong style={{ color: '#38bdf8' }}>{log.case_id}</strong>: {log.reason}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* MANAGER TAB 3: CUSTOMER DIRECTORY OVERVIEW */}
            {userRole === 'manager' && activeTab === 'overview' && (
              <div className="card">
                <div className="card-header">
                  <div className="card-title">👥 Enterprise Customer Profiles</div>
                </div>
                {allCustomers.map((cust) => (
                  <div key={cust.customer_id} className="account-item">
                    <div>
                      <strong>{cust.name} ({cust.customer_id})</strong>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {cust.email} · {cust.tier?.toUpperCase()} Tier · Risk Band: {cust.risk_band}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right', fontSize: '0.85rem', color: '#38bdf8' }}>
                      Accounts: {cust.account_ids?.join(', ')}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </main>

      {/* FLOATING AI ASSISTANT WIDGET (Available across EVERY page at bottom right) */}
      {loggedIn && (
        <>
          <button
            className="ai-widget-button"
            onClick={() => setAiDrawerOpen(true)}
          >
            <span className="pulse-badge" />
            🤖 FinOps AI Copilot
          </button>

          {/* AI Drawer Overlay */}
          {aiDrawerOpen && (
            <div className="ai-drawer-overlay" onClick={(e) => { if (e.target === e.currentTarget) setAiDrawerOpen(false); }}>
              <div className={`ai-drawer ${aiFullScreen ? 'full-screen' : ''}`}>
                <div className="ai-drawer-header">
                  <h3>🤖 FinOps AI Assistant ({userRole === 'manager' ? 'Manager View' : 'Customer View'})</h3>
                  <div className="header-actions">
                    <button className="icon-btn" onClick={() => setAiFullScreen(!aiFullScreen)} title="Toggle Fullscreen">
                      {aiFullScreen ? '↙' : '⤢'}
                    </button>
                    <button className="icon-btn" onClick={() => setAiDrawerOpen(false)} title="Close">
                      ✕
                    </button>
                  </div>
                </div>

                <div className="ai-drawer-body">
                  <div className="chat-scenarios">
                    {demoScenarios.map((sc, idx) => (
                      <button
                        key={idx}
                        type="button"
                        className="scenario-btn"
                        disabled={actionLoading}
                        onClick={() => handleAskAgent(sc.text)}
                      >
                        {sc.label}
                      </button>
                    ))}
                  </div>

                  <div className="chat-history-box">
                    {chatMessages.map((msg, idx) => (
                      <div key={idx} className={`chat-msg ${msg.role}`}>
                        <div>{msg.content}</div>
                        {msg.trace && msg.trace.length > 0 && (
                          <div className="trace-chips">
                            {msg.trace.map((t, tidx) => (
                              <span key={tidx} className="chip">{t.agent}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                    {actionLoading && (
                      <div className="chat-msg assistant">
                        ⏳ <em>Orchestrating agents through pipeline…</em>
                      </div>
                    )}
                    <div ref={chatEndRef} />
                  </div>

                  <div className="drawer-footer">
                    <form
                      className="drawer-input-form"
                      onSubmit={(e) => {
                        e.preventDefault();
                        handleAskAgent();
                      }}
                    >
                      <input
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="Ask the AI copilot..."
                        disabled={actionLoading}
                      />
                      <button type="submit" className="btn-primary" style={{ width: 'auto' }} disabled={actionLoading || !message.trim()}>
                        {actionLoading ? 'Thinking…' : 'Send'}
                      </button>
                    </form>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;
