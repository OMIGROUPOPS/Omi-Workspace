// ── Day Sheet parser ─────────────────────────────────────────────────────────
// Parses .claude/today_sheet/LATEST.md into typed rows.
// Source regenerates 5:55a / 11a / 4p ET on the deploy branch. This module is
// pure string parsing — no network/filesystem access — so it can be unit
// tested against fixture text and reused by the API route.

import type {
  DaySheet,
  DaySheetHeader,
  SettledRow,
  OpenRow,
  UnfilledRow,
  UnfilledReason,
  NotBidRow,
  NotBidGroup,
} from "@/components/trading/arb/panels/daysheet/types";

function splitCells(line: string): string[] {
  // Markdown table row: "| a | b | c |" -> ["a","b","c"]
  const trimmed = line.trim().replace(/^\|/, "").replace(/\|$/, "");
  return trimmed.split("|").map((c) => c.trim());
}

function centsFromToken(token: string): number {
  // "38¢" -> 38, "-270¢" -> -270, "+40¢" -> 40
  const m = token.match(/(-?\+?\d+)\s*¢/);
  if (!m) return NaN;
  return parseInt(m[1].replace("+", ""), 10);
}

function isSectionHeading(line: string, marker: string): boolean {
  return line.trim().startsWith(`## ${marker}`);
}

function extractCountLabel(headingLine: string): number {
  const m = headingLine.match(/\((\d+)\)/);
  return m ? parseInt(m[1], 10) : NaN;
}

function parseHeaderBlock(lines: string[]): { header: DaySheetHeader; dateLabel: string } {
  // Line 0: "# TODAY'S SHEET — July 16, 2026 (session 12:00 AM ET onward; ◐ = carried)"
  // Line 1: "(C-TODAY-SHEET v1 — render rules vaulted + census-enforced; generated 11:56 AM ET)"
  // Line 3: "**NAV $751.17** · session realized: TAIL +259¢ | PATH +182¢ · wagered today $97.46 · **P-offered (executor) 24% (79 filled / 245 posted-unfilled)** · **P-market (funnel) 5.4% (79 filled legs / ~1476 listed legs)**"
  const titleLine = lines.find((l) => l.startsWith("# ")) ?? "";
  const dateMatch = titleLine.match(/—\s*([^(]+?)\s*\(/);
  const dateLabel = dateMatch ? dateMatch[1].trim() : "";

  const genLine = lines.find((l) => /generated .* ET\)/.test(l)) ?? "";
  const genMatch = genLine.match(/generated ([\d:apmAPM ]+ET)\)/);
  const generatedAt = genMatch ? genMatch[1].trim() : "";

  const statLine = lines.find((l) => l.includes("**NAV")) ?? "";

  const nav = parseFloat(statLine.match(/NAV \$([\d.]+)/)?.[1] ?? "NaN");
  const tailCents = parseInt(statLine.match(/TAIL ([+-]\d+)¢/)?.[1] ?? "NaN", 10);
  const pathCents = parseInt(statLine.match(/PATH ([+-]\d+)¢/)?.[1] ?? "NaN", 10);
  const wageredToday = parseFloat(statLine.match(/wagered today \$([\d.]+)/)?.[1] ?? "NaN");

  const offeredMatch = statLine.match(/P-offered \(executor\) ([\d.]+)% \((\d+) filled \/ (\d+) posted-unfilled\)/);
  const marketMatch = statLine.match(/P-market \(funnel\) ([\d.]+)% \((\d+) filled legs \/ (~?)(\d+) listed legs\)/);

  const header: DaySheetHeader = {
    dateLabel,
    generatedAt,
    nav,
    tailCents,
    pathCents,
    wageredToday,
    pOfferedPct: offeredMatch ? parseFloat(offeredMatch[1]) : NaN,
    pOfferedFilled: offeredMatch ? parseInt(offeredMatch[2], 10) : NaN,
    pOfferedPosted: offeredMatch ? parseInt(offeredMatch[3], 10) : NaN,
    pMarketPct: marketMatch ? parseFloat(marketMatch[1]) : NaN,
    pMarketFilledLegs: marketMatch ? parseInt(marketMatch[2], 10) : NaN,
    pMarketListedLegs: marketMatch ? parseInt(marketMatch[4], 10) : NaN,
    pMarketListedLegsApprox: marketMatch ? marketMatch[3] === "~" : false,
  };

  return { header, dateLabel };
}

