# The decision web — the machine as it actually runs, in human language [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. Sources: **the V52b gate code** (`98d07986`:
`window1_v52b_read_level_authority.js` → `window1_v52_judgment_gate.js` → `window1_v52_stability_onset.js`,
wrapping frozen V49b) and **V52B_FULL_DECISION_TRACE_30_GAMES** (`98d07986`; 613,394 receipts / 30 games).
Frequencies are live medians from the traces, not theory. No invented structure: every node is a question the
code asks; code values that never fired in the cohort are flagged `observed_0`. Machine-readable web (nodes +
edges) for the render seat: `DECISION_WEB.json`.

Per game, per receipt, the machine walks eight questions. Median 3,868 receipts per game.

## N1 — "Is this market awake yet?" (stability onset, clause ①; binding CODEX-INTERIM)

It looks at three things, each minute of the whole window: **the gap between best bid and best ask** (live
book, `spread`), **the two legs' mid-prices summed against 100** (both books, `midsum_abs_dev`), and
**contracts sold in the trailing hour** (sold-contract record, `trades_60min`). Two wake-up candidates:
**A** — the spread collapsed *and* the pair's mid-sum settled (else rejected
`SPREAD_AND_MIDSUM_DID_NOT_BOTH_SETTLE`); **B** — sales arrived in sustained cadence (else
`TRADE_CADENCE_DID_NOT_INCREASE`). The earliest valid candidate is selected; each receipt then classifies
**awake / not-yet**. Feeds the diary (what counts as post-onset), the level bounds, the pair lows, and the
license's first check. Lived frequencies: selected-candidate A on 480,431 rows, B on 132,963; not-awake is
the named block on 324,360 rows; median 3,211.5 of a game's 3,868 receipts sit post-onset.

## N2 — "What do I believe this side is doing?" (machine read; 300 s trail)

It consults **new highs of the best bid / new lows of the best ask** (live book), **contracts sold by an
aggressive buyer or seller** (sold record), and **the depth balance of the book's two sides**. The read
classifies into **rising / falling / settled / no-reading-possible** — the last when no directional quote or
print evidence exists in the trail (`NO_DIRECTIONAL_QUOTE_OR_PRINT_EVIDENCE`). Evidence kinds observed:
NEW_HIGH_BID 326,835 · NEW_LOW_ASK 84,292 · BUYER_LIFT_PRINT 39,859 · SELLER_HIT_PRINT 3,287 ·
QUOTE_PATH_INTERNAL_CONFLICT 156 · none 158,965. States: RISING 419,450 · FALLING 136,899 · SETTLED 57,045.
**No-reading-possible covers 25.9% of all receipts — the read-starvation lens, live.** Feeds the level
authority and the license's second check.

## N3 — "What price does the diary remember?" (post-onset true-trade diary; reference under V52b)

It remembers **the cheapest contract sold on this side since the market woke** (own sold record) and **the
same for the other side** (sibling's sold record). Classifies: a remembered low exists (277,172 rows) / none
yet (336,222). Under V52b the diary is demoted to `RECORDED_REFERENCE_INPUT_NOT_SOLE_LEVEL_AUTHORITY` — it
feeds the pair-lows sum, not the level.

## N4 — "Where should my bid stand?" (level authority — iteration 1's read-level clause)

It consults **the level the old reflex machine proposes right now and which organ proposed it** (N8's
`placement.target_cents` + authority; only join V41_ / tracking V43_ organs are supported), **the cheapest
and dearest prices observed since waking** (the post-onset bounds), **the read's evidence receipts and
timestamps** (both must be post-onset and receipt-bound), and **the sanity rails** (below the ask, under the
pair cap). Four checks — supported authority · inside bounds · evidence post-onset · receipt-bound — and the
level classifies into **evidence-backed (143,968 rows)** or **abstain (469,426)**. `observed_0`: the two
level-side block reasons never surfaced as the named block in 30 games — an earlier clause always failed
first.

## N5 — "Do my two readings agree, and is the pair under par?" (coherence, clause ④)

It consults **the two remembered lows summed against 100** (`lows_under_par`: true 234,792 / false 378,602),
**the disagreement flag between the quote-path reading and the pressure reading** (`disagreement_firing`:
true 262,345 / false 351,049 → `disagreement_clear` true 374,203 / false 239,191), and **whether the other
side is already bought** (`sibling_credited` true 207,901). **DEGENERATE, marked honestly (screw #3): when
the readings disagree the machine's only answer is freeze** — a blanket HOLD on a hair-trigger flag that
fires on a median 680 receipts per game yet is the *named* block only 5,384 times, because earlier clauses
usually fail first. Adjudicate-not-freeze is queued.

## N6 — "May this bid exist right now?" (the license verdict; fixed first-failure order)

Order: awake → reading exists → pair under par → readings agree → level authority earned → level lawful.
Observed verdict vocabulary: **blocked-market-not-awake 324,360 · blocked-no-reading 144,168 ·
blocked-pair-not-under-par 25,587 · blocked-readings-disagree 5,384 · licensed 113,895** (= 113,471
licensed-hold + 424 post). `observed_0`: authority-not-earned, no-lawful-level, and the superseded V52
diary-path blocks. Caveat carried on the node: **first-failure ordering means these are frequencies of the
named block, not of clause truth.** Median blocked receipts per game: 3,351.5.

## N7 — "What do I do with the standing bid?" (action selection)

Consults the standing bid's level and the licensed target. Classifies: **PLACE_REST 47 · REPRICE_REST 377
(direction UP/DOWN) · HOLD_REST 612,970** (blocked holds 499,499 + licensed holds 113,471 + already-standing).
`observed_0`: the guard-cancel passthrough of a licensed rest (`INCUMBENT_LICENSED_REST_GUARD`) never
occurred. Median per game: hold 3,847.5 · place 2 · reprice 1 · post-verdicts 3.

## N8 — "What would the old reflex do?" (frozen V49b, consulted never obeyed pre-license)

The whole pre-gate machine runs underneath on every receipt and its proposal is an *input*, not an order:
join arming (V41 join + already-at-target: 417,636 rows), tracking placement (V43-C3 + already-at-target:
182,808), deep-gap withhold-new-rest (V43-C2: 12,737), stand-at-P (V49B: 213); incumbent actions PLACE
369,659 / HOLD 241,629 / REPRICE 2,106. Its guard and cancel intents pass through only after a licensed rest
exists. **Scavenger: specced OFF on all 613,394 rows** (`V52_SCAVENGER_SPECCED_OFF`).

## The edges

N1 → N3, N4, N5, N6 · N2 → N4, N6 · N3 → N5 · N8 → N4, N7 · N4 → N6, N7 · N5 → N6 · N6 → N7 → the book
(and the next receipt's standing-bid input). Full adjacency in the JSON.

## Conservation

613,394 trace rows / 30 games; every license field, block reason, and action kind appearing anywhere in the
traces maps to exactly one node's vocabulary (`gate_verdict`/`blocked_clause`/`reason` → N6+N7 · `final_action`
→ N7 · `incumbent_*` → N8 · `onset.*` → N1 · `read.*` → N2 · `diary.*` → N3 · `coherence.*` → N5 · `level.*` →
N4 · `scavenger` → N8). **Named gaps: none** — nothing in the traces is absent from the web; five code-present
values are flagged `observed_0`, listed per node. ANALYTICAL_ESTIMATE.
