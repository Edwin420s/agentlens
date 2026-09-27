import React, { useState } from 'react';
import {
  AlertTriangle,
  AlertCircle,
  CheckCircle2,
  Clock,
  HelpCircle,
  User,
  Bot,
  Wrench,
  Terminal,
  Copy,
  Check,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';

export function SeverityBadge({ severity }) {
  const s = (severity || 'medium').toLowerCase();
  const styles = {
    critical: 'badge-severity-critical',
    high: 'badge-severity-high',
    medium: 'badge-severity-medium',
    low: 'badge-severity-low',
  };

  return (
    <span className={`badge ${styles[s] || styles.medium}`}>
      {s === 'critical' && <AlertCircle size={12} />}
      {s === 'high' && <AlertTriangle size={12} />}
      {s === 'medium' && <HelpCircle size={12} />}
      {s === 'low' && <Clock size={12} />}
      <span>{s.toUpperCase()}</span>
    </span>
  );
}

export function StatusBadge({ status, type = 'session' }) {
  const st = (status || 'unknown').toLowerCase();
  let colorClass = 'badge-neutral';
  let Icon = HelpCircle;

  if (type === 'session') {
    if (st === 'success') {
      colorClass = 'badge-success';
      Icon = CheckCircle2;
    } else if (st === 'failure') {
      colorClass = 'badge-danger';
      Icon = AlertCircle;
    } else if (st === 'ambiguous') {
      colorClass = 'badge-warning';
      Icon = AlertTriangle;
    }
  } else {
    // failure lifecycle status
    if (st === 'new') {
      colorClass = 'badge-danger';
      Icon = AlertCircle;
    } else if (st === 'investigating') {
      colorClass = 'badge-warning';
      Icon = Clock;
    } else if (st === 'reviewed') {
      colorClass = 'badge-info';
      Icon = HelpCircle;
    } else if (st === 'resolved') {
      colorClass = 'badge-success';
      Icon = CheckCircle2;
    }
  }

  return (
    <span className={`badge ${colorClass}`}>
      <Icon size={12} />
      <span>{st.toUpperCase()}</span>
    </span>
  );
}

export function ActorBadge({ actor }) {
  const a = (actor || 'system').toLowerCase();
  const iconMap = {
    user: <User size={12} />,
    agent: <Bot size={12} />,
    tool: <Wrench size={12} />,
    system: <Terminal size={12} />,
  };

  const styleMap = {
    user: 'actor-user',
    agent: 'actor-agent',
    tool: 'actor-tool',
    system: 'actor-system',
  };

  return (
    <span className={`actor-badge ${styleMap[a] || 'actor-system'}`}>
      {iconMap[a] || <Terminal size={12} />}
      <span>{a}</span>
    </span>
  );
}

export function SignalTag({ signal }) {
  const label = (signal || '').replace(/_/g, ' ');
  return (
    <span className="signal-tag" title={signal}>
      #{label}
    </span>
  );
}

export function JsonViewer({ data, title = 'Payload' }) {
  const [copied, setCopied] = useState(false);
  const [open, setOpen] = useState(false);

  if (!data || Object.keys(data).length === 0) return null;

  const jsonStr = typeof data === 'string' ? data : JSON.stringify(data, null, 2);

  const handleCopy = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(jsonStr);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="json-viewer">
      <div className="json-header" onClick={() => setOpen(!open)}>
        <span className="json-title">
          {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          {title} <small>({typeof data === 'object' ? Object.keys(data).length + ' keys' : 'raw'})</small>
        </span>
        <button type="button" className="btn-icon" onClick={handleCopy} title="Copy JSON">
          {copied ? <Check size={12} className="text-success" /> : <Copy size={12} />}
        </button>
      </div>
      {open && (
        <pre className="json-content">
          <code>{jsonStr}</code>
        </pre>
      )}
    </div>
  );
}

export function EmptyState({ icon: Icon = HelpCircle, title, message, action }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">
        <Icon size={32} />
      </div>
      <h3>{title}</h3>
      <p>{message}</p>
      {action && <div className="empty-action">{action}</div>}
    </div>
  );
}

export function ErrorBanner({ message, onDismiss }) {
  if (!message) return null;
  return (
    <div className="error-banner">
      <AlertCircle size={18} />
      <span className="error-text">{message}</span>
      {onDismiss && (
        <button type="button" className="btn-close" onClick={onDismiss}>
          &times;
        </button>
      )}
    </div>
  );
}

export function Spinner({ size = 20 }) {
  return <div className="spinner" style={{ width: size, height: size }} />;
}
