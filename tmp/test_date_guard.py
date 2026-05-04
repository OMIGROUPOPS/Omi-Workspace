import re
from datetime import datetime, timezone

_month_map = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
              "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}

def date_ok(event_ticker, sched_start_time):
    """Mirrors _date_ok from the patched function."""
    _dm = re.search(r"-(\d{2})([A-Z]{3})(\d{2})", event_ticker)
    if not _dm:
        return True, None
    try:
        tk_date = datetime(2000+int(_dm.group(1)), _month_map[_dm.group(2)],
                           int(_dm.group(3)), 16, 0, tzinfo=timezone.utc)
        sched_dt = datetime.fromisoformat(sched_start_time.replace("Z", "+00:00"))
        delta = abs((sched_dt - tk_date).total_seconds())
        return delta <= 43200, delta
    except Exception:
        return True, None

# Test 1: APR24 ticker against APR25 schedule entry (the bug case)
print("=== TEST 1: APR24 ticker matched against APR25 schedule (BUG CASE) ===")
print("Expected: date_ok=False for all (>12h mismatch)")
print()
test_cases_1 = [
    ("KXATPMATCH-26APR24CERHAN", "2026-04-25T09:00:00Z"),
    ("KXATPMATCH-26APR24MUNRUU", "2026-04-25T10:30:00Z"),
    ("KXATPMATCH-26APR24DAVCAR", "2026-04-25T09:00:00Z"),
    ("KXATPMATCH-26APR24HUMATM", "2026-04-25T12:00:00Z"),
    ("KXATPMATCH-26APR24BUBTSI", "2026-04-25T19:30:00Z"),
]
for ticker, sched_start in test_cases_1:
    ok, delta = date_ok(ticker, sched_start)
    delta_h = delta / 3600 if delta else 0
    status = "PASS" if not ok else "FAIL"
    print("  [%s] %-40s vs %-22s date_ok=%-5s delta=%.1fh" % (status, ticker, sched_start, ok, delta_h))

# Test 2: Same-day normal matches
print()
print("=== TEST 2: APR25 ticker matched against APR25 schedule (NORMAL CASE) ===")
print("Expected: date_ok=True for all (same-day match)")
print()
test_cases_2 = [
    ("KXATPMATCH-26APR25SOMPLR", "2026-04-25T09:00:00Z"),   # 5am ET
    ("KXATPMATCH-26APR25SOMPLR", "2026-04-25T13:00:00Z"),   # 9am ET
    ("KXATPMATCH-26APR25SOMPLR", "2026-04-25T22:00:00Z"),   # 6pm ET
    ("KXATPCHALLENGERMATCH-26APR25ONCHEM", "2026-04-25T17:40:00Z"),  # 1:40pm ET
    ("KXWTAMATCH-26APR25BAPPAO", "2026-04-25T12:00:00Z"),   # 8am ET
]
for ticker, sched_start in test_cases_2:
    ok, delta = date_ok(ticker, sched_start)
    delta_h = delta / 3600 if delta else 0
    status = "PASS" if ok else "FAIL"
    print("  [%s] %-40s vs %-22s date_ok=%-5s delta=%.1fh" % (status, ticker, sched_start, ok, delta_h))

# Test 3: Edge case - same day but UTC crosses midnight
print()
print("=== TEST 3: Edge cases - timezone boundary ===")
print("APR24 ticker, 16:00 UTC anchor = APR24 noon ET")
print("12h window = APR24 04:00 UTC to APR25 04:00 UTC")
print()
test_cases_3 = [
    ("KXATPMATCH-26APR24SOMPLR", "2026-04-25T03:00:00Z", True,  "APR24 11pm ET, within 12h window"),
    ("KXATPMATCH-26APR24SOMPLR", "2026-04-25T04:00:00Z", True,  "APR25 midnight ET, exactly at 12h boundary"),
    ("KXATPMATCH-26APR24SOMPLR", "2026-04-25T05:00:00Z", False, "APR25 1am ET, 13h from anchor -> rejected"),
    ("KXATPMATCH-26APR24SOMPLR", "2026-04-24T03:00:00Z", False, "APR23 11pm ET, 13h before anchor -> rejected"),
    ("KXATPMATCH-26APR24SOMPLR", "2026-04-24T04:00:00Z", True,  "APR24 midnight ET, exactly at -12h boundary"),
    ("KXATPMATCH-26APR24SOMPLR", "2026-04-24T16:00:00Z", True,  "APR24 noon ET, delta=0"),
]
for ticker, sched_start, expected, desc in test_cases_3:
    ok, delta = date_ok(ticker, sched_start)
    delta_h = delta / 3600 if delta else 0
    status = "PASS" if ok == expected else "FAIL"
    print("  [%s] %-22s delta=%5.1fh  date_ok=%-5s  expected=%-5s  %s" % (
        status, sched_start, delta_h, ok, expected, desc))

# Test 4: No date in ticker (defensive)
print()
print("=== TEST 4: No date in ticker (defensive path) ===")
ok, delta = date_ok("KXWEIRDTICKER", "2026-04-25T09:00:00Z")
status = "PASS" if ok else "FAIL"
print("  [%s] No regex match -> date_ok=%s (should be True, allow match)" % (status, ok))

# Summary
print()
print("=== SUMMARY ===")
all_tests = test_cases_1 + test_cases_2
pass_count = 0
fail_count = 0
for ticker, sched_start in test_cases_1:
    ok, _ = date_ok(ticker, sched_start)
    if not ok: pass_count += 1
    else: fail_count += 1
for ticker, sched_start in test_cases_2:
    ok, _ = date_ok(ticker, sched_start)
    if ok: pass_count += 1
    else: fail_count += 1
for ticker, sched_start, expected, desc in test_cases_3:
    ok, _ = date_ok(ticker, sched_start)
    if ok == expected: pass_count += 1
    else: fail_count += 1
# test 4
ok, _ = date_ok("KXWEIRDTICKER", "2026-04-25T09:00:00Z")
if ok: pass_count += 1
else: fail_count += 1
print("  Passed: %d  Failed: %d" % (pass_count, fail_count))
