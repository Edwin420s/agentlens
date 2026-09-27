import React, { useState } from 'react';
import {
  Sparkles,
  Upload,
  ArrowRight,
  Database,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  ShieldCheck,
  Cpu,
} from 'lucide-react';
import { Spinner, ErrorBanner } from './common';

export function LandingView({ investigations, onLoadDemo, onImportCustom, onSelectInvestigation, loading }) {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');

  const handleFileUpload = (file) => {
    setError('');
    if (!file) return;
    if (!file.name.endsWith('.json')) {
      setError('Please upload a valid JSON dataset file.');
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const parsed = JSON.parse(e.target.result);
        onImportCustom(parsed);
      } catch (err) {
        setError('Failed to parse JSON file: ' + err.message);
      }
    };
    reader.readAsText(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="landing-container">
      <section className="hero-section">
        <div className="hero-content">
          <div className="challenge-tag">
            <ShieldCheck size={14} />
            <span>SUPPLYZPRO CHALLENGE · FIND THE HIDDEN FAILURES</span>
          </div>
          <h1 className="hero-title">
            See where an AI agent says <span className="highlight-success">“success”</span> while the workflow{' '}
            <span className="highlight-danger">quietly fails</span>.
          </h1>
          <p className="hero-subtitle">
            AgentLens analyzes agent execution traces across 9 deterministic failure signals, clusters recurring
            semantic patterns, grounds conclusions in verifiable event logs, and guides engineers to root causes.
          </p>

          <div className="hero-actions">
            <button
              type="button"
              className="btn btn-primary btn-lg"
              onClick={onLoadDemo}
              disabled={loading}
            >
              {loading ? (
                <>
                  <Spinner size={18} />
                  <span>Ingesting 100 Sessions...</span>
                </>
              ) : (
                <>
                  <Sparkles size={18} />
                  <span>Load 100-Session Demo</span>
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </div>
        </div>

        <div className="hero-card">
          <div className="hero-card-header">
            <span className="card-badge">FROZEN BENCHMARK</span>
            <span className="card-domain">NovaCart E-Commerce</span>
          </div>
          <div className="stat-huge">100</div>
          <div className="stat-label">Full Agent Sessions Processed</div>
          <div className="hero-card-stats">
            <div className="pill-stat">
              <strong className="text-danger">26</strong> Failures
            </div>
            <div className="pill-stat">
              <strong className="text-warning">2</strong> Ambiguous
            </div>
            <div className="pill-stat">
              <strong className="text-success">72</strong> Successes
            </div>
          </div>
          <div className="feature-tags">
            <span>#unsupported_success</span>
            <span>#no_progress</span>
            <span>#wrong_record</span>
            <span>#repeated_question</span>
            <span>#incomplete_request</span>
          </div>
        </div>
      </section>

      {error && <ErrorBanner message={error} onDismiss={() => setError('')} />}

      <section className="landing-grid">
        {/* Upload Custom Dataset */}
        <div className="panel upload-panel">
          <h2>
            <Upload size={18} /> Import Custom Dataset
          </h2>
          <p className="panel-desc">Upload your agent session traces in standard AgentLens JSON format.</p>
          <div
            className={`dropzone ${dragActive ? 'active' : ''}`}
            onDragOver={(e) => {
              e.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
          >
            <Upload size={32} className="drop-icon" />
            <p>Drag and drop a .json file here</p>
            <span>or</span>
            <label className="btn btn-secondary btn-sm file-input-label">
              Browse File
              <input
                type="file"
                accept=".json"
                style={{ display: 'none' }}
                onChange={(e) => handleFileUpload(e.target.files[0])}
              />
            </label>
          </div>
        </div>

        {/* Existing Investigations */}
        <div className="panel history-panel">
          <div className="panel-header">
            <h2>
              <Layers size={18} /> Previous Investigations
            </h2>
            <span className="count-badge">{investigations.length} recorded</span>
          </div>

          {investigations.length === 0 ? (
            <div className="empty-sub">
              <Database size={24} />
              <p>No investigations stored in MongoDB yet. Click “Load 100-Session Demo” above to start!</p>
            </div>
          ) : (
            <div className="investigations-list">
              {investigations.map((inv) => (
                <div
                  key={inv.investigation_id}
                  className="investigation-item"
                  onClick={() => onSelectInvestigation(inv.investigation_id)}
                >
                  <div className="inv-info">
                    <div className="inv-title-row">
                      <strong className="inv-name">{inv.name}</strong>
                      <span className={`status-pill ${inv.status}`}>{inv.status}</span>
                    </div>
                    <div className="inv-meta">
                      <span>ID: {inv.investigation_id}</span>
                      <span>·</span>
                      <span>Dataset: {inv.dataset_name}</span>
                      <span>·</span>
                      <span>{inv.total_sessions || 0} sessions</span>
                      <span>·</span>
                      <span className="text-danger">{inv.failure_count || 0} failures</span>
                    </div>
                  </div>
                  <button type="button" className="btn btn-icon-round" title="Open Investigation">
                    <ArrowRight size={16} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Architecture Highlights */}
      <section className="architecture-strip">
        <div className="arch-item">
          <Cpu size={20} className="arch-icon text-cyan" />
          <div>
            <strong>Deterministic Rule Engine</strong>
            <p>9 frozen signals analyze sequence events with legitimate-retry suppression.</p>
          </div>
        </div>
        <div className="arch-item">
          <Sparkles size={20} className="arch-icon text-purple" />
          <div>
            <strong>AI Root-Cause Intelligence</strong>
            <p>Groq / Gemini models synthesize failure groups with strict fallback handling.</p>
          </div>
        </div>
        <div className="arch-item">
          <ShieldCheck size={20} className="arch-icon text-green" />
          <div>
            <strong>Zero Ground-Truth Leakage</strong>
            <p>Evaluation labels are strictly isolated in a separate collection.</p>
          </div>
        </div>
      </section>
    </div>
  );
}
