# Window-1 Cursor Convergence State

Read-only reconciliation for Claude Chat / Fable, Cursor Codex, Cursor Claude Code, and the operator.

State observed: 2026-07-27 at approximately 20:25 ET. No code, live state, orders, positions, benchmarks, candidates, or research artifacts were mutated during this census. Process state may change after the observation time.

## Executive answer

Claude Chat is correct that no Round-4 research artifacts landed on `blend/kalshi-occ-fallback`. That branch is the live/operations lane. Window-1 research proceeded on:

- `codex/window1-definition` for frozen implementations and deterministic executions.
- `audit/window1-independent` for independent Claude Code audits.

The current next-generation research package is T2 causal-divot. Its files have been generated locally in the Cursor Codex research worktree, but at the observation time they remain uncommitted and unpushed. Therefore:

- T2 is not yet a version-frozen PRE-RUN.
- T2 has not received an independent Claude Code PRE-RUN audit.
- No T2 scoring package or scoring execution is authorized.
- No T2 benchmark is running.

The current T2 report calls itself a frozen score-free build, but Git is controlling: every T2 file is still untracked. It is generated, not version-frozen.

The standing live halt at `058282b9` remains the higher-priority operational issue. CASUKA-CAS has three excess resting exits, FARRIU is pair-incomplete, and the halt has not been cleared by a passing re-audit. Cursor Claude Code should own immediate read-only reproduction of CASUKA; any code repair should be implemented separately by Cursor Codex in a clean live-safety worktree and returned to Claude Code for independent audit.

## Branch and artifact state

| Lane | Branch / location | Observed tip or state | Purpose |
|---|---|---:|---|
| Live / operations | `origin/blend/kalshi-occ-fallback` | `b060dabacad7bd384cf01b6490da8b529db3474c` | Nightlies, today sheets, live halt and operational records |
| Window-1 implementation | `origin/codex/window1-definition` | `d710ba0606084f67625e255e87ebad1cd016bf6a` | Frozen research implementations and T1 results |
| Independent audit | `origin/audit/window1-independent` | `33ae7350f1bd67387146acae51951f0b76d52313` at census start | Independent audit findings and PASS/BLOCK rulings |
| T2 local generation | `C:\Users\omigr\OMI-Workspace-codex-w1-range-attack-v2-execution` | Untracked T2 additions | Current Cursor Codex research worktree |

The T2 local artifacts are:

- `.claude/window1_t2_causal_divot_prerun_20260727/PRE_RUN_MANIFEST.json`
- `.claude/window1_t2_causal_divot_prerun_20260727/PRE_RUN_REPORT.md`
- `.claude/window1_t2_causal_divot_prerun_20260727/MECHANISM_STATUS_TABLE.json`
- `arb-executor/analysis/window1_t2_causal_divot_instrument.py`
- `arb-executor/analysis/window1_t2_causal_divot_prerun.py`
- `arb-executor/docs/research/window1/WINDOW1_T2_CAUSAL_DIVOT_CANDIDATES_V1.json`
- `arb-executor/tests/test_window1_t2_causal_divot_prerun.py`

The canonical Living Vault at `arb-executor/docs/LIVING_VAULT.md` has a local 123-line edit in the independent-audit worktree. It is on the Cursor filesystem but is not committed or pushed. It must not be treated as remotely published or controlling until separately reconciled and committed.

## Job / owner / status table

| Job | Owner | Status at approximately 20:25 ET | Start / completion | ETA | Blocker |
|---|---|---|---|---|---|
| T2 source and artifact generation | Cursor Codex | Generation finished; all T2 files still untracked | Source writes began about 19:45 ET; artifacts finished about 20:11:52 ET | Complete as a local build only | Focused test, full validation, deterministic regeneration, commit and push |
| T2 focused test | Cursor Codex | Running: PID 25312, `python -B -m pytest arb-executor/tests/test_window1_t2_causal_divot_prerun.py -q` | Started 20:12:31 ET; responsive with about 13 minutes CPU at last check | No defensible ETA encoded by the process | Must exit successfully before further validation |
| T2 full relevant test suite | Cursor Codex | Waiting | Not started | Unknown | Focused test |
| T2 deterministic regeneration and byte comparison | Cursor Codex | Waiting | Not started | Unknown | Tests |
| T2 commit and push | Cursor Codex | Waiting | Not started | Unknown | All local validation and clean scope checks |
| T2 independent PRE-RUN audit | Cursor Claude Code | Not started | N/A | Unknown | Requires a committed, pushed T2 SHA |
| T2 scoring package | Unassigned until PRE-RUN PASS | Not authorized or running | N/A | N/A | Independent PRE-RUN PASS |
| T2 scoring execution / benchmark | Unassigned until package PASS and explicit authorization | Not authorized or running | N/A | N/A | Audited scoring package and one-execution authorization |
| Substrate build | None | Not running | N/A | N/A | None scheduled |
| Backfill | None | Not running | N/A | N/A | None scheduled |
| Tuning lap | None | Not running | N/A | N/A | No audited/scored T2 package |
| Autonomous nightlies | Live/ops automation | Earlier jobs completed; no long-running nightly observed | Earlier July 27 | Complete | N/A |
| CASUKA/FARRIU live-halt reproduction | Cursor Claude Code should own | No active reproducer observed | Not started | Immediate priority; no honest completion ETA yet | Must reproduce frozen orders/positions and re-audit halt causes |

