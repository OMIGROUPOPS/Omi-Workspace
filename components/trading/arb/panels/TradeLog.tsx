"use client";

import React from "react";
import type { TradeEntry } from "../types";
import { tradePnl, sportBadge, statusBadge, formatDateTime, netColor, getL1Depth, depthColor, fmtNum } from "../helpers";

interface Props {
  trades: TradeEntry[];
  expandedTrade: number | null;
  setExpandedTrade: (idx: number | null) => void;
}

function normPmNum(pm: number | undefined): number {
  if (typeof pm !== "number") return 0;
  return pm < 1 && pm > 0 ? pm * 100 : pm;
}

function normPm(pm: number | undefined): string {
  if (typeof pm !== "number") return "-";
  return pm < 1 ? (pm * 100).toFixed(1) : pm.toFixed(1);
}

function legsLabel(t: TradeEntry) {
  const pmVal = normPmNum(t.pm_price);
  const kVal = typeof t.k_price === "number" ? t.k_price : 0;
  const team = t.team || "?";
  const opp = t.opponent || "?";

  if (t.direction === "BUY_PM_SELL_K") {
    // PM: buy team YES @pm, K: sell team YES = buy opponent YES @(100-k)
    const kOppCost = kVal > 0 ? 100 - kVal : 0;
    const totalCost = pmVal + kOppCost;
    const spread = 100 - totalCost;
    return (
      <>
        <span className="text-emerald-400">PM: {team} @{pmVal.toFixed(0)}c</span>
        <span className="text-gray-700 mx-1">|</span>
        <span className="text-blue-400">K: {opp} @{kOppCost.toFixed(0)}c</span>
        <span className="text-gray-600 ml-1.5 text-[9px]">[{totalCost.toFixed(0)}c&rarr;{spread.toFixed(0)}c]</span>
      </>
    );
  }
  // BUY_K_SELL_PM: K: buy team YES @k, PM: buy opponent YES @pm
  const totalCost = kVal + pmVal;
  const spread = 100 - totalCost;
  return (
    <>
      <span className="text-emerald-400">K: {team} @{kVal}c</span>
      <span className="text-gray-700 mx-1">|</span>
      <span className="text-blue-400">PM: {opp} @{pmVal.toFixed(0)}c</span>
      <span className="text-gray-600 ml-1.5 text-[9px]">[{totalCost.toFixed(0)}c&rarr;{spread.toFixed(0)}c]</span>
    </>
  );
}

