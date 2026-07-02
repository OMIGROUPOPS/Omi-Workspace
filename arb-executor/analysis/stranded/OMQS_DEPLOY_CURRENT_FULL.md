# OMQS — CURRENT DEPLOYMENT: FULL GRADE (standing report card) — refreshed 2026-07-02 (post-overnight slate)

**The box:** Jun 30 15:46 ET bisect (`2b23b5d`) → now. **Config unchanged across the whole window** — `git log 2b23b5d..HEAD -- config/` is EMPTY (last config commit = the bisect itself, 15:42). Spans the Jul-01 04:03 disk-crash outage + respawn (PID 501822, still the live process). **Boot flags:** `MAKER_ONLY_ENTRY=true` → `miss_fallback = CANCEL-no-replace` · `marketable_taker GATED` · `t20m_fallback GATED (fallback_maker_clamp=on)`; bisect flags OFF (`liquid_repost`/`grace_kill`/`sustained_flow`); `pair_governor` OFF. Read-only. Re-run as the slate grows (`grade_current.py`). **This refresh adds the full Jul-01→Jul-02 overnight slate.**

## Report card — **122 events, 233 legs** (was 74 / 133)
| rubric | result | prior card |
|---|---|---|
| ① **completion** | **48%** — BOTH 58 · ONE-sided 38 · MISSED-both 26 | 27% |
| ② **combined (BOTH-filled)** | **<100: 27** (of which **≤97: 6**) · **≥100: 31** · dist min 80 / **med 100** / max 108 | <100:14 (≤97:4) · med 99 |
| ③ **best-fillable gap** | med **+9¢** · overpaid 100/116 · worst +79¢ — **⚠ inflated by low-print tape artifacts (see caveat)** | med +3¢ |
| miss classes | **PULLED 20** · NEVER_LAID 9 · TOO_DEEP 1 | PULLED 12 · NL 6 · TD 3 |
| **realized P&L** (64 settled legs; rest pending) | **−$55.10** | −$11.05 (23 legs) |

### The overnight signal (headline)
Completion nearly **doubled** (27→48%), but the incremental completions landed **at/over par**: median combined moved **99 → 100**, and **31 of 58 both-fills are now ≥100** (zero/negative locked edge) vs 27 under 100. Realized P&L fell **−$11 → −$55** as the slate settled. **More volume, worse quality** — the "par-bound and bleeding" thesis amplified. The walk still carries completions (**41/58 = 71% involved a walk**) but now drags their combined to **par (med 100)**, not sub-par. This is exactly the defect a **97-combined cap** targets (→ P6).

### Caveat on ③ (fill-quality gap)
Several `best_fillable` reads are implausibly low (NASCHA CHA=5 / NAS=7; BOUHAR BOU=44) — the known depth-recorder `last`/size artifact. The +9¢/+79¢ magnitude is corrupted by those low prints; the **trustworthy** degradation signals are ①②④ (completion up, combined up to par, P&L down), **not** the gap magnitude. Do not act on +9¢ as a calibrated number.

## Mechanism rollup — dollar-weighted, ranked
| mechanism | pairs touched | realized $ on them | change implied |
|---|--:|--:|---|
| **walk (`v4_move_repost`)** | **67** | −$35.00 | **THE completion engine — 41/58 both-fills (71%) involved a walk** (combined med **100**). Bid-walk carries completions but to **par**; the 97-cap is meant to keep the walk while forcing sub-par locks. |
| `v4_t20m_fallback` | 53 | −$29.60 | stale-schedule cancel footprint; re-posts via the walk but strands where the re-lay is blocked → **gate cancels on true match-start.** |
| `itf_recent_volume_floor` | 32 | −$18.00 | blocks posting windows → drives MISSED-both; **loosen where postability evidence shows a book existed.** |
| `maker_only_no_late_entry` | 2 | −$3.65 | the re-lay block (NASCHA-class); kills a completable pair per event → **allow late re-lay when a bid was already worked.** |
| `completion_ceiling` (completion_fill) | 0 | $0 | still inactive in this box (armed d2ac207 but no `completion_fill` fired yet). |

**Headline for change decisions:** the **walk carries completions (71%)** but at **par (combined med 100)** — the incremental overnight volume added **no locked edge** and **−$44** more realized loss. The two highest-leverage moves unchanged: (1) preserve the walk but **cap its combined** (P6); (2) stop the stale-clock cancels (t20m + match_live) from pulling worked bids (PULLED = 20, the largest miss class).

## Exhibit — BOUHAR (the sub-100 win, combined 98)
`KXITFMATCH-26JUL01BOUHAR` (ITF_M). Both legs filled, **BOU 57 + HAR 41 = 98** (<100, locked; settlement pending).
- **HAR (dog/faller, 41):** post 41 @21:05 → t20m cancel @22:41 → re-post 41 → **FILL 41 @23:32.**
- **BOU (riser, 56→57):** post 56 @21:30 → **walk 56→57 @22:31** → t20m cancel @22:41 → re-post 57 → **FILL 57 @00:23.**
- The **walk chased the riser 56→57 and held it through the t20m cancel to the fill** — the walk + hold-through-t20m is what made this pair complete sub-100.

## Exhibit — NASCHA (the miss, forfeited a ~100 completion)
`KXITFMATCH-26JUL01NASCHA` (ITF_M). ONE-sided: CHA filled, NAS pulled.
- **CHA (57→59):** post 57 @20:30 → walk 57→59 → t20m cancel @21:41 → re-post 59 → **FILL 59 @22:09.**
- **NAS (41, the faller):** post 41 @19:53 → t20m cancel @21:41 → re-post 41 → **`match_live_cancel` @23:14 — NEVER FILLED.**
- **Miss = PULLED:** `match_live_cancel` pulled the NAS 41 bid at 23:14; had NAS held, the pair completes at **CHA 59 + NAS 41 = 100** (par). The stale-clock cancel chain killed a completable pair — the PULLED pattern (now 20 of the box's misses).

Method: `grade_current.py` → `/root/shadow_p4/grade_current.json`. Re-run appends new trades; settlements refresh as legs settle (64/233 legs settled so far → realized will grow).
