# Corrected Overnight Analysis

Generated: 2026-02-01 10:43:57

**Filters Applied:** MIN_BUY_PRICE=15c, MAX_CONTRACTS=100, MIN_CONTRACTS=20

## BEFORE (No MIN_BUY_PRICE Filter)

- **Total arbs:** 139
- **Time span:** 01/31 09:02 to 01/31 22:34 (13.5 hours)
- **TAM profit:** $1056.00
- **TAM at risk:** $13436.00
- **TAM ROI:** 7.9%
- **Avg individual ROI:** 35.9% (skewed by outliers)
- **Realistic profit (100 cap):** $528.00
- **Outliers (<15c buy):** 9 arbs

## AFTER (With MIN_BUY_PRICE = 15c Filter)

- **Total arbs:** 130
- **TAM profit:** $834.00
- **TAM at risk:** $13308.00
- **TAM ROI:** 6.3%
- **Realistic profit (100 cap):** $417.00
- **Realistic at risk:** $6654.00
- **Realistic ROI:** 6.3%
- **Avg individual ROI:** 7.1%
- **Avg spread:** 3.2c
- **Avg buy price:** 51.2c

## COMPARISON

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total Arbs | 139 | 130 | -9 |
| TAM Profit | $1056.00 | $834.00 | -$222.00 |
| TAM ROI | 7.9% | 6.3% | -1.6% |
| Realistic Profit | $528.00 | $417.00 | -$111.00 |
| Avg Individual ROI | 35.9% | 7.1% | -28.8% |

## FILTERED OUT (9 Garbage Arbs)

These 9 arbs with buy price < 15c were contributing $111.00 of 'fake' profit.

| Time | Game | Sport | Spread | Buy Price | Fake ROI | Reason |
|------|------|-------|--------|-----------|----------|--------|
| 15:22:21 | HAMP | CBB | 21c | 1c | 2100% | Below 15c min |
| 15:26:19 | PHI | NHL | 43c | 3c | 1433% | Below 15c min |
| 15:24:53 | LA | NHL | 39c | 12c | 325% | Below 15c min |
| 22:34:20 | MIA | NBA | 3c | 2c | 150% | Below 15c min |
| 09:02:18 | CIN | CBB | 1c | 8c | 12% | Below 15c min |
| 20:33:11 | MISS | CBB | 1c | 8c | 12% | Below 15c min |
| 22:33:52 | DAL | NBA | 1c | 9c | 11% | Below 15c min |
| 15:22:25 | NJIT | CBB | 1c | 10c | 10% | Below 15c min |
| 20:35:53 | MEM | NBA | 1c | 11c | 9% | Below 15c min |

## TRUE PERFORMANCE (Corrected)

**Data period:** 13.5 hours

### Realistic Profit (100 contract cap)
- **Total in data:** $417.00
- **Hourly rate:** $30.81/hr
- **Arbs per hour:** 9.6
- **Avg profit per arb:** $3.21

### Projected Daily (3 prime hours, 70% success)
- **Gross:** $92.43
- **After 70% success:** $64.70

### Projected Monthly
- **30 days:** $1941.12
- **Annual:** $23,293.41
- **Annual ROI on $20K:** 116%

### ROI Sanity Check
- Avg spread: 3.2c
- Avg buy price: 51.2c
- Calculated ROI: 6.3%
- Actual avg ROI: 7.1%
- **Math checks out!**

## SUMMARY

```
BEFORE (with garbage data):
  Arbs: 139
  Avg ROI: 35.9% (INFLATED)
  Realistic profit: $528.00

AFTER (filtered):
  Arbs: 130
  Avg ROI: 7.1% (ACCURATE)
  Realistic profit: $417.00

FILTERED OUT:
  Garbage arbs: 9
  Fake profit removed: $111.00
```
