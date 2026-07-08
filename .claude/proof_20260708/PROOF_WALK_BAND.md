# OUTCOME PROOF (C46, two-lane) — C-BAND-CLAMP-WALK (walk-chokepoint half of the [5,95) band law)

**Candidate SHA: `a5a64962`** (pre-cancel band guard on the projected walk landing price + non-corrupting failed-re-place aftermath in `_v4_move_repost`).

## Prior art (C45)
- **C-BAND-CLAMP `31c0f69f` (07-08 preflight)** — the placement-chokepoint half; PROOF_BAND_CLAMP.md anticipated the reconcile/repost loop ("the clamp is what makes the cancel stick") but not the walk's cancel-first ordering.
- **The 07-08 MORNING DOSSIER Part 1 side-answer (a)** — flagged "29/639 post-boot buys outside [5,95) via the walk/repost path, 1 filled @4¢ (HARMAI-HAR)" and routed it to BOARD as item 2. **This proof AMENDS that reading (flag, not smoothing):** the jsonl scan (`/root/walk_band_scan.py`, both log files) shows **all 29 out-of-band placements land in the 23:12→23:57 window — before the clamp boot**; HARMAI-HAR @4 was placed 23:53:09, filled 23:55, clamp live 23:57. **Since 23:57: ZERO out-of-band buy placements** (placement clamp airtight — every placement site flows through `place_order`). The live post-clamp class at the walk chokepoint is **starvation**, not placement.
- **C-CHURN-FIX `_projected_repost_price`** — the pre-cancel projection primitive this guard reuses (same caps + never-cross as the post-cancel path, silent).
- **C47-ENFORCE / `validate_resting_buys` (:8446)** — skips legs with `entry_order_id == ""`; the reason a starved leg is invisible to every healer.
- **C-OWNERSHIP / P0-RACE site 7** — the same function's established abort-before-place discipline; this guard extends it to abort-before-CANCEL.

## The convicted class (exchange + jsonl truth, post-clamp exhibits)
| leg | resting bid | walk event | result under old code |
|---|---|---|---|
| KXITFMATCH-26JUL07ICHOCH-OCH | 28¢ (resting, in-band) | 00:43:32 walk→4¢: cancel OK, place `band_refused` | leg starved; **phantom `entry_price=4` stamped, oid=""**; settled WIN 00:53 with qty 0 |
| KXITFMATCH-26JUL08PIAPIE-PIE | 8¢ (resting, in-band) | 02:34:40 walk→2¢: cancel OK, place `band_refused` | leg starved; phantom `entry_price=2`; process died 02:52 |
| (pre-clamp era, same path) | — | 23:12→23:57: 29 out-of-band walk/repost placements | **HARMAI-HAR @4 FILLED 23:55** (the dossier's exhibit) |

## LANE 1 — MECHANISM (deterministic replay vs the prior slate)
- **Replay of every `v4_move_repost` decision on the 07-07/07-08 tape under the guard:** the projection (`_projected_repost_price`) is computed from the same decision-time inputs the old path used; for the 2 post-clamp walk-origin `band_refused` events (out of 33 total on the overnight file — the other 31 were initial-placement refusals with no cancel, unaffected), the guard fires BEFORE the cancel → **ICHOCH-OCH keeps its 28¢ resting bid, PIAPIE-PIE keeps its 8¢ bid; no phantom basis, no oid="" state.** Pre-clamp era replay: all 29 out-of-band walk placements refuse pre-cancel → HARMAI-HAR's 4¢ bid never rests → the @4 fill cannot occur.
- **In-band walks byte-identical:** the guard is a pure pre-check (no await, no state); today's boot has 66 `v4_move_repost` events, **all in-band → projection passes through, zero behavior delta.** The projection reuses the exact caps/never-cross the post-cancel path applies (`_projected_repost_price`, C-CHURN-FIX's own parity primitive).
- **Residue closed, not just narrowed:** post-cancel lowering steps the projection can't see (`_express_target` join/improve, leg2 bound recheck — both LOWER-only) can still land out-of-band → `place_order` refuses → the NEW aftermath re-places at the just-cancelled price (known-good: it was resting seconds earlier) instead of stamping `entry_price=new_target` with oid="". Recovery failure logs `repost_place_failed{recovered:false}` — loud, truthful state, C47-visible.
- Construction verdict: **no walk can place outside [5,95) (either era), no walk can starve its own leg via cancel-then-refuse, no failure path stamps a phantom basis.** All other `place_order` failure classes at this site (buy_guard_api_fail, order_error) inherit the same non-corrupting aftermath.

## LANE 2 — SETTLEMENT P&L
$0 claimed (refusal-only guard + state-integrity aftermath). Flagged and NOT claimed: ICHOCH-OCH settled WIN at 100 eleven minutes after its 28¢ bid was destroyed — the counterfactual +$3.60 (5 sh × 72¢) is a LUCK-POLLUTED n=1 and is recorded here as an exhibit, not a claim.

**Verdict: enforcement of an already-ruled law (the operator's [5,95) band, PROOF_BAND_CLAMP economics) at the one chokepoint whose ORDERING evaded it. Deploys through the full gate; config untouched (week standing order defect exemption).**

## ADDENDUM (same day, 15:0x ET) — aftermath completion, candidate SHA `c31fe7f9`
First live occurrence of a FULL recovery failure found the aftermath's last gap: at 14:23 ET the **conception halt** (GEAZIN boot-audit FAIL window) blocked the walk re-place AND the recovery re-place → `repost_place_failed{recovered:false}` ×3 (REARAB-REA, MILMIS-MIL, LAUTOR-LAU), each leg left **tracked with oid=""** — the state every healer skips (validate_resting_buys :8487 guard; the sibling scan sees a tracked pos and stands down), and MILMIS-MIL is the HELD MIS leg's missing completion bid (pairing-law violation in effect). **Fix (`c31fe7f9`, one branch): on failed recovery, `_untombstone_entry` — unfilled legs freed (pos deleted + processed_events cleared → router re-conceives next pass, downstream of halt/horizon gates); partial fills keep their managed position. This is byte-identical to every other terminal-cancel teardown in the same function's family.** Lane 1: replay of the 14:23 window under the fix — all three legs free at 14:23, re-conceived on the first router pass after the 14:25:44 halt clear; zero delta on successful recoveries and all in-band walks. Lane 2: $0 claimed. The deploy restart itself heals the three currently-starved legs (boot reconcile drops empty tracked positions and re-conceives).

## Verification exhibits
- Scan: `/root/walk_band_scan.py` output over `live_v3_20260707.jsonl` + `live_v3_20260708.jsonl` (post-clamp out-of-band placements = 0; walk-origin starved band_refused = 2; today's boot: 0 and 0).
- Midday live-book verify (same boot, pre-deploy, 17:09Z): **PASS** — 45/45 held legs exit=qty exact, 0 stacks, 0 out-of-band resting buys; raw dumps `/root/midday_verify_20260708/`.
