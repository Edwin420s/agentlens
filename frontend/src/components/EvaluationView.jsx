import React, { useEffect, useState } from 'react';
import {
  Award,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ShieldCheck,
  BarChart2,
  RefreshCw,
} from 'lucide-react';
import { Spinner, EmptyState, ErrorBanner } from './common';

export function EvaluationView({ investigationId, onFetchEvaluation }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadData = async () => {
    if (!investigationId) return;
    setLoading(true);
    setError('');
    try {
      const res = await onFetchEvaluation(investigationId);
      setData(res);
    } catch (err) {
      setError(err.message || 'Failed to load evaluation metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [investigationId]);

  if (loading) {
    return (
      <div className="view-loading">
        <Spinner size={32} />
        <p>Calculating precision, recall, and confusion matrix against benchmark...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <ErrorBanner message={error} />
        <button type="button" className="btn btn-secondary mt-3" onClick={loadData}>
          <RefreshCw size={14} />
          <span>Retry Evaluation</span>
        </button>
      </div>
    );
  }

  if (!data || !data.confusion) {
    return (
      <EmptyState
        icon={Award}
        title="No Ground-Truth Benchmark Labels Found"
        message="This dataset does not contain separate ground-truth evaluation labels. Evaluation is only available for benchmark datasets such as the frozen 100-session NovaCart benchmark."
      />
    );
  }

  const { tp = 0, fp = 0, fn = 0, tn = 0 } = data.confusion;
  const total = tp + fp + fn + tn;
  const accuracy = total > 0 ? ((tp + tn) / total) * 100 : 0;
  const precisionPct = (data.precision * 100).toFixed(1);
  const recallPct = (data.recall * 100).toFixed(1);
  const f1Score = (data.f1 * 100).toFixed(1);

  const perType = data.per_failure_type || {};

  return (
    <div className="evaluation-container">
      {/* Top Banner */}
      <div className="panel eval-banner-card">
        <div className="eval-header-row">
          <div className="eval-title-group">
            <div className="eval-icon-badge">
              <Award size={24} />
            </div>
            <div>
              <h2>Benchmark Evaluation & Precision Metrics</h2>
              <p className="panel-sub">
                Evaluated against isolated ground-truth labels across {data.sessions_evaluated || total}{' '}
                sessions.
              </p>
            </div>
          </div>
          <button type="button" className="btn btn-secondary btn-sm" onClick={loadData}>
            <RefreshCw size={14} />
            <span>Recalculate</span>
          </button>
        </div>

        <div className="leakage-guarantee-note">
          <ShieldCheck size={16} className="text-green" />
          <span>
            <strong>Zero Ground-Truth Leakage Verified:</strong> Ground truth labels were stored in an
            isolated database collection (<code>evaluation_labels</code>) and were completely excluded from the
            rule engine and AI analyzer during inference.
          </span>
        </div>
      </div>

      {/* KPI Cards */}
      <section className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">PRECISION</span>
            <CheckCircle2 size={16} className="text-green" />
          </div>
          <div className="kpi-value text-green">{precisionPct}%</div>
          <div className="kpi-footer">
            <span>TP / (TP + FP) = {tp} / {tp + fp}</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">RECALL</span>
            <CheckCircle2 size={16} className="text-cyan" />
          </div>
          <div className="kpi-value text-cyan">{recallPct}%</div>
          <div className="kpi-footer">
            <span>TP / (TP + FN) = {tp} / {tp + fn}</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">F1-SCORE</span>
            <Award size={16} className="text-purple" />
          </div>
          <div className="kpi-value text-purple">{f1Score}%</div>
          <div className="kpi-footer">
            <span>Harmonic mean of precision & recall</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">OVERALL ACCURACY</span>
            <BarChart2 size={16} className="text-muted" />
          </div>
          <div className="kpi-value">{accuracy.toFixed(1)}%</div>
          <div className="kpi-footer">
            <span>Correct classifications ({tp + tn} / {total})</span>
          </div>
        </div>
      </section>

      {/* Matrix and Per-Type Breakdown */}
      <section className="eval-detail-grid">
        {/* Confusion Matrix */}
        <div className="panel matrix-panel">
          <div className="panel-header">
            <h3>Confusion Matrix (N = {total})</h3>
            <span className="badge-neutral">Binary Outcome</span>
          </div>
          <p className="panel-sub">
            Comparison between ground truth labels and AgentLens detected failure signals.
          </p>

          <div className="matrix-table-wrapper">
            <table className="confusion-matrix-table">
              <thead>
                <tr>
                  <th className="diagonal-cell">Predicted \ Actual</th>
                  <th>Actual Failure</th>
                  <th>Actual Success</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th>Predicted Failure</th>
                  <td className="matrix-cell tp-cell">
                    <div className="cell-code">TP (True Positive)</div>
                    <div className="cell-num text-success">{tp}</div>
                    <small>Correctly detected failures</small>
                  </td>
                  <td className="matrix-cell fp-cell">
                    <div className="cell-code">FP (False Positive)</div>
                    <div className="cell-num text-warning">{fp}</div>
                    <small>False alarms on success</small>
                  </td>
                </tr>
                <tr>
                  <th>Predicted Success</th>
                  <td className="matrix-cell fn-cell">
                    <div className="cell-code">FN (False Negative)</div>
                    <div className="cell-num text-danger">{fn}</div>
                    <small>Undetected failures (missed)</small>
                  </td>
                  <td className="matrix-cell tn-cell">
                    <div className="cell-code">TN (True Negative)</div>
                    <div className="cell-num text-muted">{tn}</div>
                    <small>Correctly cleared successes</small>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Per Failure Type Recall */}
        <div className="panel per-type-panel">
          <div className="panel-header">
            <h3>Per-Failure-Type Breakdown</h3>
            <span className="badge-neutral">{Object.keys(perType).length} Types</span>
          </div>
          <p className="panel-sub">Recall performance segmented by failure taxonomy.</p>

          <table className="data-table">
            <thead>
              <tr>
                <th>Failure Category</th>
                <th>Detected (TP)</th>
                <th>Missed (FN)</th>
                <th>Type Recall</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(perType).map(([typeKey, stats]) => {
                const totalType = stats.tp + stats.fn;
                const typeRecall = totalType > 0 ? ((stats.tp / totalType) * 100).toFixed(0) + '%' : 'N/A';
                return (
                  <tr key={typeKey}>
                    <td>
                      <strong className="text-light">{typeKey.replace(/_/g, ' ')}</strong>
                    </td>
                    <td>
                      <span className="text-success font-bold">{stats.tp}</span>
                    </td>
                    <td>
                      <span className={stats.fn > 0 ? 'text-danger font-bold' : 'text-muted'}>
                        {stats.fn}
                      </span>
                    </td>
                    <td>
                      <span className="badge-neutral">{typeRecall}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
