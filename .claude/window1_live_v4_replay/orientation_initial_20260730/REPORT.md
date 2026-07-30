# Orientation-governed initial aim — five-game replay

**Ruling: it did not beat ATLAS, so the code/config change was reverted and is not a repair.**

| Metric | ATLAS control | Orientation: riser near now |
|---|---:|---:|
| Legs filled | 4/10 | 4/10 |
| Pairs completed | 0/5 | 0/5 |
| Negative combined-delta pairs | 0/5 | 0/5 |
| Mean fill-to-own-fillable-low gap | 5.50¢ | 5.75¢ |
| Median fill-to-own-fillable-low gap | 6.00¢ | 5.50¢ |

The fillable-low denominator is the minimum true print or opposite best ask inside the frozen evaluator window, matching `RESTING_TOUCH_FILL_V1`. It is not the five-contract floor.

NIK–VRB did not change outcome. ATLAS filled NIK at 24¢ and missed VRB; orientation filled NIK at 24¢ and missed VRB. NIK's aim moved 29→26; VRB's riser aim remained 67 because “near now” and the ATLAS control were already the same price.

Across the five games, only two fills changed:

- BRAVED/VED got 2¢ worse: 58→60, moving the low gap 3→5.
- KORJIM/JIM got 1¢ better: 36→35, moving the low gap 6→5.

HURBIG/HUR and NIKVRB/NIK were unchanged. No missing leg was recovered, so completions and combined-delta results stayed at zero.

## Merge `6e45d42b`

This was a manual semantic resolution, not Git choosing one parent. Git can legally write an arbitrary merge tree, and `arb-executor/live_v4.py` was the listed conflict.

| Flag | Parent 1 | Parent 2 | Merge |
|---|---:|---:|---:|
| `entry_table_prior_enabled` | true | true | false |
| `pair_class_steer_enabled` | true | true | false |
| `one_authority_enabled` | true | true | false |
| `contention_drop_enforced` | true | key absent | false |

Yes: the manual resolution was made in this Codex workstream. Git names Druid Osullivan as author/committer and cannot fingerprint a model instance, but this workstream owns it.

The values matched the operator's then-standing instructions to hold sealed action and DROP enforcement. I restored none: none was disarmed contrary to that instruction, and the present instruction also says sealed, DROP, and cohort worsen the sample. The failure was reporting: I buried four semantic flag changes in an unrelated merge instead of naming them.

All five variant traces were valid, with zero input breaks. The replay used the retained read-only tennis snapshot: 17,509,449,728 bytes, `quick_check=ok`, SHA-256 `5219b14349f0c08a4bbdf789614f1cbccb51bf80e387471a9f2b3713b67e7a9c`.

The machine-readable per-game comparison is `ORIENTATION_INITIAL_REPLAY.json`.
