import { BOT_SERVER_URL } from "./config";
import type { BotStatus, Trade, MarketData, GamePriceHistory, MatchupInfo } from "./types";

export async function fetchStatus(): Promise<BotStatus | null> {
  try {
    const res = await fetch(`${BOT_SERVER_URL}/status`);
    if (res.ok) return res.json();
    return null;
  } catch {
    return null;
  }
}

export async function fetchTrades(): Promise<Trade[]> {
  try {
    const res = await fetch(`${BOT_SERVER_URL}/trades`);
    if (res.ok) {
      const data = await res.json();
      return data.trades || [];
    }
    return [];
  } catch {
    return [];
  }
}

export async function startBot(): Promise<{ ok: boolean; error?: string }> {
  try {
    const res = await fetch(`${BOT_SERVER_URL}/start`, { method: "POST" });
    if (!res.ok) {
      const d = await res.json();
      return { ok: false, error: d.detail || "Failed to start bot" };
    }
    return { ok: true };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : "Failed to start bot" };
  }
}

export async function stopBot(): Promise<{ ok: boolean; error?: string }> {
  try {
    const res = await fetch(`${BOT_SERVER_URL}/stop`, { method: "POST" });
    if (!res.ok) {
      const d = await res.json();
      return { ok: false, error: d.detail || "Failed to stop bot" };
    }
    return { ok: true };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : "Failed to stop bot" };
  }
}

export async function setMode(
  newMode: "paper" | "live"
): Promise<{ ok: boolean; error?: string }> {
  try {
    const res = await fetch(`${BOT_SERVER_URL}/mode`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: newMode }),
    });
    if (!res.ok) {
      const d = await res.json();
      return { ok: false, error: d.detail || "Failed to change mode" };
    }
    return { ok: true };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : "Failed to change mode" };
  }
}

export async function clearData(): Promise<boolean> {
  try {
    const res = await fetch(`${BOT_SERVER_URL}/clear`, { method: "POST" });
    return res.ok;
  } catch {
    return false;
  }
}

export async function measureLatency(): Promise<number | null> {
  try {
    const start = performance.now();
    const res = await fetch(`${BOT_SERVER_URL}/status`, { method: "GET" });
    if (res.ok) return Math.round(performance.now() - start);
    return null;
  } catch {
    return null;
  }
}

export async function fetchMarkets(): Promise<MarketData | null> {
  try {
    const res = await fetch(`${BOT_SERVER_URL}/markets`);
    return res.ok ? res.json() : null;
  } catch {
    return null;
  }
}

export async function fetchMatchups(sport: string): Promise<MatchupInfo[]> {
  try {
    const res = await fetch(`${BOT_SERVER_URL}/matchups/${sport}`);
    if (res.ok) {
      const data = await res.json();
      return data.matchups || [];
    }
    return [];
  } catch {
    return [];
  }
}

export async function fetchGamePrices(
  gameId: string,
  hours: number = 0,
  maxPoints: number = 500
): Promise<GamePriceHistory | null> {
  try {
    const params = new URLSearchParams();
    if (hours > 0) params.set("hours", hours.toString());
    if (maxPoints !== 500) params.set("max_points", maxPoints.toString());

    const url = `${BOT_SERVER_URL}/game/${encodeURIComponent(gameId)}/prices${params.toString() ? "?" + params : ""}`;
    const res = await fetch(url);
    return res.ok ? res.json() : null;
  } catch {
    return null;
  }
}
