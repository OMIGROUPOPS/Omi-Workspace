# OMQS LIVE FORENSIC — KXITFWMATCH-26JUL01HUIAHN (Hui vs Ahn, W15 San Diego ITF)

**Live test of the M-α1 conclusion.** We hold **AHN only** (favorite), naked, at a bad price. Hui (dog) sat low-30s premarket with real dip flow; we never filled it. Read-only, from today's log + tape.

**Verdict up front:** Hui IS effectively **NEVER-LAID at divot time** — confirmed live, the M-α1 signature. **But this is a DOUBLE failure, and always-lay-both alone would NOT have rescued it:** even catching Hui at its dip, the pair combines to **104¢ > par** because the AHN leg was overpaid (73¢ when it traded 41-54¢). This event validates M-α1's NEVER-LAID finding *and* its caveat (only 41% of completions clear ≤97; an overpaid favorite dooms the combined).

## (1) Order timeline — both legs (discrete)
| ts ET | leg | event | detail |
|---|---|---|---|
| 14:32–15:20 | BOTH | **skipped ×~90** | `reason=itf_recent_volume_floor` (ITF volume gate blocked all posting ~48 min) |
| 15:20:35 | HUI | v4_place + order_placed | **bid 24** (cell 24, resting_maker, ask 27, runway=late_window) |
| 15:24:56 | HUI | cancel→repost | 24→**25** (move_repost, ask 27) |
| 15:30:48 | AHN | v4_place + order_placed | **bid 72** (cell 75, ask 76, runway=sub_60) |
| 15:31:40 | AHN | cancel→repost | 72→**73** (join_queue) |
| 15:42:44 | HUI | cancel→repost | 25→**26** (engagement_join, ask 30) |
| 16:07:42 | HUI | cancel→repost | 26→**27** (engagement_join, ask 32) |
| **16:09:50** | **AHN** | **entry_filled** | **fill 73¢, qty 5, v4_resting_maker (MAKER), executed** → exit posted @91 |
| 16:10:12 | HUI | **order_cancelled** | **`label=v4_t20m_fallback`** → churn: repost 31, cancel `v4_move_repost`, repost 25, cancel **`no_fallback_fat_spread`** |
| 16:10:13→16:15 | HUI | **skipped ×many** | **`reason=maker_only_no_late_entry`** → **Hui bid NEVER re-laid** |

**Where was our Hui bid?** Resting at **24→25→26→27¢** from 15:20 to 16:10, then **cancelled at 16:10:12 (v4_t20m_fallback) and never re-posted.** Scheduled start was ~T-20m before 16:10 (~4:30 PM); the **real match went live ~17:53 (5:53 PM)** — so the t20m cancel killed the bid **~1.7 h before the real start**, and `maker_only_no_late_entry` blocked every re-lay after.

## (2) The Hui miss — classified (M-α1 classes)
The dog's `taker_side=no` prints at/near our level, premarket→live:
| ts ET | px | ct | our Hui bid | class |
|---|--:|--:|--:|---|
| 17:44:03 | 32 | 1 | none | NEVER_LAID |
| 17:50:31 | 31 | 15 | none | PULLED (we'd had a 31 bid, cancelled 16:10) |
| 17:53:18 | 33 | 0 | none | NEVER_LAID |
| 17:54:23 | 32/33 | 250/172/100/78/22 | none | NEVER_LAID *(≈ match-live ramp, in-play)* |
| 17:55:10 | 34 | 31 | none | NEVER_LAID |

**Class: 9 NEVER_LAID + 1 PULLED.** But two honest caveats:
- **We were also TOO DEEP:** our actual resting bids were **24-27¢** while the dog's flow traded **31-34¢** — a resting 27 bid would not have caught a 31-34 sell anyway. The fix isn't just "lay" — it's **lay at the right level (join 31) and don't cancel.**
- **ITF thinness / catchable size:** the genuinely-premarket catchable size at a proper bid was **thin** — ~15 contracts at 31¢ (17:50). The big prints (250+172+100 at 17:54) are **at/after the 17:53 match-live ramp = in-play, not maker-catchable premarket.** So the "719 contracts ≤35¢" headline is inflated by in-play ramp; the real premarket maker-catchable dog flow was small.

## (3) The Ahn fill vs tape
- **Filled 73¢** @ 16:09:50, MAKER (`v4_resting_maker`, executed), qty 5.
- Tape at fill: **bid_1 72 (250) / ask_1 76 (32) / last_trade 73**.
- **AHN premarket trade range: 41–80¢** (first 76, last 54, n=365). We filled at **73 — near the top of the window**; AHN was available in the **41-54¢** zone earlier. **Overpaid ~19-32¢** vs the window (the classic "fill the favorite high" bleed).

## (4) Pair math
- **AHN actual fill 73¢** (held naked) + **best catchable HUI divot 31¢** = **combined 104¢ → OVER 100.**
- Even a perfect Hui catch gives a **locked-loss pair** — the AHN overpay alone busts par. There was **no achievable ≤97 (or ≤100) completion** on this pair given the 73¢ AHN fill.
- **Actual:** one leg (AHN 73¢) naked, Hui never filled — the worst branch.

## (5) Config flags that governed it
`itf_recent_volume_floor` (blocked posting 48 min) → **`v4_t20m_fallback`** (cancelled the Hui bid ~1.7 h early on the stale scheduled clock) → **`MAKER_ONLY_ENTRY=true` / miss_fallback = CANCEL-no-replace** → **`maker_only_no_late_entry`** (blocked every re-lay) → `no_fallback_fat_spread`. This is the **stale-schedule cancel + no-re-lay chain** — the same mechanism behind the stranded-winner bleed (Vault §6 / cancel-timing), now live.

## Tie to M-α1
- **NEVER-LAID confirmed live** — at divot time we had no Hui bid, exactly the +$26 M-α1 class. **The always-lay lever failed again in real time.**
- **BUT the exhibit is weaker than it looks:** (a) our bids were *too deep* (24-27 vs 31-34), (b) premarket maker-catchable size was *thin*, (c) the pair was *combined-doomed at 104* by the overpaid AHN. So **always-lay-both alone would not have saved this pair** — it needed lay-at-the-right-price **and** a cheaper AHN. This is precisely M-α1's caveat that the fix *stanches* the bleed (only 41% clear ≤97) rather than turning it +EV.

Method: `forensic_huiahn.py`. Note: AHN still open at forensic time (unrealized ROI −$1.20 per operator).