export function TradeLog({ trades, expandedTrade, setExpandedTrade }: Props) {
  if (trades.length === 0) {
    return (
      <div className="rounded-lg border border-gray-800 bg-[#111] p-4 text-center text-sm text-gray-500">
        No trades in current view
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] overflow-hidden">
      <div className="px-3 py-2 border-b border-gray-800">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
          Recent Trades ({trades.length})
        </h3>
      </div>
      <div className="overflow-x-auto" style={{ maxHeight: "400px" }}>
        <table className="w-full text-xs">
          <thead className="sticky top-0 bg-[#111] z-10">
            <tr className="border-b border-gray-800 text-gray-500">
              <th className="px-2 py-1.5 text-left font-medium">TIME</th>
              <th className="px-2 py-1.5 text-left font-medium">MATCHUP</th>
              <th className="px-2 py-1.5 text-left font-medium">LEGS</th>
              <th className="px-2 py-1.5 text-left font-medium">STATUS</th>
              <th className="px-2 py-1.5 text-right font-medium">QTY</th>
              <th className="px-2 py-1.5 text-right font-medium">SPREAD</th>
              <th className="px-2 py-1.5 text-right font-medium">DEPTH</th>
              <th className="px-2 py-1.5 text-right font-medium">NET P&L</th>
              <th className="px-2 py-1.5 text-right font-medium">MS</th>
            </tr>
          </thead>
          <tbody>
            {trades.slice(0, 50).map((t, i) => {
              const pnl = tradePnl(t);
              const badge = statusBadge(t.status);
              const depth = getL1Depth(t);
              const isExpanded = expandedTrade === i;

              return (
                <React.Fragment key={`${t.timestamp}-${t.team}-${i}`}>
                  <tr
                    className="border-b border-gray-800/50 hover:bg-gray-800/30 cursor-pointer"
                    onClick={() => setExpandedTrade(isExpanded ? null : i)}
                  >
                    <td className="px-2 py-1.5 text-gray-500 whitespace-nowrap font-mono text-[10px]">
                      {formatDateTime(t.timestamp)}
                    </td>
                    <td className="px-2 py-1.5 whitespace-nowrap">
                      <span className={`inline-block rounded px-1 py-0.5 text-[9px] mr-1 ${sportBadge(t.sport)}`}>
                        {t.sport}
                      </span>
                      <span className="font-bold text-white">{t.team_full_name || t.team}</span>
                      {(t.opponent_full_name || t.opponent) ? (
                        <span className="text-gray-500 text-[10px] ml-1">vs {t.opponent_full_name || t.opponent}</span>
                      ) : null}
                    </td>
                    <td className="px-2 py-1.5 whitespace-nowrap text-[10px] font-mono">
                      {legsLabel(t)}
                    </td>
                    <td className="px-2 py-1.5">
                      <span className={`rounded px-1 py-0.5 text-[9px] font-medium ${badge.bg} ${badge.text}`}>
                        {t.tier || t.status}
                      </span>
                    </td>
                    <td className="px-2 py-1.5 text-right font-mono text-gray-300">
                      {t.contracts_filled || 0}
                    </td>
                    <td className="px-2 py-1.5 text-right font-mono text-gray-400">
                      {t.spread_cents?.toFixed(1) ?? "-"}c
                    </td>
                    <td className="px-2 py-1.5 text-right font-mono whitespace-nowrap text-[10px]">
                      {depth.k !== null || depth.pm !== null ? (
                        <>
                          <span className={depthColor(depth.k)}>K:{fmtNum(depth.k!)}</span>
                          <span className="text-gray-700 mx-0.5">|</span>
                          <span className={depthColor(depth.pm)}>PM:{fmtNum(depth.pm!)}</span>
                        </>
                      ) : "\u2014"}
                    </td>
                    <td className={`px-2 py-1.5 text-right font-mono ${
                      pnl.totalDollars === null ? "text-gray-500" :
                      Math.abs(pnl.totalDollars) >= 1 ? `font-bold ${netColor(pnl.totalDollars)}` :
                      netColor(pnl.totalDollars)
                    }`}>
                      {pnl.totalDollars !== null
                        ? `$${pnl.totalDollars.toFixed(4)}`
                        : pnl.isOpen ? "OPEN" : "-"}
                    </td>
                    <td className="px-2 py-1.5 text-right text-gray-600 font-mono text-[10px]">
                      {t.execution_time_ms || "-"}
                    </td>
                  </tr>
                  {isExpanded && (
                    <tr className="bg-gray-900/50">
                      <td colSpan={9} className="px-4 py-3">
                        <div className="grid grid-cols-3 gap-x-6 gap-y-2 text-[10px]">
                          <div>
                            <span className="text-gray-500 block">Game ID</span>
                            <span className="text-gray-300 font-mono">{t.game_id}</span>
                          </div>
                          <div>
                            <span className="text-gray-500 block">Direction</span>
                            <span className="text-gray-300">{t.direction}</span>
                          </div>
                          <div>
                            <span className="text-gray-500 block">Phase</span>
                            <span className="text-gray-300">{t.execution_phase || "ioc"}{t.is_maker ? " (maker)" : ""}</span>
                          </div>
                          <div>
                            <span className="text-gray-500 block">K Price / Order</span>
                            <span className="text-gray-300 font-mono">{t.k_price}c ({t.k_order_ms || "-"}ms)</span>
                          </div>
                          <div>
                            <span className="text-gray-500 block">PM Price / Order</span>
                            <span className="text-gray-300 font-mono">
                              {normPm(t.pm_price)}c ({t.pm_order_ms || "-"}ms)
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-500 block">Total Execution</span>
                            <span className="text-gray-300 font-mono">{t.execution_time_ms || "-"}ms</span>
                          </div>
                          <div>
                            <span className="text-gray-500 block">Fees (PM / K)</span>
                            <span className="text-yellow-400 font-mono">
                              ${(t.pm_fee || 0).toFixed(3)} / ${(t.k_fee || 0).toFixed(3)}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-500 block">Hedged</span>
                            <span className={t.hedged ? "text-emerald-400" : "text-red-400"}>
                              {t.hedged ? "Yes" : "No"}
                            </span>
                          </div>
                          {t.sizing_details && (
                            <>
                              {depth.k !== null && (
                                <div>
                                  <span className="text-gray-500 block">L1 at Arb Price</span>
                                  <span className="font-mono">
                                    <span className={depthColor(depth.k)}>K: {fmtNum(depth.k)}</span>
                                    {" @ "}{t.sizing_details.depth_walk_log?.[0]?.k_price ?? "-"}c
                                    <span className="text-gray-700 mx-1">|</span>
                                    <span className={depthColor(depth.pm)}>PM: {fmtNum(depth.pm!)}</span>
                                    {" @ "}{t.sizing_details.depth_walk_log?.[0]?.pm_cost ?? "-"}c
                                  </span>
                                </div>
                              )}
                              <div>
                                <span className="text-gray-500 block">Total Book Depth</span>
                                <span className="text-gray-300 font-mono">
                                  K: {fmtNum(t.sizing_details.k_depth)} | PM: {fmtNum(t.sizing_details.pm_depth)} ({t.sizing_details.limit_reason})
                                </span>
                              </div>
                            </>
                          )}
                          {t.pm_slug && (
                            <div>
                              <span className="text-gray-500 block">PM Slug</span>
                              <span className="text-gray-300 font-mono text-[9px]">{t.pm_slug}</span>
                            </div>
                          )}
                          {t.kalshi_ticker && (
                            <div>
                              <span className="text-gray-500 block">Kalshi Ticker</span>
                              <span className="text-gray-300 font-mono text-[9px]">{t.kalshi_ticker}</span>
                            </div>
                          )}
                          {t.sizing_details?.depth_walk_log && t.sizing_details.depth_walk_log.length > 0 && (
                            <div className="col-span-3 mt-1">
                              <span className="text-gray-500 block mb-1">Depth Walk</span>
                              <table className="w-full text-[10px] font-mono">
                                <thead>
                                  <tr className="text-gray-600">
                                    <th className="text-left pr-2">LVL</th>
                                    <th className="text-right pr-2">K</th>
                                    <th className="text-right pr-2">PM</th>
                                    <th className="text-right pr-2">SPREAD</th>
                                    <th className="text-right pr-2">FEES</th>
                                    <th className="text-right pr-2">NET</th>
                                    <th className="text-right pr-2">QTY</th>
                                    <th className="text-right">CUM</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {t.sizing_details.depth_walk_log.map((l) => (
                                    <tr key={l.level} className={l.stopped ? "text-red-400/80" : "text-emerald-400/80"}>
                                      <td className="text-left pr-2">{l.stopped ? "\u2717" : "\u2713"} L{l.level}</td>
                                      <td className="text-right pr-2">{l.k_price}c</td>
                                      <td className="text-right pr-2">{l.pm_cost}c</td>
                                      <td className="text-right pr-2">{l.spread}c</td>
                                      <td className="text-right pr-2">{l.fees}c</td>
                                      <td className={`text-right pr-2 font-bold ${l.marginal_profit >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                                        {l.marginal_profit}c
                                      </td>
                                      <td className="text-right pr-2">{l.contracts_at_level ?? "-"}</td>
                                      <td className="text-right">{l.cumulative_contracts}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          )}
                          {t.settlement_pnl != null && (
                            <div>
                              <span className="text-gray-500 block">Settlement P&L</span>
                              <span className={t.settlement_pnl >= 0 ? "text-emerald-400 font-bold" : "text-red-400 font-bold"}>
                                ${t.settlement_pnl.toFixed(4)}
                              </span>
                            </div>
                          )}
                          {t.gtc_cancel_reason && (
                            <div>
                              <span className="text-gray-500 block">GTC Cancel</span>
                              <span className="text-gray-300">{t.gtc_cancel_reason}</span>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
