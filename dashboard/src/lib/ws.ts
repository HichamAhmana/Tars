/**
 * Tiny typed wrapper around the TARS event WebSocket.
 *
 * Automatically reconnects with exponential backoff (capped at 15s) and
 * exposes a subscribe/unsubscribe API that works nicely inside React
 * effects.
 */
import { wsUrl } from './api';

export type TarsEvent = {
  type:
    | 'hello'
    | 'command.new'
    | 'engine.state'
    | 'engine.speak'
    | 'settings.updated'
    | 'command.custom.new'
    | 'command.custom.updated'
    | 'command.custom.deleted'
    | 'history.cleared'
    | string;
  data: Record<string, unknown>;
};

export type Listener = (event: TarsEvent) => void;

export class EventStream {
  private socket: WebSocket | null = null;
  private listeners = new Set<Listener>();
  private retries = 0;
  private closed = false;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(private readonly url: string = wsUrl()) {}

  connect() {
    if (typeof window === 'undefined' || this.socket) return;
    try {
      this.socket = new WebSocket(this.url);
    } catch {
      this.scheduleReconnect();
      return;
    }
    this.socket.onopen = () => { this.retries = 0; };
    this.socket.onmessage = (msg) => {
      try {
        const evt = JSON.parse(msg.data) as TarsEvent;
        this.listeners.forEach(l => l(evt));
      } catch { /* ignore malformed frames */ }
    };
    this.socket.onclose = () => {
      this.socket = null;
      if (!this.closed) this.scheduleReconnect();
    };
    this.socket.onerror = () => { this.socket?.close(); };
  }

  private scheduleReconnect() {
    if (this.closed) return;
    const delay = Math.min(1000 * 2 ** this.retries, 15000);
    this.retries += 1;
    this.reconnectTimer = setTimeout(() => this.connect(), delay);
  }

  subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => { this.listeners.delete(listener); };
  }

  close() {
    this.closed = true;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.socket?.close();
    this.socket = null;
    this.listeners.clear();
  }
}
