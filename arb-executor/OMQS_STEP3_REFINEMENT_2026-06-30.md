# OMQS STEP 3 — PEAK-THEN-REVERSE REFINEMENT (Jun 24–29 held-out) → STOP signal

Source: Kalshi /markets/trades tick-tape, 588 gun-detected settled legs Jun 24–29 (held-out). Refinement of Step 2's peak-then-reverse discriminator to a TIGHT (Step-1-like) rule. FOUR gates, ALL must pass: (a) NET +ve EVERY day, (b) plateau robustness, (c) fire rate 20–40%, (d) NET ≥ +$300/wk. MEASUREMENT ONLY. Step 1's shadow run was NOT gated on this (ran in parallel).

---

## REFINEMENT 1 — confirmed-clean post-peak monotonic

Fire iff: giveback X¢ from running peak AND post-giveback monotonic-down for M min (no re-print above the confirmation level). Re-peakers spared. Swept X∈{5,8,10,12}, M∈{10,15,20,30}, confirmation level ∈ {peak−X/2, peak−X}.

**Result: FAILS gates (a) and (d) in EVERY cell.** Best total NET = **+$3.5** (X=5,M=30,level); most cells **negative**. No cell positive-every-day (best 4/6). Fire rate often hit the 20–40% band (gate c), but NET is ~$0/negative — the discriminator earns nothing.

Representative (confirmation = peak−X/2):
```
 X   M  | TOTAL$  fire%  +days  min-day$
 5  10  |   +3.0  32.0%  4/6     -8.6
 8  15  |  -19.8  34.2%  2/6     -9.4
10  20  |  -31.1  32.3%  1/6    -10.9
12  15  |  -40.0  39.6%  1/6    -19.8
```

## REFINEMENT 2 — confirmed-clean monotonic GATED on peak-gain ≤ Y

Adds the secondary gate (only fire if peak ≤ fill+Y; ERHROD peaked +14). Swept Y∈{8,12,16,20,∞}.

**Result: ALSO FAILS (a) and (d).** Best total NET = **+$0.7** (X=5,M=10,Y=8); fire rate now sits squarely in the 20–40% discriminator band — but NET stays ~$0/negative, no cell positive-every-day (best 4/6).
```
 X  M  Y  | TOTAL$  fire%  +days
 5 10  8  |   +0.7  20.1%  4/6
 5 10 12  |   +0.4  23.5%  3/6
 8 10 12  |  -17.1  28.7%  1/6
```

---

## WHY IT FAILS — the irreducible selectivity-vs-save tension

Step 2's high-NET version (trail-stop at the giveback level, +$591/wk) fires on **81%** of legs because it cuts on **every** pullback — it cannot tell a will-die reversal from a will-re-peak wobble at the trigger instant, so it cuts both. To become a **discriminator** (spare the re-peakers, drop fire rate to 20–40%) you must **confirm** the reversal — wait M minutes of monotonic-down. **But the ERHROD reversals are FAST (84→0); by the time M minutes of decline have confirmed it, the price is already near the bottom, so the flatten happens low and the save evaporates.** The discriminating information (die-or-re-peak) only arrives *after* the price has already fallen.

So: **high save XOR low fire rate — you cannot have both.** This is unlike Step 1's one-way knives, which are discriminable AT THE GUN (no peak masks them; you see the monotonic fall from entry early and flatten at fill−10, a high level). The peak-then-reverse class hides the reversal behind the peak until it has already paid out.

---

## VERDICT — STOP tape-discriminators; the band-asymmetric exit is the structural lever

Per the locked decision tree: **(1) and (1)+(2) both fail the every-day gate AND the NET-floor gate → STOP iterating on tape-discriminators.** The peak-then-reverse class (ERHROD, −$648/wk, 65% of the loss) is **not real-time tape-discriminable** — the selectivity needed to be a clean rule destroys the save.

This is a **different problem class.** The lever moves to the **band-asymmetric exit itself**:
- **Per-cell band recalibration** — the May sealed exit surface is the CURRENT DEPLOYED config, NOT proof it is optimal (per the JUNE_VAULT date-caveat discipline). The ERHROD legs are high-fill favorites whose +band is structurally unreachable on reversal; a tighter / asymmetric band on those cells may net positive where a tape-cut cannot.
- **Band-asymmetric flatten on peak-gain magnitude** — set the exit/flatten as a function of fill price (favorites get a tighter band or a hard downside), decided AT ENTRY (no confirmation-wait), so the save is captured before the fall.

Do NOT force a marginal tape-rule through. Cut #1 (monotonic, shipped `b1aaef9`) stands as the only tape-discriminable lever; the ERHROD residual is an exit-geometry problem, not a tape-timing problem.
