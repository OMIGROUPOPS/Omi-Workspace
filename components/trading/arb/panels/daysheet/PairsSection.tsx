"use client";

import React, { useMemo, useState } from "react";
import type { GamePair, PairLegSlot } from "./types";
import { buildGamePairs, catBadgeColor, fmtSignedCents } from "./helpers";

interface Props {
  settled: Parameters<typeof buildGamePairs>[0]["settled"];
  open: Parameters<typeof buildGamePairs>[0]["open"];
  unfilled: Parameters<typeof buildGamePairs>[0]["unfilled"];
  notBid: Parameters<typeof buildGamePairs>[0]["notBid"];
}

/** Delta-in-cents column: our fill/aim minus that leg's own W1 low. Positive
 * (worse — we paid/aimed above the leg's best W1 print) renders red-leaning;
 * negative or zero (at/below the leg's own best print) renders green-leaning.
 * Doctrine citation for "own W1 low" as the comparison object: THE LEG
 * COLUMNS LAW (THE_DAILY_STANDARD.md lines 61–62) and the per-leg S
 * redefinition (LIVING_VAULT: "each leg within 4¢ of its OWN fillable W1
 * low"). */
function DeltaCell({ leg }: { leg: PairLegSlot }) {
  if (leg.deltaCents == null) {
    return <span className="text-[#ffffff]/30 font-mono text-[9px]">{leg.w1LowNote ?? "—"}</span>;
  }
  const d = leg.deltaCents;
  const color = d <= 0 ? "#00ff88" : d <= 4 ? "#ff8c00" : "#c0505a";
  return (
    <span className="font-mono text-[10px] font-bold" style={{ color }}>
      {d >= 0 ? "+" : ""}
      {d}¢
    </span>
  );
}

/** Bell-source honesty badge — rendered as an open data-quality flag per
 * operator point (3), never as a violation verdict. */
function BellBadge({ leg }: { leg: PairLegSlot }) {
  if (leg.bellHonesty === "unknown") return null;
  const isLive = leg.bellHonesty === "live";
  return (
    <span
      className={`text-[7px] font-mono px-1 rounded-none border ml-1 ${
        isLive ? "text-[#00bfff] border-[#00bfff]/30 bg-[#00bfff]/5" : "text-[#ffffff]/50 border-[#1a1a2e] bg-white/[0.02]"
      }`}
      title={
        isLive
          ? `Bell source: ${leg.realBellSource} (live-fired / evidence-observed)`
          : `Bell source: fallback_bell — a schedule-clock ESTIMATE, not a confirmed live gun. Open question, not a violation.`
      }
    >
      {isLive ? "LIVE-FIRED" : "EST. BELL"}
    </span>
  );
}

function LegCell({ leg }: { leg: PairLegSlot }) {
  if (leg.bucket === "not_bid") {
    return (
      <div className="flex flex-col gap-0.5">
        <span className="font-mono text-[9px] text-[#ffffff]/40 italic" title={leg.plainReason ?? undefined}>
          not bid — {leg.plainReason ?? "—"}
        </span>
      </div>
    );
  }
  const ourLabel = leg.ourCents != null ? `${leg.ourCents}¢` : "—";
  return (
    <div className="flex flex-col gap-0.5">
      <div className="flex items-center gap-1.5">
        <span className="font-mono text-[10px] text-[#ff8c00] font-bold">{leg.leg}</span>
        <span className={`inline-block rounded-none px-1 py-0.5 text-[7px] font-mono ${catBadgeColor(leg.cat)}`}>
          {leg.cat.replace("_", " ")}
        </span>
        {leg.bucket === "open" && (
          <span className="text-[7px] font-mono px-1 rounded-none border border-[#7aa8d6]/30 text-[#7aa8d6]">OPEN</span>
        )}
        {leg.bucket === "unfilled" && (
          <span className="text-[7px] font-mono px-1 rounded-none border border-[#ffffff]/20 text-[#ffffff]/40">UNFILLED</span>
        )}
      </div>
      <div className="flex items-center gap-2 flex-wrap">
        <span className="font-mono text-[10px] text-[#ffffff]">
          {leg.ourIsAim ? "aim " : "fill "}
          <span className="font-bold">{ourLabel}</span>
        </span>
        <span className="text-[#1a1a2e]">vs</span>
        <span className="font-mono text-[9px] text-[#ffffff]/60">
          W1-low{" "}
          {leg.w1LowCents != null ? (
            <>
              <span className="text-[#00bfff]">{leg.w1LowCents}¢</span>
              {leg.w1LowAt && <span className="text-[#ffffff]/30"> @{leg.w1LowAt}</span>}
            </>
          ) : (
            <span className="text-[#ffffff]/30">{leg.w1LowNote ?? "—"}</span>
          )}
        </span>
        <BellBadge leg={leg} />
      </div>
      {leg.bucket === "unfilled" && leg.reasonRaw && (
        <span className="text-[8px] font-mono text-[#ffffff]/40 italic" title={leg.reasonRaw}>
          {leg.reasonRaw}
        </span>
      )}
      {leg.outcome && leg.pnlCents != null && (
        <span className={`font-mono text-[9px] font-bold ${leg.outcome === "win" ? "text-[#00ff88]" : "text-[#ff3333]"}`}>
          {fmtSignedCents(leg.pnlCents)}
        </span>
      )}
    </div>
  );
}

