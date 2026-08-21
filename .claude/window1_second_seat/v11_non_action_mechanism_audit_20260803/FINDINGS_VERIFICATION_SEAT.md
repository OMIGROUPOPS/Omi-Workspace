# FINDINGS — verification seat ledger (L20: banked at discovery, one line each, receipt SHA, status)

F-VS-001 | The 612-census (`22441e05`) is coverage-limited: 25 of exam #4's 30 games are NOT_BOUND; it cannot serve as an offered denominator | `d449889e` F24_SCOREBOARD + this commit | SUPERSEDES: any "% of offered" on definition A
F-VS-002 | ONE denominator published: valid-fill completes ÷ truth-table OFFERED_UNDER_PAR (680-basis, UNKNOWN_BELL excluded both sides) | this commit OFFER_DENOMINATOR.md | NEW
F-VS-003 | Exam #4 (V53-04b Stage-1) grades on the old ruler: closes from INDEPENDENT_CLOSE_AUDIT_1608 (`a30f5ccd`), offers from `22441e05`, no truth-table binding — contrary to L11 / `fc17d0d3` | `d449889e` F24_SCOREBOARD.offer_source/own_w1_close_source | CONTRADICTS: L11 as applied to the V53 stage-1 lane
F-VS-004 | Exam #4's 23 completes decompose to 15 VALID / 3 POST-BELL / 4 PRE-FORMATION / 1 UNKNOWN-SPAN on the truth table | this commit OFFER_DENOMINATOR_EXAM4_WORKED.csv | NEW
F-VS-005 | Exam #4 credits MERDRO's formation-era 6¢+6¢ prints as a complete (combined 12¢) — the V52l pin disposition "formation-era 6c prints not credited" (`6678fd0c`) is reversed by the V53 stage-1 grading; L6 formation law | `d449889e` F24 game_rows MERDRO | CONTRADICTS: `6678fd0c` pin disposition
F-VS-006 | Exam #4's honest ratio is 15/28 = 53.6%, not "75% of 4 offered" and not 23/30 | this commit | NEW
