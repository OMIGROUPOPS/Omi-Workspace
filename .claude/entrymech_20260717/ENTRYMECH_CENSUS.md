# ENTRY-MECHANICS RETRO CENSUS — 07-17 (P1 queue bill · P1 orientation column · P3 flow re-grade)

## A. THE FITTED-HOUR BILL (Jul 15-17 logs, 2018 placements)
- discovery -> placement lag: median 7.76h · p25 3.19h · p75 8.51h · max 27.4h
- placements waiting >4h after the event was on the tape: **1417 of 2018 (70%)**
- queue forfeited at the fitted-hour join (join_queue depth_at_post, earlier pull): median 300 shares, p75 2,176 — the queue a discovery-time park would have owned.

## B. ORIENTATION COLUMN — the leader-rises role-prior vs the realized riser
- basis: window-open price vs last observed print/bid per leg (shadow-series resolution); relative-gain winner = realized riser; moves <3c apart = undetermined.
- **prior called the riser RIGHT 116 / WRONG 368 (76% wrong) · undetermined 264** of 754 two-leg events observed

## C. P3 RE-GRADE — today's join_queue reads, birth-clock vs last-post clock (1911 reads)
- reads whose birth-latency is >2x the order-age latency the meter reported (the churn-blinded class): **1584 of 1911 (83%)**
- median reported latency 145s vs median TRUE (birth) latency 5896s — the meter under-read the wait by 40.7x
    - 15JOSKRO-JOS cancel: reported 638s, true 27801s, 1 reposts
    - 15POPMIC-MIC cancel: reported 1900s, true 28965s, 1 reposts
    - 15POPMIC-MIC cancel: reported 2098s, true 29164s, 1 reposts
    - 15JOSKRO-KRO cancel: reported 2912s, true 27814s, 2 reposts
    - 15SCHHOS-HOS cancel: reported 81s, true 24006s, 1 reposts


## D. P5 — THE SHARP-BLEND FEED DIAGNOSIS (from the box, 14:4x ET 07-17)

- **ALL 14 odds-API books frozen simultaneously since 2026-07-10 13:00–13:42
  ET (169 hours = 7 days stale)** — pinnacle / betfair_ex_eu / matchbook (the
  entire SHARP_BOOKS blend) among them. One provider, one death: the same
  freeze minute across every book = the-odds-api's tennis coverage went dark,
  not fourteen books.
- **Not our key, not our poller**: key alive (quota 4,427,636 remaining /
  572,364 used); `tennis_odds` polls every ~90s and the provider's `/sports`
  returns **zero active `tennis_*` keys** — the poller's 06-12 dynamic-
  discovery fix works and will resume automatically when the provider
  re-lists tennis.
- **Consequence measured at the consumption site**: 477/477 of 07-17's
  placements priced with `fv_reason=stale_sources` — the blend contributed
  nothing to any placement for a week.
- **The one living source**: betexplorer (scraper, fresh 0.6h) — NOT in
  SHARP_BOOKS. Promoting it into the blend is an operator/ruling lever, not
  armed here; the fv_gap dossier voice reads NO-READ honestly until the blend
  breathes, and the panel freshness meter now carries the staleness on the
  glass.

## E. VERDICT LINES

- P1: the fitted hour cost 70% of placements >4h of queue time (median 300
  shares ahead at the join); the leader-rises role-prior was WRONG on 76% of
  determinable events — orientation must be a prior, and today the prior's
  strongest voices (chain tape n<300, fv blend dark) are thin: the swap bar
  (conviction >= 0.7, n >= 2) will fire rarely until the feeds breathe. Honest.
- P2/P3: 2,839 reposts/123 legs on 07-17 (top 40-53/leg/hr); the flow meter
  under-read true waits 40.7x median, 83% of reads churn-blinded.
