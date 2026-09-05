# FACE v2 — custody proof

Worktree: `C:\Users\omigr\omi-w1-face`, branch `face/window1-watch-20260903`.
Only `window1-watch/` belongs to this change. No engine replay or engine edit was
needed for either proof game. Existing unrelated work was left untouched.

## Reproduce

```powershell
.\window1-watch\rerun_game.ps1 -Event KXATPMATCH-26JUL12ALTGAS -Custody C:\tmp\v54_altgas_extra_2dfb5b0a_20260902_run2_custody
.\window1-watch\rerun_game.ps1 -Event KXATPCHALLENGERMATCH-26JUL14URSPAL -Custody C:\tmp\v54_insufficient_evidence_veto_e53df11_20260902_run1_custody
node --test window1-watch/test_face_v2.mjs
cd window1-watch\shell
npm run dev
# In another terminal in shell/:
node scripts/tune-proof.mjs
```

ALTGAS: `http://localhost:8080/?event=KXATPMATCH-26JUL12ALTGAS&gate=480`

URSPAL: `http://localhost:8080/?event=KXATPCHALLENGERMATCH-26JUL14URSPAL&gate=480`

The optional no-custody fallback keeps the four bed games and replaces the saved
ALTGAS extra with the requested extra on the same stories line, then restores the
original builder bytes in `finally`. Its preparation was checked read-only against
the real builder: existing ALT/URSPAL changed no lines; an extra changed only line
24, leaving five stories. PowerShell parsing passed. The expensive fallback itself
was **not executed**. It requires the frozen inputs named in `rerun_altgas.ps1`.

## Custody hashes

| Game | Trace SHA256 | Bound historical OS SHA256 |
|---|---|---|
| ALTGAS | c2fe78f28b12abf02f53ad8ec37ffe252fb0fb99f79cc6d83c7732f555c6d480 | 986b8233be188cc484574536e2ab1ff8dd42a7d9a0b7a3a804cc852fcb984ec1 |
| URSPAL | ab2345dea8b3db2237dca97bf03f3fcece95eae334e3f4940f5b6583271171a0 | a394097bd8aacc1b110b05dcb7677aef837f2cd09c170dcaacec470d73a3a0b2 |

These hashes come from each run's source receipt plus its exact trace custody
binding, not from today's engine file.

Bench SHA256: `12df2861b5298fe45c141cc84c7924b326fa0ee347faad391d4a35fa0d79d2f1`.

Bench label, unchanged: **PROOF RUN — STALE LIBRARY (ends 2026-05-01) — NOT A RULING**.

## Five verification lines

`t` is hours from that trace's first stage, not hours since the first pair tick.

```text
ALT FIRST_REST 55c; t=5.38860166642401h; minutes_to_bell=3967.800566665332; receipt=49fc71e7-75ce-5546-9c79-30b8a02aaeb2
GAS FIRST_FILL 42c; t=23.506452777518167h; minutes_to_bell=2880.729499999683; receipt=87517932-7806-63a5-6104-8b6bf4d17f87
URSPAL PAL FIRST_REST 39c; t=6.167399166425069h; minutes_to_bell=351.42271666526796; receipt=038f03f3-2dcd-7363-da5f-06677e3be932
URSPAL PAL FIRST_FILL 39c; t=11.974332221945128h; minutes_to_bell=3.0067333340644353; receipt=11b32855-2577-5868-896c-0afb9e64bb69
ALT PLACE inspector: lane=INSUFFICIENT_AUTHORITY_NO_WRITER; authority_source=ENGINE_VOTES_LICENSED_DEPTH_PRIOR_WITH_NO_OWN_EVIDENCE_YET
```

The apparently conflicting ALT placement and NO_WRITER lane are both stored in
the original row; the face does not reconcile or relabel them.

## Checkpoint 480: important clock flag

ALTGAS's first traded pair is at 3963.582566666604 minutes before its trace bell;
480 is a playable gate. Its aligned bench VALIDITY at 480 is 13.86%.

URSPAL's first traded pair is at **351.42271666526796** minutes before its trace
bell. Consequently 480 is **pre-first-tick inspection**, not a playable checkpoint.
The screenshot explicitly labels it, disables Play/scrub there, and leaves the
playable level starting at the actual pair tick. Next checkpoint reaches the
first playable gate at 240 without manufacturing an earlier tick.

URSPAL bench bell is **2853 seconds later** than the requested trace bell. Its
bench source/hash remain visible, but ESS, VALIDITY and role joins are STORE SILENT.
No shifted or nearest benchmark was substituted. The old trace's original bell
source is `TAPE_SIGNATURE_OPERATOR_RULED`; ALTGAS's is `MACHINE_RECEIPT`.

## STORE SILENT and field meaning

Both requested old traces lack overlap member_count, weight_sum, weighted no-dip
share and candidate-level q10/q25/q50/q75/q90 for every leg. No count is borrowed
from shape survival, no band is filled in, and no bench family authors an OS family.
Other absent receipt-specific last/low, P/Q/X, action cents, author, lane and pair
exposure values stay silent individually. At URSPAL 480, PAL has no true last/low
yet. Missing benchmark data or the clock mismatch never lights the validity meter.

The legacy sentence X field remains `phase_projection_telemetry_cents`, as in
FIELDS.md. It is not silently changed into a deadline; full stored deadline fields
are available in the lazy inspector.

## Verification and performance

- Both final `rerun_game.ps1 -Custody` commands exited successfully.
- Six source-contract tests passed, including equal-time receipt order and a
  distinct selectable frame for every receipt.
- `npm run typecheck` and direct `vite build` passed. The package's database
  migration command was not run, and nothing was deployed.
- Browser proof passed: picker/URL, Prev/Next receipts, 480 → 360 checkpoint jump,
  miss fade, recorded fill markers, no eager inspector fetch, the full ALT
  arbitration/source, and a 390px viewport with no horizontal overflow.
- GAS PLACE and FILL share one timestamp but occupy frames 82 and 89. The fill
  marker is absent at PLACE and present at FILL; the rest clears only at FILL.
- Static, source-clock-clipped step paths preserve causal observations and avoid
  per-receipt chart rebuilds. In the recorded headless Chrome development-server
  playback sample: 360 frames, median 6.1ms, maximum 10ms, zero above 16.67ms.
  This is a measured local sample, not a hardware-independent frame-rate guarantee.
- Browser reported no page errors. See `browser-verification.json` and the two
  gate screenshots; `alt-place-inspector.png` shows the stored contradiction.

| Main face | Uncompressed bytes | Gzip transfer bytes | Frames | Receipts |
|---|---:|---:|---:|---:|
| ALTGAS | 719603 | 60784 | 375 | 195 |
| URSPAL | 7477557 | 381259 | 3332 | 1220 |

All **1415** inspector rows were re-audited against the original uncompressed
copies: full `row` content is identical. Lazy `.json` URLs are served with HTTP gzip
from `.json.gz` files by the local Vite middleware. No stage field is whitelisted
away. There is no production hosting change in this commit.

Cleanup approval was not received: **2148480593 bytes** of verified redundant
uncompressed inspector copies remain locally, ignored by git. Nothing was deleted.
