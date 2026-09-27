import React from 'react';
import {
  Users,
  AlertTriangle,
  AlertCircle,
  HelpCircle,
  TrendingDown,
  Layers,
  ArrowRight,
  Flame,
} from 'lucide-react';
import { SeverityBadge, Spinner, EmptyState } from './common';

export function OverviewView({ dashboard, onSelectGroup, onSelectFailure, loading }) {
  if (loading || !dashboard) {
    return (
      <div className="view-loading">
        <Spinner size={32} />
        <p>Loading investigation dashboard...</p>
      </div>
    );
  }

  const { summary, failure_distribution = [], severity_distribution = [], groups = [], recent_failures = [] } =
    dashboard;

  const totalSessions = summary.total_sessions || 0;
  const totalFailures = summary.total_failures || 0;
  const failureRate = totalSessions > 0 ? ((totalFailures / totalSessions) * 100).toFixed(1) : 0;
  const avgConfidence = summary.average_confidence
    ? (summary.average_confidence * 100).toFixed(1) + '%'
    : 'N/A';

  // Calculate maximum count for distribution bar scaling
  const maxCount = Math.max(...failure_distribution.map((x) => x.count), 1);

  return (
    <div className="overview-container">
      {/* KPI Cards Row */}
      <section className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">TOTAL SESSIONS</span>
            <Users size={16} className="text-muted" />
          </div>
          <div className="kpi-value">{totalSessions.toLocaleString()}</div>
          <div className="kpi-footer">
            <span className="text-success">{summary.successful_sessions || 0} succeeded</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">FAILURES DETECTED</span>
            <AlertCircle size={16} className="text-danger" />
          </div>
          <div className="kpi-value text-danger">{totalFailures.toLocaleString()}</div>
          <div className="kpi-footer">
            <span>Failure Rate: <strong>{failureRate}%</strong></span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">CRITICAL FAILURES</span>
            <Flame size={16} className="text-danger" />
          </div>
          <div className="kpi-value text-critical">{summary.critical_failures || 0}</div>
          <div className="kpi-footer">
            <span>Severe workflow breakages</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">AMBIGUOUS SESSIONS</span>
            <HelpCircle size={16} className="text-warning" />
          </div>
          <div className="kpi-value text-warning">{summary.ambiguous_sessions || 0}</div>
          <div className="kpi-footer">
            <span>Uncertain / pending state</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">RECURRING GROUPS</span>
            <Layers size={16} className="text-purple" />
          </div>
          <div className="kpi-value text-purple">{summary.total_groups || 0}</div>
          <div className="kpi-footer">
            <span>Clustered failure patterns</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">AVG CONFIDENCE</span>
            <TrendingDown size={16} className="text-cyan" />
          </div>
          <div className="kpi-value text-cyan">{avgConfidence}</div>
          <div className="kpi-footer">
            <span>Rule & AI certainty score</span>
          </div>
        </div>
      </section>

      {/* Charts & Breakdown Grid */}
      <section className="dashboard-grid">
        {/* Failure Distribution */}
        <div className="panel">
          <div className="panel-header">
            <h2>Failure Type Distribution</h2>
            <span className="badge-neutral">{failure_distribution.length} categories</span>
          </div>
          <p className="panel-sub">Breakdown of semantic failures identified by the rule engine & AI.</p>

          <div className="distribution-list">
            {failure_distribution.length === 0 ? (
              <EmptyState title="No Failures" message="No failure patterns detected in this dataset." />
            ) : (
              failure_distribution.map((item) => {
                const widthPct = Math.round((item.count / maxCount) * 100);
                const displayType = (item.failure_type || '').replace(/_/g, ' ');
                return (
                  <div key={item.failure_type} className="dist-row">
                    <div className="dist-label-row">
                      <span className="dist-type-name">{displayType}</span>
                      <span className="dist-count">{item.count} sessions</span>
                    </div>
                    <div className="bar-track">
                      <div className="bar-fill" style={{ width: `${Math.max(widthPct, 4)}%` }} />
                    </div>
                  </div>
                );
              })
            )}
          </div>

          <div className="severity-summary-strip">
            <div className="sev-label">Severity Breakdown:</div>
            <div className="sev-pills">
              {severity_distribution.map((s) => (
                <div key={s.severity} className="sev-pill-item">
                  <SeverityBadge severity={s.severity} />
                  <strong>{s.count}</strong>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recurring Groups */}
        <div className="panel">
          <div className="panel-header">
            <h2>Recurring Failure Patterns</h2>
            <span className="badge-neutral">{groups.length} groups</span>
          </div>
          <p className="panel-sub">Clustered failure signatures prioritized by recurrence and impact.</p>

          <div className="groups-list">
            {groups.length === 0 ? (
              <EmptyState title="No Groups" message="No failure groups have been generated." />
            ) : (
              groups.map((group) => (
                <div
                  key={group.group_id}
                  className="group-card"
                  onClick={() => onSelectGroup(group.group_id)}
                >
                  <div className="group-card-left">
                    <div className="group-card-title-row">
                      <strong className="group-title">{group.title}</strong>
                      <SeverityBadge severity={group.severity} />
                    </div>
                    <div className="group-meta-row">
                      <span className="group-type-badge">{group.failure_type.replace(/_/g, ' ')}</span>
                      <span>·</span>
                      <span>Confidence: {Math.round(group.confidence * 100)}%</span>
                      <span>·</span>
                      <span className="status-text">{group.status}</span>
                    </div>
                  </div>

                  <div className="group-card-right">
                    <div className="group-occurrence">
                      <span className="occ-count">{group.occurrence_count}</span>
                      <span className="occ-label">sessions</span>
                    </div>
                    <ArrowRight size={16} className="group-arrow" />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </section>

      {/* Recent Failures Stream */}
      <section className="panel recent-failures-panel">
        <div className="panel-header">
          <h2>Recent Failure Stream</h2>
          <span className="count-badge">{recent_failures.length} latest instances</span>
        </div>
        <p className="panel-sub">Individual failures with direct links into session evidence.</p>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Failure ID</th>
                <th>Failure Type</th>
                <th>Severity</th>
                <th>Title / Observation</th>
                <th>Session</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {recent_failures.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center py-4 text-muted">
                    No individual failures recorded.
                  </td>
                </tr>
              ) : (
                recent_failures.map((f) => (
                  <tr key={f.failure_id} onClick={() => onSelectFailure(f.failure_id)} className="clickable-row">
                    <td>
                      <code className="id-code">{f.failure_id}</code>
                    </td>
                    <td>
                      <span className="type-tag">{f.failure_type.replace(/_/g, ' ')}</span>
                    </td>
                    <td>
                      <SeverityBadge severity={f.severity} />
                    </td>
                    <td className="max-w-md">
                      <span className="cell-truncate">{f.title}</span>
                    </td>
                    <td>
                      <code className="id-code-sub">{f.session_id}</code>
                    </td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-ghost btn-xs"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectFailure(f.failure_id);
                        }}
                      >
                        Inspect Evidence
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
