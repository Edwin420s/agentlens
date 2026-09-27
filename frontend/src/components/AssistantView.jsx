import React, { useState } from 'react';
import {
  Bot,
  Sparkles,
  Send,
  HelpCircle,
  ShieldCheck,
  AlertTriangle,
  Lightbulb,
  CheckCircle2,
  Bookmark,
  ExternalLink,
} from 'lucide-react';
import { Spinner, EmptyState } from './common';

export function AssistantView({
  investigationId,
  onQuery,
  onSelectFailure,
  onSelectSession,
  loading,
}) {
  const [question, setQuestion] = useState(
    'Which failure pattern should engineers investigate first and why?'
  );
  const [answer, setAnswer] = useState(null);
  const [querying, setQuerying] = useState(false);
  const [error, setError] = useState('');

  const quickPrompts = [
    'Which failure pattern should engineers investigate first and why?',
    'Where does the agent claim success while the workflow quietly failed?',
    'What are the common patterns in wrong record retrieval?',
    'Summarize all critical failures with their impacted customers or orders.',
    'What engineering safeguards should be added to the tool-calling layer?',
  ];

  const handleAsk = async (qToAsk) => {
    const q = qToAsk || question;
    if (!q.trim()) return;
    setError('');
    setQuerying(true);
    try {
      const res = await onQuery(q);
      setAnswer(res);
    } catch (err) {
      setError(err.message || 'Failed to query assistant');
    } finally {
      setQuerying(false);
    }
  };

  // Safe normalizers for observed_facts, recommendations, uncertainty
  const observedFacts = Array.isArray(answer?.observed_facts)
    ? answer.observed_facts
    : answer?.observed_facts
    ? [answer.observed_facts]
    : [];

  const recommendations = Array.isArray(answer?.recommendation)
    ? answer.recommendation
    : Array.isArray(answer?.recommendations)
    ? answer.recommendations
    : answer?.recommendation
    ? [answer.recommendation]
    : [];

  const uncertainty = Array.isArray(answer?.uncertainty)
    ? answer.uncertainty
    : answer?.uncertainty
    ? [answer.uncertainty]
    : [];

  const citations = Array.isArray(answer?.evidence_citations)
    ? answer.evidence_citations
    : [];

  return (
    <div className="assistant-view-container">
      {/* Query Bar & Presets */}
      <div className="panel assistant-query-panel">
        <div className="assistant-header-row">
          <div className="assistant-title-group">
            <div className="assistant-avatar">
              <Bot size={22} />
            </div>
            <div>
              <h2>Investigation Assistant</h2>
              <p className="panel-desc">
                Ask root-cause questions grounded directly in stored evidence. Answers explicitly separate
                observed proof from model interpretation.
              </p>
            </div>
          </div>
        </div>

        {/* Quick prompt chips */}
        <div className="prompt-chips-row">
          <span className="chips-label">Suggested Prompts:</span>
          <div className="chips-list">
            {quickPrompts.map((p, idx) => (
              <button
                key={idx}
                type="button"
                className="prompt-chip"
                onClick={() => {
                  setQuestion(p);
                  handleAsk(p);
                }}
              >
                <span>{p}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Query Input Box */}
        <div className="query-input-wrapper">
          <textarea
            className="assistant-textarea"
            rows={3}
            placeholder="Ask a question about failure patterns, root causes, or session traces..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                handleAsk();
              }
            }}
          />
          <div className="query-input-footer">
            <span className="shortcut-hint">Press ⌘+Enter or click Investigate</span>
            <button
              type="button"
              className="btn btn-primary"
              disabled={querying || !question.trim()}
              onClick={() => handleAsk()}
            >
              {querying ? (
                <>
                  <Spinner size={16} />
                  <span>Synthesizing Evidence...</span>
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  <span>Investigate</span>
                  <Send size={14} />
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-banner mb-4">
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Answer Section */}
      {querying ? (
        <div className="panel assistant-loading-card">
          <Spinner size={36} />
          <h3>Grounding response in verifiable traces...</h3>
          <p className="text-muted">
            Analyzing deterministic signals, failure groups, and session logs.
          </p>
        </div>
      ) : answer ? (
        <div className="assistant-result-container">
          {/* Main Synthesized Answer */}
          <div className="panel answer-primary-card">
            <div className="answer-section-header">
              <Sparkles size={18} className="text-purple" />
              <h3>Synthesized Finding</h3>
            </div>
            <div className="answer-body-prose">{answer.answer}</div>
          </div>

          <div className="answer-two-col-grid">
            {/* Observed Facts (Ground Truth) */}
            <div className="panel facts-card">
              <div className="answer-section-header">
                <CheckCircle2 size={18} className="text-green" />
                <h3>Verifiable Observed Facts</h3>
              </div>
              <p className="panel-sub">Concrete trace observations proven in stored logs.</p>
              {observedFacts.length === 0 ? (
                <p className="text-muted">No explicit bullet facts extracted.</p>
              ) : (
                <ul className="evidence-bullets">
                  {observedFacts.map((fact, idx) => (
                    <li key={idx}>
                      <span className="bullet-dot" />
                      <span>{fact}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Recommendations */}
            <div className="panel recommendations-card">
              <div className="answer-section-header">
                <Lightbulb size={18} className="text-warning" />
                <h3>Actionable Recommendations</h3>
              </div>
              <p className="panel-sub">Engineering fixes for prompt, tools, or validation rules.</p>
              {recommendations.length === 0 ? (
                <p className="text-muted">No specific recommendations provided.</p>
              ) : (
                <ul className="evidence-bullets">
                  {recommendations.map((rec, idx) => (
                    <li key={idx}>
                      <span className="bullet-dot warning" />
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Uncertainty & Limitations */}
          {uncertainty.length > 0 && (
            <div className="panel uncertainty-card">
              <div className="answer-section-header">
                <HelpCircle size={18} className="text-cyan" />
                <h3>Uncertainty & Analysis Boundaries</h3>
              </div>
              <ul className="evidence-bullets">
                {uncertainty.map((item, idx) => (
                  <li key={idx}>
                    <span className="bullet-dot cyan" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Citations */}
          {citations.length > 0 && (
            <div className="panel citations-card">
              <div className="answer-section-header">
                <Bookmark size={16} />
                <h3>Cited Evidence IDs ({citations.length})</h3>
              </div>
              <div className="citations-list">
                {citations.map((c, idx) => (
                  <span key={idx} className="citation-pill">
                    {c}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <EmptyState
          icon={Bot}
          title="Ready to Investigate"
          message="Type a custom query above or click one of the suggested prompts to investigate failure causes, tool mismatches, and agent hallucinations."
        />
      )}
    </div>
  );
}
