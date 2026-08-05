# Window-1 V31 dip-pressure governor — 2026-08-05

V31 is a repair-with-earned-authority on V29-R3. The six causal bands use the e64b0837 120-second EWMA definition. The governor never creates a BUY and never assigns role: immediately before an incumbent or mirror BUY already authorized by R3, a category with earned walk-forward authority may demote a HIGH-pressure buy to a strictly lower resting target. LOW pressure and every category without earned authority are byte-identical to R3.

Authority is earned only when held-out HIGH-pressure precision exceeds the held-out category base rate by at least five percentage points and has at least 20 HIGH calls. The threshold and pressure-implied deeper-floor drop are learned only from chronologically prior decisions. No clock is a policy input.

R3 JOINT floor: 68. V31 JOINT: 67. Changed legs: 26; unchanged semantic-hash-identical legs: 1582. Deeper fills: 7; demoted then lost: 19. Joint gained: 0; joint lost: 1.

**VERDICT: REJECTED — JOINT REGRESSION; V29-R3 REMAINS OPERATIVE.** Test PASS means the receipt is internally valid, not that the candidate is ratified.

ARNROM|ROM at 42: pressure=LOW, authority=false, disposition=UNTOUCHED, final entry=42.