The Cursor Claude Code terminal was open, but no active child audit job was observed. It was waiting for an assignment.

## T2 frozen-contract status

The local T2 manifest declares:

- Exact parent: `d710ba0606084f67625e255e87ebad1cd016bf6a`
- Controlling T1 results audit: `33ae7350f1bd67387146acae51951f0b76d52313`
- D = 804 for each of eight candidates
- 6,432 candidate/event overlays
- 4,576,794 target-surface rows
- 2,996,560 lawful sibling-X observations
- 166,644 recognized divots
- 176,435 later recurrences
- 140 later-divot actions
- 81 cases with still-later independent fill evidence
- 274 evidence-decay replacements
- 38,061 lawful positive-d2 target constructions
- 54 positive-d2 targets actually exposed
- `scored: false`
- `benchmark_execution_authorized: false`
- C, PC, IC, S, and all performance fields null

These are local construction claims, not independently audited findings.

### Candidate matrix

Under each of the macro-hold and macro-micro parent regimes, T2 contains:

1. Fixed-admission parent control.
2. Non-displacing target completeness.
3. Target completeness plus evidence decay.
4. Full causal-divot stack: response, target completeness, evidence decay, and recurrence.

The local contract claims no free numeric parameters. It explicitly retracts T1 unconditional persistence, the inert response-only label, and automatic positive-d2 `bid+1` preference.

## Mechanism manifest

### BOUND

1. Positive-size true prints.
2. Nonself BBO and top-five depth.
3. Trendpath Atlas discovery.
4. Limited LIVE_AIM mapping.
5. Guidebook deep tier.
6. Positive-print microdivot.
7. Causal later recurrence.
8. Pair combined headroom.
9. Timestamped policy clock.
10. External-ask maker safety.
11. Non-displacing target completeness.
12. Causal evidence-decay exit.

### PROXIED

1. Carried last trade.
2. Standalone volume direction.
3. Top-five pressure sign.
4. Close-keyed recut.
5. Taker reach.
6. Drift surfaces.
7. Band map.
8. Divot tables.
9. Library timing.
10. Orientation consumer.

### ABSENT

1. Pinnacle.
2. Authoritative bookmaker / fair-value surfaces.
3. Full depth beyond top five.
4. Independent shape mapping.

### RETRACTED

1. Moving-bid edge.
2. Universal 50 split.
3. Last-trade direction gate.
4. Pressure/taker direction gate.
5. Borrowed sealed pair shape.
6. T1 unconditional persistence.
7. T1 inert response-only label.
8. Automatic positive-d2 `bid+1` preference.

## Critical binding correction

T2 does not bind the complete live conception/dial pipeline. It is a post-first-fill research overlay, and its candidate contract leaves first-leg behavior unchanged. It imports frozen Range-Attack and T1 research instruments rather than the complete live engine.

| Live conception / OS component | Current T2 status |
|---|---|
| Full conception cascade | Not bound |
| Cohort steering | Not explicitly bound |
| Reach | Proxied |
| Catch | Divot tables proxied; print microdivot and causal recurrence bound |
| Orientation | Proxied |
| Walk / park | T2 has receipt-backed HOLD / REPRICE / PARK states, but equivalence to the complete live walk/park laws is not proven |
| Print-triggered, walk-cap-bounded, queue-preserving ladder | Partial components present; complete live binding not proven |
| Recognition re-calls | Bound through causal recurrence |
| Corridor tiers | Not explicitly bound; only the timestamped policy clock is bound |
| Volume / cadence | Recorded, but standalone causal authority is proxied |
| Depth | Top-five bound; depth beyond top five absent |
| Pinnacle / bookmaker fair value | Absent |

An independent Claude Code audit must challenge any claim that the full OS is bound.

## Date law

The current research development population remains July 12–20 with D = 804. July 24–26 holdout access remains sealed.

The local T2 manifest does not encode a July 12–17 fit versus July 18–20 post-slice verdict split. No T2 scoring contract exists. If the operator requires that split, it must be frozen into the contract and independently audited before any scoring execution.

## What the research has accomplished

