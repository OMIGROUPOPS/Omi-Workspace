# Window 1 live-book initial-aim replay

This is a cold, score-free five-event replay. The five-event set includes NIKVRB; NIKVRB is also retained as the detailed specimen, not counted as a sixth game.

Raw replay/reference source:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_live_v4_replay/live_book_initial_aim_20260731/REPLAY_AND_REFERENCE_PANEL.json

Raw five-event change source:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_live_v4_replay/live_book_initial_aim_20260731/FIVE_EVENT_CHANGE_RECEIPT.json

Raw suppression source:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_live_v4_replay/live_book_initial_aim_20260731/INITIAL_AIM_FILL_SUPPRESSION_CENSUS.json

Raw capacity-ceiling source:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_live_v4_replay/live_book_initial_aim_20260731/ASK_10S_FIVE_CONTRACT_CEILING.json

Raw legacy-invalidation source:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_live_v4_replay/live_book_initial_aim_20260731/LEGACY_CAPACITY_INVALIDATION_RECEIPT.json

## Per-leg current versus corrected

### KXATPCHALLENGERMATCH-26JUL19HURBIG

| Branch | Leg | Entry | Own W1 close | Δclose | Own bell | Δbell | Own ask-low (10s) | Δask-low | Independent pair ref | Δpair ref |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| current | BIG | NO_CREDIT | 60 | NULL | 60 | NULL | 55 | NULL | NOT_BOUND | NOT_BOUND |
| current | HUR | 41 | 42 | -1 | 42 | -1 | 37 | +4 | NOT_BOUND | NOT_BOUND |
| corrected | BIG | NO_CREDIT | 60 | NULL | 60 | NULL | 55 | NULL | NOT_BOUND | NOT_BOUND |
| corrected | HUR | 47 | 42 | +5 | 42 | +5 | 37 | +10 | NOT_BOUND | NOT_BOUND |

### KXATPCHALLENGERMATCH-26JUL19NIKVRB

| Branch | Leg | Entry | Own W1 close | Δclose | Own bell | Δbell | Own ask-low (10s) | Δask-low | Independent pair ref | Δpair ref |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| current | NIK | 18 | 19 | -1 | 19 | -1 | 18 | +0 | NOT_BOUND | NOT_BOUND |
| current | VRB | 68 | 83 | -15 | 83 | -15 | 68 | +0 | NOT_BOUND | NOT_BOUND |
| corrected | NIK | 18 | 19 | -1 | 19 | -1 | 18 | +0 | NOT_BOUND | NOT_BOUND |
| corrected | VRB | 68 | 83 | -15 | 83 | -15 | 68 | +0 | NOT_BOUND | NOT_BOUND |

### KXATPMATCH-26JUL12LAJVAN

| Branch | Leg | Entry | Own W1 close | Δclose | Own bell | Δbell | Own ask-low (10s) | Δask-low | Independent pair ref | Δpair ref |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| current | LAJ | 50 | 45 | +5 | 45 | +5 | 45 | +5 | NOT_BOUND | NOT_BOUND |
| current | VAN | NO_CREDIT | 57 | NULL | 57 | NULL | 50 | NULL | NOT_BOUND | NOT_BOUND |
| corrected | LAJ | 50 | 45 | +5 | 45 | +5 | 45 | +5 | NOT_BOUND | NOT_BOUND |
| corrected | VAN | NO_CREDIT | 57 | NULL | 57 | NULL | 50 | NULL | NOT_BOUND | NOT_BOUND |

### KXWTACHALLENGERMATCH-26JUL16BRAVED

| Branch | Leg | Entry | Own W1 close | Δclose | Own bell | Δbell | Own ask-low (10s) | Δask-low | Independent pair ref | Δpair ref |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| current | BRA | NO_CREDIT | 44 | NULL | 44 | NULL | 40 | NULL | NOT_BOUND | NOT_BOUND |
| current | VED | 60 | 57 | +3 | 57 | +3 | 57 | +3 | NOT_BOUND | NOT_BOUND |
| corrected | BRA | NO_CREDIT | 44 | NULL | 44 | NULL | 40 | NULL | NOT_BOUND | NOT_BOUND |
| corrected | VED | 60 | 57 | +3 | 57 | +3 | 57 | +3 | NOT_BOUND | NOT_BOUND |

### KXWTAMATCH-26JUL20KORJIM

| Branch | Leg | Entry | Own W1 close | Δclose | Own bell | Δbell | Own ask-low (10s) | Δask-low | Independent pair ref | Δpair ref |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| current | JIM | 39 | 32 | +7 | 32 | +7 | 30 | +9 | NOT_BOUND | NOT_BOUND |
| current | KOR | NO_CREDIT | 70 | NULL | 70 | NULL | 60 | NULL | NOT_BOUND | NOT_BOUND |
| corrected | JIM | 39 | 32 | +7 | 32 | +7 | 30 | +9 | NOT_BOUND | NOT_BOUND |
| corrected | KOR | NO_CREDIT | 70 | NULL | 70 | NULL | 60 | NULL | NOT_BOUND | NOT_BOUND |

## Five-game gate

The change does **not** pass the five-game gate. NIKVRB remains 68/18, but ATP_CHALL HUR (the faller) changes from 41 to 47. Its own-close delta moves from -1 to +5 and its ask-low gap from +4 to +10. The live-BBO initial signer fired in a quiet-book faller where the earlier deeper order was beneficial; preventing bid-only chase did not provide a later patience signal. This is the breaking shape. No 804-policy replay was run.

## Population diagnostics

- Initial aim was below every 10-second ask reach on 1137 unfilled legs across 670 events.
- 983 legs had exactly one posted exposure, proving the only bid was unreachable. The other 154 require interval streams before assigning sole causality.
- The old 532 event price-reach ceiling becomes 516 when both legs require contemporaneous top-five capacity of at least five after ten seconds; 16 are removed from creditable opportunity.
- The old ATLAS 10-second replay's 217 leg assignments and 49 pair completions have zero bound capacity identities. Under the current law those specific completion claims become zero. The 217 leg rows are not subtracted from the 532 event ceiling; the capacity ceiling is independently recomputed at event grain.

All partitions and identities are in the JSON receipts. No scorer, holdout, live, or trading surface was used.
