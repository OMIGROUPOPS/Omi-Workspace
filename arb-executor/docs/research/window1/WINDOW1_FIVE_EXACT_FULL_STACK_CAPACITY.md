# Five exact-start full-stack capacity validation

Hold gate: **FAIL**. The 804 run was **not permitted**.

Pair reference is `NOT_BOUND`. A displayed ask capacity of at least five at or below the resting limit is required for credit; price reach with absent/sub-five capacity is reported separately.

| category | price region | event | leg | entry | pair ref | delta pair | own W1 close | delta close | own bell | delta bell | own ask-low | delta ask-low | accounting |
|---|---|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| ATP_CHALL | 51_75 | KXATPCHALLENGERMATCH-26JUL19HURBIG | RISER:BIG | NULL | NOT_BOUND | NOT_BOUND | 60 | NULL | 60 | NULL | 55 | NULL | NOT_FILLED |
| ATP_CHALL | 26_50 | KXATPCHALLENGERMATCH-26JUL19HURBIG | FALLER:HUR | 41 | NOT_BOUND | NOT_BOUND | 42 | -1 | 42 | -1 | 37 | +4 | CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN |
| ATP_CHALL | le25 | KXATPCHALLENGERMATCH-26JUL19NIKVRB | FALLER:NIK | 18 | NOT_BOUND | NOT_BOUND | 19 | -1 | 19 | -1 | 18 | +0 | CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN |
| ATP_CHALL | le25 | KXATPCHALLENGERMATCH-26JUL19NIKVRB | RISER:VRB | 68 | NOT_BOUND | NOT_BOUND | 83 | -15 | 83 | -15 | 68 | +0 | CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN |
| ATP_MAIN | 26_50 | KXATPMATCH-26JUL12LAJVAN | FALLER:LAJ | 50 | NOT_BOUND | NOT_BOUND | 45 | +5 | 45 | +5 | 45 | +5 | CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN |
| ATP_MAIN | 26_50 | KXATPMATCH-26JUL12LAJVAN | RISER:VAN | NULL | NOT_BOUND | NOT_BOUND | 57 | NULL | 57 | NULL | 50 | NULL | NOT_FILLED |
| WTA_CHALL | 26_50 | KXWTACHALLENGERMATCH-26JUL16BRAVED | FALLER:BRA | NULL | NOT_BOUND | NOT_BOUND | 44 | NULL | 44 | NULL | 40 | NULL | NOT_FILLED |
| WTA_CHALL | 51_75 | KXWTACHALLENGERMATCH-26JUL16BRAVED | RISER:VED | 60 | NOT_BOUND | NOT_BOUND | 57 | +3 | 57 | +3 | 57 | +3 | CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN |
| WTA_MAIN | 26_50 | KXWTAMATCH-26JUL20KORJIM | FALLER:JIM | 39 | NOT_BOUND | NOT_BOUND | 32 | +7 | 32 | +7 | 30 | +9 | CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN |
| WTA_MAIN | 51_75 | KXWTAMATCH-26JUL20KORJIM | RISER:KOR | NULL | NOT_BOUND | NOT_BOUND | 70 | NULL | 70 | NULL | 60 | NULL | NOT_FILLED |

## Category and price-region partitions

Every cell is thin in this five-game validation; none is aggregated upward.

| category | price region | leg rows | credited legs | at/below own close | status |
|---|---|---:|---:|---:|---|
| ATP_CHALL | 51_75 | 1 | 0 | 0 | THIN |
| ATP_CHALL | 26_50 | 1 | 1 | 1 | THIN |
| ATP_CHALL | le25 | 2 | 2 | 2 | THIN |
| ATP_MAIN | 26_50 | 2 | 1 | 0 | THIN |
| WTA_CHALL | 26_50 | 1 | 0 | 0 | THIN |
| WTA_CHALL | 51_75 | 1 | 1 | 0 | THIN |
| WTA_MAIN | 26_50 | 1 | 1 | 0 | THIN |
| WTA_MAIN | 51_75 | 1 | 0 | 0 | THIN |

