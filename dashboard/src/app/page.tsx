'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { api, EngineStatus, CommandRecord, CustomCommand } from '@/lib/api';

/* ── Helpers ───────────────────────────────────────────────────────────── */
function fmtTime(iso: string) {
  const d = new Date(iso);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

/* ── Status Orb ─────────────────────────────────────────────────────────── */
function StatusOrb({ online, loading, onToggle }: { online: boolean; loading: boolean; onToggle: () => void }) {
  return (
    <div className="status-orb-wrap">
      <div className="orb-container">
        {online && <div className="orb-pulse" />}
        <div className={`orb-ring ${online ? 'online' : ''}`} />
        <div className={`orb ${online ? 'online' : 'offline'}`} />
      </div>
      <span className={`status-label ${online ? 'online' : 'offline'}`}>
        {online ? '● ONLINE' : '○ OFFLINE'}
      </span>
      <div style={{ display: 'flex', gap: 10 }}>
        <button
          className="btn btn-primary"
          onClick={onToggle}
          disabled={loading}
        >
          {loading ? '...' : online ? 'Stop Tars' : 'Start Tars'}
        </button>
      </div>
    </div>
  );
}

/* ── Stat Pills ─────────────────────────────────────────────────────────── */
function Stats({ total, success }: { total: number; success: number }) {
  const rate = total > 0 ? Math.round((success / total) * 100) : 0;
  return (
    <div className="stat-row">
      <div className="stat-pill">
        <span className="stat-num">{total}</span>
        <span className="stat-desc">Commands</span>
      </div>
      <div className="stat-pill">
        <span className="stat-num">{success}</span>
        <span className="stat-desc">Executed</span>
      </div>
      <div className="stat-pill">
        <span className="stat-num">{rate}%</span>
        <span className="stat-desc">Success</span>
      </div>
    </div>
  );
}

/* ── Command Log ─────────────────────────────────────────────────────────── */
function CommandLog({ records, onClear }: { records: CommandRecord[]; onClear: () => void }) {
  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [records]);

  return (
    <div className="card" style={{ gridColumn: '1 / -1' }}>
      <div className="card-title" style={{ justifyContent: 'space-between' }}>
        <span>Command Log</span>
        <button className="btn btn-ghost" style={{ fontSize: '0.6rem', padding: '6px 14px' }} onClick={onClear}>
          Clear
        </button>
      </div>
      <div className="log-list">
        {records.length === 0
          ? <p className="empty">No commands yet. Say "Tars" to activate!</p>
          : records.map(r => (
            <div key={r.id} className="log-row">
              <div className={`log-dot ${r.success ? 'success' : 'fail'}`} />
              <span className="log-command">{r.command}</span>
              <span className="log-time">{fmtTime(r.timestamp)}</span>
            </div>
          ))
        }
        <div ref={bottomRef} />
      </div>
    </div>
  );
}

/* ── Custom Commands ─────────────────────────────────────────────────────── */
function CustomCommands({ commands, onCreate, onDelete }: {
  commands: CustomCommand[];
  onCreate: (data: { trigger: string; action: string; description: string }) => void;
  onDelete: (id: number) => void;
}) {
  const [trigger, setTrigger]   = useState('');
  const [action, setAction]     = useState('');
  const [desc, setDesc]         = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!trigger || !action) return;
    onCreate({ trigger, action, description: desc });
    setTrigger(''); setAction(''); setDesc('');
  };

  return (
    <div className="card">
      <div className="card-title">Custom Commands</div>
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <input className="input" placeholder='Trigger phrase (e.g., "work mode")' value={trigger} onChange={e => setTrigger(e.target.value)} />
          <input className="input" placeholder='Action (e.g., "start code")' value={action} onChange={e => setAction(e.target.value)} />
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <input className="input" style={{ flex: 1 }} placeholder="Description (optional)" value={desc} onChange={e => setDesc(e.target.value)} />
          <button type="submit" className="btn btn-primary" style={{ whiteSpace: 'nowrap' }}>+ Add</button>
        </div>
      </form>
      <div className="cmd-list">
        {commands.length === 0
          ? <p className="empty">No custom commands yet.</p>
          : commands.map(c => (
            <div key={c.id} className="cmd-row">
              <span className="cmd-trigger">{c.trigger}</span>
              <span className="cmd-action">→ {c.action}</span>
              <button className="cmd-delete" onClick={() => onDelete(c.id)} title="Delete">✕</button>
            </div>
          ))
        }
      </div>
    </div>
  );
}

