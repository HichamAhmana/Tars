/**
 * TARS REST client.
 *
 * Every call routes through a single `request<T>()` helper that handles:
 *   - base URL (configurable via NEXT_PUBLIC_TARS_API_BASE)
 *   - optional bearer-style token (set TARS_API_TOKEN in localStorage
 *     or NEXT_PUBLIC_TARS_API_TOKEN at build time)
 *   - JSON encoding + friendly error messages
 */

// -- Types --------------------------------------------------------------------
export interface EngineStatus {
  engine_running: boolean;
  wake_word: string;
  tts_rate: number;
  tts_volume: number;
  brain_provider: string;
  stt_provider: string;
  tts_provider: string;
}

export interface CommandRecord {
  id: number;
  command: string;
  success: boolean;
  skill: string;
  timestamp: string;
}

export interface CustomCommand {
  id: number;
  trigger: string;
  action: string;
  description: string;
  created_at: string;
}

export interface Skill {
  name: string;
  description: string;
  triggers: string[];
  priority: number;
}

// -- Config -------------------------------------------------------------------
const API_BASE =
  (typeof window !== 'undefined' && (window as unknown as { __TARS_API_BASE__?: string }).__TARS_API_BASE__) ||
  process.env.NEXT_PUBLIC_TARS_API_BASE ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8000/api';

const API_TOKEN =
  (typeof window !== 'undefined' && window.localStorage?.getItem('TARS_API_TOKEN')) ||
  process.env.NEXT_PUBLIC_TARS_API_TOKEN ||
  '';

// -- Core request -------------------------------------------------------------
async function request<T>(
  path: string,
  init: RequestInit & { parse?: 'json' | 'none' } = {},
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(init.headers as Record<string, string> | undefined),
  };
  if (API_TOKEN) headers.Authorization = `Token ${API_TOKEN}`;

  const res = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (!res.ok) {
    let detail: string | undefined;
    try {
      const payload = await res.json();
      if (payload?.detail) {
        detail = payload.detail;
      } else if (typeof payload === 'string') {
        detail = payload;
      } else if (payload && typeof payload === 'object') {
        detail = Object.values(payload)
          .flatMap(value => Array.isArray(value) ? value : [value])
          .filter(Boolean)
          .join(' | ');
      }
    } catch {
      detail = await res.text();
    }
    throw new Error(detail || `Request failed (${res.status})`);
  }
  if (init.parse === 'none' || res.status === 204) return undefined as unknown as T;
  return res.json() as Promise<T>;
}

// -- Public API ---------------------------------------------------------------
export const api = {
  // Engine
  getStatus:   ()                      => request<EngineStatus>('/engine/status/'),
  startEngine: ()                      => request<{ message: string }>('/engine/status/', {
                                            method: 'POST',
                                            body: JSON.stringify({ action: 'start' }),
                                          }),
  stopEngine:  ()                      => request<{ message: string }>('/engine/status/', {
                                            method: 'POST',
                                            body: JSON.stringify({ action: 'stop' }),
                                          }),
  speak:       (text: string)          => request<{ ok: boolean }>('/engine/speak/', {
                                            method: 'POST',
                                            body: JSON.stringify({ text }),
                                          }),
  executeCommand: (text: string)       => request<{ ok: boolean; success: boolean; skill: string | null }>('/engine/command/', {
                                            method: 'POST',
                                            body: JSON.stringify({ text }),
                                          }),
  // History
  getHistory:  (limit = 100)           => request<CommandRecord[]>(`/history/?limit=${limit}`),
  clearHistory:()                      => request<void>('/history/', { method: 'DELETE', parse: 'none' }),
  logCommand:  (command: string, success: boolean, skill = '') =>
                                          request<CommandRecord>('/history/', {
                                            method: 'POST',
                                            body: JSON.stringify({ command, success, skill }),
                                          }),

  // Custom commands
  getCommands: ()                      => request<CustomCommand[]>('/commands/'),
  createCommand: (data: { trigger: string; action: string; description: string }) =>
                                          request<CustomCommand>('/commands/', {
                                            method: 'POST', body: JSON.stringify(data),
                                          }),
  deleteCommand: (id: number)          => request<void>(`/commands/${id}/`, { method: 'DELETE', parse: 'none' }),

  // Settings
  patchSettings: (data: Partial<EngineStatus>) =>
                                          request<EngineStatus>('/settings/', {
                                            method: 'PATCH', body: JSON.stringify(data),
                                          }),

  // Skills
  getSkills:   ()                      => request<Skill[]>('/skills/'),
};

export function wsUrl(): string {
  const base = API_BASE.replace(/^http/, 'ws').replace(/\/api$/, '');
  const tok = API_TOKEN ? `?token=${encodeURIComponent(API_TOKEN)}` : '';
  return `${base}/ws/events/${tok}`;
}
