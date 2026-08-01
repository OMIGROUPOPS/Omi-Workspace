# VRB print/book clock correction

The 70-cent print occurred at 2026-07-19 07:13:56.179481 AM EDT (epoch 1784459636.179481; T-316:03.820519 scheduled / T-321:03.820519 bell). The latest distinct-prior-second book was 69/70 at 2026-07-19 07:13:52 AM; both book rows stamped 07:13:56 were also 69/70. The ask was 70, not 68.

The print was 93.179481 seconds after visit 1 ended and 85.820519 seconds before visit 2 began. It was outside every 67/68 interval.

| visit | exact half-open interval epoch | scheduled/bell start | bid/ask | prints |
|---:|---|---|---|---|
| 1 | [1784459531, 1784459543) | T-317:49.000000 / T-322:49.000000 | 67/68 | NONE |
| 2 | [1784459722, 1784459781) | T-314:38.000000 / T-319:38.000000 | 67/68 | NONE |
| 3 | [1784460072, 1784460080) | T-308:48.000000 / T-313:48.000000 | 67/68 | NONE |
| 4 | [1784460132, 1784460140) | T-307:48.000000 / T-312:48.000000 | 67/68 | NONE |
| 5 | [1784460195, 1784460200) | T-306:45.000000 / T-311:45.000000 | 67/68 | NONE |
| 6 | [1784460253, 1784460260) | T-305:47.000000 / T-310:47.000000 | 67/68 | NONE |
| 7 | [1784460490, 1784460500) | T-301:50.000000 / T-306:50.000000 | 67/68 | NONE |
| 8 | [1784460551, 1784460560) | T-300:49.000000 / T-305:49.000000 | 67/68 | NONE |
| 9 | [1784460617, 1784461140) | T-299:43.000000 / T-304:43.000000 | 67/68 | NONE |

The streams share a normalized Unix-epoch basis and are directly comparable across distinct seconds. The book source has only one-second precision, so cross-stream order inside one second is not authoritative. Here that limitation is immaterial: the 07:13:52 book and both 07:13:56 book rows all show 69/70.
