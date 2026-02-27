"use client";

import React from "react";
import type { TradeEntry, TradeSortKey } from "../types";
import { tradePnl, sportBadge, statusBadge, formatDateTime, toDateStr, todayET, getL1Depth, depthColor, fmtNum } from "../helpers";

interface Props {
  trades: TradeEntry[];
  tradeSortKey: TradeSortKey;
  tradeSortAsc: boolean;
  handleSort: (key: TradeSortKey) => void;
  sortArrow: (key: TradeSortKey) => string;
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

export function PnlTradeTable({
  trades,
  tradeSortKey,
  tradeSortAsc,
  handleSort,
  sortArrow,
  expandedTrade,
  setExpandedTrade,
}: Props) {
  // Today summary
  const today = todayET();
  const todayTrades = trades.filter((t) => toDateStr(t.timestamp) === today);
  const todayStats = {
    count: todayTrades.length,
    wins: todayTrades.filter((t) => { const p = tradePnl(t); return p.totalDollars !== null && p.totalDollars > 0; }).length,
    losses: todayTrades.filter((t) => { const p = tradePnl(t); return p.totalDollars !== null && p.totalDollars < 0; }).length,
    gross: todayTrades.reduce((s, t) => s + (tradePnl(t).totalDollars || 0), 0),
    fees: todayTrades.reduce((s, t) => s + (t.pm_fee || 0) + (t.k_fee || 0), 0),
  };

  return (
    <div className="rounded-lg border border-gray-800 bg-[#111] overflow-hidden">
      {/* Today summary row */}
      {todayTrades.length > 0 && (
        <div className="px-3 py-2 border-b border-gray-800 bg-gray-800/30 flex items-center gap-4 text-xs">
          <span className="text-gray-400">Today:</span>
          <span className="text-white font-bold">{todayStats.count} trades</span>
          <span className="text-emerald-400">{todayStats.wins}W</span>
          <span className="text-red-400">{todayStats.losses}L</span>
          <span className={todayStats.gross >= 0 ? "text-emerald-400" : "text-red-400"}>
            ${todayStats.gross.toFixed(2)}
          </span>
          <span className="text-yellow-400">-${todayStats.fees.toFixed(2)} fees</span>
          <span className={todayStats.gross - todayStats.fees >= 0 ? "text-emerald-400 font-bold" : "text-red-400 font-bold"}>
            Net: ${(todayStats.gross - todayStats.fees).toFixed(2)}
          </span>
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-gray-800 text-gray-500">
              <th className="px-2 py-1.5 text-left font-medium cursor-pointer hover:text-gray-300" onClick={() => handleSort("time")}>
                TIME{sortArrow("time")}
              </th>
              <th className="px-2 py-1.5 text-left font-medium">MATCHUP</th>
              <th className="px-2 py-1.5 text-left font-medium">LEGS</th>
              <th className="px-2 py-1.5 text-left font-medium">STATUS</th>
              <th className="px-2 py-1.5 text-right font-medium cursor-pointer hover:text-gray-300" onClick={() => handleSort("qty")}>
                K QTY{sortArrow("qty")}
              </th>
              <th className="px-2 py-1.5 text-right font-medium">
                PM QTY
              </th>
              <th className="px-2 py-1.5 text-right font-medium cursor-pointer hover:text-gray-300" onClick={() => handleSort("spread")}>
                SPREAD{sortArrow("spread")}
              </th>
              <th className="px-2 py-1.5 text-right font-medium">DEPTH</th>
              <th className="px-2 py-1.5 text-right font-medium">FEES</th>
              <th className="px-2 py-1.5 text-right font-medium cursor-pointer hover:text-gray-300" onClick={() => handleSort("net")}>
                NET P&L{sortArrow("net")}
              </th>
              <th className="px-2 py-1.5 text-right font-medium cursor-pointer hover:text-gray-300" onClick={() => handleSort("phase")}>
                PHASE{sortArrow("phase")}
              </th>
            </tr>
          </thead>
          <tbody>
            {trades.slice(0, 100).map((t, i) => {
              const pnl = tradePnl(t);
              const badge = statusBadge(t.status, t.tier);
              const fees = (t.pm_fee || 0) + (t.k_fee || 0);
              const depth = getL1Depth(t);
              const isExpanded = expandedTrade === i;

              return (
                <React.Fragment key={`${t.timestamp}-${t.team}-${i}`}>
                  <tr
                    className="border-b border-gray-800/50 hover:bg-gray-800/30 cursor-pointer"
                    onClick={() => setExpandedTrade(isExpanded ? null : i)}
                  >
                    <td className="px-2 py-1.5 text-gray-400 whitespace-nowrap font-mono">
                      {formatDateTime(t.timestamp)}
                    </td>
                    <td className="px-2 py-1.5 whitespace-nowrap">
                      <span className={`inline-block rounded px-1 py-0.5 text-[10px] mr-1 ${sportBadge(t.sport)}`}>
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
                      <span className={`rounded px-1 py-0.5 text-[10px] font-medium ${badge.bg} ${badge.text}`} title={badge.tooltip}>
                        {badge.label}
                      </span>
                    </td>
                    <td className="px-2 py-1.5 text-right font-mono whitespace-nowrap">
                      <span className="text-blue-400">{t.kalshi_fill ?? t.contracts_filled ?? 0}x</span>
                      <div className="text-[9px] text-gray-600">@{typeof t.k_price === 'number' ? t.k_price : '-'}c</div>
                    </td>
                    <td className="px-2 py-1.5 text-right font-mono whitespace-nowrap">
                      <span className="text-emerald-400">{t.pm_fill ?? t.contracts_filled ?? 0}x</span>
                      <div className="text-[9px] text-gray-600">@{normPmNum(t.pm_price).toFixed(0)}c</div>
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
                    <td className="px-2 py-1.5 text-right font-mono text-yellow-400">
                      {fees > 0 ? `$${fees.toFixed(2)}` : "-"}
                    </td>
                    <td className={`px-2 py-1.5 text-right font-mono font-bold ${
                      pnl.totalDollars === null ? "text-gray-500" :
                      pnl.totalDollars > 0 ? "text-emerald-400" :
                      pnl.totalDollars < 0 ? "text-red-400" : "text-gray-400"
                    }`}>
                      {pnl.totalDollars !== null ? `$${pnl.totalDollars.toFixed(4)}` : pnl.isOpen ? "OPEN" : "-"}
                    </td>
                    <td className="px-2 py-1.5 text-right text-gray-500 text-[10px]">
                      {t.execution_phase || "ioc"}
                      {t.is_maker && <span className="ml-0.5 text-purple-400">M</span>}
                    </td>
                  </tr>
                  {isExpanded && (
                    <tr className="bg-gray-900/50">
                      <td colSpan={11} className="px-4 py-2">
                        <div className="grid grid-cols-4 gap-3 text-[10px]">
                          <div>
                            <span className="text-gray-500">Execution:</span>{" "}
                            <span className="text-gray-300">{t.execution_time_ms}ms total</span>
                          </div>
                          <div>
                            <span className="text-gray-500">K order:</span>{" "}
                            <span className="text-gray-300">{t.k_order_ms || "-"}ms</span>
                          </div>
                          <div>
                            <span className="text-gray-500">PM order:</span>{" "}
                            <span className="text-gray-300">{t.pm_order_ms || "-"}ms</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Game:</span>{" "}
                            <span className="text-gray-300">{t.game_id}</span>
                          </div>
                          {t.pm_slug && (
                            <div>
                              <span className="text-gray-500">PM Slug:</span>{" "}
                              <span className="text-gray-300 font-mono text-[9px]">{t.pm_slug}</span>
                            </div>
                          )}
                          {t.kalshi_ticker && (
                            <div>
                              <span className="text-gray-500">K Ticker:</span>{" "}
                              <span className="text-gray-300 font-mono text-[9px]">{t.kalshi_ticker}</span>
                            </div>
                          )}
                          {t.sizing_details && (
                            <>
                              {depth.k !== null && (
                                <div className="col-span-2">
                                  <span className="text-gray-500">L1 at arb price:</span>{" "}
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
                                <span className="text-gray-500">Total depth:</span>{" "}
                                <span className="text-gray-300 font-mono">K: {fmtNum(t.sizing_details.k_depth)} | PM: {fmtNum(t.sizing_details.pm_depth)}</span>
                              </div>
                              <div>
                                <span className="text-gray-500">Limit:</span>{" "}
                                <span className="text-gray-300">{t.sizing_details.limit_reason}</span>
                              </div>
                            </>
                          )}
                          {t.actual_pnl && (
                            <>
                              <div>
                                <span className="text-gray-500">Gross:</span>{" "}
                                <span className="text-gray-300">${t.actual_pnl.gross_profit_dollars.toFixed(4)}</span>
                              </div>
                              <div>
                                <span className="text-gray-500">Fees:</span>{" "}
                                <span className="text-yellow-400">${t.actual_pnl.fees_dollars.toFixed(4)}</span>
                              </div>
                              <div>
                                <span className="text-gray-500">Net:</span>{" "}
                                <span className={t.actual_pnl.net_profit_dollars >= 0 ? "text-emerald-400" : "text-red-400"}>
                                  ${t.actual_pnl.net_profit_dollars.toFixed(4)}
                                </span>
                              </div>
                            </>
                          )}
                          {t.settlement_pnl != null && (
                            <div>
                              <span className="text-gray-500">Settlement:</span>{" "}
                              <span className={t.settlement_pnl >= 0 ? "text-emerald-400" : "text-red-400"}>
                                ${t.settlement_pnl.toFixed(4)}
                              </span>
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
      {trades.length > 100 && (
        <div className="px-3 py-2 text-center text-xs text-gray-500 border-t border-gray-800">
          Showing 100 of {trades.length} trades
        </div>
      )}
    </div>
  );
}
