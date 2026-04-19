'use client';

import { useEffect, useState, useCallback, useRef, useMemo } from 'react';
import { api, EngineStatus, CommandRecord, CustomCommand, Skill } from '@/lib/api';
import { EventStream, TarsEvent } from '@/lib/ws';

/* -- Helpers ------------------------------------------------------------- */
function fmtTime(iso: string) {
  const d = new Date(iso);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

/* -- Minimal typing for the WebSpeech API -------------------------------- */
interface SpeechRecognitionLike extends EventTarget {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start(): void;
  stop(): void;
  onresult: ((e: { results: ArrayLike<{ 0: { transcript: string } }> }) => void) | null;
  onerror: (() => void) | null;
  onend:   (() => void) | null;
}
type SpeechRecognitionCtor = new () => SpeechRecognitionLike;
function getSpeechRecognition(): SpeechRecognitionCtor | null {
  if (typeof window === 'undefined') return null;
  const w = window as unknown as {
    SpeechRecognition?: SpeechRecognitionCtor;
    webkitSpeechRecognition?: SpeechRecognitionCtor;
  };
  return w.SpeechRecognition || w.webkitSpeechRecognition || null;
}

/* -- Status Orb ----------------------------------------------------------- */
function StatusOrb({
  online, loading, onToggle,
}: { online: boolean; loading: boolean; onToggle: () => void }) {
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
        <button className="btn btn-primary" onClick={onToggle} disabled={loading}>
          {loading ? '...' : online ? 'Stop Tars' : 'Start Tars'}
        </button>
      </div>
    </div>
  );
}

