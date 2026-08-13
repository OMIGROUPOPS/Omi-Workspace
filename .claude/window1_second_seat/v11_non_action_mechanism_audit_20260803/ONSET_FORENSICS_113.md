# Onset forensics on the 113 — screw #1's evidence base [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. No mechanism proposals — the operator rules the primed design from this table.
Population: the 113 offered games whose exam shortfall carries dominant block STABILITY_ONSET_NOT_REACHED
(@ `0e16068e`). Sources: the exam's full-804 decision trace (positional receipt-grain diary, 101 chunks @
`4716657a`), its capture ledger, my offer census (`22441e05`), fit-local prints and tapes. Prior art cited:
the trace-span provenance audit (`4716657a`) — **EXPORT_ONLY_TRUNCATION; runner full-span** (and its SHEVAN
standing attestation corrects my `d9d9a4e3` Part-B conditional reading: VAN credited 58 and SHE 34 before the
collapse; neither rest stood at the later crossings). Deliverables: **`ONSET_FORENSICS_113.csv`** (all 113 ×
2 legs, one row per leg — the decision table) · `ONSET_FORENSICS_113.json` (full rows + divergence set) ·
`onset113_exemplars/` (six full five-trajectory CSVs for MERDRO/DEGEE/MULSHE).

## What the receipts actually say — four measurements that reframe screw #1

1. **Runtime onset fired on every leg: 226/226, NEVER = 0.** The dominant STABILITY_ONSET_NOT_REACHED
   block is a **receipt-count artifact of long formation spans** — those receipts were spent *waiting*,
   lawfully; onset was reached in every one of these games.
2. **Post-onset time was ample: onset→edge p25 123 · median 407 · p75 746 minutes.** Lateness is not the
   class mechanism.
3. **The read formed instantly at wake: first evidence-sufficient read (clause ②'s own standard, from the
   trace) − onset-passed = median 0.0 min (p75 0.2).** Read starvation is not the class mechanism either.
4. **Every offered floor printed after census onset (226/226)** — the offers are genuinely post-onset.

**The located divergence — runtime vs census onset: 27 legs disagree** (199 agree exactly). The disagreement
is by receipt: the runtime's onset is computed on the exam's materialized receipt stream, the census's on the
fit-local minute grid — same arithmetic (`226/226` when inputs align), different input grain. The divergent
set is concentrated and large where it exists: TOKMIY +715/+657 min · PERTOB +639/+639 · SHIHAR +623/+572 ·
DEGEE +534/+534 (full list in the JSON). **In 11 legs the offered floor printed BEFORE the runtime onset** —
on those legs the runtime machine woke after the discount had already passed (DEGEE-DE, GANJAN-GAN,
PERTOB-both, SHIHAR-SHI, ADDIVA-IVA, …): the one place where "onset" genuinely cost the offer, and it is an
input-grain divergence, not the onset law itself.

**Attribution caveat, stated plainly:** with onset passed everywhere, ample time, instant reads, and
post-onset floors, the 113's completion failures are NOT explained by the dominant-block label. The
receipt-count attribution measures where receipts were spent, not what refused completion at the decisive
moments. The per-game mechanism is heterogeneous and downstream — visible in the exemplars.

## The three exemplars, walked (full trajectories in `onset113_exemplars/`)

**MERDRO (exact, margin 13; window 1,032 min):** both legs' onset at T+133 (candidate A, runtime = census
exactly); reads formed at T+133.4. **DRO's decision rows end at T+164 — DRO credited (~31 min after wake,
per the span-audit export law).** MER ran licensed to the edge (last receipt T+1,032): its 48¢ floor printed
at **T+141 — 8 minutes after wake, 23 minutes before the sibling credit** — and was never converted in the
remaining 891 minutes. The onset did not fail MERDRO; whatever refused MER's completion sits downstream of a
passed license, and this table does not name it (no proposals).

**DEGEE (exact, margin 12; window 2,472 min):** **the divergence exemplar.** Census onset T+1,190; runtime
onset T+1,727 (+534 min, both legs). DE's 37¢ floor printed at **T+1,310 — after the census onset, 417
minutes BEFORE the runtime onset.** Under the census's wake the offer was live; the runtime machine slept
through it by input grain. GEE's floor (51) printed T+2,424, near the edge; GEE's rows end T+2,233
(credited); DE ran uncredited to the edge.

**MULSHE (exact, margin 11; window 4,420 min):** onset T+382 (runtime = census); reads at T+383. **MUL's
rows end at T+891 (credited); its 35¢ floor printed much later at T+3,753 — post-fill, unreachable by the
leg that had already bought.** SHE ran licensed to the edge, its 54¢ floor printing at T+516; not converted
in the remaining 3,900 minutes. The margin here was sequential and the machine's first fill preceded the
deep half of the offer.

## Conservation

113 games / 226 legs, all rows in the CSV; runtime onset 226 passed + 0 never; runtime-vs-census 199 agree +
27 diverge = 226; floors 226/226 post-census-onset, 11 pre-runtime-onset (subset of the divergent legs'
games); read-gap distribution over all 226; exemplar trajectory CSVs 6/6. ANALYTICAL_ESTIMATE.
