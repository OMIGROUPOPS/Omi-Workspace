# The substitution audit — every declined instrument checked for the strawman signature

Analysis seat only. Read-only. Per instrument: the doctrine/receipt it claimed to test (cited) · what the
mechanics actually did · FAITHFUL / SUBSTITUTED (named) / PARTIAL · the faithful test in one line. This audit
does not spare the auditor: **two of the substitutions below are in my own analytics** (ex-post conditioning),
where the executable machines that "killed" the doctrine were in fact the faithful tests. Machine list:
`THE_SUBSTITUTION_AUDIT.json`.

## The graveyard, one verdict each

**1. V38 pulse-floor** (`2c54d724`; doctrine = the divot census `d1ac9497`: risers pulse to a *recurring*
session floor). Mechanics: rest at the lowest ask level revisited ≥2× **within a trailing 300 s horizon**.
**SUBSTITUTED — TRAILING-WINDOW MYOPIA**: the census's recurrence is session-scale (episodes hours apart,
`6b28b4af`); a 5-minute lookback tests a different, far stricter law. Faithful: rest at the deepest ask level
with ≥2 visits over the **whole post-stand session**, census dwell params.

**2. Wide-spread ask-anchor** (`57583640`; doctrine = the VRB class: catch the wide-spread riser's first
dwelled divot). Mechanics: gated on **median** spread > 3¢ — which excluded VRB itself (median 2¢, transient
max 87¢); my own report noted the gate was wrong and scored the law anyway. **SUBSTITUTED — MEDIAN GATE FOR
PER-MOMENT SPREAD**. Faithful: trigger the anchor when the *current* spread > 3¢ at the divot moment.

**3. k-depth curve** (d40bc010-era; doctrine = deeper fixed rests catch deep flow). Mechanics: fills credited
when the tape **best-bid path touched** the level — a descending bid at your level does not fill you; it makes
you best bid. **SUBSTITUTED — BID-TOUCH RULER FOR TRADE-TRUTH** (pre-CANON era). Faithful: re-run k∈{1,2,3,5,8}
under trades-as-truth (any true trade ≤ bid−k after stood).

