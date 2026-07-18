# P2 — THE SUBSECOND CENSUS (one store; the scatter killed)

store: state/subsecond_store.db · prints rows: 2041870 · sources:

- **book_transition(premarket_ticks)**: files 3694 · rows 1158313 · span 07-11→07-18 · cats {'ATP_CHALL': 230204, 'ATP_MAIN': 119939, 'ITF_M': 323993, 'ITF_W': 364595, 'WTA_CHALL': 57638, 'WTA_MAIN': 61944} · 
- **depth_recorder (book-grade, NOT in prints)**: files 238 · rows 0 · span 07-07→07-18 · 5-level book deltas
- **kalshi_price_snapshots (poll-grade, NOT in prints)**: files 0 · rows 0 · span ?→? · sqlite table, Apr-21→now, 3.35M rows
- **public_tape(daysheet_tape)**: files 463 · rows 883557 · span 07-12→07-17 · cats {'ATP_CHALL': 292594, 'ATP_MAIN': 188677, 'ITF_M': 129019, 'ITF_W': 136191, '?': 4670, 'WTA_CHALL': 71008, 'WTA_MAIN': 61398} · 
- **ws_depth_recorder (book-grade, NOT in prints)**: files 27 · rows 0 · span 07-17→07-18 · ws book archive
- **ws_log(engine jsonl)**: files 41 · rows 0 · span ?→? · 

## coverage by month × source (prints store)
- 2026-07 book_transition: 1158313
- 2026-07 public_tape: 883557

(append-forward: nightly cron re-runs this script; ingest_log is the resume key — no re-scatter, no dupes.)
