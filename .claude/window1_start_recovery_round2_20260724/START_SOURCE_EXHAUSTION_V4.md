# Round-2 start-source disposition

All extraction remained blind to execution and policy outcomes.

| source | availability | new D promotions | disposition |
|---|---:|---:|---|
| tennis.db.matches | excluded | 0 | mixed execution/policy table; blindness law forbids row reads and frozen event identity already supplies D |
| tennis.db.live_scores | partial | 0 | UNIQUE(te_match_id) INSERT OR REPLACE retains current/final state, not monotonic status history; one-sided upper only |
| tennis.db.score_status_history | unavailable | 0 | no append-only historical table existed for July 12-20 |
| tennis.db.observed_starts_main | partial | 0 | set-once first sighting supplies a live-by upper but no independent pre-live lower |
| state/observed_starts.db | partial | 0 | first in-play receipt is upper-only; joined rows corroborate but cannot independently create a two-sided interval |
| tennis.db.historical_events | identity_only | 0 | first_ts/last_ts are market-price retention clocks, not match status clocks; price behavior is prohibited |
| tennis.db.kalshi_price_snapshots | identity_time_alignment_only | 0 | open-market poll metadata does not contractually prove not-started; price fields were not read |
| betexplorer_staging/bookmaker_odds/fv_monitor/tennis_odds producer records | identity_time_alignment_only | 0 | listing/poll clocks carry no explicit pre-live or live status; odds and prices were not used |
| milestone_shadow and official bell caches | available | 0 | already consumed in V3; current D additions are not_started receipts and cannot be promoted |
| milestone_starts/corpus_events_v2 | partial | 0 | official actuals already sit in the preserved baseline; onset estimates and schedule rows cannot prove positives |
| live_v3/live_v4 immutable logs | available_previously_consumed | 0 | V3 retained policy-blind start/status candidates; the Round-2 residual scan found no new explicit pre/live pair |
| market_lifecycle_v2/raw WS lifecycle/reconnect/depth snapshots | partial_or_unavailable_for_start | 0 | retained subsecond store contains prints plus ingest provenance, not event-resolved status transitions; price movement and unproven depth continuity cannot establish start |
| public retained milestone score endpoint | available_current_state_only | 0 | current final score/status has no historical receipt or start timestamp |
| TennisExplorer historical completed-result start clock | available | 453 | same provider surface used by te_live/te_honest; exact player, tournament class/name, date, match ID, completed result, and minute clock required |

The start gate passed. No exhausted query was repeated as a new source; the existing six-family/24-policy runner remains frozen and unscored pending independent ledger review.
