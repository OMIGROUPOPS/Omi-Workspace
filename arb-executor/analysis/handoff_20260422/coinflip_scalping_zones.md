# Coinflip Scalping Zones (HR >= 80% only)

| Cell | Status | Dep X | Dep ROI | Scalping Zone | Opt X | Opt ROI | Opt $/day | Verdict | Directional (ref only) |
|------|--------|-------|---------|---------------|-------|---------|-----------|---------|------------------------|
| WTA_CHALL 45-49 | MISSING | n/a | n/a | +3c to +25c | +25c | 27.1% | $0.02 | THIN_DATA | X=+35c HR=67% ROI=16.0% $0.01/day (DIRECTIONAL) |
| ATP_MAIN 50-54 | MISSING | n/a | n/a | +3c to +12c | +12c | 22.6% | $0.02 | THIN_DATA | X=+13c HR=67% ROI=-17.6% $-0.02/day (DIRECTIONAL) |
| WTA_CHALL 40-44 | MISSING | n/a | n/a | +3c to +12c | +8c | 13.8% | $0.04 | DEPLOY +8c | X=+35c HR=71% ROI=29.1% $0.09/day (DIRECTIONAL) |
| ATP_CHALL 40-44 | ACTIVE | +10c | 7.8% | +3c to +11c | +8c | 10.6% | $0.11 | RECALIBRATE +10c -> +8c | X=+35c HR=60% ROI=10.9% $0.12/day (DIRECTIONAL) |
| ATP_CHALL 45-49 | ACTIVE | +6c | 3.2% | +3c to +16c | +13c | 10.5% | $0.08 | RECALIBRATE +6c -> +13c | X=+20c HR=78% ROI=11.1% $0.09/day (DIRECTIONAL) |
| ATP_MAIN 40-44 | ACTIVE | +7c | 7.2% | +3c to +9c | +9c | 8.4% | $0.04 | RECALIBRATE +7c -> +9c | X=+10c HR=76% ROI=-5.3% $-0.03/day (DIRECTIONAL) |
| WTA_MAIN 45-49 | ACTIVE | +14c | 5.2% | +3c to +14c | +13c | 8.3% | $0.03 | KEEP +14c | X=+16c HR=73% ROI=-1.7% $-0.01/day (DIRECTIONAL) |
| WTA_MAIN 40-44 | ACTIVE | +5c | 5.2% | +3c to +7c | +5c | 5.2% | $0.02 | KEEP +5c | X=+8c HR=79% ROI=-5.7% $-0.02/day (DIRECTIONAL) |
| WTA_CHALL 50-54 | MISSING | n/a | n/a | +3c to +15c | +15c | 4.0% | $0.01 | DEPLOY +15c | X=+16c HR=70% ROI=-7.6% $-0.01/day (DIRECTIONAL) |
| ATP_CHALL 55-59 | ACTIVE | +6c | 1.6% | +3c to +8c | +5c | 2.8% | $0.02 | KEEP +6c | X=+25c HR=71% ROI=1.6% $0.01/day (DIRECTIONAL) |
| WTA_MAIN 50-54 | ACTIVE | +26c | -9.1% | +3c to +10c | +3c | 1.4% | $0.01 | RECALIBRATE +26c -> +3c | X=+12c HR=76% ROI=-6.1% $-0.02/day (DIRECTIONAL) |
| ATP_MAIN 45-49 | MISSING | n/a | n/a | +3c to +6c | +4c | -0.2% | $-0.00 | DISABLE | X=+17c HR=69% ROI=-5.9% $-0.01/day (DIRECTIONAL) |
| ATP_CHALL 50-54 | MISSING | n/a | n/a | +3c to +10c | +9c | -1.8% | $-0.01 | DISABLE | X=+33c HR=67% ROI=10.1% $0.05/day (DIRECTIONAL) |
| WTA_MAIN 55-59 | DISABLED | n/a | n/a | +3c to +4c | +4c | -9.6% | $-0.02 | DISABLE | X=+8c HR=77% ROI=-12.2% $-0.03/day (DIRECTIONAL) |
| ATP_MAIN 55-59 | DISABLED | n/a | n/a | none (HR never >= 80%) | n/a | n/a | n/a | NO_SCALPING_ZONE | X=+9c HR=67% ROI=-22.7% $-0.06/day (DIRECTIONAL) |
| WTA_CHALL 55-59 | MISSING | n/a | n/a | n/a | n/a | n/a | n/a | NO_DATA | n/a |

