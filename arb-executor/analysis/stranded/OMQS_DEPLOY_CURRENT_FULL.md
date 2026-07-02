# OMQS — CURRENT DEPLOYMENT: FULL GRADE (standing report card) — updated 2026-07-02

**The box:** Jun 30 15:46 ET bisect (`2b23b5d`) → now. **Config unchanged across the whole window** — `git log 2b23b5d..HEAD -- config/` is EMPTY (last config commit = the bisect itself, 15:42). Spans the Jul-01 04:03 disk-crash outage + respawn (PID 501822). **Boot flags:** `MAKER_ONLY_ENTRY=true` → `miss_fallback = CANCEL-no-replace` · `marketable_taker GATED` · `t20m_fallback GATED (fallback_maker_clamp=on)`; bisect flags OFF (`liquid_repost`/`grace_kill`/`sustained_flow`); `pair_governor` OFF. Read-only. Re-runnable as the slate adds trades (`grade_current.py`).

## Report card (74 events, 133 legs)
| rubric | result |
|---|---|
| ① **completion** | **27%** — BOTH 20 · ONE-sided 31 · MISSED-both 23 |
| ② **combined (BOTH-filled)** | **<100: 14** (of which **≤97: 4**) · ≥100: 6 · dist min 80 / **med 99** / max 101 |
| ③ **best-fillable gap** (achieved − tape level that traded w/ size) | **75% of legs overpaid** (30/40), median **+3¢**, worst **+49¢** |
| miss classes | **PULLED 12** · NEVER_LAID 6 · TOO_DEEP 3 |
| **realized P&L** (23 settled legs; rest pending) | **−$11.05** so far |

Par-bound and bleeding, as prior boxes: completions cluster at 99 (only 4/20 clear ≤97), and three-quarters of fills are worse than a size-backed level that actually traded.

## Mechanism rollup — dollar-weighted, ranked (what to change)
| mechanism | pairs touched | realized $ on them | change implied |
|---|--:|--:|---|
| **walk (`v4_move_repost`)** | **38** | −$6.85 | **THE completion engine — 15/20 both-fills (75%) involved a walk** (combined med 99). Bid-walk is exactly the ingredient the no-walk shadows (P4 0% / P4b 2-6%) lacked → **test walk, do NOT close ITF/pairs on the static result.** |
| `v4_t20m_fallback` | 25 | −$6.85 | stale-schedule cancel footprint. Under `CANCEL-no-replace` it re-posts via the walk (BOUHAR survived it) but strands where the re-lay is then blocked → **gate cancels on true match-start.** |
| `itf_recent_volume_floor` | 29 | −$4.40 | blocks posting windows → drives MISSED-both; **loosen where postability evidence shows a book existed.** |
| `maker_only_no_late_entry` | 1 | −$3.65 | the re-lay block (NASCHA-class). Small footprint, but kills a completable pair per event → **allow late re-lay when a bid was already worked.** |
| `completion_ceiling` (completion_fill) | 0 | $0 | inactive in this box. |

**Headline for change decisions:** the **walk carries completions** (75%), the **t20m/match_live cancel chain and the volume-floor block them**, and **entry targets sit ~3¢ (up to 49¢) below the fillable level** yet still overpay. The two highest-leverage moves: (1) preserve/extend the walk; (2) stop the stale-clock cancels (t20m + match_live) from pulling worked bids.

## Exhibit — BOUHAR (the win, completed at 98 <100)
`KXITFMATCH-26JUL01BOUHAR` (ITF_M). Both legs filled, combined **57 + 41 = 98** (locked pair; settlement pending).
- **HAR (dog/faller, 41):** post 41 @21:05 → t20m cancel @22:41 → **re-post 41** → **FILL 41 @23:32.** best-fillable 36 (overpaid +5¢).
- **BOU (riser, 56→57):** post 56 @21:30 → **walk 56→57 @22:31** → t20m cancel @22:41 → re-post 57 → **FILL 57 @00:23.** best-fillable 56 (overpaid +1¢).
- **Sequence: faller (HAR 41) filled first (23:32), riser (BOU 57) filled last (00:23)** — the walk chased the riser up 56→57 and held it through the t20m cancel to the fill. **The walk + hold-through-t20m is what made this pair complete.**

## Exhibit — NASCHA (the miss, 41→56, forfeited a ~100 completion)
`KXITFMATCH-26JUL01NASCHA` (ITF_M). ONE-sided: CHA filled, NAS pulled.
- **CHA (57→59):** post 57 @20:30 → walk 57→59 → t20m cancel @21:41 → re-post 59 → **FILL 59 @22:09.** best-fillable 52 (overpaid +7¢).
- **NAS (41, the faller):** post 41 @19:53 → t20m cancel @21:41 → re-post 41 → **`match_live_cancel` @23:14 — NEVER FILLED.** best-fillable 39; NAS traded 41-44 then ran to 56.
- **Miss = PULLED:** `match_live_cancel` pulled the NAS 41 bid at 23:14 while NAS was at/near our level (fillable 39-44), then it ran to 56. Had NAS held, the pair completes at **CHA 59 + NAS 41 = 100** (par). **Forfeited combined ≈ 100** — the stale-clock cancel chain killed a completable pair, the exact PULLED pattern.

Method: `grade_current.py` → `/root/shadow_p4/grade_current.json`. Re-run appends new trades; settlements refresh as legs settle (23/133 so far → realized will grow).
