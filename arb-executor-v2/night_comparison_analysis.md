# Night-Over-Night Comparison Analysis

Generated: 2026-02-01 10:48:37

**Filters Applied:** MIN_BUY_PRICE=15c, MAX_CONTRACTS=100, MIN_CONTRACTS=20

## NIGHT-OVER-NIGHT COMPARISON

| Metric | Jan 29-30 | Jan 31/Feb 1 | Difference |
|--------|-----------|--------------|------------|
| Hours of data | 29.8 | 13.5 | -16.3 |
| Total arbs (raw) | 5175 | 139 | -5036 (-97%) |
| Arbs after filter | 4507 | 130 | -4377 (-97%) |
| Garbage filtered | 668 | 9 | -659 |
| Realistic profit | $9818.00 | $417.00 | $-9401.00 (-96%) |
| Hourly rate | $329.58/hr | $30.81/hr | $-298.77 (-91%) |
| Arbs per hour | 151.3 | 9.6 | -142 (-94%) |
| Avg spread | 2.2c | 3.2c | +1.0c |
| Avg buy price | 55.8c | 51.2c | -4.6c |
| Avg ROI | 5.1% | 7.1% | +2.0% |

## BY SPORT COMPARISON

| Sport | Jan 29-30 Arbs | Jan 31/Feb 1 Arbs | Jan 29-30 Profit | Jan 31/Feb 1 Profit |
|-------|----------------|-------------------|------------------|---------------------|
| CBB | 2506 | 73 | $5442.00 | $185.00 |
| NBA | 1565 | 31 | $2826.00 | $69.00 |
| NHL | 436 | 26 | $1550.00 | $163.00 |
| **TOTAL** | **4507** | **130** | **$9818.00** | **$417.00** |

## TIME OF DAY COMPARISON

Arb frequency by hour (filtered arbs only):

| Hour | Jan 29-30 | Jan 31/Feb 1 |
|------|-----------|--------------|
| 00:00 | 48 | 0 |
| 09:00 | 0 | 3 |
| 11:00 | 6 | 0 |
| 12:00 | 11 | 0 |
| 13:00 | 81 | 0 |
| 14:00 | 38 | 0 |
| 15:00 | 41 | 38 |
| 16:00 | 18 | 0 |
| 17:00 | 62 | 0 |
| 18:00 | 101 | 0 |
| 19:00 | 1045 | 0 |
| 20:00 | 1113 | 82 |
| 21:00 | 977 | 0 |
| 22:00 | 694 | 7 |
| 23:00 | 272 | 0 |

### Peak Hours

**Jan 29-30 peak hours:** 20:00 (1113 arbs), 19:00 (1045 arbs), 21:00 (977 arbs)
**Jan 31/Feb 1 peak hours:** 20:00 (82 arbs), 15:00 (38 arbs), 22:00 (7 arbs)

## GARBAGE ARBS FILTERED

### Jan 29-30 (668 filtered)
| Game | Sport | Spread | Buy | ROI |
|------|-------|--------|-----|-----|
| DET | NHL | 37c | 4c | 925% |
| SAC | NBA | 27c | 4c | 675% |
| MSM | CBB | 3c | 1c | 300% |
| DAY | CBB | 5c | 2c | 250% |
| DAY | CBB | 2c | 1c | 200% |

### Jan 31/Feb 1 (9 filtered)
| Game | Sport | Spread | Buy | ROI |
|------|-------|--------|-----|-----|
| HAMP | CBB | 21c | 1c | 2100% |
| PHI | NHL | 43c | 3c | 1433% |
| LA | NHL | 39c | 12c | 325% |
| MIA | NBA | 3c | 2c | 150% |
| CIN | CBB | 1c | 8c | 12% |

## KEY QUESTIONS ANSWERED

### 1. Is performance consistent night-over-night?

**PARTIALLY** - Some variance in hourly rates ($329.58/hr vs $30.81/hr)
Variance: 166% - could be due to different game schedules.

### 2. Are there outlier nights or is this repeatable?

**Some variance** - ROI differs by 2.0% between nights
- Jan 29-30: 5.1% avg ROI
- Jan 31/Feb 1: 7.1% avg ROI

### 3. Which night was better and why?

**Jan 29-30** was better at $329.58/hr vs $30.81/hr

Possible reasons:
- Different game schedules (more/fewer games)
- Market volatility differences
- Time of day coverage differences

## SUMMARY

```
Jan 29-30:
  Duration: 29.8 hours
  Arbs: 4507 (after filter)
  Profit: $9818.00
  Hourly: $329.58/hr
  Avg ROI: 5.1%

Jan 31/Feb 1:
  Duration: 13.5 hours
  Arbs: 130 (after filter)
  Profit: $417.00
  Hourly: $30.81/hr
  Avg ROI: 7.1%

COMBINED AVERAGE:
  Avg hourly: $180.20/hr
  Avg ROI: 6.1%
  Projected daily (3hr, 70%): $378.41
  Projected monthly: $11352.38
  Projected annual: $138,120.58
```