## ATP_MAIN 40-44
Status: ACTIVE | Deployed: +7c | N: 38 | Avg entry: 41.8c
Scalping zone (HR>=80%): +3c to +9c
Cliff at X=+10c (HR drops below 80%)
Optimal in zone: +9c (HR=89%, PnL=+3.5c, ROI=8.4%, $0.04/day)
  Deployed +7c: HR=92%, PnL=+3.0c, ROI=7.2%, $0.03/day
  Delta: +1.2% ROI, +0.01 $/day
Directional trap: X=+10c HR=76% ROI=-5.3% $-0.03/day (DIRECTIONAL)
**Verdict: RECALIBRATE +7c -> +9c**

## ATP_MAIN 45-49
Status: MISSING | Deployed: n/a | N: 13 | Avg entry: 46.8c
Scalping zone (HR>=80%): +3c to +6c
Cliff at X=+7c (HR drops below 80%)
Optimal in zone: +4c (HR=92%, PnL=-0.1c, ROI=-0.2%, $-0.00/day)
Directional trap: X=+17c HR=69% ROI=-5.9% $-0.01/day (DIRECTIONAL)
**Verdict: DISABLE**

## ATP_MAIN 50-54
Status: MISSING | Deployed: n/a | N: 6 | Avg entry: 53.2c
Scalping zone (HR>=80%): +3c to +12c
Cliff at X=+13c (HR drops below 80%)
Optimal in zone: +12c (HR=100%, PnL=+12.0c, ROI=22.6%, $0.02/day)
Directional trap: X=+13c HR=67% ROI=-17.6% $-0.02/day (DIRECTIONAL)
Flags: THIN_DATA
**Verdict: THIN_DATA**

## ATP_MAIN 55-59
Status: DISABLED | Deployed: n/a | N: 15 | Avg entry: 57.0c
Scalping zone (HR>=80%): none (HR never >= 80%)
Cliff at X=+3c (HR drops below 80%)
Directional trap: X=+9c HR=67% ROI=-22.7% $-0.06/day (DIRECTIONAL)
Flags: NO_SCALPING_ZONE
**Verdict: NO_SCALPING_ZONE**

## ATP_CHALL 40-44
Status: ACTIVE | Deployed: +10c | N: 86 | Avg entry: 41.9c
Scalping zone (HR>=80%): +3c to +11c
Cliff at X=+12c (HR drops below 80%)
Optimal in zone: +8c (HR=93%, PnL=+4.4c, ROI=10.6%, $0.11/day)
  Deployed +10c: HR=87%, PnL=+3.3c, ROI=7.8%, $0.08/day
  Delta: +2.8% ROI, +0.03 $/day
Directional trap: X=+35c HR=60% ROI=10.9% $0.12/day (DIRECTIONAL)
**Verdict: RECALIBRATE +10c -> +8c**

## ATP_CHALL 45-49
Status: ACTIVE | Deployed: +6c | N: 58 | Avg entry: 46.2c
Scalping zone (HR>=80%): +3c to +16c
Cliff at X=+17c (HR drops below 80%)
Optimal in zone: +13c (HR=86%, PnL=+4.8c, ROI=10.5%, $0.08/day)
  Deployed +6c: HR=91%, PnL=+1.5c, ROI=3.2%, $0.03/day
  Delta: +7.3% ROI, +0.06 $/day
Directional trap: X=+20c HR=78% ROI=11.1% $0.09/day (DIRECTIONAL)
**Verdict: RECALIBRATE +6c -> +13c**

## ATP_CHALL 50-54
Status: MISSING | Deployed: n/a | N: 30 | Avg entry: 51.0c
Scalping zone (HR>=80%): +3c to +10c
Cliff at X=+11c (HR drops below 80%)
Optimal in zone: +9c (HR=83%, PnL=-0.9c, ROI=-1.8%, $-0.01/day)
Directional trap: X=+33c HR=67% ROI=10.1% $0.05/day (DIRECTIONAL)
**Verdict: DISABLE**

## ATP_CHALL 55-59
Status: ACTIVE | Deployed: +6c | N: 38 | Avg entry: 57.9c
Scalping zone (HR>=80%): +3c to +8c
Cliff at X=+9c (HR drops below 80%)
Optimal in zone: +5c (HR=95%, PnL=+1.6c, ROI=2.8%, $0.02/day)
  Deployed +6c: HR=92%, PnL=+0.9c, ROI=1.6%, $0.01/day
  Delta: +1.3% ROI, +0.01 $/day
