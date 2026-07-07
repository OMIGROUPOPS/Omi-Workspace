# KNOWLEDGE INVENTORY — 2026-07-07 (Phase 1 of the consolidation)

**Method:** full walk of both branches (`blend/kalshi-occ-fallback` working tree + `origin/blend/agent-derivation` via git show), every knowledge artifact cataloged (docs/, docs/policy/, docs/handoffs/, .claude/ rulings/autopsies/proofs/live-boards/nightlies/overnights, analysis READMEs). Per item: topic · last real update · judgment (CURRENT / SUPERSEDED-BY / FROZEN-HISTORICAL / CONTRADICTED / STAGED-NEVER-ARMED). Judgments are mine, dated today; the catalogs beneath are as-found.

## 0 · THE VERDICT SHAPE (what Phase 2 merges)

- **The living surfaces (the spine-to-be):** `docs/LESSONS.md` (A–G + C39–C49, current through today) · `JUNE_VAULT.md` on agent-derivation (canonical through §0E, 2026-07-06) · `.claude/PRIOR_ART_INDEX.md` · `.claude/rulings/` (14 files, all current law) · `WEEK_STANDING_ORDER.md` (07-05→07-12) · `SLATE_LEDGER_20260706.md` (refreshed in place today — THE book) · `LIVE_STATUS.md` (monitor, rolling) · today's `FORENSIC_20260707_MORNING.md` + `BLEED_ATTRIBUTION_20260707.md`.
- **The fork:** ROADMAP.md and SESSION_HANDOFF.md died quietly (frozen 06-01 / 06-05 on BOTH branches) while the Vault became the de-facto handoff — and the Vault itself lives on a branch the deploy tree can't see without a URL. Phase 2 kills the fork: LIVING_VAULT.md + BOARD.md on the deploy branch, tombstones everywhere else.
- **Two VAULT_PENDING docs** (`aim_table_doctrine` 07-03, `retention_fix` 07-06) never merged anywhere — Phase 2 absorbs them into LIVING_VAULT.
- **One standing contradiction:** `.claude/autopsy_20260707/VERIFY_20260707_0230.md` ("ex-self fields ABSENT / deploy never completed") is **REVERSED** by `BLEED_ATTRIBUTION_20260707.md §4` (1,668 jsonl occurrences from 02:34:33 ET; console-truncation artifact; C47). The VERIFY doc stands as the exhibit of the measurement failure, not as fact.

## 1 · JUDGMENTS ON THE MAJORS