**4. LAW B mirror** (`e177c2fb`; KNOWN — the template; doctrine = derive the sibling's placement from the
trusted eye's inverse). Mechanics: inverse=RISING siblings got a **one-shot join at the current bid** ("fills
if touched") — not the vaulted riser stack. **SUBSTITUTED — ONE-SHOT LEVEL FOR THE FULL RISER STACK**.
Faithful: run the sibling under the complete V47 riser machinery (persistence join + release + loosen) armed
at the trust moment, trades-as-truth scored.

**5. Dual-rest** (`d34fc6ce`; doctrine = A join + B tracker ≥1¢ above A, first-fill-wins). Mechanics
implemented the order as specified, including the ≥A+1 constraint and first-fill-wins cancellation.
**FAITHFUL** — the finding (B front-runs A; only-A = 0) is a real property of the ordered law. Stays dead.

**6. Classifier-34% / the read organ** (mirror RIGHT/WRONG, L2 misread 63%, `fdeb7516`/`e177c2fb`; doctrine =
the state read is wrong at decision moments). Mechanics: reads judged against the **frozen QR leg_direction —
an ex-post whole-window label** (close-vs-open). A leg genuinely FALLING at hour 2 of a window that ends RISING
scores the classifier "wrong" for a correct momentary read. **SUBSTITUTED — EX-POST TERMINAL LABELS FOR
MOMENT-TRUTH**. Faithful: judge each read against the forward price path over the following 30-60 min horizon.

**7. Walk-lag removal** (`9ddfe8c6` WALK arm; doctrine = the faller reprices every receipt to its running
evidence low). Mechanics: analytic — the walk was *granted* an instant fill at the evidence low (favorable),
adverse tail then marked to close. **PARTIAL — ANALYTIC, ERROR FAVORING THE INSTRUMENT** (it lost even when
favored, so the decline likely survives). Faithful: an executable per-receipt reprice replay.

**8. Transient tombstone** (`cca7c6c1` P4; doctrine = the 336-class signature announces an imminent transient
dip). Mechanics: during the signature, held at the **running past excursion low** — a historical level — rather
than repricing toward the announced imminent one. **PARTIAL — PAST LOW FOR ANNOUNCED LEVEL**. Faithful: at
signature onset, reprice to current ask−1 for the signature's duration, trades-as-truth scored.

**9. V44 dry-sibling** (`480b1ee1`, BLOCKED; doctrine = my Dial B `b503e4ed`: +417¢ true book, naked fixed).
The machine's mechanics were **FAITHFUL** (decision-time withhold, causal lift) — **the substitution was in MY
analytic**: Dial B withheld fills **only on games that ended naked — ex-post conditioning no causal machine can
implement**. V44's causal version withheld first fills in games that later completed (flow never returned) and
destroyed 20 pairs. Verdict on the graveyard entry: **TEST FAITHFUL / SUPPORTING ANALYTIC SUBSTITUTED (mine)**.
Faithful reopen: maturity-conditioned withhold — only after the sibling has had N hours of two-sided book and
still shows no flow within 3¢ of a lawful level.

**10. V46 gap-credit** (`1b1b6a65`, BLOCKED; doctrine = my footprint `aa884cc5`: pair-gated gap-credit +121¢).
The machine's gate (reprice only after the sibling is credited) is the **only causal reading of "pair-gated"**
and it is nearly empty (5 walks, 0 fills) — because in 39 of my 50, the pair completed *because of* the
unfrozen fill, not before it. **TEST FAITHFUL / SUPPORTING ANALYTIC SUBSTITUTED (mine — ex-post
pair-conditioning)**. Faithful reopen: **ungated** gap-credit with the 11 naked knives priced to close, two
columns — the honest net may still be positive.

**11. V49 evidenced-standing** (`1c8700fa`, BLOCKED; doctrine = standability v2 `fe4747cd`: a rest may lawfully
stand **AT** the evidenced level P during the ask>P window). Mechanics: added evidence *tracking* but **kept the
bid−1 placement offset** — the dominant non-convert reason in the 81 ledger is literally
`BID_MINUS_ONE_OFFSET_AT_P`, and `EVIDENCE_CEILING_ABOVE_P` blocked standing where the evidence min sat above P.
**SUBSTITUTED — P−1 OFFSET RETAINED WHERE THE DOCTRINE SAYS STAND AT P**. Faithful: join semantics at exactly P
(no −1) whenever evidence exists and best ask > P.

**12. Mirror × divot fusion** (`63f5ece9`; KNOWN; doctrine = the vaulted riser placement for the trusted
inverse). Mechanics: rested at the **deepest trailing trough** — a level a vindicated *rising* sibling by
construction never revisits — instead of the at-bid persistence join. **SUBSTITUTED — DEEP TRAILING TROUGH FOR
AT-BID JOIN**. Faithful: collapses into #4's test (full riser stack from the trust moment).

## The reopen list — ranked by the original claim's value

| # | instrument | original claim | the faithful test |
|--:|---|---|---|
| 1 | **V49 evidenced-standing** | +81 games / the ~477 lawful ceiling (`fe4747cd`) | V49b: stand **AT** P (join semantics, no −1) when evidence exists and ask > P |
| 2 | **dry-sibling doctrine** | naked book fixed (+417¢ analytic) | V44b: maturity-conditioned withhold (dry after N h of two-sided book) |
| 3 | **LAW B mirror + fusion** | the 240-game one-eyed class, 71-91% vindication | full V47 riser stack on the sibling from the trust moment |
| 4 | **the read organ** | L2 = top machine-side breaker | re-judge all reads vs forward 30-60 min truth, not terminal labels |
| 5 | **V38 pulse floor** | the riser divot doctrine itself | session-scale recurrence floor (census params, no trailing horizon) |
| 6 | **gap-credit ungated** | +121¢ locked minus knife cost | V46b: ungated, knives marked to close, two columns |
| 7 | **k-depth curve** | the depth-value curve | re-run under trades-as-truth crediting |
| 8 | **wide-spread anchor** | the VRB transient-wide class | per-moment spread gate at the divot |
| 9 | **transient tombstone** | the 336-signature's cents | reprice to announced level at signature onset |
| 10 | **walk-lag** | faller reprice cents | executable replay (low priority — failed even when favored) |

## Conservation

12 graveyard entries, one verdict each: **FAITHFUL 1** (dual-rest) · **SUBSTITUTED 7** (V38 pulse-floor,
wide-spread anchor, k-depth, LAW B, classifier labels, V49, divot fusion) · **PARTIAL 2** (walk-lag, transient
tombstone) · **TEST-FAITHFUL-WITH-SUBSTITUTED-ANALYTIC 2** (V44, V46 — the substitution was in this seat's own
supporting analytics, stated plainly). Reopen list ranked 1-10; dual-rest stays dead. Cites: 2c54d724,
57583640, d40bc010, e177c2fb, d34fc6ce, fdeb7516, 9ddfe8c6, cca7c6c1, 480b1ee1, 1b1b6a65, 1c8700fa, 63f5ece9,
b503e4ed, aa884cc5, fe4747cd, d1ac9497, 6b28b4af, 084df125.
