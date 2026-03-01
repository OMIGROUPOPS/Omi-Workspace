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

  const ecb = t.estimated_costs_breakdown;
  const kFeeCents = ecb?.k_fee ?? (typeof t.k_fee === 'number' ? t.k_fee : 0);
  const pmFeeCents = ecb?.pm_fee ?? (typeof t.pm_fee === 'number' ? t.pm_fee : 0);
  const netCents = ecb?.net_cents ?? (t.estimated_net_profit_cents || 0);
  const totalCosts = ecb?.total_costs ?? (kFeeCents + pmFeeCents);

  let pmAction: string, pmTeam: string, pmPrice: string, pmPriceCents: number;
  let kAction: string, kTeam: string, kPrice: string, kPriceCents: number;

  const pmDisplayPrice = t.pm_is_buy_short ? (100 - pmVal) : pmVal;

  if (t.direction === "BUY_PM_SELL_K") {
    pmAction = "BUY YES";
    pmTeam = t.pm_is_buy_short ? opp : team;
    pmPriceCents = pmDisplayPrice;
    pmPrice = `${pmDisplayPrice.toFixed(0)}c`;
    kAction = "BUY NO";
    kTeam = team;
    kPriceCents = 100 - kVal;
    kPrice = `${kPriceCents}c`;
  } else {
    kAction = "BUY YES";
    kTeam = team;
    kPriceCents = kVal;
    kPrice = `${kVal}c`;
    pmAction = "BUY YES";
    pmTeam = t.pm_is_buy_short ? opp : team;
    pmPriceCents = pmDisplayPrice;
    pmPrice = `${pmDisplayPrice.toFixed(0)}c`;
  }

  const kCostPerContract = kPriceCents / 100;
  const pmCostPerContract = pmPriceCents / 100;
  const kTotalCost = kCostPerContract * qty;
  const pmTotalCost = pmCostPerContract * qty;

  return (
    <div className="border border-[#1a1a2e] bg-[#0a0a12] overflow-hidden rounded-none">
      <div className="flex items-center justify-between px-3 py-1.5 bg-black border-b border-[#1a1a2e]">
        <span className="text-[9px] font-mono font-bold text-[#4a4a6a] uppercase tracking-widest">
          TRADE SPECS
        </span>
        <span className="text-[8px] text-[#3a3a5a] font-mono">
          {t.game_id} &middot; {t.direction}
        </span>
      </div>
      <div className="grid grid-cols-2 divide-x divide-[#1a1a2e]">
        {/* PM Leg */}
        <div className="px-3 py-2">
          <div className="flex items-center gap-1.5 mb-1">
            <span className="rounded-none bg-[#00ff88]/10 border border-[#00ff88]/30 px-1.5 py-0.5 text-[9px] font-bold font-mono text-[#00ff88]">
              PM
            </span>
            <span className="text-[10px] font-bold font-mono text-[#ff8c00]">{pmAction}</span>
            <span className="text-[10px] font-mono text-[#4a4a6a]">{pmTeam}</span>
          </div>
          <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[9px] font-mono">
            <div><span className="text-[#4a4a6a]">Fill Price</span> <span className="text-[#00ff88] ml-1">{pmPrice}</span> <span className="text-[#4a4a6a] ml-0.5">(${pmCostPerContract.toFixed(2)})</span></div>
            <div><span className="text-[#4a4a6a]">Qty</span> <span className="text-[#ff8c00] ml-1">{qty}</span></div>
            <div className="col-span-2"><span className="text-[#4a4a6a]">Total Cost</span> <span className="text-[#00ff88] ml-1 font-bold">${pmTotalCost.toFixed(2)}</span></div>
            <div><span className="text-[#4a4a6a]">Latency</span> <span className="text-[#ff8c00] ml-1">{t.pm_order_ms || "-"}ms</span></div>
            <div><span className="text-[#4a4a6a]">Fee</span> <span className="text-[#ff8c00]/80 ml-1">{pmFeeCents.toFixed(2)}c</span></div>
            {t.pm_bid != null && (
              <div className="col-span-2"><span className="text-[#4a4a6a]">BBO at Detection</span> <span className="text-[#ff8c00] ml-1">{t.pm_bid}c / {t.pm_ask}c</span></div>
            )}
          </div>
          {pmLink && (
            <a href={pmLink} target="_blank" rel="noopener noreferrer"
               className="inline-flex items-center gap-1 mt-1.5 text-[9px] text-[#00ff88]/70 hover:text-[#00ff88] transition-colors font-mono">
              <span>View on Polymarket</span>
              <span className="text-[8px]">&rarr;</span>
            </a>
          )}
          {t.pm_order_id && (
            <div className="mt-0.5 text-[8px] text-[#3a3a5a] font-mono truncate">
              order: {typeof t.pm_order_id === 'string' ? t.pm_order_id.slice(0, 20) : t.pm_order_id}...
            </div>
          )}
        </div>
        {/* Kalshi Leg */}
        <div className="px-3 py-2">
          <div className="flex items-center gap-1.5 mb-1">
            <span className="rounded-none bg-[#00bfff]/10 border border-[#00bfff]/30 px-1.5 py-0.5 text-[9px] font-bold font-mono text-[#00bfff]">
              K
            </span>
            <span className="text-[10px] font-bold font-mono text-[#ff8c00]">{kAction}</span>
            <span className="text-[10px] font-mono text-[#4a4a6a]">{kTeam}</span>
          </div>
          <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[9px] font-mono">
            <div><span className="text-[#4a4a6a]">Fill Price</span> <span className="text-[#00bfff] ml-1">{kPrice}</span> <span className="text-[#4a4a6a] ml-0.5">(${kCostPerContract.toFixed(2)})</span></div>
            <div><span className="text-[#4a4a6a]">Qty</span> <span className="text-[#ff8c00] ml-1">{qty}</span></div>
            <div className="col-span-2"><span className="text-[#4a4a6a]">Total Cost</span> <span className="text-[#00bfff] ml-1 font-bold">${kTotalCost.toFixed(2)}</span></div>
            <div><span className="text-[#4a4a6a]">Latency</span> <span className="text-[#ff8c00] ml-1">{t.k_order_ms || "-"}ms</span></div>
            <div><span className="text-[#4a4a6a]">Fee</span> <span className="text-[#ff8c00]/80 ml-1">{kFeeCents.toFixed(1)}c</span></div>
            {t.k_bid != null && (
              <div className="col-span-2"><span className="text-[#4a4a6a]">BBO at Detection</span> <span className="text-[#ff8c00] ml-1">{t.k_bid}c / {t.k_ask}c</span></div>
            )}
          </div>
          {kLink && (
            <a href={kLink} target="_blank" rel="noopener noreferrer"
               className="inline-flex items-center gap-1 mt-1.5 text-[9px] text-[#00bfff]/70 hover:text-[#00bfff] transition-colors font-mono">
              <span>View on Kalshi</span>
              <span className="text-[8px]">&rarr;</span>
            </a>
          )}
          {t.k_order_id && (
            <div className="mt-0.5 text-[8px] text-[#3a3a5a] font-mono truncate">
              order: {typeof t.k_order_id === 'string' ? t.k_order_id.slice(0, 20) : t.k_order_id}...
            </div>
          )}
        </div>
      </div>
      {/* Net Profit Summary Bar */}
      {(() => {
        const arbNetCPC = (t as any).arb_net_cents_per_contract;
        const arbNetTotal = (t as any).arb_net_total_cents;
        const useArbNet = typeof arbNetCPC === 'number';
        const displayNetCents = useArbNet ? arbNetCPC : netCents;
        const displayTotalDollars = useArbNet ? (arbNetTotal / 100) : ((netCents * qty) / 100);
        return (
          <div className="flex items-center justify-between px-3 py-1.5 bg-black border-t-2 border-[#ff8c00]/30 text-[9px] font-mono">
            <div className="flex items-center gap-3">
              <span className="text-[#4a4a6a]">{useArbNet ? 'Arb Net' : 'Spread'}</span>
              <span className="text-[#ff8c00]">{useArbNet ? `${arbNetCPC.toFixed(2)}c` : `${t.spread_cents}c`}</span>
              {!useArbNet && (
                <>
                  <span className="text-[#3a3a5a]">−</span>
                  <span className="text-[#4a4a6a]">Fees</span>
                  <span className="text-[#ff8c00]/80">{totalCosts.toFixed(1)}c</span>
                  <span className="text-[#3a3a5a]">=</span>
                </>
              )}
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-[#4a4a6a]">Net</span>
              <span className={`font-bold text-[10px] ${displayNetCents > 0 ? 'text-[#00ff88]' : displayNetCents < 0 ? 'text-[#ff3333]' : 'text-[#4a4a6a]'}`}>
                {displayNetCents > 0 ? '+' : ''}{displayNetCents.toFixed(2)}c
              </span>
              <span className="text-[#3a3a5a]">/contract</span>
              {qty > 0 && (
                <>
                  <span className="text-[#1a1a2e] mx-1">|</span>
                  <span className={`font-bold text-[10px] ${displayTotalDollars > 0 ? 'text-[#00ff88]' : displayTotalDollars < 0 ? 'text-[#ff3333]' : 'text-[#4a4a6a]'}`}>
                    ${displayTotalDollars.toFixed(2)}
                  </span>
                  <span className="text-[#3a3a5a]">total</span>
                </>
              )}
            </div>
          </div>
        );
      })()}
    </div>
  );
}