function timeToMinutes(t: string): number | null {
  // "09:31 AM" -> minutes since midnight. Returns null if unparseable.
  const m = t.match(/(\d{1,2}):(\d{2})\s*(AM|PM)/i);
  if (!m) return null;
  let h = parseInt(m[1], 10) % 12;
  const min = parseInt(m[2], 10);
  if (m[3].toUpperCase() === "PM") h += 12;
  return h * 60 + min;
}

function parseSettledRow(cells: string[]): SettledRow {
  const [
    matchRaw, cat, leg, bandRaw, placedET, filledET, fillRaw, w1Raw, bellRaw, schedRaw,
    exitReqRaw, bestTickRaw, closeLabel, pnlRaw,
  ] = cells;

  const carried = matchRaw.includes("◐carried");
  const match = matchRaw.replace(/\s*◐carried\s*$/, "").trim();

  const bellMatch = bellRaw.match(/bell (\d{1,2}:\d{2} [AP]M)\s*\(([^)]+)\)/) || bellRaw.match(/(no bell yet)/);
  const realBell = bellMatch && bellMatch[1] && bellMatch[1] !== "no bell yet" ? bellMatch[1] : (bellRaw.includes("no bell yet") ? "" : "");
  const realBellSource = bellMatch && bellMatch[2] ? bellMatch[2] : (bellRaw.includes("no bell yet") ? "no_bell_yet" : "");

  const schedMatch = schedRaw.match(/sched (\d{1,2}:\d{2} [AP]M)(?:\s*\(Δ([+-]\d+)m\))?/);
  const schedET = schedMatch ? schedMatch[1] : "";
  const schedDeltaMin = schedMatch && schedMatch[2] ? parseInt(schedMatch[2], 10) : 0;

  const exitReqMatch = exitReqRaw.match(/(\d+)¢\s*\(([+-]\d+)\)/);
  const bestTickMatch = bestTickRaw.match(/(\d+)¢\s*@(.+)/);
  const w1Match = w1Raw.match(/(\d+)¢\s*@(.+)/);
  // "W1-best" and "Best tick after fill" sometimes carry a note instead of a
  // number ("no pre-bell tape", "—") — preserve the note rather than coercing to NaN.
  const w1Note = !w1Match ? w1Raw.trim() : null;
  const bestTickNote = !bestTickMatch ? bestTickRaw.trim() : null;

  // Win rows print an unsigned percentage ("105% of basis"); loss rows print a
  // signed negative one ("-500% of basis"). Normalize both to a signed number.
  const pnlMatch = pnlRaw.match(/([+-]\d+)¢\s*\((-?\d+)% of basis \d+¢\)/);
  const pnlCents = pnlMatch ? parseInt(pnlMatch[1], 10) : centsFromToken(pnlRaw);
  const pnlPctOfBasis = pnlMatch ? parseInt(pnlMatch[2], 10) : NaN;

  const filledMin = timeToMinutes(filledET);
  const bellMin = realBell ? timeToMinutes(realBell) : null;
  const postBellFill = filledMin != null && bellMin != null ? filledMin > bellMin : false;

  return {
    match,
    carried,
    cat,
    leg,
    bandCents: centsFromToken(bandRaw),
    placedET,
    filledET,
    fillCents: centsFromToken(fillRaw),
    w1BestCents: w1Match ? parseInt(w1Match[1], 10) : null,
    w1BestAt: w1Match ? w1Match[2] : "",
    w1BestNote: w1Note,
    realBell,
    realBellSource,
    schedET,
    schedDeltaMin,
    exitRequiredCents: exitReqMatch ? parseInt(exitReqMatch[1], 10) : NaN,
    exitRequiredDeltaCents: exitReqMatch ? parseInt(exitReqMatch[2], 10) : NaN,
    bestTickAfterFillCents: bestTickMatch ? parseInt(bestTickMatch[1], 10) : null,
    bestTickAfterFillAt: bestTickMatch ? bestTickMatch[2] : "",
    bestTickAfterFillNote: bestTickNote,
    closeLabel,
    pnlCents,
    pnlPctOfBasis,
    outcome: pnlCents >= 0 ? "win" : "loss",
    postBellFill,
  };
}

