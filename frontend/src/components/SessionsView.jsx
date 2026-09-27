import React, { useState } from 'react';
import {
  Clock,
  Search,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Wrench,
  Bot,
  User,
  Terminal,
  ChevronDown,
  ChevronRight,
  Flame,
  ArrowRight,
  Filter,
} from 'lucide-react';
import {
  StatusBadge,
  ActorBadge,
  SeverityBadge,
  SignalTag,
  JsonViewer,
  Spinner,
  EmptyState,
} from './common';

export function SessionsView({
  sessions = [],
  selectedSession,
  onSelectSession,
  onSelectFailure,
  loading,
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const filteredSessions = sessions.filter((s) => {
    if (statusFilter !== 'all' && s.session_status !== statusFilter) return false;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      return (
        s.session_id?.toLowerCase().includes(term) ||
        s.user_request?.toLowerCase().includes(term) ||
        s.domain?.toLowerCase().includes(term)
      );
    }
    return true;
  });

  const sessionData = selectedSession?.session || selectedSession;
  const events = selectedSession?.events || [];
  const linkedFailures = selectedSession?.failures || [];

  return (
    <div className="split-view-container">
      {/* Sessions Sidebar */}
      <div className="split-sidebar">
        <div className="sidebar-header">
          <div className="sidebar-title-row">
            <h2>Sessions</h2>
            <span className="count-pill">{filteredSessions.length}</span>
          </div>

          <div className="search-box">
            <Search size={14} className="search-icon" />
            <input
              type="text"
              placeholder="Search request or session ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="filter-chips">
            {['all', 'success', 'failure', 'ambiguous'].map((st) => (
              <button
                key={st}
                type="button"
                className={`chip ${statusFilter === st ? 'active' : ''}`}
                onClick={() => setStatusFilter(st)}
              >
                {st.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        <div className="sidebar-scrollable">
          {filteredSessions.length === 0 ? (
            <div className="p-4 text-center text-muted">No sessions match filter.</div>
          ) : (
            filteredSessions.map((s) => {
              const isSelected = sessionData?.session_id === s.session_id;
              return (
                <div
                  key={s.session_id}
                  className={`list-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => onSelectSession(s.session_id)}
                >
                  <div className="list-card-top">
                    <span className="id-sub">{s.session_id}</span>
                    <StatusBadge status={s.session_status} type="session" />
                  </div>
                  <strong className="list-card-title">{s.user_request}</strong>
                  <div className="list-card-bottom">
                    <span className="type-micro">{s.domain || 'general'}</span>
                    {s.failure_count > 0 && (
                      <span className="text-danger font-bold text-xs">
                        {s.failure_count} failure{s.failure_count > 1 ? 's' : ''}
                      </span>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Session Detail & Timeline */}
      <div className="split-content">
        {loading ? (
          <div className="view-loading">
            <Spinner size={32} />
            <p>Loading session timeline and trace events...</p>
          </div>
        ) : !sessionData ? (
          <EmptyState
            icon={Clock}
            title="Select a Session"
            message="Choose an execution trace from the sidebar to inspect its turn-by-turn messages, tool calls, and payload data."
          />
        ) : (
          <div className="detail-container">
            {/* Session Header Card */}
            <div className="detail-header-card">
              <div className="detail-top-row">
                <div className="header-badges">
                  <span className="group-id-pill">{sessionData.session_id}</span>
                  <StatusBadge status={sessionData.session_status} type="session" />
                  <span className="badge-neutral">{sessionData.domain || 'e-commerce'}</span>
                </div>
                <span className="text-muted text-xs">
                  {events.length} turn{events.length !== 1 ? 's' : ''} recorded
                </span>
              </div>

              <div className="session-request-box">
                <div className="request-label">
                  <User size={14} />
                  <span>USER REQUEST:</span>
                </div>
                <p className="request-text">{sessionData.user_request}</p>
              </div>

              {sessionData.expected_outcome && (
                <div className="expected-outcome-box">
                  <span className="expected-label">Expected Outcome:</span>
                  <p>{sessionData.expected_outcome}</p>
                </div>
              )}

              {sessionData.final_response && (
                <div className="final-response-box">
                  <div className="final-label">
                    <Bot size={14} />
                    <span>FINAL AGENT RESPONSE:</span>
                  </div>
                  <p className="final-text">{sessionData.final_response}</p>
                </div>
              )}
            </div>

            {/* Linked Failures Notification Banner */}
            {linkedFailures.length > 0 && (
              <div className="linked-failures-banner">
                <div className="banner-title">
                  <Flame size={18} className="text-danger" />
                  <strong>Detected Failures in this Session ({linkedFailures.length})</strong>
                </div>
                <div className="linked-failures-grid">
                  {linkedFailures.map((f) => (
                    <div
                      key={f.failure_id}
                      className="linked-failure-chip"
                      onClick={() => onSelectFailure(f.failure_id)}
                    >
                      <div>
                        <code>{f.failure_id}</code>: <span>{f.title || f.summary}</span>
                      </div>
                      <div className="chip-actions">
                        <SeverityBadge severity={f.severity} />
                        <ArrowRight size={14} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Turn-by-Turn Timeline */}
            <div className="panel detail-section">
              <div className="section-header-row">
                <h3>Execution Trace Timeline</h3>
                <span className="text-muted text-xs">Verifiable log sequence</span>
              </div>

              <div className="timeline-container">
                {events.length === 0 ? (
                  <p className="p-4 text-muted">No events recorded for this session.</p>
                ) : (
                  events.map((evt, idx) => {
                    const isTool = evt.event_type === 'tool_call' || evt.event_type === 'tool_result';
                    const isError =
                      evt.status === 'failed' ||
                      (evt.tool_output &&
                        (evt.tool_output.status === 'error' ||
                          evt.tool_output.success === false ||
                          evt.tool_output.error));

                    return (
                      <div key={evt.event_id || idx} className={`timeline-item ${isError ? 'has-error' : ''}`}>
                        <div className="timeline-left-marker">
                          <div className={`timeline-dot ${evt.actor}`}>
                            {evt.actor === 'user' && <User size={12} />}
                            {evt.actor === 'agent' && <Bot size={12} />}
                            {evt.actor === 'tool' && <Wrench size={12} />}
                            {evt.actor === 'system' && <Terminal size={12} />}
                          </div>
                          {idx < events.length - 1 && <div className="timeline-line" />}
                        </div>

                        <div className="timeline-content-card">
                          <div className="timeline-meta-bar">
                            <div className="meta-left">
                              <span className="step-tag">#{evt.sequence}</span>
                              <ActorBadge actor={evt.actor} />
                              <span className="event-type-badge">{evt.event_type}</span>
                              {evt.status && (
                                <span className={`action-status-pill ${evt.status}`}>{evt.status}</span>
                              )}
                            </div>
                            <code className="event-id-text">{evt.event_id}</code>
                          </div>

                          {evt.tool_name && (
                            <div className="tool-invocation-title">
                              <Wrench size={14} className="text-cyan" />
                              <span className="tool-kw">Tool Call:</span>
                              <code className="tool-name-code">{evt.tool_name}</code>
                            </div>
                          )}

                          {evt.content && <div className="event-message-body">{evt.content}</div>}

                          {evt.tool_input && (
                            <JsonViewer data={evt.tool_input} title="Tool Input Arguments" />
                          )}

                          {evt.tool_output && (
                            <JsonViewer data={evt.tool_output} title="Tool Output Result" />
                          )}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