Directional trap: X=+25c HR=71% ROI=1.6% $0.01/day (DIRECTIONAL)
**Verdict: KEEP +6c**

## WTA_MAIN 40-44
Status: ACTIVE | Deployed: +5c | N: 34 | Avg entry: 42.2c
Scalping zone (HR>=80%): +3c to +7c
Cliff at X=+8c (HR drops below 80%)
Optimal in zone: +5c (HR=94%, PnL=+2.2c, ROI=5.2%, $0.02/day)
  Deployed +5c: HR=94%, PnL=+2.2c, ROI=5.2%, $0.02/day
  Delta: +0.0% ROI, +0.00 $/day
Directional trap: X=+8c HR=79% ROI=-5.7% $-0.02/day (DIRECTIONAL)
**Verdict: KEEP +5c**

## WTA_MAIN 45-49
Status: ACTIVE | Deployed: +14c | N: 26 | Avg entry: 46.7c
Scalping zone (HR>=80%): +3c to +14c
Cliff at X=+15c (HR drops below 80%)
Optimal in zone: +13c (HR=85%, PnL=+3.9c, ROI=8.3%, $0.03/day)
  Deployed +14c: HR=81%, PnL=+2.4c, ROI=5.2%, $0.02/day
  Delta: +3.1% ROI, +0.01 $/day
Directional trap: X=+16c HR=73% ROI=-1.7% $-0.01/day (DIRECTIONAL)
**Verdict: KEEP +14c**

## WTA_MAIN 50-54
Status: ACTIVE | Deployed: +26c | N: 25 | Avg entry: 50.9c
Scalping zone (HR>=80%): +3c to +10c
Cliff at X=+11c (HR drops below 80%)
Optimal in zone: +3c (HR=96%, PnL=+0.7c, ROI=1.4%, $0.01/day)
  Deployed +26c: HR=60%, PnL=-4.6c, ROI=-9.1%, $-0.03/day
  Delta: +10.5% ROI, +0.04 $/day
Directional trap: X=+12c HR=76% ROI=-6.1% $-0.02/day (DIRECTIONAL)
**Verdict: RECALIBRATE +26c -> +3c**

## WTA_MAIN 55-59
Status: DISABLED | Deployed: n/a | N: 13 | Avg entry: 57.2c
Scalping zone (HR>=80%): +3c to +4c
Cliff at X=+5c (HR drops below 80%)
Optimal in zone: +4c (HR=85%, PnL=-5.5c, ROI=-9.6%, $-0.02/day)
Directional trap: X=+8c HR=77% ROI=-12.2% $-0.03/day (DIRECTIONAL)
**Verdict: DISABLE**

## WTA_CHALL 40-44
Status: MISSING | Deployed: n/a | N: 24 | Avg entry: 42.3c
Scalping zone (HR>=80%): +3c to +12c
Cliff at X=+13c (HR drops below 80%)
Optimal in zone: +8c (HR=96%, PnL=+5.8c, ROI=13.8%, $0.04/day)
Directional trap: X=+35c HR=71% ROI=29.1% $0.09/day (DIRECTIONAL)
**Verdict: DEPLOY +8c**

## WTA_CHALL 45-49
Status: MISSING | Deployed: n/a | N: 6 | Avg entry: 46.8c
Scalping zone (HR>=80%): +3c to +25c
Cliff at X=+26c (HR drops below 80%)
Optimal in zone: +25c (HR=83%, PnL=+12.7c, ROI=27.1%, $0.02/day)
Directional trap: X=+35c HR=67% ROI=16.0% $0.01/day (DIRECTIONAL)
Flags: THIN_DATA
**Verdict: THIN_DATA**

## WTA_CHALL 50-54
Status: MISSING | Deployed: n/a | N: 10 | Avg entry: 50.2c
Scalping zone (HR>=80%): +3c to +15c
Cliff at X=+16c (HR drops below 80%)
Optimal in zone: +15c (HR=80%, PnL=+2.0c, ROI=4.0%, $0.01/day)
Directional trap: X=+16c HR=70% ROI=-7.6% $-0.01/day (DIRECTIONAL)
**Verdict: DEPLOY +15c**

## WTA_CHALL 55-59
No sweep data.

