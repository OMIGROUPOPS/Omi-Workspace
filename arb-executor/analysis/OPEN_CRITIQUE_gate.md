# OPEN CRITIQUE — the gate is not lockable as a constant (for adversarial review)

Framing (user, standing): this is STILL just the exit problem on the WORST-CASE T-20 entry
floor. No Part 2 discounts yet. "What would Jim Simons do" — don't rubber-stamp convergence;
try to break it. Everything stays on the table.

## What's robust
Within-regime jumps sit at a stable **4** across floor∈[0.05,0.10], any npos∈{2,3,5}.
So "4 survivors" is a real basin, not a cherry-pick. Good.

## What BREAKS the lock (the critique neither agent has answered)
Sweep the gate threshold:
```
 floor  npos  within-jumps  nHOLD
 0.05    3       4          19
 0.10    3       4          35
 0.20    3       0          71   <-- "perfect continuity" by gating 71/90 to HOLD
```
**Continuity → 0 is achievable simply by declaring most of the surface dead.** Therefore
continuity alone CANNOT be the objective — it is trivially gamed by over-holding. We are
currently picking floor=0.05 by eye. That is an unjustified free parameter sitting on a
slope that trades coverage for smoothness with no principled stopping point.

## The deeper coupling (T-20)
Every EV here is at the pessimistic T-20 entry price. A cell gated to HOLD today (EV≈0 at full
price) is exactly the kind of cell that goes LIVE once a Part 2 entry discount drops its cost
basis. So:
  - the gate threshold is NOT a constant — it is a function of an entry price we have not set;
  - a "safe" high gate today silently discards the cells most likely to become the engine later
    (cheap-underdog deep-bounce cells — the doctrine's "engine", not the "ballast").

## Questions for adversarial review (Opus + agent, both attack)
1. **What is the second axis?** If continuity is gameable by holding everything, what objective
   pins the gate? Candidates: (a) maximize Σ deployed-capital·EV subject to a continuity ceiling;
   (b) gate on a STATISTICAL conviction test (is peak score distinguishable from the cell's own
   noise floor at some confidence) rather than an absolute number — makes the gate scale-free and
   T-20-invariant; (c) coverage floor (≥X% of cents must emit a live config).
2. **Is the gate even the right object, or a symptom?** A cell with EV≈0 at T-20 isn't dead — it's
   priced-to-the-floor. Should "HOLD" instead be "PARK — re-evaluate at entry price" so Part 2
   reactivates it, rather than a permanent silence?
3. **Does option (b) — distinguishable-from-own-noise — make floor=0.05 disappear** as a free
   parameter and survive the T-20→discounted-price shift unchanged? That's the test that would
   make this lockable rather than tuned.
4. **Steelman the over-hold:** is there a regime where gating 35–71 cents to HOLD is actually
   correct at the T-20 floor (i.e., you genuinely shouldn't trade most cents until discounts land)?
   If so, the "engine" only switches on in Part 2 and the exit surface today is mostly ballast.
   That's a strategy statement, not a bug — but we should say it out loud.
