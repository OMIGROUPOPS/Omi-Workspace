# Why the 948-row run fail-closed

At 11:42:57–11:43:28 AM ET, an external process replaced the working-tree
versions introduced by commit `2afc3081ccd9c3767dfbf9f62983df33c7baaf12`
with the exact blobs from its parent, without moving `HEAD`.

This was not a hand edit to `live_v4.py` and it was not caused by the replay.
It was a whole-commit worktree rollback:

- `HEAD` remained `2afc3081`.
- Nine tracked paths changed together.
- The diff was 30 insertions and 2,215 deletions.
- Every checked worktree blob matched `HEAD^` byte-for-byte and did not match
  `HEAD`.
- `live_v4.py` changed at 11:43:26.658 ET from HEAD blob
  `c25cd3129248710a665d77eb815a9df6a93c9009` to parent blob
  `05322babf3540227a7a707b9c3ca8280f9146739`.
- The eight workers all raised `RuntimeError: live_v4.py changed during replay`
  and preserved the 948 completed rows.

The exact executable or agent cannot be named from the surviving evidence.
Git records content and ref changes, not the process that wrote a worktree.
The current Codex transcript contains no write command in that interval, and
the Claude session store contains no timestamped action in that interval.
Therefore the strongest honest attribution is:

> An external local process performed a bulk restore/export of the parent
> commit over the active worktree. The specific process identity was not
> recorded.

The subsequent replay was moved to a new clean worktree at the intended commit.

## Checked files

| File | Worktree blob | Parent blob | HEAD blob | Worktree mtime ET |
|---|---|---|---|---|
| `arb-executor/ws_depth_recorder.py` | `62896a7e…` | `62896a7e…` | `d91d465f…` | 11:42:57.981 |
| `arb-executor/tests/test_live_v4_authority_order_contract.py` | `3d52386a…` | `3d52386a…` | `f7a354be…` | 11:43:20.504 |
| `arb-executor/config/deploy_v5_live.json` | `9cd464d5…` | `9cd464d5…` | `38bd5d63…` | 11:43:23.944 |
| `arb-executor/live_v4.py` | `05322bab…` | `05322bab…` | `c25cd312…` | 11:43:26.659 |
| `arb-executor/analysis/window1_live_v4_replay.py` | `0ca50ec4…` | `0ca50ec4…` | `0e18808b…` | 11:43:28.072 |
