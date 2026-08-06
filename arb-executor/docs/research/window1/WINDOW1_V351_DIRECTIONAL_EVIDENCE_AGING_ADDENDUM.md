# Window-1 V35.1 directional evidence aging — rejected

Evidence commit: `3f073c443aafb6c30509d69e22f02aac1eb8f6a5`

V35.1 applied one receipt-driven repair to V35: an all-time downward minimum
remains authoritative while the side is FALLING; outside FALLING, only
downward receipts inside the existing 300-second state horizon remain live,
and only a qualifying-ask floor genuinely re-formed on the current
non-falling receipt may replace the stale minimum. There is no timer or
wall-clock action trigger. Living rests, strict fill law, hard pre-bell edge,
pair cap, and close-free grading are unchanged.

The named regression passes: ARNROM completes `38 + 56 = 94`; KRALOR|LOR
remains 5; BOSCOP|BOS remains 32; ARNROM|ROM remains 38 with zero regret.

The population acceptance fails. STRICT completed/under-par pairs rise from
V35's 264 to 283, but the strict `<=93 / <=95 / <=97` frontier changes from
`9 / 25 / 82` to `7 / 24 / 82`. CENSUS_PRICED completed/under-par pairs are
552. The repair displaced deep incumbent catches, so V35.1 is frozen as a
rejected variant. V35 remains operative.

STRICT regret is median 2c, p75 5c, p90 12c, total 5,666c over 1,048 numeric
legs; 560 rows remain null. CENSUS regret is median 1c, p75 3c, p90 8c,
total 4,908c over 1,337 numeric legs; 271 remain null.

REST_SANITY remains exact: STRICT 2,020,817/2,020,817 and CENSUS
1,607,376/1,607,376 tracked receipts, maximum absolute gap 0c. Two clean
builds reproduced 46 files byte-identically. Thirteen focused and inherited
tests passed. Holdout, live, network-runtime, order, position, exit,
settlement, DCA, and deployment accesses are zero.

Acceptance receipt:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3f073c443aafb6c30509d69e22f02aac1eb8f6a5/.claude/window1_live_v4_replay/v351_directional_evidence_aging_20260806/ACCEPTANCE_RECEIPT.json

Two-column scorecard:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3f073c443aafb6c30509d69e22f02aac1eb8f6a5/.claude/window1_live_v4_replay/v351_directional_evidence_aging_20260806/SCORECARD_TWO_COLUMN.json

Strict frontier:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3f073c443aafb6c30509d69e22f02aac1eb8f6a5/.claude/window1_live_v4_replay/v351_directional_evidence_aging_20260806/STRICT_FRONTIER.json

Named regressions:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3f073c443aafb6c30509d69e22f02aac1eb8f6a5/.claude/window1_live_v4_replay/v351_directional_evidence_aging_20260806/NAMED_REGRESSION_RECEIPT.json

Differential versus V35:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3f073c443aafb6c30509d69e22f02aac1eb8f6a5/.claude/window1_live_v4_replay/v351_directional_evidence_aging_20260806/DIFFERENTIAL_VS_V35.json

Bleed census:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3f073c443aafb6c30509d69e22f02aac1eb8f6a5/.claude/window1_live_v4_replay/v351_directional_evidence_aging_20260806/BLEED_CENSUS_DELTA.json

REST_SANITY:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3f073c443aafb6c30509d69e22f02aac1eb8f6a5/.claude/window1_live_v4_replay/v351_directional_evidence_aging_20260806/REST_SANITY.json

Determinism:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3f073c443aafb6c30509d69e22f02aac1eb8f6a5/.claude/window1_live_v4_replay/v351_directional_evidence_aging_20260806/DETERMINISM_RECEIPT.json

Forbidden access:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3f073c443aafb6c30509d69e22f02aac1eb8f6a5/.claude/window1_live_v4_replay/v351_directional_evidence_aging_20260806/FORBIDDEN_ACCESS_RECEIPT.json
