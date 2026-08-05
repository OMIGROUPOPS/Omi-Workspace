# V30 read-moment ceiling — two-tier, model-free, all 804

Analysis seat only. Read-only; no live mutation, no orders/positions/credentials, no
access to Codex's estimator. Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V30_READMOMENT_CEILING.json`
(per-event rows + rollups).

## Source note — why this is model-free, not "from the V28 trace"

The V28 trace at 3339f30 carries **no** per-event shape-resolution moment and **no**
CHASED/PATIENT role cast: only 138 / 1,608 legs have any shape verdict (all `FLOOR`),
terminal `direction` is `UNKNOWN` throughout, and no V28/V29/sibling-source artifact
emits a RISER/FALLER cast. So the read-moment and roles here are **reconstructed
model-free from raw tape + audited closes** — this is the analysis seat's grammar,
explicitly *not* V28's. Per the operator ruling, run as two tiers.

**Read-moment** = first *coherent qualifying-ask descent* per leg (best-ask at a
running-min, ≥10 s dwell, ≥5-lot displayed), taking the **earlier of the pair** as the
orientation trigger. `read_complete` = the later of the two legs' first descent — the
first moment both legs have declared, so roles are *assignable*.

## Conservation — 804

| verdict | events |
|---|---:|
| RESOLVED | **772** |
| READ_NEVER_RESOLVED | **19** |
| UNDETERMINED_CLOSE (no audited close on a leg) | 13 |
| **total** | **804** |

**READ_NEVER_RESOLVED = 19** is a finding on its own: neither leg ever formed a
qualifying-ask descent (no ≥10 s, ≥5-lot running-min ask) inside the guarded window.
Concentrated in **WTA_MAIN 10, ATP_MAIN 6, ATP_CHALL 3** — thin-book games where the
grammar never gets a read.

## Tier A — oracle ceiling (roles known ex-post from closes)

Roles assigned from audited closes: **PATIENT/FALLER = the lower-close side** (decays
to its floor), **CHASED/RISER = the higher-close side** (climbs; we need a knock-down
to buy). Cap-compatible aims: `aim_patient = min(own_close−1, 99 − chased_maker_floor)`,
`aim_chased = min(own_close−1, 99 − patient_maker_floor)`.

- **PATIENT-floor timing vs read.** The patient's cap-compatible qualifying floor
  (≤ `aim_patient`) is measured against `read_complete`. **52 events are a V30 miss** —
  the cheap patient floor formed *before* both legs declared, so no role read could
  have armed a bid in time. Lead-before-read: median **1.6 min**, tail to **8.3 h**.
  By cat: ATP_CHALL 24, ATP_MAIN 14, WTA_MAIN 10, WTA_CHALL 4.
- **CHASED buy-window.** After the read, count distinct qualifying dips ≤ `aim_chased`
  before the bell (per-event `chased_windows_after_read`, `chased_first_delta_min`).

**Tier A oracle ceiling = 179** — events that are price-winnable (both maker floors <
own close AND floor sum < 100), *and* read early enough (not a V30 miss), *and* have ≥1
chased buy-window after the read.

| cat | Tier A ceiling |
|---|---:|
| ATP_CHALL | 108 |
| ATP_MAIN | 36 |
| WTA_MAIN | 21 |
| WTA_CHALL | 14 |
| **total** | **179** |

This is the upper bound: what V30 wins **if roles were known at the read**.

## Tier B — callable roles (decision-time signals only)

At the same `read_moment`, call the roles from causal tape signals only (rows ≤ read,
≤600 s lookback with a last-15-rows fallback). **Explicit causal rule (the ARNROM
signature):**

> For each leg compute `D = ask_walk_down − bid_stack`, where `ask_walk_down` = cents
> the best-ask fell over the window (ask walking *into* demand) and `bid_stack` = best-
> bid rise + a bid-size-stacking flag (bid stacking *under* a pinned ask). **PATIENT =
> the leg with the higher `D`** (ask walking down); **CHASED = the other** (bid
> stacking under a pinned ask).

**Accuracy vs the Tier A oracle: 121 / 212 = 57.1%** — barely above a coin flip.

| category | role accuracy (where callable) |
|---|---|
| WTA_CHALL | 23/37 = 62.2% |
| ATP_CHALL | 60/101 = 59.4% |
| ATP_MAIN | 20/35 = 57.1% |
| WTA_MAIN | 18/39 = **46.2%** (below chance) |

The binding problem is **callability, not just accuracy**: of 772 resolved events,
**560 are UNCALLABLE at the read-moment** — at the earliest orientation the *second*
leg has not yet printed enough book to read its role. Only 212 are callable at all
(121 correct, 91 wrong).

## The V30 ceiling

**V30 ceiling = Tier A events whose roles are also callable-correct at Tier B = 24.**

Of the 179 oracle events: **24 callable-correct · 26 miscalled · 129 uncallable.** The
price structure permits 179, but decision-time role-calling collapses it to 24 — the
read, not the book, is the constraint.

| cat | V30 ceiling |
|---|---:|
| ATP_CHALL | 16 |
| ATP_MAIN | 3 |
| WTA_MAIN | 3 |
| WTA_CHALL | 2 |
| **total** | **24** |

**ARNROM** is instructive: Tier A ceiling = true (patient ROM close 39, chased ARN
close 62; winnable; 2 chased windows after read), but it is **uncallable** at its
23:46 ET Jul-11 orientation — ROM had not yet printed in the pre-read window, and the
famous ARN-pinned-ask / ROM-walk-down signature only forms hours later (18:35–18:55 ET
Jul 12). The earliest read cannot see the signature that names the roles.

## Conservation ledger

804 = 772 RESOLVED + 19 READ_NEVER_RESOLVED + 13 UNDETERMINED_CLOSE. Resolved 772 →
Tier A ceiling 179 (+ 52 V30-miss counted separately, + the rest failing winnable or
no chased window). Tier A 179 = 24 callable-correct (**V30 ceiling**) + 26 miscalled +
129 uncallable. Tier B callable 212 = 121 correct + 91 wrong; 560 uncallable.

## Caveat / available extension

Tier B is scored at `read_moment` (earliest orientation) per the operator spec, which
is why callability is low — one book is barely formed. Re-scoring the role call at
`read_complete` (both books present) would raise callability at the cost of a later
decision point; available on request as a sensitivity, not run here.
