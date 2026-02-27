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

// ── Trade Specs: Plain English breakdown of each leg ──────────────────────────

function pmUrl(slug: string | undefined): string | null {
  return slug ? `https://polymarket.com/event/${slug}` : null;
}

function kalshiUrl(ticker: string | undefined): string | null {
  if (!ticker) return null;
  // Extract event ticker: KXNCAAMBGAME-26FEB26MOSULT-LT → event is the ticker itself
  // Kalshi market pages: https://kalshi.com/markets/{ticker}
  return `https://kalshi.com/markets/${ticker}`;
}

function TradeSpecs({ t }: { t: TradeEntry }) {
  const pmVal = normPmNum(t.pm_price);
  const kVal = typeof t.k_price === "number" ? t.k_price : 0;
  const team = t.team_full_name || t.team || "?";
  const opp = t.opponent_full_name || t.opponent || "?";
  const qty = t.contracts_filled || 0;
  const pmLink = pmUrl(t.pm_slug);
  const kLink = kalshiUrl(t.kalshi_ticker);

  // Determine what we did on each exchange
  let pmAction: string, pmTeam: string, pmPrice: string, pmSide: string;
  let kAction: string, kTeam: string, kPrice: string, kSide: string;

  if (t.direction === "BUY_PM_SELL_K") {
    // PM: buy team YES, K: sell opp YES (= buy opp NO)
    if (t.pm_is_buy_short) {
      pmAction = "SELL YES";
      pmTeam = team;
      pmSide = "short";
    } else {
      pmAction = "BUY YES";
      pmTeam = team;
      pmSide = "long";
    }
    pmPrice = `${pmVal.toFixed(0)}c`;
    kAction = "SELL YES";
    kTeam = opp;
    kPrice = `${kVal}c`;
    kSide = "short";
  } else {
    // BUY_K_SELL_PM: K: buy team YES, PM: sell team YES / buy opp YES
    kAction = "BUY YES";
    kTeam = team;
    kPrice = `${kVal}c`;
    kSide = "long";
    if (t.pm_is_buy_short) {
      pmAction = "SELL YES";
      pmTeam = team;
      pmSide = "short";
    } else {
      pmAction = "BUY YES";
      pmTeam = opp;
      pmSide = "long";
    }
    pmPrice = `${pmVal.toFixed(0)}c`;
  }

  return (
    <div className="rounded border border-gray-700/60 bg-gray-800/40 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-gray-800/60 border-b border-gray-700/40">
        <span className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">
          Trade Specs
        </span>
        <span className="text-[9px] text-gray-600 font-mono">
          {t.game_id} &middot; {t.direction}
        </span>
      </div>
      {/* Two-column leg breakdown */}
      <div className="grid grid-cols-2 divide-x divide-gray-700/40">
        {/* PM Leg */}
        <div className="px-3 py-2">
          <div className="flex items-center gap-1.5 mb-1">
            <span className="rounded bg-emerald-900/50 px-1.5 py-0.5 text-[9px] font-bold text-emerald-400">
              PM
            </span>
            <span className="text-[10px] font-bold text-white">{pmAction}</span>
            <span className="text-[10px] text-gray-400">{pmTeam}</span>
          </div>
          <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[9px] font-mono">
            <div><span className="text-gray-500">Fill Price</span> <span className="text-emerald-400 ml-1">{pmPrice}</span></div>
            <div><span className="text-gray-500">Qty</span> <span className="text-gray-300 ml-1">{qty}</span></div>
            <div><span className="text-gray-500">Latency</span> <span className="text-gray-300 ml-1">{t.pm_order_ms || "-"}ms</span></div>
            <div><span className="text-gray-500">Side</span> <span className={`ml-1 ${pmSide === 'long' ? 'text-emerald-400' : 'text-red-400'}`}>{pmSide}</span></div>
            {t.pm_bid != null && (
              <div className="col-span-2"><span className="text-gray-500">BBO at Detection</span> <span className="text-gray-400 ml-1">{t.pm_bid}c / {t.pm_ask}c</span></div>
            )}
          </div>
          {pmLink && (
            <a href={pmLink} target="_blank" rel="noopener noreferrer"
               className="inline-flex items-center gap-1 mt-1.5 text-[9px] text-emerald-400/70 hover:text-emerald-400 transition-colors">
              <span>View on Polymarket</span>
              <span className="text-[8px]">&rarr;</span>
            </a>
          )}
          {t.pm_order_id && (
            <div className="mt-0.5 text-[8px] text-gray-600 font-mono truncate">
              order: {typeof t.pm_order_id === 'string' ? t.pm_order_id.slice(0, 20) : t.pm_order_id}...
            </div>
          )}
        </div>
        {/* Kalshi Leg */}
        <div className="px-3 py-2">
          <div className="flex items-center gap-1.5 mb-1">
            <span className="rounded bg-blue-900/50 px-1.5 py-0.5 text-[9px] font-bold text-blue-400">
              K
            </span>
            <span className="text-[10px] font-bold text-white">{kAction}</span>
            <span className="text-[10px] text-gray-400">{kTeam}</span>
          </div>
          <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[9px] font-mono">
            <div><span className="text-gray-500">Fill Price</span> <span className="text-blue-400 ml-1">{kPrice}</span></div>
            <div><span className="text-gray-500">Qty</span> <span className="text-gray-300 ml-1">{qty}</span></div>
            <div><span className="text-gray-500">Latency</span> <span className="text-gray-300 ml-1">{t.k_order_ms || "-"}ms</span></div>
            <div><span className="text-gray-500">Side</span> <span className={`ml-1 ${kSide === 'long' ? 'text-emerald-400' : 'text-red-400'}`}>{kSide}</span></div>
            {t.k_bid != null && (
              <div className="col-span-2"><span className="text-gray-500">BBO at Detection</span> <span className="text-gray-400 ml-1">{t.k_bid}c / {t.k_ask}c</span></div>
            )}
          </div>
          {kLink && (
            <a href={kLink} target="_blank" rel="noopener noreferrer"
               className="inline-flex items-center gap-1 mt-1.5 text-[9px] text-blue-400/70 hover:text-blue-400 transition-colors">
              <span>View on Kalshi</span>
              <span className="text-[8px]">&rarr;</span>
            </a>
          )}
          {t.k_order_id && (
            <div className="mt-0.5 text-[8px] text-gray-600 font-mono truncate">
              order: {typeof t.k_order_id === 'string' ? t.k_order_id.slice(0, 20) : t.k_order_id}...
            </div>
          )}
        </div>
      </div>
    </div>
  );
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
              <th className="px-2 py-1.5 text-right font-medium">K QTY</th>
              <th className="px-2 py-1.5 text-right font-medium">PM QTY</th>
              <th className="px-2 py-1.5 text-right font-medium">SPREAD</th>
              <th className="px-2 py-1.5 text-right font-medium">DEPTH</th>
              <th className="px-2 py-1.5 text-right font-medium">NET P&L</th>
              <th className="px-2 py-1.5 text-right font-medium">MS</th>
            </tr>
          </thead>
          <tbody>
            {trades.slice(0, 50).map((t, i) => {
              const pnl = tradePnl(t);
              const badge = statusBadge(t.status, t.tier);
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
                      <span className={`rounded px-1 py-0.5 text-[9px] font-medium ${badge.bg} ${badge.text}`} title={badge.tooltip}>
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
                      <td colSpan={10} className="px-4 py-3">
                        {/* ── TRADE SPECS: What exactly was traded ── */}
                        <TradeSpecs t={t} />

                        {/* ── NO-FILL DIAGNOSTIC (PM_NO_FILL only) ── */}
                        {t.nofill_reason && (
                          <div className="mt-3 rounded border border-amber-800/50 bg-amber-950/30 px-3 py-2">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-amber-400 font-bold text-[10px] uppercase tracking-wide">No-Fill Diagnosis</span>
                              <span className="rounded bg-amber-800/50 px-1.5 py-0.5 text-[9px] font-mono text-amber-300">
                                {t.nofill_reason}
                              </span>
                            </div>
                            <p className="text-[10px] text-amber-200/80">{t.nofill_explanation}</p>
                            {t.nofill_details && (
                              <div className="mt-1.5 grid grid-cols-4 gap-x-4 gap-y-1 text-[9px] font-mono">
                                {t.nofill_details.pm_data_age_ms != null && (
                                  <div>
                                    <span className="text-gray-500">Data Age</span>
                                    <span className={`ml-1 ${(t.nofill_details.pm_data_age_ms as number) > 500 ? 'text-red-400' : 'text-gray-300'}`}>
                                      {String(t.nofill_details.pm_data_age_ms)}ms
                                    </span>
                                  </div>
                                )}
                                {t.nofill_details.pm_order_ms != null && (
                                  <div>
                                    <span className="text-gray-500">Order Latency</span>
                                    <span className="text-gray-300 ml-1">{String(t.nofill_details.pm_order_ms)}ms</span>
                                  </div>
                                )}
                                {t.nofill_details.pre_bbo != null && (
                                  <div>
                                    <span className="text-gray-500">Pre-BBO</span>
                                    <span className="text-gray-300 ml-1">
                                      {String((t.nofill_details.pre_bbo as Record<string, string | number>).bid_cents)}c / {String((t.nofill_details.pre_bbo as Record<string, string | number>).ask_cents)}c
                                    </span>
                                  </div>
                                )}
                                {t.nofill_details.post_bbo != null && (
                                  <div>
                                    <span className="text-gray-500">Post-BBO</span>
                                    <span className="text-gray-300 ml-1">
                                      {String((t.nofill_details.post_bbo as Record<string, string | number>).bid_cents)}c / {String((t.nofill_details.post_bbo as Record<string, string | number>).ask_cents)}c
                                    </span>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        )}

                        {/* ── EXECUTION & FINANCIAL DETAIL ── */}
                        <div className="mt-3 grid grid-cols-3 gap-x-6 gap-y-2 text-[10px]">
                          <div>
                            <span className="text-gray-500 block">Phase</span>
                            <span className="text-gray-300">{t.execution_phase || "ioc"}{t.is_maker ? " (maker)" : ""}</span>
                          </div>
                          <div>
                            <span className="text-gray-500 block">Total Execution</span>
                            <span className="text-gray-300 font-mono">{t.execution_time_ms || "-"}ms</span>
                          </div>
                          <div>
                            <span className="text-gray-500 block">Hedged</span>
                            <span className={t.hedged ? "text-emerald-400" : "text-red-400"}>
                              {t.hedged ? "Yes" : "No"}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-500 block">Fees (PM / K)</span>
                            <span className="text-yellow-400 font-mono">
                              ${(t.pm_fee || 0).toFixed(3)} / ${(t.k_fee || 0).toFixed(3)}
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

                        {/* ── DEPTH WALK TABLE ── */}
                        {t.sizing_details?.depth_walk_log && t.sizing_details.depth_walk_log.length > 0 && (
                          <div className="mt-3">
                            <span className="text-gray-500 block mb-1 text-[10px]">Depth Walk</span>
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
