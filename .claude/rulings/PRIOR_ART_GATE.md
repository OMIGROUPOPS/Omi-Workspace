# THE PRIOR-ART GATE — standing law (operator, 2026-07-05)

**Joins the deploy law of 2026-07-04 (LESSONS C40): the gate is now LINT + SMOKE + PRIOR-ART.**
Lesson code: **C45 (MEASURE-BEFORE-READ)** in LESSONS.md; Vault exhibit: JUNE_VAULT.md §0B on blend/agent-derivation.

## The law
Every **build, measurement, or audit doc** from now on OPENS with a **Prior art** section:

1. **Grep** `LESSONS.md` + `JUNE_VAULT.md` (+APPENDIX) + `ROADMAP.md` + `.claude/rulings/` for the topic
   (start at `.claude/PRIOR_ART_INDEX.md` — one lookup, not archaeology).
2. **Cite what's already established** — lesson codes and verbatim lines.
3. **State the DELTA** being built or measured — what this doc adds that the record does not already hold.
4. If nothing: state **"no prior art after grep"** *with the grep shown* (pattern + files searched).

**No doc without it passes the gate.** A doc whose "findings" turn out to be re-derived documented facts is
ceremony, not work — the prior-art section makes that visible before the tokens are spent.

**Prior art includes STAGED-BUT-NEVER-ARMED builds — check the gated flags inventory (grep
`self.config.get(` in live_v4.py + the config keys), not just the lessons; a designed-whole fix must never
ship in halves.** (Addendum, operator 2026-07-05 — from the C-KALSHI-OCC → kalshi_schedule_primary
regression, where an armed flag took Gen-2's SOURCE without its ENVELOPE. Full chain in the Vault exhibit.)

## The exhibit (why this law exists — vaulted as JUNE_VAULT §0B "MEASURE-BEFORE-READ")
This week's clock audit (CLOCK_AUDIT.md, 2026-07-05) re-derived, as discoveries, facts that were on disk:
- **ROADMAP.md:211 (T51, 2026-06-01):** "Kalshi's API exposes no live-tracking start field
  (`occurrence_datetime`/`expected_expiration_time` are frozen coarse placeholders)" — LESSONS §6 (same date)
  adds the full form: "frozen coarse placeholders — **uniform noon-UTC** across all main-draw matches."
- **T51_HARDENING_SPEC.md:8:** the entry buffer keys on a stale/drifting placeholder — "`event_start_time`
  is locked on first estimate … the T-15m buffer fire[s] at the wrong wall-clock."
- **C32 (LESSONS.md:288, 2026-05-12):** `expected_expiration_ts > settlement_ts` on **100% of the probe
  sample** — the expiration field postdates reality as a matter of course.
- **OSOWAL (OMQS_LIVE_DUMP_2026-06-30.md):** fills booked 8–10h after the "scheduled start" on a 26JUN29 event.
- **SHINIS (OMQS_LIVE_FORENSIC_SHINIS.md):** the scheduled-vs-gun divergence already measured live (gun fired
  tts −16min; the T-20 "fallback" fired against the placeholder clock).
- And the sharpest form: **`kalshi_schedule_primary` was armed (Jul 2, config; captured to VC in ba08243)
  promoting a KNOWN-coarse placeholder to THE primary clock — the characterization was on disk when we armed it.**

The audit's genuine delta (per-cat offset quantification, gun certification against an independent anchor,
"ITF has no premarket") did not need the re-derivation to precede it. MEASURE-BEFORE-READ is the build-level
form of the §0 recurring failure; **the prior-art gate is its fix.**

## Template (paste at the top of every doc)
```markdown
## Prior art (gate)
- Greps: <pattern(s)> over LESSONS.md, JUNE_VAULT.md(+APPENDIX), ROADMAP.md, .claude/rulings/, gated-flag inventory
- Established: <code/doc:line — verbatim line or tight paraphrase> (one bullet per fact)
- Staged-but-never-armed prior builds on this topic: <flag names / commit> or "none"
- DELTA this doc adds: <the new thing, stated plainly>
```
