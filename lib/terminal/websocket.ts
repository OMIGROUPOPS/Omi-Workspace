// OMNI Terminal — WebSocket connection manager
// Placeholder for relay server connection. The terminal will connect to a
// lightweight WS relay that bridges the Python scanner's internal state
// to the browser. For now, stubs that return mock/empty data.

import type { ConnectionStatus, ScannerStats } from "./types";

export const WS_RELAY_URL =
  process.env.NEXT_PUBLIC_TERMINAL_WS_URL || "ws://localhost:8765";

export type MessageHandler = (data: Record<string, unknown>) => void;

export class TerminalSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectDelay = 1000;
  private maxReconnectDelay = 30000;
  private handlers: Map<string, MessageHandler[]> = new Map();
  private _status: ConnectionStatus = "disconnected";
  private onStatusChange?: (status: ConnectionStatus) => void;

  constructor(url: string = WS_RELAY_URL) {
    this.url = url;
  }

  get status(): ConnectionStatus {
    return this._status;
  }

  setStatusCallback(cb: (status: ConnectionStatus) => void) {
    this.onStatusChange = cb;
  }

  private setStatus(s: ConnectionStatus) {
    this._status = s;
    this.onStatusChange?.(s);
  }

  connect() {
    if (this.ws) return;
    this.setStatus("connecting");

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.setStatus("connected");
        this.reconnectDelay = 1000;
        console.log("[TerminalSocket] Connected");
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const type = data.type as string;
          const handlers = this.handlers.get(type) || [];
          for (const h of handlers) h(data);
          // Also fire wildcard
          const wildcardHandlers = this.handlers.get("*") || [];
          for (const h of wildcardHandlers) h(data);
        } catch {
          // ignore parse errors
        }
      };

      this.ws.onclose = () => {
        this.ws = null;
        this.setStatus("disconnected");
        // Auto-reconnect
        setTimeout(() => {
          this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
          this.connect();
        }, this.reconnectDelay);
      };

      this.ws.onerror = () => {
        this.setStatus("error");
      };
    } catch {
      this.setStatus("error");
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.setStatus("disconnected");
  }

  on(type: string, handler: MessageHandler) {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, []);
    }
    this.handlers.get(type)!.push(handler);
  }

  off(type: string, handler: MessageHandler) {
    const list = this.handlers.get(type);
    if (list) {
      const idx = list.indexOf(handler);
      if (idx >= 0) list.splice(idx, 1);
    }
  }

  send(data: Record<string, unknown>) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}

// Singleton instance
let _instance: TerminalSocket | null = null;

export function getTerminalSocket(): TerminalSocket {
  if (!_instance) {
    _instance = new TerminalSocket();
  }
  return _instance;
}

// Empty stats for initial render
export const EMPTY_STATS: ScannerStats = {
  uptime: 0,
  ws_connected: false,
  ws_messages: 0,
  bbo_updates: 0,
  scan_signals: 0,
  paper_trades_opened: 0,
  paper_trades_closed: 0,
  open_trades: 0,
  total_pnl: 0,
  winners: 0,
  losers: 0,
  whale_fills_interval: 0,
  whale_fills_total: 0,
  lambda_median: 0,
  tickers_subscribed: 0,
  active_books: 0,
};