function legsLabel(t: TradeEntry) {
  const pmVal = normPmNum(t.pm_price);
  const kVal = typeof t.k_price === "number" ? t.k_price : 0;
  const team = t.team || "?";
  const opp = t.opponent || "?";

  const pmDisplayPrice = t.pm_is_buy_short ? (100 - pmVal) : pmVal;

  if (t.direction === "BUY_PM_SELL_K") {
    const pmFighter = t.pm_is_buy_short ? opp : team;
    const kNoCost = kVal > 0 ? 100 - kVal : 0;
    const totalCost = pmVal + kNoCost;
    const spread = 100 - totalCost;
    return (
      <>
        <span className="text-[#00ff88]">PM: {pmFighter} @{pmDisplayPrice.toFixed(0)}c</span>
        <span className="text-[#1a1a2e] mx-1">|</span>
        <span className="text-[#00bfff]">K: NO {team} @{kNoCost.toFixed(0)}c</span>
        <span className="text-[#3a3a5a] ml-1.5 text-[9px]">[{totalCost.toFixed(0)}c&rarr;{spread.toFixed(0)}c]</span>
      </>
    );
  }
  const pmFighter = t.pm_is_buy_short ? opp : team;
  const totalCost = kVal + pmVal;
  const spread = 100 - totalCost;
  return (
    <>
      <span className="text-[#00bfff]">K: {team} @{kVal}c</span>
      <span className="text-[#1a1a2e] mx-1">|</span>
      <span className="text-[#00ff88]">PM: {pmFighter} @{pmDisplayPrice.toFixed(0)}c</span>
      <span className="text-[#3a3a5a] ml-1.5 text-[9px]">[{totalCost.toFixed(0)}c&rarr;{spread.toFixed(0)}c]</span>
    </>
  );
}