function parseOpenRow(cells: string[]): OpenRow {
  const [
    matchRaw, cat, leg, bandRaw, placedET, filledET, fillRaw, w1Raw, bellRaw, schedRaw,
    exitReqRaw, bestTickRaw, _close, markRaw, exitRestingRaw,
  ] = cells;

  const carried = matchRaw.includes("◐carried");
  const match = matchRaw.replace(/\s*◐carried\s*$/, "").trim();

  const bellMatch = bellRaw.match(/bell (\d{1,2}:\d{2} [AP]M)\s*\(([^)]+)\)/);
  const realBell = bellMatch ? bellMatch[1] : "";
  const realBellSource = bellMatch ? bellMatch[2] : (bellRaw.includes("no bell yet") ? "no_bell_yet" : "");

  const schedMatch = schedRaw.match(/sched (\d{1,2}:\d{2} [AP]M)(?:\s*\(Δ([+-]\d+)m\))?/);
  const schedET = schedMatch ? schedMatch[1] : "";
  const schedDeltaMin = schedMatch && schedMatch[2] ? parseInt(schedMatch[2], 10) : 0;

  const exitReqMatch = exitReqRaw.match(/(\d+)¢\s*\(([+-]\d+)\)/);
  const bestTickMatch = bestTickRaw.match(/(\d+)¢\s*@(.+)/);
  const w1Match = w1Raw.match(/(\d+)¢\s*@(.+)/);
  const w1Note = !w1Match ? w1Raw.trim() : null;
  const bestTickNote = !bestTickMatch ? bestTickRaw.trim() : null;
  const markMatch = markRaw.match(/(\d+)¢\s*\(([+-]\d+)¢ vs basis\)/);
  const exitRestingMatch = exitRestingRaw.match(/(\d+)¢\s*×(\d+)\s*\(order ([^)]+)\)/);

  return {
    match,
    carried,
    cat,
    leg,
    bandCents: centsFromToken(bandRaw),
    placedET,
    filledET,
    fillCents: centsFromToken(fillRaw),
    w1BestCents: w1Match ? parseInt(w1Match[1], 10) : null,
    w1BestAt: w1Match ? w1Match[2] : "",
    w1BestNote: w1Note,
    realBell,
    realBellSource,
    schedET,
    schedDeltaMin,
    exitRequiredCents: exitReqMatch ? parseInt(exitReqMatch[1], 10) : NaN,
    exitRequiredDeltaCents: exitReqMatch ? parseInt(exitReqMatch[2], 10) : NaN,
    bestTickAfterFillCents: bestTickMatch ? parseInt(bestTickMatch[1], 10) : null,
    bestTickAfterFillAt: bestTickMatch ? bestTickMatch[2] : "",
    bestTickAfterFillNote: bestTickNote,
    markCents: markMatch ? parseInt(markMatch[1], 10) : NaN,
    markVsBasisCents: markMatch ? parseInt(markMatch[2], 10) : NaN,
    exitRestingCents: exitRestingMatch ? parseInt(exitRestingMatch[1], 10) : NaN,
    exitRestingQty: exitRestingMatch ? parseInt(exitRestingMatch[2], 10) : NaN,
    exitOrderId: exitRestingMatch ? exitRestingMatch[3] : "",
  };
}

function classifyUnfilledReason(reasonRaw: string): UnfilledReason {
  if (reasonRaw.startsWith("never traded that low")) return "never_traded_that_low";
  if (reasonRaw.startsWith("we pulled it")) return "we_pulled_it";
  if (reasonRaw.startsWith("traded")) return "traded_but_late";
  return "never_traded_that_low";
}

