# L5 receipt pull — the LUZTSE·TSE contradiction, resolved

Analysis seat only. Read-only. Plex flagged a contradiction: the autopsy (`fdeb7516`) tagged TSE **L5_STALE_REPRICE**, yet the tape shows `resting_target = 79` the full window (presence, not staleness). **Plex is right — and the tag was a scalar cross-wire.** Machine artifact: `…/V45_L5_RECEIPT_PULL.json`.

## What the L5 tag was actually computed from

There is **no per-receipt divergence series** behind the L5 tag. It was a **two-scalar heuristic**: `anytime union_reach < resting_target − 3`. For TSE that read `1 < 79 − 3 → stale`. **The bug: it keyed on the *anytime* reach, which includes pre-trigger flow — not the *causal* reach** (post-lawful-rest). TSE's rest never moved; the '1' is not where the rest was, it is a print from long before the rest could lawfully stand.

## Where TSE's union_reach = 1 came from — real, not a cross-wire

TSE (a **climbing favorite**) traded at **1¢ early** — **48 in-window prints ≤ 3¢, min 1¢, source TRADED_AT_LEVEL** — then climbed to bid 79 (snapshot bid 79 / ask 86). The `union_reach_cents = 1` is TSE's **own** real early print, correctly recorded; it is **pre-trigger** (the persistence-only join armed at 79 long after). The **causal** reach is **79** = the rest level. So the rest stood *at the collectable level the whole time*. **Plex's 'presence' read is correct; Plex's 'no TSE print near 1¢' is not — TSE did trade at 1¢, early and uncollectably.** No ledger cross-wire; the fault is the tag heuristic.

## The re-tag — TSE and the other L5 headliners

| leg | anytime reach | causal reach | rest (stable) | law at rest | **re-tag** |
|---|--:|--:|--:|---|---|

- **LUZTSE·TSE → L6 PRESENT_BUT_NO_COUNTERPARTY.** Rest held at 79 (the persistence-join level = causal reach 79); the anytime 1¢ was pre-trigger. The machine stood correctly; **no seller ever crossed to 79** (TSE's ask sat at 86). A market-no verdict, not staleness.
- **KHOZHA·KHO (77/78) · KRASAL·KRA (78/79) · PANFAL·FAL (44/47)** — identical pattern: present at the causal level, a pre-trigger anytime dip (6/43/30¢) fired the heuristic. All re-tag **L6 NO_COUNTERPARTY**.
- **PANFAL·PAN → L5 STALE_REPRICE (genuine).** Here the *causal* flow reached **45¢**, a full **9¢ below** the rest at 54¢, and the rest did not track down — a real non-tracking miss, the only genuine L5 among the headliners. Its anytime 1¢ is a red herring, but the causal-45-vs-rest-54 divergence is real.

## Class correction — L5 was almost entirely the cross-wire

Re-keyed on the **causal** reach (L5 iff causal flow ran > 3¢ below the present rest), **L5_STALE_REPRICE collapses 34 → 4**. The 30 spurious legs were standing present at their causal level; they move to **L6** (present-but-no-counterparty / over-par). Corrected chain totals:

| link | corrected legs | (autopsy fdeb7516) |
|---|--:|--:|
| **L2 MISREAD** | 62 | (58) |
| **L3 NO_TARGET** | 4 | (4) |
| **L3 WRONG_LEVEL** | 11 | (11) |
| **L4 LATE_POST** | 47 | (47) |
| **L5 STALE_REPRICE** | 4 | (34) |
| **L6 NO_COUNTERPARTY** | 185 | (173) |
| **L6 OVERPAR** | 157 | (143) |
| **total** | **470** | (470) |

**The correction strengthens the autopsy's headline**: the residual is now **342/470 (73%) legitimate market-no (L6)** and only 128 machine faults. L5 was never a real class at scale — it was a heuristic misreading pre-trigger prints as staleness. **L2 MISREAD (62) remains the top machine fault**; genuine STALE_REPRICE is a 4-leg tail (PANFAL·PAN its cleanest case).

## Conservation

470 unfilled legs re-classified (sum 470). L5 34→4; the delta moved to L6 (+26) and L2 (+4). TSE union_reach=1 confirmed a real pre-trigger print (48 prints ≤3¢), not a cross-wire. Corrects fdeb7516. Source V45 3bda0a54, causal reach d3db740f, prints fit-local, closes 57daf3c1.