export function TradeLog({ trades, expandedTrade, setExpandedTrade }: Props) {
  if (trades.length === 0) {
    return (
      <div className="p-4 text-center text-[10px] font-mono text-[#3a3a5a]">
        NO TRADES IN CURRENT VIEW
      </div>
    );
  }

  return (
    <div className="overflow-hidden">
      <div className="overflow-x-auto" style={{ maxHeight: "400px" }}>
        <table className="w-full text-xs">
          <thead className="sticky top-0 bg-[#0a0a0a] z-10 border-b border-[#1a1a2e]">
            <tr className="text-[#4a4a6a]">
              <th className="px-2 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">TIME</th>
              <th className="px-2 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">GAME</th>
              <th className="px-2 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">LEGS</th>
              <th className="px-2 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">STATUS</th>
              <th className="px-2 py-1.5 text-right font-mono text-[9px] uppercase tracking-wider font-medium">SPREAD</th>
              <th className="px-2 py-1.5 text-right font-mono text-[9px] uppercase tracking-wider font-medium">NET P&L</th>
            </tr>
          </thead>
          <tbody>
            {trades.slice(0, 50).map((t, i) => {
              const pnl = tradePnl(t);
              const badge = statusBadge(t.status, t.tier);
              const depth = getL1Depth(t);
              const isExpanded = expandedTrade === i;
              const isOdd = i % 2 === 1;

              return (
                <React.Fragment key={`${t.timestamp}-${t.team}-${i}`}>
                  <tr
                    className={`border-b border-[#1a1a2e]/50 hover:bg-[#ff8c00]/[0.04] cursor-pointer transition-colors ${isOdd ? "bg-white/[0.02]" : ""}`}
                    onClick={() => setExpandedTrade(isExpanded ? null : i)}
                  >
                    <td className="px-2 py-1.5 text-[#4a4a6a] whitespace-nowrap font-mono text-[10px]">
                      {formatDateTime(t.timestamp)}
                      {(t as any).unwind_timestamp_est && (
                        <div className="text-[9px] text-[#ff8c00] mt-0.5">
                          &#x21A9; {(t as any).unwind_timestamp_est}
                        </div>
                      )}
                    </td>
                    <td className="px-2 py-1.5 whitespace-nowrap">
                      <span className={`inline-block rounded-none px-1 py-0.5 text-[8px] font-mono mr-1 ${sportBadge(t.sport)}`}>
                        {t.sport}
                      </span>
                      <span className="font-bold font-mono text-[#ff8c00]">{t.team_full_name || t.team}</span>
                      {(t.opponent_full_name || t.opponent) ? (
                        <span className="text-[#4a4a6a] font-mono text-[10px] ml-1">vs {t.opponent_full_name || t.opponent}</span>
                      ) : null}
                    </td>
                    <td className="px-2 py-1.5 whitespace-nowrap text-[10px] font-mono">
                      {legsLabel(t)}
                      {(t as any).unwind_close_action && (
                        <div className="text-[9px] text-[#ff8c00] mt-0.5">
                          &#x21A9; {(t as any).unwind_close_action} &#x2192; {(t as any).unwind_reopen_action}
                        </div>
                      )}
                    </td>
                    <td className="px-2 py-1.5">
                      <span className={`rounded-none px-1 py-0.5 text-[9px] font-mono font-medium ${badge.bg} ${badge.text}`} title={badge.tooltip}>
                        {badge.label}
                      </span>
                    </td>
                    <td className="px-2 py-1.5 text-right font-mono text-[#ff8c00]">
                      {t.spread_cents?.toFixed(1) ?? "-"}c
                    </td>
                    <td className={`px-2 py-1.5 text-right font-mono ${
                      pnl.totalDollars === null ? "text-[#4a4a6a]" :
                      Math.abs(pnl.totalDollars) >= 1 ? `font-bold ${netColor(pnl.totalDollars)}` :
                      netColor(pnl.totalDollars)
                    }`}>
                      {pnl.totalDollars !== null
                        ? `$${pnl.totalDollars.toFixed(4)}`
                        : pnl.isOpen ? <span className="text-[#ff8c00]">OPEN</span> : "-"}
                    </td>
                  </tr>
                  {isExpanded && (
                    <tr className="bg-[#0a0a12]">
                      <td colSpan={6} className="px-4 py-3">
                        <TradeSpecs t={t} />

                        {/* No-fill diagnostic */}
                        {t.nofill_reason && (
                          <div className="mt-3 border border-[#ff8c00]/30 bg-[#ff8c00]/5 px-3 py-2">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-[#ff8c00] font-bold font-mono text-[9px] uppercase tracking-wider">No-Fill Diagnosis</span>
                              <span className="rounded-none bg-[#ff8c00]/20 border border-[#ff8c00]/30 px-1.5 py-0.5 text-[9px] font-mono text-[#ff8c00]">
                                {t.nofill_reason}
                              </span>
                            </div>
                            <p className="text-[10px] font-mono text-[#ff8c00]/80">{t.nofill_explanation}</p>
                            {t.nofill_details && (
                              <div className="mt-1.5 grid grid-cols-4 gap-x-4 gap-y-1 text-[9px] font-mono">
                                {t.nofill_details.pm_data_age_ms != null && (
                                  <div>
                                    <span className="text-[#4a4a6a]">Data Age</span>
                                    <span className={`ml-1 ${(t.nofill_details.pm_data_age_ms as number) > 500 ? 'text-[#ff3333]' : 'text-[#ff8c00]'}`}>
                                      {String(t.nofill_details.pm_data_age_ms)}ms
                                    </span>
                                  </div>
                                )}
                                {t.nofill_details.pm_order_ms != null && (
                                  <div>
                                    <span className="text-[#4a4a6a]">Order Latency</span>
                                    <span className="text-[#ff8c00] ml-1">{String(t.nofill_details.pm_order_ms)}ms</span>
                                  </div>
                                )}
                                {t.nofill_details.pre_bbo != null && (
                                  <div>
                                    <span className="text-[#4a4a6a]">Pre-BBO</span>
                                    <span className="text-[#ff8c00] ml-1">
                                      {String((t.nofill_details.pre_bbo as Record<string, string | number>).bid_cents)}c / {String((t.nofill_details.pre_bbo as Record<string, string | number>).ask_cents)}c
                                    </span>
                                  </div>
                                )}
                                {t.nofill_details.post_bbo != null && (
                                  <div>
                                    <span className="text-[#4a4a6a]">Post-BBO</span>
                                    <span className="text-[#ff8c00] ml-1">
                                      {String((t.nofill_details.post_bbo as Record<string, string | number>).bid_cents)}c / {String((t.nofill_details.post_bbo as Record<string, string | number>).ask_cents)}c
                                    </span>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        )}

                        {/* Execution detail */}
                        <div className="mt-3 grid grid-cols-3 gap-x-6 gap-y-2 text-[10px] font-mono">
                          <div>
                            <span className="text-[#4a4a6a] block text-[9px] uppercase tracking-wider">Phase</span>
                            <span className="text-[#ff8c00]">{t.execution_phase || "ioc"}{t.is_maker ? " (maker)" : ""}</span>
                          </div>
                          <div>
                            <span className="text-[#4a4a6a] block text-[9px] uppercase tracking-wider">Total Execution</span>
                            <span className="text-[#ff8c00]">{t.execution_time_ms || "-"}ms</span>
                          </div>
                          <div>
                            <span className="text-[#4a4a6a] block text-[9px] uppercase tracking-wider">Hedged</span>
                            <span className={t.hedged ? "text-[#00ff88]" : "text-[#ff3333]"}>
                              {t.hedged ? "YES" : "NO"}
                            </span>
                          </div>
                          <div>
                            <span className="text-[#4a4a6a] block text-[9px] uppercase tracking-wider">Fills (K / PM)</span>
                            <span className="text-[#ff8c00]">
                              {t.kalshi_fill ?? t.contracts_filled ?? 0}x / {t.pm_fill ?? t.contracts_filled ?? 0}x
                            </span>
                          </div>
                          <div>
                            <span className="text-[#4a4a6a] block text-[9px] uppercase tracking-wider">Fees (PM / K)</span>
                            <span className="text-[#ff8c00]">
                              ${(t.pm_fee || 0).toFixed(3)} / ${(t.k_fee || 0).toFixed(3)}
                            </span>
                          </div>
                          {t.sizing_details && (
                            <>
                              {depth.k !== null && (
                                <div>
                                  <span className="text-[#4a4a6a] block text-[9px] uppercase tracking-wider">L1 at Arb Price</span>
                                  <span>
                                    <span className={depthColor(depth.k)}>K: {fmtNum(depth.k)}</span>
                                    {" @ "}{t.sizing_details.depth_walk_log?.[0]?.k_price ?? "-"}c
                                    <span className="text-[#3a3a5a] mx-1">|</span>
                                    <span className={depthColor(depth.pm)}>PM: {fmtNum(depth.pm!)}</span>
                                    {" @ "}{t.sizing_details.depth_walk_log?.[0]?.pm_cost ?? "-"}c
                                  </span>
                                </div>
                              )}
                              <div>
                                <span className="text-[#4a4a6a] block text-[9px] uppercase tracking-wider">Total Book Depth</span>
                                <span className="text-[#ff8c00]">
                                  K: {fmtNum(t.sizing_details.k_depth)} | PM: {fmtNum(t.sizing_details.pm_depth)} ({t.sizing_details.limit_reason})
                                </span>
                              </div>
                            </>
                          )}
                          {t.settlement_pnl != null && (
                            <div>
                              <span className="text-[#4a4a6a] block text-[9px] uppercase tracking-wider">Settlement P&L</span>
                              <span className={t.settlement_pnl >= 0 ? "text-[#00ff88] font-bold" : "text-[#ff3333] font-bold"}>
                                ${t.settlement_pnl.toFixed(4)}
                              </span>
                            </div>
                          )}
                          {t.gtc_cancel_reason && (
                            <div>
                              <span className="text-[#4a4a6a] block text-[9px] uppercase tracking-wider">GTC Cancel</span>
                              <span className="text-[#ff8c00]">{t.gtc_cancel_reason}</span>
                            </div>
                          )}
                        </div>

                        {/* Depth walk table */}
                        {t.sizing_details?.depth_walk_log && t.sizing_details.depth_walk_log.length > 0 && (
                          <div className="mt-3">
                            <span className="text-[#4a4a6a] block mb-1 text-[9px] font-mono uppercase tracking-wider">Depth Walk</span>
                            <table className="w-full text-[10px] font-mono">
                              <thead>
                                <tr className="text-[#4a4a6a] border-b border-[#1a1a2e]">
                                  <th className="text-left pr-2 py-1 font-medium">LVL</th>
                                  <th className="text-right pr-2 py-1 font-medium">K</th>
                                  <th className="text-right pr-2 py-1 font-medium">PM</th>
                                  <th className="text-right pr-2 py-1 font-medium">SPREAD</th>
                                  <th className="text-right pr-2 py-1 font-medium">FEES</th>
                                  <th className="text-right pr-2 py-1 font-medium">NET</th>
                                  <th className="text-right pr-2 py-1 font-medium">QTY</th>
                                  <th className="text-right py-1 font-medium">CUM</th>
                                </tr>
                              </thead>
                              <tbody>
                                {t.sizing_details.depth_walk_log.map((l) => (
                                  <tr key={l.level} className={l.stopped ? "text-[#ff3333]" : "text-[#00ff88]"}>
                                    <td className="text-left pr-2 py-0.5">{l.stopped ? "\u2717" : "\u2713"} L{l.level}</td>
                                    <td className="text-right pr-2">{l.k_price}c</td>
                                    <td className="text-right pr-2">{l.pm_cost}c</td>
                                    <td className="text-right pr-2">{l.spread}c</td>
                                    <td className="text-right pr-2">{l.fees}c</td>
                                    <td className={`text-right pr-2 font-bold ${l.marginal_profit >= 0 ? "text-[#00ff88]" : "text-[#ff3333]"}`}>
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
