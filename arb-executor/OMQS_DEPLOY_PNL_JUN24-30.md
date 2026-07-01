# OMQS — PER-DEPLOYMENT P&L, boxed by config live AT ENTRY (SS4C arm/disarm boundaries)

Every settled leg boxed by which flag-config was live at its ENTRY (first buy-yes fill) time -- NOT settled-date, NOT calendar day. Boundaries = the SS4C arm/disarm timestamps. Net = payout-cost-fee per leg (Kalshi settlement). n=836 settled legs entered Jun24-30, total net **$-155.17**, total gross-loss $-1061.34. Read-only.

## Per-deploy-window
| window | n | **net $** | gross $ | win% | $/day | loss $ | % of all loss |
|---|--:|--:|--:|--:|--:|--:|--:|
| W1 pre-green tail (Jun24-25) | 187 | **-102.35** | -72.00 | 65% | $-51.2 | -602.81 | 57% |
| W2 GREEN six-pack (Jun26-28) | 209 | **-51.31** | -43.27 | 81% | $-16.1 | -149.19 | 14% |
| W3 Jun29 AM +liquid_repost 04:31 | 192 | **+10.43** | +13.48 | 80% | $+24.1 | -77.44 | 7% |
| W4 Jun29 mid +grace_kill/sustained * | 21 | **+4.85** | +9.22 | 81% | $+13.7 | -118.50 | 11% |
| W5 Jun29 night pair_gov DISARM 23:24 * | 7 | **+3.50** | +3.50 | 100% | (1.5h) | +0.00 | -0% |
| W6 Jun30 +completion_ceiling 00:56 | 209 | **-19.41** | -16.09 | 77% | $-31.4 | -108.23 | 10% |
| W7 Jun30 BISECT flip 15:46 (3 flags OFF) * | 11 | **-0.87** | -0.87 | 73% | $-2.5 | -5.17 | 0% |

(* n<40 = thin window, $/day and net are high-variance; robust windows are W1/W2/W3/W6 with n~190-210.)

## GREEN vs after
- GREEN (Jun26-28), boxed by entry: net **$-51.31 over 3.19d = $-16.1/day** (win 81%). **It did NOT earn.**
- POST-GREEN (all Jun29-30 windows): net $-1.50 over 1.82d = $-0.8/day (n=440).

## VERDICT -- the premise is overturned
**Boxed by the config live at ENTRY, GREEN (Jun26-28) LOST $16.1/day (net -$51.31, 81%% win).** The belief that "green earned" is a SETTLED-DATE illusion: the profitable cash that landed Jun26-28 was PRE-green entries settling (green-entered legs mostly settled later and lost). By entry-config the bleed is continuous and FUCKUP-3-shaped everywhere (high win-rate 65-81%%, but the -bid losers outweigh the +band winners).

**No arm/disarm flipped us from earning to bleeding, because no large window was ever robustly earning -- EXCEPT the one the earlier hypothesis blamed:**
- WORST: W1 pre-green tail (Jun24-25) -$51.2/day, 57%% of all loss -- the bleed was already largest BEFORE green.
- W2 GREEN: -$16.1/day (losing, just less).
- **W3 Jun29-AM (+liquid_repost) = the BEST config: +$24.1/day (net +$10.43, n=192).** The flag suspected of "breaking Monday" was in fact the single best-performing window.
- W4 Jun29-midday (+grace_kill/sustained): +$13.7/day (thin-ish n=21, noisy).
- **W6 Jun30 (+completion_ceiling): -$31.4/day (net -$19.41, n=209) -- the recent bleed window.** If any boundary marks a turn back to bleeding, it is the completion_ceiling arm (Jun30 00:56), NOT any Jun29 flag.
- W7 Jun30 bisect (3 Monday flags OFF): n=11 only -- too thin to judge; the cohort is still settling.

**Bottom line:** green never earned (settlement-timing illusion); the bleed is continuous FUCKUP-3; liquid_repost (Jun29-AM) was the best config, not the culprit; the completion_ceiling window is the recent bleed. The lever is not a flag rollback -- it is the exit-geometry / naked-favorite loss the win-rate hides.