## Change firing

Each value is `FIRED` or `DID_NOTHING`; a fired decision mechanism is not itself fill credit.

### KXATPCHALLENGERMATCH-26JUL19HURBIG

- BIG: orientation_conditioned_initial_tree=FIRED; quiet_book_anchor=FIRED; per_tick_ask_breathing=DID_NOTHING; sibling_conditioned_faller_patience=DID_NOTHING; ask_only_dwell_reachability=DID_NOTHING
- HUR: orientation_conditioned_initial_tree=FIRED; quiet_book_anchor=FIRED; per_tick_ask_breathing=DID_NOTHING; sibling_conditioned_faller_patience=DID_NOTHING; ask_only_dwell_reachability=FIRED

### KXATPCHALLENGERMATCH-26JUL19NIKVRB

- NIK: orientation_conditioned_initial_tree=FIRED; quiet_book_anchor=DID_NOTHING; per_tick_ask_breathing=DID_NOTHING; sibling_conditioned_faller_patience=FIRED; ask_only_dwell_reachability=FIRED
- VRB: orientation_conditioned_initial_tree=FIRED; quiet_book_anchor=FIRED; per_tick_ask_breathing=FIRED; sibling_conditioned_faller_patience=DID_NOTHING; ask_only_dwell_reachability=FIRED

### KXATPMATCH-26JUL12LAJVAN

- LAJ: orientation_conditioned_initial_tree=DID_NOTHING; quiet_book_anchor=FIRED; per_tick_ask_breathing=FIRED; sibling_conditioned_faller_patience=DID_NOTHING; ask_only_dwell_reachability=FIRED
- VAN: orientation_conditioned_initial_tree=FIRED; quiet_book_anchor=FIRED; per_tick_ask_breathing=FIRED; sibling_conditioned_faller_patience=DID_NOTHING; ask_only_dwell_reachability=DID_NOTHING

### KXWTACHALLENGERMATCH-26JUL16BRAVED

- BRA: orientation_conditioned_initial_tree=FIRED; quiet_book_anchor=FIRED; per_tick_ask_breathing=DID_NOTHING; sibling_conditioned_faller_patience=DID_NOTHING; ask_only_dwell_reachability=DID_NOTHING
- VED: orientation_conditioned_initial_tree=FIRED; quiet_book_anchor=FIRED; per_tick_ask_breathing=FIRED; sibling_conditioned_faller_patience=DID_NOTHING; ask_only_dwell_reachability=FIRED

### KXWTAMATCH-26JUL20KORJIM

- JIM: orientation_conditioned_initial_tree=DID_NOTHING; quiet_book_anchor=FIRED; per_tick_ask_breathing=DID_NOTHING; sibling_conditioned_faller_patience=DID_NOTHING; ask_only_dwell_reachability=FIRED
- KOR: orientation_conditioned_initial_tree=FIRED; quiet_book_anchor=FIRED; per_tick_ask_breathing=FIRED; sibling_conditioned_faller_patience=DID_NOTHING; ask_only_dwell_reachability=DID_NOTHING

## Blocking shapes

- KXATPCHALLENGERMATCH-26JUL19HURBIG: BIG:NOT_FILLED:delta_close=NULL; patience=not armed.
- KXATPMATCH-26JUL12LAJVAN: LAJ:CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN:delta_close=+5, VAN:NOT_FILLED:delta_close=NULL; patience=not armed.
- KXWTACHALLENGERMATCH-26JUL16BRAVED: BRA:NOT_FILLED:delta_close=NULL, VED:CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN:delta_close=+3; patience=not armed.
- KXWTAMATCH-26JUL20KORJIM: JIM:CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN:delta_close=+7, KOR:NOT_FILLED:delta_close=NULL; patience=not armed.