/* ── Settings Panel ─────────────────────────────────────────────────────── */
function SettingsPanel({ status, onPatch }: { status: EngineStatus | null; onPatch: (d: Partial<EngineStatus>) => void }) {
  if (!status) return <div className="card"><p className="empty">Loading settings…</p></div>;
  return (
    <div className="card">
      <div className="card-title">Engine Settings</div>
      <div className="settings-grid">
        <div className="setting-row">
          <span className="setting-label">Wake Word</span>
          <input
            className="input"
            style={{ width: 120, textAlign: 'center' }}
            defaultValue={status.wake_word}
            onBlur={e => onPatch({ wake_word: e.target.value })}
          />
        </div>
        <div className="setting-row">
          <span className="setting-label">Speech Rate</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <input
              type="range" min={80} max={300} step={5}
              defaultValue={status.tts_rate}
              onMouseUp={e => onPatch({ tts_rate: Number((e.target as HTMLInputElement).value) })}
            />
            <span className="setting-value">{status.tts_rate}</span>
          </div>
        </div>
        <div className="setting-row">
          <span className="setting-label">Volume</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <input
              type="range" min={0} max={1} step={0.05}
              defaultValue={status.tts_volume}
              onMouseUp={e => onPatch({ tts_volume: Number((e.target as HTMLInputElement).value) })}
            />
            <span className="setting-value">{Math.round(status.tts_volume * 100)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── Main Page ───────────────────────────────────────────────────────────── */
export default function Dashboard() {
  const [status,   setStatus]   = useState<EngineStatus | null>(null);
  const [history,  setHistory]  = useState<CommandRecord[]>([]);
  const [commands, setCommands] = useState<CustomCommand[]>([]);
  const [toggling, setToggling] = useState(false);
  const [apiError, setApiError] = useState('');

  // Fetch all data
  const refresh = useCallback(async () => {
    try {
      const [s, h, c] = await Promise.all([api.getStatus(), api.getHistory(), api.getCommands()]);
      setStatus(s);
      setHistory(h);
      setCommands(c);
      setApiError('');
    } catch {
      setApiError('Cannot reach TARS backend. Make sure Django is running on port 8000.');
    }
  }, []);

  // Poll every 3s
  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 3000);
    return () => clearInterval(id);
  }, [refresh]);

  const toggleEngine = async () => {
    if (!status) return;
    setToggling(true);
    try {
      if (status.engine_running) await api.stopEngine();
      else                       await api.startEngine();
      await refresh();
    } finally { setToggling(false); }
  };

  const successCount = history.filter(r => r.success).length;

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="header">
        <div>
          <div className="header-brand">TARS</div>
          <div className="header-sub">Voice-Controlled PC Assistant</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          {apiError && <span className="error-badge">⚠ Backend offline</span>}
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      </header>

      {/* Grid */}
      <main style={{ padding: 0 }}>
        <div className="main-grid">

          {/* Engine Control */}
          <div className="card">
            <div className="card-title">Engine Control</div>
            <StatusOrb
              online={status?.engine_running ?? false}
              loading={toggling}
              onToggle={toggleEngine}
            />
          </div>

          {/* Settings */}
          <SettingsPanel status={status} onPatch={async (d) => { await api.patchSettings(d); refresh(); }} />

          {/* Stats */}
          <div className="card">
            <div className="card-title">Statistics</div>
            <Stats total={history.length} success={successCount} />
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Wake word: <span style={{ color: 'var(--accent)', fontFamily: 'var(--font-display)', fontSize: '0.75rem' }}>
                {status?.wake_word?.toUpperCase() ?? '—'}
              </span>
            </p>
          </div>

          {/* Custom Commands */}
          <CustomCommands
            commands={commands}
            onCreate={async (data) => { await api.createCommand(data); refresh(); }}
            onDelete={async (id) => { await api.deleteCommand(id); refresh(); }}
          />

          {/* Command Log — full width */}
          <CommandLog
            records={[...history].reverse()}
            onClear={async () => { await api.clearHistory(); refresh(); }}
          />
        </div>
      </main>
    </div>
  );
}
