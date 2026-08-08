# Wide-spread riser law — causal measurement before build

Analysis seat only. Read-only. **Population**: riser legs whose **median in-window spread > 3¢** — the VRB/COP class — **9 of 1,608 legs** (9/409 of risers). **Law under test**: for wide risers, from the **first descended ask-divot with dwell ≥10 s** (observable, T2-class trigger) the rest anchors to that trough level (inside the spread), cap-bounded, sanity (rest < ask at placement); it fills causally when post-anchor flow **returns** (a trade/seller-print ≤ R, or the ask re-dwells ≤ R for 10 s). Narrow risers keep the **V41 join** (persistence-only). Fallers fixed. Scored causally (3-channel, post-trigger flow) vs V41. Machine artifact: `…/WIDE_SPREAD_RISER_LAW.json`.

## Verdict — do not build

The wide-spread class is negligible and the ask-anchor is **shallower than the join where it applies**; the one leg it would help is gated out. Three findings, each fatal:

1. **The class is 0.6% of legs** — 9/1,608. Almost every riser trades a tight book (median ≤3¢).
2. **Where it applies, it loses to the join.** On the wide subset the ask-anchor completes the *same* pairs as V41 but locks **9¢ less** (V41 4/23¢ → HYBRID 4/14¢): ask troughs sit shallower than the persistent-bid join.
3. **It is mis-gated away from the one case it helps.** VRB's ask-anchor *does* catch the 68 dip — but VRB's median spread is 2¢, so the >3¢ gate classifies it narrow and hands it back to the join, which forfeits it.

## Aggregate — HYBRID vs V41 (bar 632 / 5,217¢)

| law | riser legs filled | pairs under-par | locked ¢ | ≤93/≤95/≤97/<100 | riser forfeits |
|---|--:|--:|--:|---|--:|
| **V41 (all-join)** | 291 | 485 | **3524** | 83/123/214/485 | 118 |
| **HYBRID (wide→ask-anchor)** | 295 | 485 | **3515** | 82/122/213/485 | 114 |

Identical under-par (485); HYBRID fills 4 more riser legs but locks **9¢ less** — the extra fills are shallow ask-troughs. **False arms: 0** (the wide-spread asks recur, so anchors that arm do fill — the T2-frontier's 89 false arms do not materialize in this tiny, chronically-wide subset).

## Per category — under-par (locked ¢)

| category | V41 under-par | V41 ¢ | HYBRID under-par | HYBRID ¢ |
|---|--:|--:|--:|--:|
| ATP_CHALL | 204 | 1166 | 205 | 1163 |
| ATP_MAIN | 104 | 563 | 103 | 559 |
| WTA_CHALL | 87 | 1328 | 87 | 1328 |
| WTA_MAIN | 90 | 467 | 90 | 465 |

## Named

| leg | anytime | median spread | wide? | ask-anchor fill | join fill | HYBRID | V41 |
|---|--:|--:|:-:|--:|--:|--:|--:|
| **VRB** | 68 | 2 | no | 68 | None | None | None |
| **COP** | 47 | 41 | YES | 69 | 64 | 69 | 64 |
| **NIK** | 18 | 2 | no | 29 | 29 | 29 | 29 |

- **VRB — the anchor works, the gate fails it.** The ask-anchor realizes **68** (the post-07:13 dip, which the ask revisits nine times — 12 s / 59 s / 523 s dwells), exactly the target. But VRB's **median spread is 2¢** → classified narrow → keeps the join → **join is null → HYBRID forfeits VRB**. Gating on *median* spread misses VRB, whose opportunity is a *transient* wide moment (max spread 87) on a median-tight leg.
- **COP — wide, and the anchor loses.** Median spread 41¢ (truly wide). Ask-anchor **69**, join **64** → HYBRID takes the shallower 69, pushing BOSCOP to combined **97 vs V41's 92**. The persistent-bid join beats the ask-trough here.
- **NIKVRB — completes under neither.** NIK (narrow) joins at 29; VRB forfeits (narrow→join→null) → the pair is **null** under both HYBRID and V41. The 86 target needs VRB's ask-anchor 68 + NIK ~18 — but the median gate denies VRB the anchor and the join denies NIK the deeper 18.

## What the measurement actually recommends

Keep the **V41 join for all risers**. If the ask-anchor is worth anything it is **not** on median-wide legs (too few, and shallower than the join) but on **transient wide moments** on median-tight legs (the real VRB case) — a *per-moment* spread trigger, not a *median* gate. That is a different law; this one, as specified, is a 9¢ loss.

## Conservation

409 riser legs, 637 games; fallers fixed. Wide class 9/1,608 (median spread >3¢). Bar 632/5,217¢. V41 485/3524¢ (filled 291, forfeits 118); HYBRID 485/3515¢ (filled 295, forfeits 114). Wide subset: V41 4/23¢ vs HYBRID 4/14¢. False arms 0. Machinery cca7c6c1, sealed union 57daf3c1, divot census d1ac9497.