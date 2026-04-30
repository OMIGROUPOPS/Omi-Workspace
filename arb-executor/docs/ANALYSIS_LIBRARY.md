# OMI Analysis Library — Catalog of Prior Analyses

**Purpose:** Catalog every prior analysis script and result file in the OMI tennis trading operation, classified by analysis depth, data tier, variables used, question answered, validity status, and output location. Source of truth for "what has already been done." Future chats consult this before designing any new analysis to avoid redoing work and to know which prior conclusions are valid vs invalidated.

**Cross-references:**
- Taxonomy used for classification: TAXONOMY.md.
- Lessons that motivate this library: A23, E25, E26.

---

## SECTION 1: ENTRY FORMAT

Each analysis is one entry with the following fields:[Analysis name]

File path: [VPS path or git location]
Date created: [date or git commit date]
Author / origin: [chat session or CC session]
Depth: [0-6 per TAXONOMY.md Section 2]
Data tier: [A / B / C / mixed]
Variables used: [columns from TAXONOMY Section 4]
Question answered: [one sentence]
Validity status: [valid / partial / broken / unverified]
Output location: [where the result lives]
Notes: [known issues, dependencies, supersession info]


---

## SECTION 2: ANALYSES BY DEPTH

[TO BE POPULATED from depth-inventory CC probe. Each analysis script in /tmp and /root/Omi-Workspace will be classified and entered below, grouped by depth level.]

### Depth 0 — Existence
[TO BE POPULATED]

### Depth 1 — Distribution
[TO BE POPULATED]

### Depth 2 — Trajectory
[TO BE POPULATED]

### Depth 3 — Capacity
[TO BE POPULATED]

### Depth 4 — Microstructure
[TO BE POPULATED]

### Depth 5 — Strategy simulation
[TO BE POPULATED]

### Depth 6 — Cross-sectional context
[TO BE POPULATED]

---

## SECTION 3: BROKEN OR INVALID ANALYSES

Analyses that ran but produced invalid results due to bugs, methodology errors, or data corruption. Listed here so future chats know not to cite their conclusions.

[TO BE POPULATED. Known entry: greeks_decomposition.csv broken via degenerate first-bid bug; schema valid, numbers not.]

---

## SECTION 4: NOTABLE PRIOR FINDINGS (currently asserted)

Findings from prior analyses that are currently treated as anchor evidence in the operation. Each must be classified to its proper depth and noted with the limits of that depth.

- **70.7% bilateral double-cash rate at +10c (April 14, 458 paired matches).** Depth 0 existence proof. Variables used: first_price and max_price both sides. Tier: C-tier (historical_events). Strict reading: bilateral oscillation exists at the +10c threshold. Does NOT establish capturability, fillability, profitability, or per-cell consistency. See LESSONS.md E18 (assertion) and E25 (depth-0 caveat).

[Additional notable findings TO BE POPULATED as ANALYSIS_LIBRARY entries are added.]

---

## SECTION 5: CHANGELOG

- 2026-04-30: Initial scaffolding. Section 4 has one entry (70.7%) reflecting current chat-state knowledge; Sections 2 and 3 await depth-inventory CC probe.
