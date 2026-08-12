# The aim error census — was the miss an aiming failure, and did the vault already know? [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. Splits only, no builds, no models. Population: the RIGHT_READ_WRONG_PLAY legs
from DECISION_AUDIT @ `35ac1f5b`. **Conservation flag (reported, not forced): the ordered "362 + 190"
double-counts — the 190 execution-shortfall partial legs are a subset of the 362 RRWP legs; distinct
population = 362, `esf` flag carried per row.** Scored 355 (7 legs had no true trade in the frozen W1 span —
no lawful low exists). Per leg: **aim error = evidence-named P** (`evidenced_standing_authority.level_cents`,
fallback edge target/join level) **− the leg's lawful in-window low** (true trades, frozen span). Machine
artifact with all rows: `AIM_ERROR_CENSUS.json`.

## The headline — these are not aiming failures

**Aim error (355): p25 0 · median +2 · p75 +4.** The sign matters: positive means the market traded **below
the level we stood** and we still weren't credited — under trades-as-truth that is only possible if the rest
was not standing (at that level) when the low printed. The right-read unfilled legs did not under-aim; they
stood at or above the eventual low and missed on **standing-time**. The greedy tail (negative aim error —
stood below the market's floor) is small: p25 is 0.

Per category × cell band (medians): ATP_CHALL +2 · ATP_MAIN +3 · WTA_CHALL 0 · WTA_MAIN +3; cell bands <50:
+1, 50–74: +2, 75–94: +2, 95+: +4 (65 legs lack a QR close → band "?", median +1). Full cat × band grid in
the JSON.

## The predictability test — four features, splits of realized aim error

| feature | bins (n / median aim error) | separates? |
|---|---|---|
| (a) vault edge_p50 bin (SEQFLOOR_RECUT, cat×close-cell) | 0: 63/+1 · 1–4: 180/+2 · 5–9: 12/+1 · 10+: 17/+2 · none: 83/+1 | **NO — flat** |
| (b) category | ATP_CHALL +2 · ATP_MAIN +3 · WTA_CHALL 0 · WTA_MAIN +3 | weak |
| (c) sibling state at our arm | sib armed first (RISING 180/+2 · FALLING 91/+2 · SETTLED 34/+1) vs **sib armed later 47/0** | modest — arming first is clean |
| (d) volume tier | 1–99: 32/0 · 100–999: 112/+1 · 1k–10k: 150/+2 · **>10k: 61/+4** | **YES — monotone, the strongest** |

**The vault-knew answer, stated precisely:** the vault's cell table predicted **where the floor would land**
almost exactly — residual (close − edge_p50) − realized low = **p25 −1 · median 0 · p75 +3** (272 legs with
both). So yes: game by game, SEQFLOOR_RECUT already knew the level. But it could not have fixed these legs,
because the realized aim error is *positive* — they already stood at-or-above that floor. Aiming lower (the
only thing a discount table changes) would have made every one of them worse. What separates the misses is
**tape busyness** (aim error grows monotonically with volume — busy tapes print more sub-P flow during the
moments the rest isn't standing) and **arm order** (when we armed before the sibling, aim error ≈ 0). The
discount knowledge was in the vault; the missing knowledge — when the rest must be standing — is not in any
cell table.

## Doctrine-2 check — what would trivially inflate predictability, stratified out

1. **Close-cell leak**: the cell key is the W1 *close* — ex-post knowledge at conception. Stratum: re-keyed
   every leg by conception-time P-cell (`vault_bin_pcell`): medians 1/2/1/2 across bins — equally flat; the
   (a) verdict is not a leak artifact.
2. **Dipless triviality**: on legs whose window never dipped below the close, "the vault predicted 0 and
   nothing was missed" is true by construction. Stratum: dipless 71 legs (median aim error 0) vs dipped 219
   (+2); the vault-residual claim rests on the dipped stratum and holds there.
3. **Fit overlap**: SEQFLOOR_RECUT was fit on the 2,435-pair seqfloor pull; its overlap with dev-804 is not
   established in machine records — if these games are inside that corpus the residual-0 result is partially
   in-sample. REPORTED as unresolved, per standing rule.

## Conservation

Population 362 RRWP legs (esf subset 190, contained); scored 355 = 362 − 7 no-lawful-low; splits each sum 355
(vault-residual row count 272 = legs with both close and a populated vault cell). Sources: V49b staged ledger,
fit-local prints (frozen W1 spans), QR closes, `recut_cells.json` (6-cat 1¢ grid). ANALYTICAL_ESTIMATE.
