const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  };

  try {
    const res = await fetch(url, config);
    const json = await res.json();
    if (!res.ok || json.success === false) {
      const msg = json.error?.message || `Request failed with status ${res.status}`;
      throw new Error(msg);
    }
    return json.data;
  } catch (err) {
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error('Cannot connect to AgentLens backend at ' + BASE_URL + '. Is the server running?');
    }
    throw err;
  }
}

export const api = {
  // Health
  health: () => request('/health'),

  // Investigations
  listInvestigations: (limit = 100, offset = 0) =>
    request(`/investigations?limit=${limit}&offset=${offset}`),
  getInvestigation: (id) =>
    request(`/investigations/${id}`),
  createInvestigation: (payload) =>
    request('/investigations', { method: 'POST', body: JSON.stringify(payload) }),
  attachDataset: (id, datasetPayload) =>
    request(`/investigations/${id}/dataset`, { method: 'POST', body: JSON.stringify(datasetPayload) }),
  analyzeInvestigation: (id) =>
    request(`/investigations/${id}/analyze`, { method: 'POST' }),

  // Dashboard
  getDashboard: (investigationId) =>
    request(`/investigations/${investigationId}/dashboard`),

  // Sessions
  listSessions: (investigationId, status = null, limit = 200, offset = 0) => {
    const q = status && status !== 'all' ? `&status=${status}` : '';
    return request(`/investigations/${investigationId}/sessions?limit=${limit}&offset=${offset}${q}`);
  },
  getSession: (sessionId) =>
    request(`/sessions/${sessionId}`),

  // Failures
  listFailures: (investigationId, filters = {}, limit = 200, offset = 0) => {
    const params = new URLSearchParams({ limit, offset });
    if (filters.failure_type && filters.failure_type !== 'all') params.append('failure_type', filters.failure_type);
    if (filters.severity && filters.severity !== 'all') params.append('severity', filters.severity);
    if (filters.status && filters.status !== 'all') params.append('status', filters.status);
    return request(`/investigations/${investigationId}/failures?${params.toString()}`);
  },
  getFailure: (failureId) =>
    request(`/failures/${failureId}`),
  updateFailureStatus: (failureId, status) =>
    request(`/failures/${failureId}/status`, { method: 'PATCH', body: JSON.stringify({ status }) }),

  // Failure Groups
  listFailureGroups: (investigationId) =>
    request(`/investigations/${investigationId}/failure-groups`),
  getFailureGroup: (groupId) =>
    request(`/failure-groups/${groupId}`),

  // Assistant
  queryAssistant: (investigationId, question) =>
    request(`/investigations/${investigationId}/assistant`, {
      method: 'POST',
      body: JSON.stringify({ question }),
    }),

  // Evaluation
  getEvaluation: (investigationId) =>
    request(`/investigations/${investigationId}/evaluation`),

  // Export
  exportData: (investigationId, format = 'json') =>
    request(`/investigations/${investigationId}/export?format=${format}`),

  // Direct Ingestion
  importDataset: (payload) =>
    request('/datasets/import', { method: 'POST', body: JSON.stringify(payload) }),
  listDatasets: () =>
    request('/datasets'),
};
