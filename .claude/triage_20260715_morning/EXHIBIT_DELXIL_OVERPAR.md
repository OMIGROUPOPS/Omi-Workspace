# EXHIBIT — DELXIL over-par fork (C-MORNING-TRIAGE Part 3, 07-15)

## PRIOR ART (C45)
- C-COMPLETION-POLICY v1 + the taker word (07-12): completion verdicts ACT; taker cross = IOC at ask; the C-BOUND remainder CEILING (97−basis) retained for MAKER completion pricing (operator adjudication 07-05). Delta exhibited here: **the taker branch crosses at ask with no combined ceiling — over-par completions are reachable and one occurred.**
- RULING_COMBINED_PRICE_CLAUSE: no fixed-line rate headlines without the dynamic-floor gap — this exhibit prices the fork per branch.

## THE TAPE (KXATPCHALLENGERMATCH-26JUL14DELXIL, exchange-reconciled)
- 07-14 4:30 AM: pair conceived (DEL 82→83, XIL 15→16→17, trades T-20260714-0386/0387).
- XIL filled 5@17 in THREE tranches: 2.00 (9:14:39 AM), 0.21 (10:18:48), 2.79 (12:31:57 PM) — **fractional fills, the dup-storm int-floor class on the tape again**; exits 22×2 + 22×3 posted. DEL's 80 bid match_live-cancelled 1:22 PM.
- In-play, DEL (the leader) pulled ahead; XIL's 22 exit unreachable.
- **07-15 12:45:38 AM — THE FORK: `completion_action` verdict `taker_complete`, IOC buy DEL 5@85 (taker, fee $0.0447, order `d673d0a2`), kept_basis 17, ev −1.52¢ → combined pair cost 17+85 = 102 — OVER PAR.** Exit 98×5 posted 12:46:10 (order `1cc90e51`).
- DEL exit filled 5@98 (8:19 AM, maker, fee 0) → +65¢. XIL settled LOSS −85¢ (12:26 PM settle).
- **Pair net: −20¢ − $0.045 fees ≈ −24.5¢.**

## THE FORK, PRICED (at 12:45 AM, XIL 5@17 held, DEL ask 85, XIL bid ~13)
| branch | mechanics | locked/expected outcome | realized |
|---|---|---|---|
| **A — taker-complete at 85 (TAKEN)** | combined 102 > 100: certain loss if both ride (−10¢); DEL exit 98 adds +13¢ over settle if filled pre-close but sacrifices nothing (DEL won) — realized −20¢ + fees | loss LOCKED in [−10, −20]¢ band, tail risk dead | **−24.5¢** |
| B — hold XIL naked | XIL wins +415¢ (P small, DEL was ahead in-play) / XIL loses −85¢ | E ≈ −60¢ at P(XIL)≈0.05 | (counterfactual −85¢: XIL lost) |
| C — flatten XIL at bid (~13) | sell 5@13 → −20¢ realized immediately, no completion | −20¢ certain | ≈ same as A without the DEL leg's fee/velocity |
| D — maker-complete at ceiling 80 (97−17) | C-BOUND-lawful price; may never fill (DEL traded 85+) | unfilled → collapses to branch B | — |

## THE READING
1. **The taker cross beat the naked ride** (−24.5 vs −85 realized; −60 expected) — the completion engine's verdict was EV-correct against branch B.
2. **But the cross was OVER PAR — and the 97 combined ceiling does not bind the taker branch.** The maker completion path prices at 97−basis by law; the IOC cross paid 102. Branch C (flatten the kept leg) priced the SAME realized loss without breaching par. On this tape A≈C economically; the doctrine question is whether a taker completion may ever pay above the pair cap when a flatten at bid prices the same escape.
3. **DOCTRINE GAP NAMED (census intake): TAKER-COMPLETE has no combined-price clause.** Instance: DELXIL 07-15 12:45 AM, combined 102, ev −1.52 accepted. Remedy shapes for the operator's word (not armed): (i) cap taker cross at 100−basis−fee (never over par); (ii) require taker_complete EV to beat the flatten-at-bid branch, not just the ride; (iii) leave as-is, billed nightly. The completion engine already prints both branches' EV — the gate is one comparison.

## SIDE FACTS FILED
- Fractional-fill class instance (0.21 + 2.79 tranches) — the int-floor fractionals thread from the 07-07 dup-buy storm remains open.
- The 12:45 AM completion executed during W2 on a stale-dated event (26JUL14 ticker completing past midnight) — completions are deliberately exempt from the new discovery floor (pair law: never strand a filled leg); this exhibit is why the exemption is correct: the cross killed an −85 tail.
