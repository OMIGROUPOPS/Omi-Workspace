# OMQS — P4: ITF-SIMULTANEOUS SHADOW (schema validated; replay refutes the static spec) 2026-07-02

**Architecture (as ruled):** `shadow_itf.py` is a **standalone pure observer** — reads the L1 tape + borrowed cell targets, applies the policy, logs would-post/would-fill to `/root/shadow_p4/shadow_itf_log.jsonl`. **NO Kalshi client, NO auth, NO order path, NO write to the repo, does NOT touch `live_v4.py` / the bot (PID 501822).** Disk-guarded (self-exits ≥95%).

**Spec implemented:** ITF-only; window = re-anchored W1 (ONSET-Q per P3a) clamped to T-4h; **simultaneous resting posts, both legs at cell targets** = ITF-borrow (ATP_CHALL `per_regime_offsets_v2`, `target_bid = current_ask − offset`, matching `v4_place`); postability gate before every post (two-sided + combined spread ≤6¢ + depth≥1); bucket-partitioned T-4h→T-2h vs T-2h→T-0. Fill = a trade prints ≤ target OR the ask descends ≤ target after post; current-box counterfactual cancels at T-20m.

## Schema VALIDATED — the 7 logs emit correctly
Replay on the 26JUL01 ITF slate (318 paired events; 108 posted; `shadow_itf_log.jsonl` = 318 lines). All 7 logs populate: (1) post ts/duration/fill-or-timeout/side/bucket; (2) achieved-combined per completion; (3) bucket rates; (4) counterfactual; (5) gate fire/skip; (6) fills/day hook; (7) strand rate.

## Replay result — the STATIC-SIMULTANEOUS SPEC REFUTES ITSELF on ITF
| bucket | posts | **complete** | ≤97 | strand |
|---|--:|--:|--:|--:|
| T-4h→T-2h | 92 | **0 (0%)** | 0 | 19 (21%) |
| T-2h→T-0 | 16 | **0 (0%)** | 0 | 3 (19%) |

- **Both-leg completion ≈ 0%** despite the postability gate firing 18,646× and P3b's ≤97 combined being *quotable* 90% of the time.
- **Single-leg strand = 20% (22/108).** One leg fills; the inverse leg does not — **the seesaw defeats simultaneous static posting**, exactly as §0A doctrine predicts. When leg A's ask descends to our bid (fill), leg B's ask *rises* (never fills).
- **Counterfactual (PRIMARY): shadow 0% vs current-box 0%, DELTA +0pp** — the static simultaneous policy does not beat the current box here.
- Strand 20% is below the M-α1 NEVER_LAID baseline (~53%), so it does **not** trip the early-kill — but the 0% completion is the damning number.

## ⚠ Caveat — static (no bid-walk), faithful to "original Build-1 spec"
The shadow posts once and holds (no `v4_move_repost` walk), matching the dispatch's "original Build-1 spec." **The live bot WALKS and fills more.** So 0% is the *static-simultaneous* result, not a walk-augmented one. This is a genuine finding about the **spec as written** (static simultaneous fails on ITF via the seesaw), not proof that no ITF policy works.

## Recommendation — clock-start decision to Plex (NOT started)
The replay already refutes the licensed static spec (0% completion), and **disk is at 92%** (the unbounded `tennis.db` again). Rather than commit a 48h clock + disk to a policy the replay nulls, the schema is validated and the finding is surfaced. **Plex to decide:** (a) start the 48h clock anyway to confirm live; (b) add bid-walk to the policy first (then it's no longer "static simultaneous"); or (c) reconsider — the seesaw may mean neither sequential (P2: ITF touch diverges) nor static-simultaneous (P4: 0% completion) works on ITF, and the ITF opportunity is a **paper opportunity** (quotable ≤97, unfillable both-leg). P4-PARALLEL (T-8h→T-4h) deferred until this is resolved (extending the window is premature when the peak-window static policy replays to 0%).

Method: `shadow_itf.py` (`--replay` / `--live` disk-guarded). Log `/root/shadow_p4/shadow_itf_log.jsonl` (not committed; grows on live).
