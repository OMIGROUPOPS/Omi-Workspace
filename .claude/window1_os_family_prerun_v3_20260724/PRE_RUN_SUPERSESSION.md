# Window-1 PRE-RUN v3 supersession

This freeze supersedes pre-run commits
`a673ac2d813e32b6b328e2d86bbb9506dbadb852` and
`004f9d404ca64a542d12104ac6a6009945a5ee43` before any candidate result
was produced or inspected.

The v2 run failed closed while loading its first event because the older
causal-fit cache did not span the corrected guarded right edge. A complete
inventory found 586 guarded events already covered, 99 events censored by
the start law, and 119 events requiring a later evidence horizon.

The v3 materializer performed no policy evaluation. It retained prior cache
payloads only where their requested horizon covered the corrected guarded
window and rebuilt all 119 shorter horizons from the already-frozen,
hash-verified true-print tape and causal top-five recorder files. The
resulting private cache passed an 804-file validation of event and ticker
identity, cache key/version, horizon coverage, snapshot/print ordering,
unique trade identity, and nonnegative print size.

The v3 PRE-RUN manifest binds:

- 804 compressed cache objects with hash-set SHA-256
  `aad8d055e90bb429f7da87b450dc9c4e2dc6a6ef114e40368535b8953b86425e`;
- cache key
  `b85371c8eb52996f66ac25d9b60f0b41f6fbbba4afe883b135962782ae491b0b`;
- cache version `window1-guarded-event-market-cache-v3`;
- the cache materializer, search runner, execution kernel, start law,
  adapter, candidate grid, feature allowlist, metric contract, source
  artifacts, and all previously frozen private input receipts.

Candidate scoring remains false. The July 24-26 holdout remains unopened and
unqueried.
