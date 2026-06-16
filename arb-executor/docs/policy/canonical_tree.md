# Canonical Tree Policy

- **`blend/agent-derivation` = CANONICAL deploy source.** The VPS production bot runs from it; all hotfixes and seals land here first.
- **`main` = ff-MIRROR of blend.** Never a deploy source, carries no independent commits, must always remain a strict ancestor-or-equal of blend (0 commits ahead).

## Cadence
`main` is **fast-forward-advanced to the blend tip at each SEAL event** — on-demand at seal, **NOT per-commit**. Between seals, blend may lead main by in-flight commits; that lead is **expected and is not "stale main."** A non-seal commit on blend (e.g. a policy doc, an analysis artifact, commit-for-review work) does not trigger a mirror.

## Mechanics (ff-only, never force)
```
git push origin origin/blend/agent-derivation:main     # default non-force = ff-only
```
Verify after: `origin/main == blend tip` AND `git diff origin/main origin/blend == empty`.
**NEVER** force-push, rebase, or rewrite either branch. If a push is ever rejected as non-ff, STOP and assess — it means main acquired an independent commit (a policy violation), do not `--force` past it.

## Owner
Run by CC at seal time; the operator countersigns the RATIFIED-AS-SHIPPED recon block.

## History note
**2026-06-15 (C-TREE-RECON-EXECUTE):** main ff'd `32d0fda → 2147d3b` (8 commits, 0 conflicts; the C-ATPMAIN-RESEAL seal record at 0da1c21 carried forward, LOCKED_DOWN content-sha `bd28613e` unchanged). The earlier "main went stale ~06-03 (`0180497`)" was a **missed mirror cadence, not a divergence** — main never held independent commits. This doc + the at-seal cadence above exist so the next "main went stale" cannot happen: main lagging blend between seals is now the documented normal state, and the seal-time ff is the owner's checklist item.