1. Round 3 fixed sibling-never-placed. Its best frozen candidate achieved PC = 6/804. Posted-but-unfilled partners then became the dominant observed failure.
2. The first Round-4 macro×micro package at `84959172` was independently blocked by audit `9a0177af` for bid-relative targeting, flattened category physics, unused volume/cadence claims, and repricing/action-law defects.
3. Range-Attack repaired key measurement failures:
   - Price-at-X print law.
   - Cumulative-five false negatives.
   - Strict-ask credit before maker-safety repricing.
   - Exact-five numeric validation.
   - Named reference ambiguity.
   - Deterministic scoring.
4. The independently audited Range-Attack results were:
   - Macro-hold: C = 132, PC = 116, IC = 38, S = 101.
   - Macro-micro: C = 125, PC = 111, IC = 36, S = 96.
5. The asynchronous census found 6,501 lawful later sibling episodes. It found recoverable later opportunities for 22/237 macro-hold naked rows and 25/240 macro-micro naked rows. Much positive second-leg delta was lawful only because the first leg financed it.
6. Decision-layer attribution localized missing or harmful behavior to inert first-fill response, target omissions, moved-away reprices, policy-horizon/corridor termination, and unresolved capacity.
7. T1 froze and independently audited eight post-first-fill candidates, their scoring package, and their one authorized execution.
8. T1's causal result was:
   - Response-only was a behavioral no-op.
   - Target completeness added three PC events per parent regime but displaced five prior successes.
   - Persistence destroyed 23 macro-hold and 20 macro-micro PC outcomes.
   - The full stack destroyed 28 macro-hold and 23 macro-micro PC outcomes.
   - Eighty-two lawful positive-d2 `bid+1` targets produced zero fills.
9. T2 is the uncommitted response to those causal findings: non-displacing target completeness, evidence-decay exits, a full causal sibling-X surface, and later recurrence.

The 15–16% completion rates from earlier candidate results are not a statement that both legs must be bought simultaneously, not a market ceiling, and not an opportunity census. They are outcomes of those specific frozen candidate policies and their measurement contract.

## Why nothing appears on `blend/kalshi-occ-fallback`

This is deliberate lane isolation, not absence of work:

- `codex/window1-definition`: research implementation and deterministic results.
- `audit/window1-independent`: independent audit and authorization.
- `blend/kalshi-occ-fallback`: live operations, nightlies, today sheets, and halt records.

Since July 24, the blend lane contains live operational activity rather than Window-1 research packages. Round-3 audit `25735d9c9d9775a122da2a067962f45312aa62dc` belongs to the audit lineage, not the blend branch ancestry.

## Standing live halt

Controlling halt:

- Commit: `058282b99cfb4da702ad85528750232f07f2c1b4`
- Artifact: `.claude/audit_halt/AUDIT_HALT_20260727_133309.md`
- State: conceptions frozen; exits may continue; halt clears only after a passing re-audit.

Known incidents:

- CASUKA-CAS: five contracts held with eight resting exits, producing three excess sell orders.
- FARRIU: FAR absent while RIU filled; pair incomplete.
- VEGKAW: VEG filled while KAW absent.

A later 16:00 today sheet showing zero open/post entries does not itself clear the halt. No passing re-audit or explicit clear was found.

### Ownership

- Cursor Claude Code: immediately reproduce and audit CASUKA-CAS, then the pair-incomplete incidents, read-only.
- Cursor Codex: finish or safely stop the currently running T2 focused test; retain ownership of the T2 research lane.
- If reproduction establishes a live-engine code defect, Cursor Codex should implement the narrow repair in a separate clean live-safety worktree.
- Cursor Claude Code should independently audit that repair before any halt clearance.
- The T2 research worktree must not be used for the live incident.
- No cancel, order mutation, position mutation, conception restart, or halt clearance is authorized by this reconciliation.

CASUKA outranks further research execution. T2 may finish its local validation, but no T2 scoring execution should proceed while the live halt is unresolved.

## Precise convergence sequence

1. Cursor Claude Code reproduces CASUKA-CAS from frozen order and position evidence and reports whether the three excess exits are ledger, engine, or reporting behavior.
2. If code change is required, Cursor Codex performs only that live-safety repair in an isolated worktree; Claude Code independently audits it.
3. The live halt remains until its controlling re-audit passes.
4. Separately, Cursor Codex allows the active T2 focused test to finish, then runs the full tests and deterministic regeneration.
5. Only after those pass does Cursor Codex commit and push the T2 PRE-RUN as one contained SHA.
6. Cursor Claude Code audits that exact T2 SHA, including the BOUND / PROXIED / ABSENT / RETRACTED table and the incomplete live-pipeline binding.
7. Only after a T2 PRE-RUN PASS may a separate scoring package be constructed. Fit/post-slice law must be frozen first if the operator requires it.
8. The local Living Vault edit must be separately reconciled against this chronology, then committed and pushed as its own reviewed change.