function parseUnfilledRow(cells: string[]): UnfilledRow {
  const [match, cat, leg, aimRaw, tapeLowRaw, reasonRaw] = cells;

  const tapeLowMatch = tapeLowRaw.match(/(\d+)¢\s*@(.+)/);
  const reason = classifyUnfilledReason(reasonRaw);

  const pulledAtMatch = reasonRaw.match(/we pulled it \(match went live, (.+?)\)/);
  const tradedLateMatch = reasonRaw.match(/traded (\d+)¢ at — but our bid arrived later/);

  return {
    match,
    cat,
    leg,
    aimCents: centsFromToken(aimRaw),
    tapeLowCents: tapeLowMatch ? parseInt(tapeLowMatch[1], 10) : null,
    tapeLowAt: tapeLowMatch ? tapeLowMatch[2] : null,
    reason,
    reasonRaw, // verbatim — bucket ③ language must not be paraphrased
    pulledAtET: pulledAtMatch ? pulledAtMatch[1] : null,
    tradedButLateCents: tradedLateMatch ? parseInt(tradedLateMatch[1], 10) : null,
  };
}

function parseNotBidRow(cells: string[]): NotBidRow {
  const [match, cat, band, intentRaw, plainReason, tapeNote] = cells;
  const intent = intentRaw.trim() === "intentional" ? "intentional" : "never_reached_decision";
  return {
    match,
    cat,
    band: band === "—" ? null : band,
    intent,
    plainReason,
    tapeNote,
  };
}

function groupNotBid(rows: NotBidRow[]): NotBidGroup[] {
  const map = new Map<string, NotBidGroup>();
  for (const r of rows) {
    if (!map.has(r.plainReason)) {
      map.set(r.plainReason, { plainReason: r.plainReason, count: 0, byCategory: {}, rows: [] });
    }
    const g = map.get(r.plainReason)!;
    g.count += 1;
    g.byCategory[r.cat] = (g.byCategory[r.cat] ?? 0) + 1;
    g.rows.push(r);
  }
  return Array.from(map.values()).sort((a, b) => b.count - a.count);
}

export function parseDaySheet(markdown: string, sourceMtimeIso: string | null = null): DaySheet {
  const lines = markdown.split("\n");

  const { header } = parseHeaderBlock(lines.slice(0, 6));

  const settled: SettledRow[] = [];
  const open: OpenRow[] = [];
  const unfilled: UnfilledRow[] = [];
  const notBid: NotBidRow[] = [];

  let settledCountLabel = NaN;
  let unfilledCountLabel = NaN;
  let notBidCountLabel = NaN;

  let section: "none" | "settled" | "open" | "unfilled" | "notbid" = "none";
  let seenHeaderSep = false;

  for (const line of lines) {
    if (isSectionHeading(line, "①")) {
      section = "settled";
      settledCountLabel = extractCountLabel(line);
      seenHeaderSep = false;
      continue;
    }
    if (isSectionHeading(line, "②")) {
      section = "open";
      seenHeaderSep = false;
      continue;
    }
    if (isSectionHeading(line, "③")) {
      section = "unfilled";
      unfilledCountLabel = extractCountLabel(line);
      seenHeaderSep = false;
      continue;
    }
    if (isSectionHeading(line, "④")) {
      section = "notbid";
      notBidCountLabel = extractCountLabel(line);
      seenHeaderSep = false;
      continue;
    }
    if (section === "none") continue;
    const trimmed = line.trim();
    if (!trimmed.startsWith("|")) continue;
    if (/^\|[\s-]*\|/.test(trimmed) && trimmed.includes("---")) {
      seenHeaderSep = true;
      continue;
    }
    if (!seenHeaderSep) continue; // still the column-name header row
    const cells = splitCells(trimmed);
    if (section === "settled") settled.push(parseSettledRow(cells));
    else if (section === "open") open.push(parseOpenRow(cells));
    else if (section === "unfilled") unfilled.push(parseUnfilledRow(cells));
    else if (section === "notbid") notBid.push(parseNotBidRow(cells));
  }

  return {
    header,
    settled,
    open,
    unfilled,
    notBid,
    notBidGrouped: groupNotBid(notBid),
    meta: {
      settledCountLabel,
      settledRowsActual: settled.length,
      unfilledCountLabel,
      unfilledRowsActual: unfilled.length,
      notBidCountLabel,
      notBidRowsActual: notBid.length,
      generatedAt: header.generatedAt,
      sourceMtimeIso,
    },
  };
}
