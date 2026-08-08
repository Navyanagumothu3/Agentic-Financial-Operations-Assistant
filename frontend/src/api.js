const API_BASE = '/api';

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

export const api = {
  health: () => request('/'),
  chat: (message, sessionId = 'default', customerId = 'C1001') =>
    request('/chat', { method: 'POST', body: JSON.stringify({ message, session_id: sessionId, customer_id: customerId }) }),
  scenarios: () => request('/chat/scenarios'),
  operate: (payload) => request('/operate', { method: 'POST', body: JSON.stringify(payload) }),
  cases: () => request('/cases'),
  pendingApprovals: () => request('/cases/pending-approval'),
  approve: (caseId, approved, reviewer) =>
    request('/approve', { method: 'POST', body: JSON.stringify({ case_id: caseId, approved, reviewer }) }),
  audit: (limit = 50) => request(`/audit?limit=${limit}`),
  customers: () => request('/customers'),
  metrics: () => request('/metrics'),
  login: (customerId, password) =>
    request('/login', { method: 'POST', body: JSON.stringify({ customer_id: customerId, password }) }),
  customer: (customerId) => request(`/customers/${customerId}`),
  accounts: (customerId) => request(`/customers/${customerId}/accounts`),
  transactions: (customerId) => request(`/customers/${customerId}/transactions`),
  analytics: (customerId) => request(`/analytics/${customerId}`),
  transfer: (payload) => request('/transfer', { method: 'POST', body: JSON.stringify(payload) }),
  withdraw: (payload) => request('/withdraw', { method: 'POST', body: JSON.stringify(payload) }),
};
