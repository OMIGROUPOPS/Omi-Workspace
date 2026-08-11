# Read-organ forward-truth re-judgment — reopen #4

Analysis seat only. Read-only. Reopen #4 of the substitution audit (`bc0ce289`): V47's (`fb74c8b8`) state read
at **every action receipt** (1,208,014 candidates; 1.06M scored per horizon; 0 excluded for tape) judged against
**forward truth** — the leg's net mid move over the following 30/60/90 min, threshold ±2¢ — with the old
ex-post whole-window ruler computed **beside it on the same receipts**. Machine artifact:
`…/READ_ORGAN_FORWARD_TRUTH.json`.

## The two rulers, side by side

| ruler | accuracy |
|---|--:|
| ex-post whole-window label (the old 34%) | **34.5%** (149,888 / 434,364 receipts with a frozen path) |
| forward 60 m, per state call | SETTLED **74.9%** · FALLING 19.6% · RISING 16.3% |

## Accuracy per state call × horizon

| state call | n (60 m) | 30 m | 60 m | 90 m |
|---|--:|--:|--:|--:|
| **SETTLED** | 6,684 | **0.819** | **0.749** | 0.691 |
| FALLING | 17,563 | 0.182 | 0.196 | 0.231 |
| RISING | 1,036,903 | 0.134 | 0.163 | 0.203 |

Per category (60 m): ATP_CHALL 0.276 · ATP_MAIN 0.110 · WTA_CHALL 0.025 · WTA_MAIN 0.248.

## The confusion structure — the indictment mostly dissolves

60-minute confusion (state call → forward truth):

| call → fwd | FALLING | RISING | **SETTLED** |
|---|--:|--:|--:|
| RISING (1.04M) | 76,803 (7.4%) | 169,158 (16.3%) | **790,942 (76.3%)** |
| FALLING (17.6k) | 3,444 (19.6%) | **4,587 (26.1%)** | 9,532 (54.3%) |
| SETTLED (6.7k) | 724 | 957 | 5,003 (74.9%) |

- **The directional calls fail into STASIS, not into the opposite direction.** A RISING call is followed by the
  *opposite* move only **7.4%** of the time; three-quarters of the time the book simply doesn't move ±2¢ in the
  next hour. The old 34%/63% "misread" indictment — built on ex-post terminal labels — was substantially the
  substitution the audit named: it scored harmless stasis as error.
- **The one real confusion: FALLING calls invert 26.1%** — a falling read is followed by a ≥2¢ *rise* one time
  in four. That is the dangerous quadrant (a tracking rest walking down into a book about to climb), and the only
  place the read organ deserves the indictment.
- The rare **SETTLED calls are excellent (75-82%)** — when the organ says nothing is happening, nothing happens.

## The money cut — read accuracy is not the profit variable

Credited fills, entry read vs forward-60 truth, marked close − entry:

| entry read | fills | total ¢ | mean ¢ |
|---|--:|--:|--:|
| forward-WRONG | 631 | +1,337 | **+2.12** |
| forward-RIGHT | 300 | +463 | +1.54 |

**Forward-wrong fills out-earned forward-right fills.** For a maker, a "wrong" directional read that resolves
to stasis is *good business* — you got filled and the price didn't run; being right about RISING means paying up
into a move. Read accuracy, on this tape, is **not** where the cents are — consistent with every placement-side
finding (the money is in first-fill discipline and presence, not in reading better).

## Conservation

1,208,014 candidate receipts (states RISING/FALLING/SETTLED), 0 excluded for missing tape; scored 30 m
1,069,183 · 60 m 1,061,150 · 90 m 1,059,152 (each receipt once per horizon; shortfall = horizon past the window
edge). Ex-post ruler on the same receipts 434,364 scored (frozen path available) → 34.5%. Money cut 931 credited
fills with close + read. Sources: V47 fb74c8b8 ACTION_TRACE + MARKET ledger, fit-local tapes, QR closes/paths
57daf3c1; reopens bc0ce289 #4.