| artifact | last update | judgment |
|---|---|---|
| docs/LESSONS.md (local) | today (C49) | **CURRENT — the principles ledger.** Joins the spine read-order. |
| JUNE_VAULT.md @agent-derivation | 07-06 (§0E) | **CURRENT content, WRONG home.** §0A/0B–0E, §1, §4E–4I, §5–8 merge into LIVING_VAULT; file FREEZES as the June archive. |
| JUNE_VAULT.md (local) | 07-02 | Already a stub → gets the FROZEN tombstone. |
| JUNE_VAULT_APPENDIX.md @deriv | 07-01 | FROZEN snapshot by design (anti-re-derivation archive @8299ca25). Stays; tombstone header added. |
| docs/ROADMAP.md (both branches) | 06-01 | **SUPERSEDED** by Vault + WEEK_STANDING_ORDER + BOARD.md (Phase 2). Tombstone. T/F/U/G/D open items that still matter re-enter via BOARD. |
| docs/SESSION_HANDOFF.md (both) | 06-05 | **SUPERSEDED** by Vault read-first protocol; its "live-state entry instrument" flag became the aim-table arc (lineage noted in LIVING_VAULT). Tombstone. |
| docs/CHAT_HANDOFF.md | 05-21 | Already stubbed into SESSION_HANDOFF — double-dead; no action needed beyond the SESSION_HANDOFF tombstone. |
| .claude/PRIOR_ART_INDEX.md | living | **CURRENT** — serves C45; Phase 3 adds LESSONS A–G ledgers explicitly to its mandatory grep surface. |
| .claude/rulings/* (14) | 07-05→07-07 | **CURRENT LAW.** PLEX_REANCHOR_RULING body still owed by relay (open slot, tracked on BOARD). |
| SLATE_LEDGER_20260706.md | today | **CURRENT — THE book.** Supersedes TRADE_ROLL_20260706 + TRADE_ROLL_BODY (its own header says so) and retires the autopsy P&L convention (CUT A divergence, named in §3). |
| AUTOPSY_20260706.md + VIOLATIONS_DEEPCUT | 07-06 | Findings CURRENT (mechanisms proven; "newer beats older" self-declared); its P&L counting convention RETIRED by the ledger. |
| proof_20260705/TIME_AXIS_PROOF.md | 07-05 | Verdict DOES-NOT-SHIP stands; superseded as method by ONE_AIM_FIX + AIM_V2 (bell-bucket rebuild). |
| VERIFY_20260707_0230.md | 07-07 02:30 | **CONTRADICTED** (see §0). Keep as the C47 exhibit. |
| VAULT_PENDING_aim_table_doctrine.md / VAULT_PENDING_retention_fix.md | 07-03 / 07-06 | UNMERGED pendings → absorbed into LIVING_VAULT (Phase 2), then tombstoned as merged. |
| docs/policy/range_final_* + canonical_tree + join_trial_abort (also duplicated at .claude/ top level) | 06-15-era | CURRENT policy where sealed (SEAL, abort specs); the `.claude/` copies are working duplicates — **canonical home = docs/policy/**, duplicates noted, not deleted this pass. |
| S0_GATE_RESULT.md / S0_GATE_V2_RESULT.md | Jun 19–22 tape | HALT verdicts STANDING — the OMQS scoring harness never passed S0; any S1–S5 claim would be uncredentialed. |
| ACTIVATION_CHECKLIST_STAGED.md / README_STAGED.md (floor-reel) + reprice_signal5 spec | undated | **STAGED-NEVER-ARMED prior art** (C45 explicitly requires checking these before any same-shape build). |
| EPOCH.md | 06-10 | CURRENT baseline anchor (exchange-truth pinned). |
| SIMONS_MODE.md / TAXONOMY.md / ANALYSIS_LIBRARY.md | 05-06/14 | CURRENT reference (ANALYSIS_LIBRARY carries its own FOUNDATION-REBUILD provisional banner). |
| May design-era specs (layer_b/_v2/_c, rung0, rung1, per_minute_universe, n_profile, t38 daemon, u4_phase3, bot_v5 shell, strategy_b, fv_state, bounce specs, forensic_replay, bug4 pair) | 04-29→05-19 | **FROZEN-HISTORICAL SPECS** — atlas/foundation lineage, dormant, none superseded by name but none current work; build only through prior-art. bug4's operational half remains a known-open (F28). |
| docs/handoffs/ 2026-05-24→27 family (cell bands, entry rules, drift envelopes, paired-R, exit swaps, v6 deploy records) | 05-24→27 | FROZEN-HISTORICAL — the pre-fork exit/entry surface work; outcomes sealed into `exit_surface_gated_optima/LOCKED_DOWN.md` + staircase SEALs. v6_deploy_record supersedes its own staged plan (self-noted). |
| handoffs 06-09→11 (entry_completion part1/replay, completion_reprice part2, c_p0_race) | 06-09→11 | CURRENT lineage docs for shipped mechanisms (completion_reprice armed 06-30; race fix live). |
| overnight/nightly/proof/live forensic reports (07-03→07-07) | this week | CURRENT evidence record, chronological; superseded only where a newer doc names it (TIME_AXIS → ONE_AIM_FIX; VERIFY → BLEED §4). |
| dead_ends/README.md | undated | Already the graves model for analysis artifacts — LIVING_VAULT's RETIRED section is its doc-level counterpart. |
| BLUEPRINT_README.md (April) + exit_charts findings (06-02 "do NOT deploy") | Apr/Jun | FROZEN-HISTORICAL; the do-NOT-deploy verdict stands. |
| .claude/audit_halt/*.md (13) | today | Auto-generated alert artifacts (C47-ENFORCE); operational record, not knowledge — retention policy can prune >7d. |

## 2 · CATALOG — local branch (as-found, agent walk)

### 2a · arb-executor/docs (33) + policy (8) + handoffs (55)
See per-file lines below (topic | date | own status markers), judgments per §1 classes.

- **docs/ top level:** ANALYSIS_LIBRARY (05-14, provisional banner) · bid_laying_policy_v1 (05-23, Canonical; §3 table superseded by v2 offsets) · bot_v5_shell (draft) · bug4_brief/probe (locked design/probe) · CHAT_HANDOFF (stub) · EPOCH (06-10) · exit_optimized_bounce_v1 (draft) · forensic_replay_v1 (spec) · fv_state_strategy_v1 (spec) · inmatch_bounce_surface_v1 (draft) · JUNE_VAULT (stub) · layer_b / layer_b_v2 / layer_c (specs) · LESSONS (living) · n_profile_v1 (draft) · per_minute_universe (spec) · README (05-21; "bot PAUSED" line stale — bot LIVE since 05-25: superseded statement) · rebuild_vs_paper_diff (report) · ROADMAP (frozen) · rung0 (v1.1) · rung1 (v0.3.2) · SESSION_HANDOFF (frozen 06-05) · SESSION10_HANDOFF (frozen) · SIMONS_MODE (canonical) · strategy_b_v1 (spec) · t38_books_daemon (draft) · T51_HARDENING (design; its wrong-clock buffer finding folded into the 07-05 clock audit) · TAXONOMY (05-14) · u4_phase3 (draft) · VAULT_PENDING ×2 (unmerged).
- **docs/policy:** canonical_tree (branch law — Phase 2 AMENDS: deploy branch carries the living spine) · exclusion_regime_v1 (06-10, ratified) · join_trial_abort (LOCKED; trial itself ended 06-18 — spec historical) · range_final abort/validation/seal/gated/caller-contract (06-15 seals: SEALED/ratified; caller contract propose-only).
- **docs/handoffs:** May-26/27 cell-band + entry-rule + drift-envelope + paired-R family (FROZEN-HISTORICAL, all carrying their own raw_max/in-sample caveats; paired_R verdict "NO real edge — DO NOT switch" stands) · exit remeasurement/swap/v6-deploy arc (v6 LIVE record supersedes staged) · c_p0_race (06-11, shipped) · completion_reprice part2 (06-10, armed 06-30) · entry_completion part1+replay (06-09/10; replay supersedes bbd88feb economics) · session_06→09 handoffs (frozen) · EXECUTION_PHASE_HANDOFF (ARCHIVED) · pre_deploy_bug_checklist (05-24; P0 gate — superseded in practice by deploy_gate.sh law C40/C46) · live_v3_v4_inventory, tape_audit, deployment_state_check (frozen evidence).

### 2b · .claude knowledge trees
- **top level:** PRIOR_ART_INDEX (living) · FORENSIC_20260707_MORNING + BLEED_ATTRIBUTION (today) · INVENTORY.md (this file) · floor-reel STAGED pair + reprice_signal5 (staged-never-armed) · S0 gate results ×2 (HALT standing) · seal_addendum/seal_append (ruling fragments — fold into rulings/ awareness; content current) · BLUEPRINT_README (April, historical) · policy duplicates ×7 (canonical home docs/policy) · canonical_tree duplicate.
- **rulings/ (14):** AIM_V2_SPEC · FLIP_REQUEST_PER_MATCH_CLOCK · OPERATOR_RULING_2C_BRANCH · OPERATOR_RULING_B_SUBGRADES · PART1_GATE_EVIDENCE · PART1_SPEC · PLEX_AIM_V2_RULING · PLEX_EXPRESSION_INVARIANT · PLEX_FLIP_RULING (#20) · PLEX_PART1_SOURCE_RULING · PLEX_REANCHOR_RULING (**slot open — body never relayed**) · PLEX_REGRESSION_RULING · POST_FLIP_AUDIT · PRIOR_ART_GATE (C45 law). All CURRENT.
- **autopsy_20260706 (12):** AIM_V2 build + operational reports (GATED-OFF) · AUTOPSY (chronological authority; P&L convention retired by ledger) · B3_DISCOUNT_COUNTERFACTUAL (11¢-missed-lows; doctrine source) · BELL_FEASIBILITY (65% detection gate) · ENTRY_CENSUS (AX2 struck + reissued role-relative) · LIVE_QUEUE (riser DISARMED) · ONE_AIM_FIX (supersedes TIME_AXIS method) · SAME_TICK_RACES · START_TIME_JOIN ("tape is the only start-time source") · TRADE_ROLL_BODY (superseded by ledger) · VIOLATIONS_DEEPCUT.
- **autopsy_20260707 (2):** SPREAD_EXPRESSION census (below-chain 54%@9.1% fill — doctrine source) · VERIFY_0230 (**CONTRADICTED**, kept as C47 exhibit).
- **live_20260705 (11):** CAUSAL_AUDIT (C44 method) · four FORENSIC_<class> defect files (live-defect record; walk_cap/combined_over_goal fixed by later builds — status per SLATE) · LIVE_STATUS (rolling) · NIGHTLY_PASS (standing runbook) · SLATE_LEDGER (THE book) · TRADE_ROLL_1552 (superseded by ledger) · WATSHI_EXHIBIT · WEEK_STANDING_ORDER (standing).
- **nightly_20260705 (4):** CLOCK_AUDIT (the C45-triggering exhibit) · FULL_TAPE_REGRADE · PLEX_RISER_BOUNCE_PACKAGE (staged, "NOT yet relayed" — BOARD item) · REPORT.
- **overnight 03/04/05 + proof 05/06/07 (14):** the week's evidence chain — RUNBOOK, reports, PROOF_PASS ×3, SCOREBOARD (pre-registered; disarm executed 07-06 RISER_DISARM), SHADOW_GRADUATION (armed c2a59a62), EXHIBIT_A_PASCOP, AIM_SHADOW/EX_SELF/AUDIT proofs. CURRENT chronological record.
- **aim_dispatch_20260703:** DISPATCH_REPORT (six entry-side patches, gated; the ba08243 lineage).

### 2c · analysis
dead_ends/README (graves, standing) · exit_charts README + drift_table_validation ("do NOT deploy" stands) · AGENT_DERIVATION_findings (verification record) · forensic_20260707/ producers (today's, referenced by the forensic docs).

## 3 · CATALOG — origin/blend/agent-derivation (tip d2faa9c3, 2026-07-06)

- Tip activity is EXCLUSIVELY JUNE_VAULT edits (0C/0D/0E, 07-05/06) — the branch is a Vault-hosting branch now, nothing else moves.
- docs/ tree = same May-era spec family as local (33 files, same judgments) + **JUNE_VAULT.md (canonical: §0 recurring-failure → §0A operator frame → 0B–0E laws → §1 settled → §4E–4I July arc → §5 thesis → §8 infra)** + **JUNE_VAULT_APPENDIX.md (694-line frozen anti-re-derivation archive: verbatim LESSONS snapshot @876daf04 + OMQS artifact index + docs index + deploy ledger)**.
- ROADMAP.md frozen 06-01 · SESSION_HANDOFF.md frozen 06-05 (same fossils as local).
- arb-executor-v2/ + ESPNData/ md files: pre-fork historical reports (out of the tennis-bot knowledge scope; untouched).

## 4 · WHAT PHASE 2 DOES WITH THIS

1. `arb-executor/docs/LIVING_VAULT.md` — chronological ledger (newest-first) merging: Vault §0A–0E/§1/§4E–4I/§5 + LESSONS C39–C49 arc + this week's verdicts (riser disarm, flip, aim_v2 gated, expression census, dup-storm family, C47/C48/C49) + the two VAULT_PENDINGs + RETIRED graves (every superseded view in §1 above, named with its killer).
2. Front page = THE ENTRY DOCTRINE (0A verbatim + gold recipe + B3 decomposition + 11¢ finding + expression invariant + ramp/gun state + W1→W1 mandate) — the contract AIM_V2's arm is judged against.
3. `.claude/BOARD.md` — the standing queue (in-flight/queued/external/cron/parked).
4. Tombstones: ROADMAP, SESSION_HANDOFF, both JUNE_VAULTs (+ APPENDIX header), VAULT_PENDINGs (as merged).
5. Phase 3 wires C50 enforcement into deploy_gate.sh and the close-out protocol.
