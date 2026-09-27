import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { api } from './api';
import './styles.css';

import { Header } from './components/Header';
import { LandingView } from './components/LandingView';
import { OverviewView } from './components/OverviewView';
import { FailureGroupsView } from './components/FailureGroupsView';
import { FailuresView } from './components/FailuresView';
import { SessionsView } from './components/SessionsView';
import { AssistantView } from './components/AssistantView';
import { EvaluationView } from './components/EvaluationView';
import { ErrorBanner, Spinner } from './components/common';

function App() {
  const [investigations, setInvestigations] = useState([]);
  const [activeInvestigation, setActiveInvestigation] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Investigation specific data
  const [dashboard, setDashboard] = useState(null);
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [failures, setFailures] = useState([]);
  const [selectedFailure, setSelectedFailure] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);

  // Status & notifications
  const [loading, setLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState('');
  const [apiHealthy, setApiHealthy] = useState(true);

  // Initial load
  useEffect(() => {
    checkHealth();
    loadInvestigations();
  }, []);

  async function checkHealth() {
    try {
      await api.health();
      setApiHealthy(true);
    } catch {
      setApiHealthy(false);
    }
  }

  async function loadInvestigations() {
    try {
      setError('');
      const data = await api.listInvestigations();
      setInvestigations(data || []);
    } catch (err) {
      setError(err.message || 'Failed to list investigations');
    }
  }

  async function openInvestigation(invId) {
    try {
      setLoading(true);
      setError('');

      // Fetch overview metadata & dashboard in parallel
      const [inv, dash, grps, fails, sess] = await Promise.all([
        api.getInvestigation(invId),
        api.getDashboard(invId),
        api.listFailureGroups(invId).catch(() => []),
        api.listFailures(invId, {}, 300).catch(() => []),
        api.listSessions(invId, 'all', 300).catch(() => []),
      ]);

      setActiveInvestigation(inv);
      setDashboard(dash);
      setGroups(grps);
      setFailures(fails);
      setSessions(sess);

      // Reset selection details
      setSelectedGroup(grps.length > 0 ? await api.getFailureGroup(grps[0].group_id).catch(() => null) : null);
      setSelectedFailure(fails.length > 0 ? await api.getFailure(fails[0].failure_id).catch(() => null) : null);
      setSelectedSession(sess.length > 0 ? await api.getSession(sess[0].session_id).catch(() => null) : null);

      setActiveTab('overview');
    } catch (err) {
      setError('Error opening investigation: ' + (err.message || String(err)));
    } finally {
      setLoading(false);
    }
  }

  async function handleLoadDemo() {
    try {
      setLoading(true);
      setError('');

      // 1. Create investigation record
      const created = await api.createInvestigation({
        name: 'NovaCart Reliability Investigation',
        description: 'Synthetic AI-agent reliability benchmark analysis across 100 customer service sessions',
        dataset_name: 'NovaCart Agent Reliability Demo',
      });

      // 2. Fetch frozen demo JSON from public asset
      const res = await fetch('/agentlens_demo_public.json');
      if (!res.ok) {
        throw new Error('Failed to load demo dataset file from /agentlens_demo_public.json');
      }
      const demoData = await res.json();

      // 3. Attach dataset and execute rule + AI pipeline
      await api.attachDataset(created.investigation_id, demoData);
      await api.analyzeInvestigation(created.investigation_id);

      // 4. Refresh investigations list and open the newly created investigation
      const all = await api.listInvestigations();
      setInvestigations(all);
      await openInvestigation(created.investigation_id);
    } catch (err) {
      setError('Demo setup failed: ' + (err.message || String(err)));
    } finally {
      setLoading(false);
    }
  }

  async function handleImportCustom(customData) {
    try {
      setLoading(true);
      setError('');

      const name = customData.name || customData.dataset_name || 'Custom Dataset Investigation';
      const created = await api.createInvestigation({
        name: `Investigation: ${name}`,
        description: `Imported dataset: ${customData.description || 'Customer agent session traces'}`,
        dataset_name: name,
      });

      await api.attachDataset(created.investigation_id, customData);
      await api.analyzeInvestigation(created.investigation_id);

      const all = await api.listInvestigations();
      setInvestigations(all);
      await openInvestigation(created.investigation_id);
    } catch (err) {
      setError('Import failed: ' + (err.message || String(err)));
    } finally {
      setLoading(false);
    }
  }

  async function handleSelectGroup(groupId) {
    try {
      setDetailLoading(true);
      const detail = await api.getFailureGroup(groupId);
      setSelectedGroup(detail);
      setActiveTab('groups');
    } catch (err) {
      setError('Failed to fetch group details: ' + err.message);
    } finally {
      setDetailLoading(false);
    }
  }

  async function handleSelectFailure(failureId) {
    try {
      setDetailLoading(true);
      const detail = await api.getFailure(failureId);
      setSelectedFailure(detail);
      setActiveTab('failures');
    } catch (err) {
      setError('Failed to fetch failure details: ' + err.message);
    } finally {
      setDetailLoading(false);
    }
  }

  async function handleSelectSession(sessionId) {
    try {
      setDetailLoading(true);
      const detail = await api.getSession(sessionId);
      setSelectedSession(detail);
      setActiveTab('sessions');
    } catch (err) {
      setError('Failed to fetch session timeline: ' + err.message);
    } finally {
      setDetailLoading(false);
    }
  }

  async function handleUpdateFailureStatus(failureId, newStatus) {
    try {
      setError('');
      const updated = await api.updateFailureStatus(failureId, newStatus);
      // Update in selectedFailure
      if (selectedFailure && selectedFailure.failure_id === failureId) {
        setSelectedFailure({ ...selectedFailure, status: newStatus });
      }
      // Update in failures array
      setFailures((prev) =>
        prev.map((f) => (f.failure_id === failureId ? { ...f, status: newStatus } : f))
      );
    } catch (err) {
      setError('Failed to update status: ' + err.message);
    }
  }

  async function handleExport(format = 'json') {
    if (!activeInvestigation) return;
    try {
      const invId = activeInvestigation.investigation_id;
      if (format === 'csv') {
        const url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/investigations/${invId}/export?format=csv`;
        window.open(url, '_blank');
      } else {
        const data = await api.exportData(invId, 'json');
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `agentlens_investigation_${invId}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      setError('Export failed: ' + err.message);
    }
  }

  // Render view router
  return (
    <div className="app-shell">
      <Header
        investigation={activeInvestigation}
        investigations={investigations}
        activeTab={activeTab}
        onTabChange={(t) => {
          setActiveTab(t);
          setError('');
        }}
        onSwitchInvestigation={(id) => openInvestigation(id)}
        onBackToLanding={() => {
          setActiveInvestigation(null);
          setDashboard(null);
          loadInvestigations();
        }}
        onExport={handleExport}
        apiHealthy={apiHealthy}
      />

      {error && (
        <div className="global-error-wrap">
          <ErrorBanner message={error} onDismiss={() => setError('')} />
        </div>
      )}

      {loading ? (
        <div className="page-loading">
          <Spinner size={48} />
          <h2>Processing Investigation Intelligence...</h2>
          <p className="text-muted">
            Executing deterministic rule evaluation, vector clustering, and evidence synthesis.
          </p>
        </div>
      ) : !activeInvestigation ? (
        <LandingView
          investigations={investigations}
          onLoadDemo={handleLoadDemo}
          onImportCustom={handleImportCustom}
          onSelectInvestigation={(id) => openInvestigation(id)}
          loading={loading}
        />
      ) : (
        <main className="main-content-area">
          {activeTab === 'overview' && (
            <OverviewView
              dashboard={dashboard}
              onSelectGroup={handleSelectGroup}
              onSelectFailure={handleSelectFailure}
              loading={loading}
            />
          )}

          {activeTab === 'groups' && (
            <FailureGroupsView
              groups={groups}
              selectedGroup={selectedGroup}
              onSelectGroup={handleSelectGroup}
              onSelectFailure={handleSelectFailure}
              loading={detailLoading}
            />
          )}

          {activeTab === 'failures' && (
            <FailuresView
              failures={failures}
              selectedFailure={selectedFailure}
              onSelectFailure={handleSelectFailure}
              onUpdateStatus={handleUpdateFailureStatus}
              onSelectSession={handleSelectSession}
              loading={detailLoading}
            />
          )}

          {activeTab === 'sessions' && (
            <SessionsView
              sessions={sessions}
              selectedSession={selectedSession}
              onSelectSession={handleSelectSession}
              onSelectFailure={handleSelectFailure}
              loading={detailLoading}
            />
          )}

          {activeTab === 'assistant' && (
            <AssistantView
              investigationId={activeInvestigation.investigation_id}
              onQuery={(q) => api.queryAssistant(activeInvestigation.investigation_id, q)}
              onSelectFailure={handleSelectFailure}
              onSelectSession={handleSelectSession}
              loading={detailLoading}
            />
          )}

          {activeTab === 'evaluation' && (
            <EvaluationView
              investigationId={activeInvestigation.investigation_id}
              onFetchEvaluation={(id) => api.getEvaluation(id)}
            />
          )}
        </main>
      )}
    </div>
  );
}

const root = createRoot(document.getElementById('root'));
root.render(<App />);
