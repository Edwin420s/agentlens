import React, { useState } from 'react';
import {
  Flame,
  Search,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock,
  HelpCircle,
  ShieldAlert,
  Cpu,
  Sparkles,
  ExternalLink,
  ChevronRight,
  Filter,
} from 'lucide-react';
import {
  SeverityBadge,
  StatusBadge,
  ActorBadge,
  SignalTag,
  JsonViewer,
  Spinner,
  EmptyState,
} from './common';

export function FailuresView({
  failures = [],
  selectedFailure,
  onSelectFailure,
  onUpdateStatus,
  onSelectSession,
  loading,
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [statusUpdating, setStatusUpdating] = useState(false);

  const failureTypes = [
    'all',
    'unsupported_success',
    'no_progress',
    'wrong_record',
    'repeated_question',
    'incomplete_request',
  ];

  const filteredFailures = failures.filter((f) => {
    if (filterType !== 'all' && f.failure_type !== filterType) return false;
    if (filterSeverity !== 'all' && f.severity !== filterSeverity) return false;
    if (filterStatus !== 'all' && f.status !== filterStatus) return false;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      return (
        f.failure_id?.toLowerCase().includes(term) ||
        f.session_id?.toLowerCase().includes(term) ||
        f.title?.toLowerCase().includes(term) ||
        f.summary?.toLowerCase().includes(term) ||
        f.failure_type?.toLowerCase().includes(term)
      );
    }
    return true;
  });

  const handleStatusChange = async (newStatus) => {
    if (!selectedFailure || !onUpdateStatus) return;
    try {
      setStatusUpdating(true);
      await onUpdateStatus(selectedFailure.failure_id, newStatus);
    } finally {
      setStatusUpdating(false);
    }
  };

  return (
    <div className="split-view-container">
      {/* Sidebar List */}
      <div className="split-sidebar">
        <div className="sidebar-header">
          <div className="sidebar-title-row">
            <h2>Failures</h2>
            <span className="count-pill">{filteredFailures.length}</span>
          </div>

          <div className="search-box">
            <Search size={14} className="search-icon" />
            <input
              type="text"
              placeholder="Search by ID, session, title..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {/* Filter dropdowns / chips */}
          <div className="filter-controls-stack">
            <div className="filter-select-group">
              <label>Type:</label>
              <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
                {failureTypes.map((t) => (
                  <option key={t} value={t}>
                    {t === 'all' ? 'All Types' : t.replace(/_/g, ' ')}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-select-group">
              <label>Severity:</label>
              <select value={filterSeverity} onChange={(e) => setFilterSeverity(e.target.value)}>
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            <div className="filter-select-group">
              <label>Status:</label>
              <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
                <option value="all">All Statuses</option>
                <option value="new">New</option>
                <option value="investigating">Investigating</option>
                <option value="reviewed">Reviewed</option>
                <option value="resolved">Resolved</option>
              </select>
            </div>
          </div>
        </div>

        <div className="sidebar-scrollable">
          {filteredFailures.length === 0 ? (
            <div className="p-4 text-center text-muted">No failures match criteria.</div>
          ) : (
            filteredFailures.map((f) => {
              const isSelected = selectedFailure?.failure_id === f.failure_id;
              return (
                <div
                  key={f.failure_id}
                  className={`list-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => onSelectFailure(f.failure_id)}
                >
                  <div className="list-card-top">
                    <span className="id-sub">{f.failure_id}</span>
                    <SeverityBadge severity={f.severity} />
                  </div>
                  <strong className="list-card-title">{f.title || f.summary}</strong>
                  <div className="list-card-bottom">
                    <span className="type-micro">{f.failure_type.replace(/_/g, ' ')}</span>
                    <span className="status-micro">{f.session_id}</span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Main Detail / Inspector */}
      <div className="split-content">
        {loading ? (
          <div className="view-loading">
            <Spinner size={32} />
            <p>Loading failure details & evidence...</p>
          </div>
        ) : !selectedFailure ? (
          <EmptyState
            icon={Flame}
            title="Select a Failure to Inspect"
            message="Choose an individual failure instance from the list to inspect its signals, root-cause hypothesis, and evidence timeline."
          />
        ) : (
          <div className="detail-container">
            {/* Header Card */}
            <div className="detail-header-card">
              <div className="detail-top-row">
                <div className="id-and-type">
                  <span className="group-id-pill">{selectedFailure.failure_id}</span>
                  <SeverityBadge severity={selectedFailure.severity} />
                  <StatusBadge status={selectedFailure.status} type="failure" />
                </div>

                {/* Status Updater */}
                <div className="status-update-control">
                  <label htmlFor="status-select">Workflow Status:</label>
                  <select
                    id="status-select"
                    value={selectedFailure.status || 'new'}
                    disabled={statusUpdating}
                    onChange={(e) => handleStatusChange(e.target.value)}
                  >
                    <option value="new">New</option>
                    <option value="investigating">Investigating</option>
                    <option value="reviewed">Reviewed</option>
                    <option value="resolved">Resolved</option>
                  </select>
                  {statusUpdating && <Spinner size={14} />}
                </div>
              </div>

              <h1 className="detail-title">{selectedFailure.title}</h1>
              <p className="detail-lead">{selectedFailure.summary}</p>

              <div className="detail-meta-strip">
                <span>
                  Type: <strong>{selectedFailure.failure_type.replace(/_/g, ' ')}</strong>
                </span>
                <span>·</span>
                <span>
                  Confidence: <strong>{Math.round((selectedFailure.confidence || 0) * 100)}%</strong>
                </span>
                <span>·</span>
                <span>
                  Session:{' '}
                  <button
                    type="button"
                    className="btn-link"
                    onClick={() => onSelectSession(selectedFailure.session_id)}
                  >
                    {selectedFailure.session_id}
                    <ExternalLink size={12} />
                  </button>
                </span>
                {selectedFailure.group_id && (
                  <>
                    <span>·</span>
                    <span>
                      Group: <code>{selectedFailure.group_id}</code>
                    </span>
                  </>
                )}
              </div>
            </div>

            {/* Analysis & Root Cause */}
            <div className="panel detail-section">
              <div className="section-header-row">
                <h3>
                  <Sparkles size={16} className="text-purple" /> Analysis & Root Cause
                </h3>
                <span className="badge-neutral">
                  Engine: {selectedFailure.signals?.length ? 'Rule + AI Verified' : 'Rule Engine'}
                </span>
              </div>

              {selectedFailure.root_cause && (
                <div className="analysis-block">
                  <strong>Hypothesis / Root Cause:</strong>
                  <p>{selectedFailure.root_cause}</p>
                </div>
              )}

              {selectedFailure.impact && (
                <div className="analysis-block">
                  <strong>Business / User Impact:</strong>
                  <p>{selectedFailure.impact}</p>
                </div>
              )}

              {selectedFailure.recommendation && (
                <div className="callout-box">
                  <div className="callout-header">
                    <ShieldAlert size={16} className="text-warning" />
                    <strong>Engineering Recommendation</strong>
                  </div>
                  <p className="callout-body">{selectedFailure.recommendation}</p>
                </div>
              )}

              {selectedFailure.signals && selectedFailure.signals.length > 0 && (
                <div className="signals-block">
                  <span className="signals-label">Triggered Rule Signals:</span>
                  <div className="tag-cloud">
                    {selectedFailure.signals.map((sig) => (
                      <SignalTag key={sig} signal={sig} />
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Evidence & Timeline */}
            <div className="panel detail-section">
              <div className="section-header-row">
                <h3>
                  <Cpu size={16} className="text-cyan" /> Cited Evidence Events (
                  {selectedFailure.evidence_event_ids?.length || 0})
                </h3>
                <button
                  type="button"
                  className="btn btn-secondary btn-xs"
                  onClick={() => onSelectSession(selectedFailure.session_id)}
                >
                  <span>Open Full Session Timeline</span>
                  <ArrowRight size={12} />
                </button>
              </div>

              <div className="evidence-events-container">
                {selectedFailure.evidence_events && selectedFailure.evidence_events.length > 0 ? (
                  selectedFailure.evidence_events.map((evt) => (
                    <div key={evt.event_id} className="evidence-step-card">
                      <div className="step-header">
                        <div className="step-meta">
                          <span className="step-num">Step #{evt.sequence}</span>
                          <ActorBadge actor={evt.actor} />
                          <span className="evt-type-pill">{evt.event_type}</span>
                        </div>
                        <code className="evt-id">{evt.event_id}</code>
                      </div>

                      <div className="step-content">
                        {evt.tool_name && (
                          <div className="tool-call-banner">
                            <strong>Tool:</strong> <code>{evt.tool_name}</code>
                          </div>
                        )}
                        {evt.content && <p className="step-message">{evt.content}</p>}
                        {evt.tool_input && (
                          <JsonViewer data={evt.tool_input} title="Tool Input Arguments" />
                        )}
                        {evt.tool_output && (
                          <JsonViewer data={evt.tool_output} title="Tool Output Result" />
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="cited-ids-only">
                    <p className="text-muted mb-2">Event IDs flagged in evidence:</p>
                    <div className="id-tags">
                      {selectedFailure.evidence_event_ids?.map((id) => (
                        <code key={id} className="id-code-sub">
                          {id}
                        </code>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
