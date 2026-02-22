"use client";

import React from "react";
import { Pulse } from "../shared/Pulse";
import { formatUptime, timeAgo } from "../helpers";

interface Props {
  specs: any;
  system: { ws_connected: boolean; ws_messages_processed: number; uptime_seconds: number; last_scan_at: string } | undefined;
}

export function WsHealthPanel({ specs, system }: Props) {
  const conn = specs?.connection || {};
  const kConnected = conn.kalshi_ws ?? false;
  const pmConnected = conn.pm_ws ?? false;
  const kMsgs = conn.k_messages ?? 0;
  const pmMsgs = conn.pm_messages ?? 0;
  const uptime = system?.uptime_seconds ?? 0;
  const kRate = uptime > 0 ? (kMsgs / uptime).toFixed(1) : "0";
  const pmRate = uptime > 0 ? (pmMsgs / uptime).toFixed(1) : "0";

  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] p-3">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
        WebSocket Health
      </h3>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Pulse active={kConnected} />
            <span className="text-sm text-white font-medium">Kalshi WS</span>
          </div>
          <div className="text-xs text-gray-400 pl-4 space-y-1">
            <div>{kMsgs.toLocaleString()} messages ({kRate}/s)</div>
          </div>
        </div>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Pulse active={pmConnected} />
            <span className="text-sm text-white font-medium">PM WS</span>
          </div>
          <div className="text-xs text-gray-400 pl-4 space-y-1">
            <div>{pmMsgs.toLocaleString()} messages ({pmRate}/s)</div>
          </div>
        </div>
        <div>
          <span className="text-[10px] text-gray-500 uppercase">Uptime</span>
          <p className="text-sm text-white font-mono">{formatUptime(uptime)}</p>
        </div>
        <div>
          <span className="text-[10px] text-gray-500 uppercase">Last Scan</span>
          <p className="text-sm text-white font-mono">{system?.last_scan_at ? timeAgo(system.last_scan_at) : "-"}</p>
        </div>
        {/* OMI Cache */}
        {conn.omi_signals_cached > 0 && (
          <>
            <div>
              <span className="text-[10px] text-gray-500 uppercase">OMI Signals</span>
              <p className="text-sm text-white font-mono">{conn.omi_signals_cached} ({conn.omi_live_count} live)</p>
            </div>
            <div>
              <span className="text-[10px] text-gray-500 uppercase">OMI Refresh</span>
              <p className={`text-sm font-mono ${conn.omi_is_stale ? "text-red-400" : "text-emerald-400"}`}>
                {conn.omi_last_refresh_ago_s != null ? `${conn.omi_last_refresh_ago_s}s ago` : "-"}
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
