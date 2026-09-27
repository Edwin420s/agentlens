import React, { useState } from 'react';
import {
  Layers,
  BarChart3,
  Flame,
  Clock,
  Bot,
  Award,
  Download,
  Activity,
  ArrowLeft,
  ChevronDown,
} from 'lucide-react';

export function Header({
  investigation,
  investigations,
  activeTab,
  onTabChange,
  onSwitchInvestigation,
  onBackToLanding,
  onExport,
  apiHealthy,
}) {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'groups', label: 'Failure Groups', icon: Layers },
    { id: 'failures', label: 'Failures', icon: Flame },
    { id: 'sessions', label: 'Sessions', icon: Clock },
    { id: 'assistant', label: 'Assistant', icon: Bot },
    { id: 'evaluation', label: 'Evaluation', icon: Award },
  ];

  return (
    <header className="app-header">
      <div className="header-top">
        <div className="brand-group">
          <div className="brand" onClick={onBackToLanding} title="AgentLens Home">
            Agent<span className="brand-highlight">Lens</span>
          </div>
          <span className="brand-tagline">AI-Agent Reliability Observability</span>
        </div>

        <div className="header-controls">
          {/* API Health Pill */}
          <div className="health-pill" title={apiHealthy ? 'Backend API Connected' : 'Backend Disconnected'}>
            <span className={`status-dot ${apiHealthy ? 'connected' : 'disconnected'}`} />
            <span>{apiHealthy ? 'API Online' : 'API Offline'}</span>
          </div>

          {/* Export Button */}
          {investigation && (
            <div className="export-group">
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => onExport('json')}
                title="Export Investigation Data as JSON"
              >
                <Download size={14} />
                <span>Export JSON</span>
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => onExport('csv')}
                title="Export Investigation Data as CSV"
              >
                <Download size={14} />
                <span>CSV</span>
              </button>
            </div>
          )}

          {/* Back / Switcher */}
          <button type="button" className="btn btn-ghost btn-sm" onClick={onBackToLanding}>
            <ArrowLeft size={14} />
            <span>All Investigations</span>
          </button>
        </div>
      </div>

      {investigation && (
        <div className="header-sub">
          <div className="investigation-selector">
            <div className="inv-badge">ACTIVE</div>
            <div className="inv-dropdown-container">
              <div
                className="inv-dropdown-trigger"
                onClick={() => setDropdownOpen(!dropdownOpen)}
                title="Click to switch investigation"
              >
                <div>
                  <strong className="inv-title">{investigation.name}</strong>
                  <span className="inv-subtext">
                    {investigation.investigation_id} · Dataset: {investigation.dataset_name} v
                    {investigation.dataset_version || '1.0'}
                  </span>
                </div>
                <ChevronDown size={16} />
              </div>

              {dropdownOpen && (
                <div className="inv-dropdown-menu">
                  <div className="dropdown-label">Switch Investigation</div>
                  {investigations.map((item) => (
                    <div
                      key={item.investigation_id}
                      className={`dropdown-item ${
                        item.investigation_id === investigation.investigation_id ? 'active' : ''
                      }`}
                      onClick={() => {
                        onSwitchInvestigation(item.investigation_id);
                        setDropdownOpen(false);
                      }}
                    >
                      <strong>{item.name}</strong>
                      <small>{item.investigation_id}</small>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <nav className="tab-nav">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  type="button"
                  className={`tab-btn ${isActive ? 'active' : ''}`}
                  onClick={() => onTabChange(tab.id)}
                >
                  <Icon size={15} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      )}
    </header>
  );
}
