# Assumption gaps

- January–March has event-grain historical aggregates but no local intramatch tape. Measurement needed: public historical trades plus timestamped book reconstruction at the same grain as the July recorder.
- The subsecond store mixes public tape and synthetic book transitions and lacks exchange trade identity on every row. Measurement needed: source-specific identity completeness by named event.
- The DO archive is connected and the pre-sealed object reader is smoked, but its July object catalog is not a January-present database. Measurement needed: event-level archive coverage joined to corpus_events_v2.
- The odds backup is connected, but its overlap with each target game is not complete. Measurement needed: immutable per-event bookmaker snapshots with source clock and player mapping.
- CRIJEA has no verified bell. Measurement needed: an independent official in-play timestamp; until then it grades nothing.
