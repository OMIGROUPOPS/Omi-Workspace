# Window-1 source and start recovery

Status: binding source-recovery receipt; no performance or ceiling verdict.

## Authority and denominator

Audit commit `ff0f336f45fde9d54ca2948949689172e8203aff`
correctly established that the empty normalized `books.jsonl` and
`prints.jsonl` files were pipeline failures, not proof that market evidence
was absent. Its first-trade start inference and its claim that all 39 absent
Spaces trade CSVs represented zero-trade markets are superseded by the
receipted evidence below.

`D` remains the immutable 804 July 12-20 big-4 games and 1,608 exact leg
tickers. Missing or corrupt evidence does not remove a row from `D`.

## Public true-print recovery

The unauthenticated public market-trades endpoint was exhausted independently
for every one of the 1,608 leg tickers:

- 1,608 complete ticker queries and 5,678 pages;
- zero failed ticker queries and an empty terminal cursor for every ticker;
- 4,836,462 canonical true prints;
- 1,766,090,446 normalized bytes;
- normalized-print SHA-256
  `e9b5a765b51ddbf0d65364c4f38744ad949ca3c675e5b3a0e472392fbcfabb55`;
- zero synthetic transition rows and zero private-receipt requirements.

The 39 missing `Spaces trades/` objects are 37 archive-ingestion gaps plus two
source-exhaustively proven zero-trade legs:

- `KXATPCHALLENGERMATCH-26JUL19KRUCAS-CAS`;
- `KXATPCHALLENGERMATCH-26JUL19SALVRB-VRB`.

A complete zero-trade query is usable evidence that no true print occurred; it
is not a missing tape. Zero or missing size still contributes zero.

## BBO and top-five depth

The immutable Spaces object manifest proves one exact `ticks/` object for all
1,608 required tickers. Exact materialization verification found 1,488
preserved local objects and 120 recovered private objects, with no size or hash
mismatch. These files are `BBO` plus `TOP5_DEPTH`; they are not called a full
chain or full depth.

The filtered object-manifest SHA-256 is
`c446bee12c9d474b42e77145b83be0f71c21f0c6256ea515ced81d7d720a57ef`.
The materialization-ledger SHA-256 is
`939daccfee17aea10125ace1526bf151112f207893acca3c374a79cd29bab2b9`.

## Top-20 preservation gap

The July 22 source-inventory receipt observed 189
`depth_recorder` files, 435,950,289 bytes, and 3,079,608 valid
change-deduplicated top-20 snapshot rows. The later frozen snapshot retained
175 files and 2,836,510 rows. The difference is 14 files and exactly 243,098
rows: the 13 July 12 files and one early July 13 file.

Only `ticks/`, `trades/`, and `ws_depth/` exist in the relevant Spaces bucket;
there is no top-20 archive prefix from which to restore those 14 objects. The
receipt proves that the source once existed but cannot reconstruct its missing
bytes. The retained 175 files may be used only as partial
`TOP20_DEPTH`/limited-depth context with explicit missingness. They are never
a full queue chain or an eligibility gate.

## Raw WebSocket delta census

The complete offline census read all 215 immutable `ws_depth/` objects:

- exact-hash objects: 215/215;
- bytes: 5,393,753,162;
- physical rows read before any corrupt edge: 282,398,961;
- `orderbook_delta` rows: 277,549,270;
- exchange trade messages: 3,324,010;
- snapshot messages: 76,798;
- internally corrupt gzip objects: 28;
- sequence gaps: 76 across seven epochs;
- required tickers with at least one retained WS row/delta: 1,608/1,608;
- required tickers with a retained positive-size WS trade: 1,601/1,608;
- snapshot messages retaining a nonempty ladder: zero;
- required tickers with sequence-valid reconstructed full depth: 0/1,608.

The exact object hashes prove that the corrupt gzip streams are source
defects, not transfer corruption. The archives are therefore classified
`RAW_WS_DELTA`. They are not classified `RECONSTRUCTED_FULL_DEPTH`: a metadata
snapshot with only market identity cannot seed a ladder, and a reconnect or
sequence gap cannot be crossed silently.

The sanitized per-ticker ledger SHA-256 is
`7947476d4b42d73177e094e252df78ace2965fcf198811f3cf33e289520982eb`.

## Metric law

The benchmark must print `D`, `C`, `PC`, `NC`, `IC`, and `X` as raw integers
before percentages:

- `C`: both legs complete exactly five contracts;
- `PC`: members of `C` with combined entry VWAP below 100;
- `NC`: members of `C` with negative combined reference delta;
- `IC`: members of `C` whose two individual reference deltas are negative;
- `X`: censored games, reported separately and still inside `D`.

`PC`, `NC`, and `IC` overlap inside `C`; they do not partition `D`. No result
from the formerly empty normalized bundle is a policy result or empirical
ceiling.

## Real-start ledger

The immutable start ledger applies the declared authority order and does not
promote first trade, first `last_trade`, or a current-state score receipt into
an exact match start. Its 804 rows classify as:

- 29 `verified_exact`;
- 79 `bounded_start_interval`;
- 625 `bounded_live_by_timestamp`;
- 71 `schedule_only_censored`.

There are 775 boundary-censored events and 32 source contradictions.
Seventy-six events have at least one defensible definitely-prestart cutoff;
the remaining games stay in `D` but cannot contribute an observed/proven
counterfactual result. Any upper result conditional on a known-live or
schedule corridor is censored.

The exact-start evidence consists of 21 exchange milestone live transitions
and eight consistent official milestone start timestamps. TE observed-inplay,
scoreboard current state, live-feed transitions, engine regime transitions,
and tape onset supply one-sided or corroborating bounds only. The complete
public-tape onset detector found a regime bound for 672 events, but none is
called the start.

The start-ledger SHA-256 is
`90a943b598baa8debe1acd08fa4b664d3661cd3762c2e5ab54e54d781819b947`.

## Mayo/Michelsen post-sample forensic

`KXATPCHALLENGERMATCH-26JUL21MICMAY` is outside the July 12-20 denominator.
The independent official start is 2026-07-21 23:00:00Z (19:00 ET). The engine
instead ingested a 22:00 ET expected-expiration/end clock as the match start.

- Mayo placement: 23:36:19.955995Z, post-start;
- Michelsen placement: 23:36:21.502612Z, post-start;
- Mayo five-contract fill/adoption known to the engine by
  23:37:30.792977Z, post-start (the exact exchange fill timestamp is not
  retained in this log);
- Michelsen successful sweep cancellation: 02:01:12.049553Z on July 22,
  post-start.

Thus the Mayo purchase and the persistent Michelsen sibling bid were not
lawful Window-1 actions. This forensic is diagnostic only and is not joined
into `D=804`.