type FilterMode = "all" | "oneSided" | "bothFilled";

export function PairsSection({ settled, open, unfilled, notBid }: Props) {
  const [filter, setFilter] = useState<FilterMode>("all");

  const pairs = useMemo(() => buildGamePairs({ settled, open, unfilled, notBid }), [settled, open, unfilled, notBid]);

  const stats = useMemo(() => {
    const oneSided = pairs.filter((p) => p.isOneSided).length;
    const bothFilled = pairs.filter((p) => p.isBothFilled).length;
    const estimatedBellLegs = pairs.reduce(
      (acc, p) => acc + p.legs.filter((l) => l.bellHonesty === "estimated").length,
      0
    );
    const liveBellLegs = pairs.reduce((acc, p) => acc + p.legs.filter((l) => l.bellHonesty === "live").length, 0);
    return { total: pairs.length, oneSided, bothFilled, estimatedBellLegs, liveBellLegs };
  }, [pairs]);

  const displayPairs = useMemo(() => {
    if (filter === "oneSided") return pairs.filter((p) => p.isOneSided);
    if (filter === "bothFilled") return pairs.filter((p) => p.isBothFilled);
    return pairs;
  }, [pairs, filter]);

  return (
    <div className="border border-[#1a1a2e] bg-[#0a0a0a] relative overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-[2px]" style={{ backgroundColor: "#ff8c00" }} />
      <div className="w-full px-3 py-1.5 bg-black border-b border-[#1a1a2e] flex items-center gap-3 text-[9px] font-mono flex-wrap">
        <span className="text-[#ffffff] uppercase tracking-widest font-bold">PER-GAME PAIRS</span>
        <span className="font-bold text-[#ff8c00]">{stats.total}</span>
        <span className="text-[#1a1a2e]">|</span>
        <span className="text-[#00ff88]">{stats.bothFilled} both-filled</span>
        <span className="text-[#c0505a] font-bold">{stats.oneSided} one-sided</span>
        <span className="text-[#1a1a2e]">|</span>
        <span className="text-[#ffffff]/50" title="Open question, not a verdict — see THE OPERATOR'S UNESTABLISHED list">
          bell honesty: <span className="text-[#00bfff]">{stats.liveBellLegs} live</span> /{" "}
          <span className="text-[#ffffff]/60">{stats.estimatedBellLegs} estimated</span>
        </span>
      </div>

      <div className="px-3 py-1 text-[8px] font-mono text-[#ffffff]/40 italic border-b border-[#1a1a2e]/50">
        §0A THE OPERATOR&rsquo;S FRAME: the whole game is filling BOTH sides of each match in Window 1 at a fair price. Dial-failure
        tagging awaits the OS&rsquo;s own logs — not rendered here as our inference.
      </div>

      <div className="px-2 pt-1.5 flex items-center gap-1.5">
        {(["all", "oneSided", "bothFilled"] as FilterMode[]).map((m) => (
          <button
            key={m}
            onClick={() => setFilter(m)}
            className={`text-[8px] font-mono px-1.5 py-0.5 border rounded-none ${
              filter === m
                ? "bg-[#ff8c00]/20 text-[#ff8c00] border-[#ff8c00]/40"
                : "text-[#ffffff]/50 border-[#1a1a2e] hover:text-[#ff8c00]"
            }`}
          >
            {m === "all" ? "ALL" : m === "oneSided" ? "ONE-SIDED ONLY" : "BOTH-FILLED ONLY"}
          </button>
        ))}
      </div>

      <div className="overflow-x-hidden" style={{ maxHeight: 560, overflowY: "auto" }}>
        <table className="w-full text-xs table-fixed">
          <colgroup>
            <col style={{ width: "23%" }} />
            <col style={{ width: "11%" }} />
            <col style={{ width: "33%" }} />
            <col style={{ width: "33%" }} />
          </colgroup>
          <thead className="sticky top-0 bg-[#0a0a0a] z-10 border-b border-[#1a1a2e]">
            <tr className="text-[#ffffff]">
              <th className="px-2 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">MATCH</th>
              <th className="px-1 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">STATUS</th>
              <th className="px-2 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">LEG 1 — fill/aim vs W1-low (Δ)</th>
              <th className="px-2 py-1.5 text-left font-mono text-[9px] uppercase tracking-wider font-medium">LEG 2 — fill/aim vs W1-low (Δ)</th>
            </tr>
          </thead>
          <tbody>
            {displayPairs.map((p, i) => {
              const isOdd = i % 2 === 1;
              const legA = p.legs[0];
              const legB = p.legs[1];
              const oneSidedHighlight = p.isOneSided ? "bg-[#c0505a]/[0.06]" : "";
              return (
                <tr
                  key={`${p.match}-${i}`}
                  className={`border-b border-[#1a1a2e]/50 hover:bg-white/[0.03] transition-colors align-top ${
                    isOdd ? "bg-white/[0.02]" : ""
                  } ${oneSidedHighlight}`}
                >
                  <td className="px-2 py-1.5 truncate" title={p.match}>
                    <span className="font-mono text-[10px] text-[#ffffff]">{p.match}</span>
                    {p.carried && <span className="text-[#7aa8d6] ml-1" title="Carried over from a prior session">◐</span>}
                  </td>
                  <td className="px-1 py-1.5">
                    {p.isOneSided && (
                      <span
                        className="inline-block whitespace-nowrap rounded-none px-1.5 py-0.5 text-[8px] font-mono font-bold bg-[#c0505a]/15 text-[#c0505a] border border-[#c0505a]/40 uppercase tracking-wider"
                        title="Doctrine's own term (§C-SHIMIC-TRACE): 'the pair went one-sided.' Only one leg has an actual fill."
                      >
                        ⚠ ONE-SIDED
                      </span>
                    )}
                    {p.isBothFilled && (
                      <span className="inline-block whitespace-nowrap rounded-none px-1.5 py-0.5 text-[8px] font-mono font-bold bg-[#00ff88]/15 text-[#00ff88] border border-[#00ff88]/40 uppercase tracking-wider">
                        ✓ BOTH FILLED
                      </span>
                    )}
                    {!p.isOneSided && !p.isBothFilled && (
                      <span className="whitespace-nowrap text-[8px] font-mono text-[#ffffff]/30 uppercase tracking-wider">no fill yet</span>
                    )}
                  </td>
                  <td className="px-2 py-1.5">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">{legA ? <LegCell leg={legA} /> : <span className="text-[#ffffff]/20 font-mono text-[9px]">—</span>}</div>
                      {legA && <div className="pt-0.5"><DeltaCell leg={legA} /></div>}
                    </div>
                  </td>
                  <td className="px-2 py-1.5">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">{legB ? <LegCell leg={legB} /> : <span className="text-[#ffffff]/20 font-mono text-[9px]">—</span>}</div>
                      {legB && <div className="pt-0.5"><DeltaCell leg={legB} /></div>}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
