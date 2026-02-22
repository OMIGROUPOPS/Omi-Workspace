import { useMemo } from "react";
import type { ArbState, AlertInfo } from "../types";

export function useAlerts(state: ArbState | null): AlertInfo[] {
  return useMemo(() => {
    if (!state) return [];
    const alerts: AlertInfo[] = [];

    // Check for high spreads
    const highSpread = state.spreads?.find(
      (s) => Math.max(s.spread_buy_pm, s.spread_buy_k) >= 7
    );
    if (highSpread) {
      alerts.push({
        type: "info",
        message: `Spread >7c detected: ${highSpread.team} (${Math.max(highSpread.spread_buy_pm, highSpread.spread_buy_k).toFixed(1)}c)`,
      });
    }

    // Check WS connectivity
    if (state.system && !state.system.ws_connected) {
      const specs = state.specs;
      if (specs?.connection) {
        if (!specs.connection.kalshi_ws) {
          alerts.push({ type: "error", message: "Kalshi WS disconnected" });
        }
        if (!specs.connection.pm_ws) {
          alerts.push({ type: "error", message: "PM WS disconnected" });
        }
      } else {
        alerts.push({ type: "error", message: "WebSocket disconnected" });
      }
    }

    // Check for recent errors
    if (state.system?.error_count > 0 && state.system?.last_error) {
      alerts.push({
        type: "warning",
        message: `Error: ${state.system.last_error}`,
      });
    }

    // Stale data
    if (state.updated_at) {
      const age = Date.now() - new Date(state.updated_at).getTime();
      if (age > 60_000) {
        alerts.push({
          type: "warning",
          message: `Data stale (${Math.floor(age / 1000)}s old)`,
        });
      }
    }

    return alerts;
  }, [state]);
}
