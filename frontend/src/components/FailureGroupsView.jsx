import React, { useState } from 'react';
import {
  Layers,
  AlertTriangle,
  Lightbulb,
  Search,
  ExternalLink,
  Wrench,
  ChevronRight,
  ShieldAlert,
} from 'lucide-react';
import { SeverityBadge, StatusBadge, SignalTag, Spinner, EmptyState } from './common';

export function FailureGroupsView({ groups, selectedGroup, onSelectGroup, onSelectFailure, loading }) {
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const grp = selectedGroup?.group || selectedGroup;
  const linkedFailures = selectedGroup?.failures || [];

  const filteredGroups = groups.filter((g) => {
    if (filterSeverity !== 'all' && g.severity !== filterSeverity) return false;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      return (
        g.title.toLowerCase().includes(term) ||
        g.group_id.toLowerCase().includes(term) ||
        g.failure_type.toLowerCase().includes(term)
      );
    }
    return true;
  });

  return (
    <div className="split-view-container">
      {/* Left List Pane */}
      <div className="split-sidebar">
        <div className="sidebar-header">
          <div className="sidebar-title-row">
            <h2>Failure Groups</h2>
            <span className="count-pill">{filteredGroups.length}</span>
          </div>

          <div className="search-box">
            <Search size={14} className="search-icon" />
            <input
              type="text"
              placeholder="Search groups..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="filter-chips">
            {['all', 'critical', 'high', 'medium', 'low'].map((sev) => (
              <button
                key={sev}
                type="button"
                className={`chip ${filterSeverity === sev ? 'active' : ''}`}
                onClick={() => setFilterSeverity(sev)}
              >
                {sev.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        <div className="sidebar-scrollable">
          {filteredGroups.length === 0 ? (
            <div className="p-4 text-center text-muted">No failure groups match filter.</div>
          ) : (
            filteredGroups.map((g) => {
              const isSelected = (selectedGroup?.group?.group_id || selectedGroup?.group_id) === g.group_id;
              return (
                <div
                  key={g.group_id}
                  className={`list-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => onSelectGroup(g.group_id)}
                >
                  <div className="list-card-top">
                    <span className="id-sub">{g.group_id}</span>
                    <SeverityBadge severity={g.severity} />
                  </div>
                  <strong className="list-card-title">{g.title}</strong>
                  <div className="list-card-bottom">
                    <span className="type-micro">{g.failure_type.replace(/_/g, ' ')}</span>
                    <span className="count-micro">{g.occurrence_count} occurrences</span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Right Detail Pane */}
      <div className="split-content">
        {loading ? (
          <div className="view-loading">
            <Spinner size={32} />
            <p>Loading group intelligence...</p>
          </div>
        ) : !grp || !grp.group_id ? (
          <EmptyState
            icon={Layers}
            title="Select a Failure Group"
            message="Choose a recurring failure group from the sidebar to inspect its pattern, engineering recommendations, and linked failures."
          />
        ) : (
          <div className="detail-container">
            {/* Header */}
            <div className="detail-header-card">
              <div className="detail-top-row">
                <span className="group-id-pill">{grp.group_id}</span>
                <div className="header-badges">
                  <SeverityBadge severity={grp.severity} />
                  <StatusBadge status={grp.status} type="failure" />
                </div>
              </div>
              <h1 className="detail-title">{grp.title}</h1>
              <div className="detail-meta-strip">
                <span>
                  Failure Type: <strong>{grp.failure_type.replace(/_/g, ' ')}</strong>
                </span>
                <span>·</span>
                <span>
                  Occurrences: <strong>{grp.occurrence_count} sessions</strong>
                </span>
                <span>·</span>
                <span>
                  Confidence: <strong>{Math.round((grp.confidence || 0) * 100)}%</strong>
                </span>
              </div>
            </div>

            {/* Pattern & Signals */}
            <div className="panel detail-section">
              <h3>
                <ShieldAlert size={16} /> Pattern Summary
              </h3>
              <p className="detail-body-text">{grp.description}</p>
              {grp.common_signals && grp.common_signals.length > 0 && (
                <div className="signals-row">
                  <span className="signals-label">Common Rule Signals:</span>
                  <div className="tag-cloud">
                    {grp.common_signals.map((sig) => (
                      <SignalTag key={sig} signal={sig} />
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Investigation Area & Recommendation */}
            <div className="callout-box">
              <div className="callout-header">
                <Lightbulb size={18} className="text-warning" />
                <strong>Where Engineers Should Look First</strong>
              </div>
              <p className="callout-body">{grp.recommendation || grp.ai_summary || grp.description}</p>
            </div>

            {/* Evidence-Linked Member Failures */}
            <div className="panel detail-section">
              <div className="section-header-row">
                <h3>Member Failures ({linkedFailures.length})</h3>
                <span className="text-muted text-xs">Linked via session evidence</span>
              </div>

              <div className="member-failures-list">
                {linkedFailures.length === 0 ? (
                  <p className="text-muted p-3">No member failure details available.</p>
                ) : (
                  linkedFailures.map((f) => (
                    <div
                      key={f.failure_id}
                      className="member-failure-card"
                      onClick={() => onSelectFailure(f.failure_id)}
                    >
                      <div className="member-fail-top">
                        <div className="fail-identity">
                          <code className="id-code">{f.failure_id}</code>
                          <span className="session-link-label">Session: {f.session_id}</span>
                        </div>
                        <SeverityBadge severity={f.severity} />
                      </div>
                      <p className="member-fail-summary">{f.summary}</p>
                      <div className="member-fail-bottom">
                        <span className="evidence-count">
                          {f.evidence_event_ids?.length || 0} events cited
                        </span>
                        <button type="button" className="btn btn-ghost btn-xs">
                          <span>Inspect Failure</span>
                          <ChevronRight size={14} />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