/* -- Push-to-Talk -------------------------------------------------------- */
function PushToTalk({ onTranscript }: { onTranscript: (text: string) => void }) {
  const [supported] = useState<boolean | null>(() =>
    typeof window === 'undefined' ? null : !!getSpeechRecognition(),
  );
  const [listening, setListening] = useState(false);
  const [interim, setInterim] = useState('');
  const recRef = useRef<SpeechRecognitionLike | null>(null);

  const start = () => {
    const Ctor = getSpeechRecognition();
    if (!Ctor) return;
    const rec = new Ctor();
    rec.lang = 'en-US';
    rec.continuous = false;
    rec.interimResults = false;
    rec.onresult = (e) => {
      const transcript = e.results[0]?.[0]?.transcript || '';
      setInterim(transcript);
      if (transcript) onTranscript(transcript);
    };
    rec.onerror = () => { setListening(false); };
    rec.onend   = () => { setListening(false); recRef.current = null; };
    recRef.current = rec;
    setInterim('');
    setListening(true);
    rec.start();
  };

  const stop = () => { recRef.current?.stop(); };

  return (
    <div className="card">
      <div className="card-title">Push to Talk</div>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14 }}>
        <button
          className={`ptt-button ${listening ? 'listening' : ''}`}
          onClick={listening ? stop : start}
          disabled={supported === false}
          aria-label="Push to talk"
        >
          {listening ? '■' : '🎙'}
        </button>
        <div style={{ textAlign: 'center' }}>
          {supported === false ? (
            <p className="empty" style={{ padding: 0 }}>
              This browser doesn&apos;t support speech input.
            </p>
          ) : (
            <>
              <span className={`status-label ${listening ? 'online' : 'offline'}`}>
                {listening ? 'LISTENING' : 'HOLD TO SPEAK'}
              </span>
              {interim && (
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 6 }}>
                  &ldquo;{interim}&rdquo;
                </p>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

/* -- Stat Pills ----------------------------------------------------------- */
function Stats({ total, success }: { total: number; success: number }) {
  const rate = total > 0 ? Math.round((success / total) * 100) : 0;
  return (
    <div className="stat-row">
      <div className="stat-pill"><span className="stat-num">{total}</span><span className="stat-desc">Commands</span></div>
      <div className="stat-pill"><span className="stat-num">{success}</span><span className="stat-desc">Executed</span></div>
      <div className="stat-pill"><span className="stat-num">{rate}%</span><span className="stat-desc">Success</span></div>
    </div>
  );
}

/* -- Command Log ----------------------------------------------------------- */
function CommandLog({ records, onClear, live }: {
  records: CommandRecord[]; onClear: () => void; live: boolean;
}) {
  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [records]);

  return (
    <div className="card" style={{ gridColumn: '1 / -1' }}>
      <div className="card-title" style={{ justifyContent: 'space-between' }}>
        <span>Command Log {live && <span className="live-badge">LIVE</span>}</span>
        <button
          className="btn btn-ghost"
          style={{ fontSize: '0.6rem', padding: '6px 14px' }}
          onClick={onClear}
        >
          Clear
        </button>
      </div>
      <div className="log-list">
        {records.length === 0
          ? <p className="empty">No commands yet. Say &quot;Tars&quot; to activate!</p>
          : records.map(r => (
              <div key={r.id} className="log-row">
                <div className={`log-dot ${r.success ? 'success' : 'fail'}`} />
                <span className="log-command">{r.command}</span>
                {r.skill && <span className="log-skill">{r.skill}</span>}
                <span className="log-time">{fmtTime(r.timestamp)}</span>
              </div>
            ))
        }
        <div ref={bottomRef} />
      </div>
    </div>
  );
}

/* -- Custom Commands ------------------------------------------------------- */
function CustomCommands({ commands, onCreate, onDelete }: {
  commands: CustomCommand[];
  onCreate: (data: { trigger: string; action: string; description: string }) => void;
  onDelete: (id: number) => void;
}) {
  const [trigger, setTrigger] = useState('');
  const [action,  setAction]  = useState('');
  const [desc,    setDesc]    = useState('');

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!trigger || !action) return;
    onCreate({ trigger, action, description: desc });
    setTrigger(''); setAction(''); setDesc('');
  };

  return (
    <div className="card">
      <div className="card-title">Custom Commands</div>
      <form onSubmit={submit}>
        <div className="form-row">
          <input className="input" placeholder='Trigger (e.g., "work mode")' value={trigger} onChange={e => setTrigger(e.target.value)} />
          <input className="input" placeholder='Action (shell command)'      value={action}  onChange={e => setAction(e.target.value)} />
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

/* -- Skills Browser ------------------------------------------------------- */
function SkillsBrowser({ skills }: { skills: Skill[] }) {
  const [filter, setFilter] = useState('');
  const filtered = useMemo(() => {
    const q = filter.trim().toLowerCase();
    if (!q) return skills;
    return skills.filter(s =>
      s.name.includes(q) || s.description.toLowerCase().includes(q) ||
      s.triggers.some(t => t.includes(q)),
    );
  }, [skills, filter]);

  return (
    <div className="card">
      <div className="card-title" style={{ justifyContent: 'space-between' }}>
        <span>Skills ({skills.length})</span>
        <input
          className="input"
          style={{ maxWidth: 160 }}
          placeholder="Filter…"
          value={filter}
          onChange={e => setFilter(e.target.value)}
        />
      </div>
      <div className="skill-list">
        {filtered.length === 0
          ? <p className="empty">No skills match.</p>
          : filtered.map(s => (
              <div key={s.name} className="skill-row">
                <div className="skill-name">{s.name}</div>
                <div className="skill-desc">{s.description || '—'}</div>
                <div className="skill-triggers">
                  {s.triggers.slice(0, 4).map(t => <span key={t} className="trigger-chip">{t}</span>)}
                </div>
              </div>
            ))
        }
      </div>
    </div>
  );
}

/* -- Settings Panel ------------------------------------------------------- */
function SettingsPanel({ status, onPatch }: {
  status: EngineStatus | null;
  onPatch: (d: Partial<EngineStatus>) => void;
}) {
  if (!status) return <div className="card"><p className="empty">Loading settings…</p></div>;
  return (
    <div className="card">
      <div className="card-title">Engine Settings</div>
      <div className="settings-grid">
        <div className="setting-row">
          <span className="setting-label">Wake Word</span>
          <input
            className="input" style={{ width: 120, textAlign: 'center' }}
            defaultValue={status.wake_word}
            onBlur={e => onPatch({ wake_word: e.target.value })}
          />
        </div>
        <div className="setting-row">
          <span className="setting-label">Speech Rate</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <input type="range" min={80} max={300} step={5}
              defaultValue={status.tts_rate}
              onMouseUp={e => onPatch({ tts_rate: Number((e.target as HTMLInputElement).value) })}
            />
            <span className="setting-value">{status.tts_rate}</span>
          </div>
        </div>
        <div className="setting-row">
          <span className="setting-label">Volume</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <input type="range" min={0} max={1} step={0.05}
              defaultValue={status.tts_volume}
              onMouseUp={e => onPatch({ tts_volume: Number((e.target as HTMLInputElement).value) })}
            />
            <span className="setting-value">{Math.round(status.tts_volume * 100)}%</span>
          </div>
        </div>
        <div className="setting-row">
          <span className="setting-label">Brain</span>
          <select
            className="input" style={{ width: 140 }}
            defaultValue={status.brain_provider}
            onChange={e => onPatch({ brain_provider: e.target.value })}
          >
            <option value="rules">rules</option>
            <option value="openai">openai</option>
            <option value="groq">groq</option>
            <option value="ollama">ollama</option>
          </select>
        </div>
        <div className="setting-row">
          <span className="setting-label">STT</span>
          <select
            className="input" style={{ width: 140 }}
            defaultValue={status.stt_provider}
            onChange={e => onPatch({ stt_provider: e.target.value })}
          >
            <option value="google">google</option>
            <option value="whisper">whisper</option>
          </select>
        </div>
        <div className="setting-row">
          <span className="setting-label">TTS</span>
          <select
            className="input" style={{ width: 140 }}
            defaultValue={status.tts_provider}
            onChange={e => onPatch({ tts_provider: e.target.value })}
          >
            <option value="pyttsx3">pyttsx3</option>
            <option value="edge">edge</option>
          </select>
        </div>
      </div>
    </div>
  );
}

/* -- Main Page ------------------------------------------------------------- */
export default function Dashboard() {
  const [status,   setStatus]   = useState<EngineStatus | null>(null);
  const [history,  setHistory]  = useState<CommandRecord[]>([]);
  const [commands, setCommands] = useState<CustomCommand[]>([]);
  const [skills,   setSkills]   = useState<Skill[]>([]);
  const [toggling, setToggling] = useState(false);
  const [apiError, setApiError] = useState('');
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    if (typeof window === 'undefined') return 'dark';
    const saved = window.localStorage.getItem('tars-theme');
    return saved === 'light' ? 'light' : 'dark';
  });
  const [wsLive, setWsLive] = useState(false);

  // Sync theme to <html data-theme> + persist
  useEffect(() => {
    if (typeof document !== 'undefined') document.documentElement.dataset.theme = theme;
    if (typeof window   !== 'undefined') window.localStorage.setItem('tars-theme', theme);
  }, [theme]);

  // Full refresh via REST
  const refresh = useCallback(async () => {
    try {
      const [s, h, c, sk] = await Promise.all([
        api.getStatus(),
        api.getHistory(),
        api.getCommands(),
        api.getSkills(),
      ]);
      setStatus(s);
      setHistory(h);
      setCommands(c);
      setSkills(sk);
      setApiError('');
    } catch {
      setApiError('Cannot reach TARS backend. Make sure Django is running on port 8000.');
    }
  }, []);

  useEffect(() => {
    // Defer initial fetch so React doesn't see a synchronous setState
    // happening inside this effect's setup phase.
    const id = setTimeout(() => { void refresh(); }, 0);
    return () => clearTimeout(id);
  }, [refresh]);

  // Realtime WebSocket stream
  useEffect(() => {
    const stream = new EventStream();
    const unsub = stream.subscribe((ev: TarsEvent) => {
      if (ev.type === 'hello') { setWsLive(true); return; }
      if (ev.type === 'command.new') {
        const record = ev.data as unknown as CommandRecord;
        setHistory(prev => [record, ...prev].slice(0, 200));
      } else if (ev.type === 'engine.state') {
        setStatus(prev => prev ? { ...prev, engine_running: Boolean(ev.data.running) } : prev);
      } else if (ev.type === 'settings.updated') {
        setStatus(prev => prev ? { ...prev, ...(ev.data as unknown as Partial<EngineStatus>) } : prev);
      } else if (ev.type === 'history.cleared') {
        setHistory([]);
      } else if (ev.type === 'command.custom.new' || ev.type === 'command.custom.updated') {
        refresh();
      } else if (ev.type === 'command.custom.deleted') {
        const id = ev.data.id as number;
        setCommands(prev => prev.filter(c => c.id !== id));
      }
    });
    stream.connect();
    return () => { unsub(); stream.close(); setWsLive(false); };
  }, [refresh]);

  // Gentle background polling in case the WS misses something (every 15s instead of 3s).
  useEffect(() => {
    const id = setInterval(refresh, 15000);
    return () => clearInterval(id);
  }, [refresh]);

  const toggleEngine = async () => {
    if (!status) return;
    setToggling(true);
    try {
      if (status.engine_running) await api.stopEngine(); else await api.startEngine();
      await refresh();
    } finally { setToggling(false); }
  };

  const handlePushToTalk = async (text: string) => {
    try {
      await api.speak(text);
      await api.logCommand(text, true, 'browser.push_to_talk');
    } catch {
      /* surface via apiError already */
    }
  };

  const successCount = history.filter(r => r.success).length;

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="header">
        <div>
          <div className="header-brand">TARS</div>
          <div className="header-sub">Voice-Controlled PC Assistant · v2</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          {apiError && <span className="error-badge">⚠ Backend offline</span>}
          <button
            className="btn btn-ghost"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            title="Toggle theme"
          >
            {theme === 'dark' ? '☾' : '☀'}
          </button>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      </header>

      {/* Grid */}
      <main style={{ padding: 0 }}>
        <div className="main-grid">
          <div className="card">
            <div className="card-title">Engine Control</div>
            <StatusOrb
              online={status?.engine_running ?? false}
              loading={toggling}
              onToggle={toggleEngine}
            />
          </div>

          <PushToTalk onTranscript={handlePushToTalk} />

          <SettingsPanel
            status={status}
            onPatch={async (d) => { await api.patchSettings(d); refresh(); }}
          />

          <div className="card">
            <div className="card-title">Statistics</div>
            <Stats total={history.length} success={successCount} />
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Wake word:  <code style={{ color: 'var(--accent)' }}>{status?.wake_word ?? '…'}</code>
              {' · '}Brain: <code style={{ color: 'var(--accent)' }}>{status?.brain_provider ?? '…'}</code>
              {' · '}STT:   <code style={{ color: 'var(--accent)' }}>{status?.stt_provider ?? '…'}</code>
            </p>
          </div>

          <SkillsBrowser skills={skills} />
          <CustomCommands
            commands={commands}
            onCreate={async (d) => { await api.createCommand(d); refresh(); }}
            onDelete={async (id) => { await api.deleteCommand(id); refresh(); }}
          />

          <CommandLog
            records={history}
            live={wsLive}
            onClear={async () => { await api.clearHistory(); setHistory([]); }}
          />
        </div>
      </main>
    </div>
  );
}
