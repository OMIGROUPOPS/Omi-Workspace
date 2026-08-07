# V38 maker-only machine — 2026-08-07

V38 is a development-804 replay build rooted at `b581cbb58f660939ed9b0c2e88ddc42163dbab9a`. It deletes the executable take path rather than gating it. The machine emits rests only: FALLING retains the V36 no-chase rest; SETTLED tracks bid minus one; RISING rests at the deepest ask level revisited at least twice inside the inherited 300-second receipt horizon. Pair cap, lazy first-fill coupling, the no-clock law, and the hard pre-bell edge remain binding.

The two fill rulers keep separate jobs. `MARKET_UNION_REACH` grades market value using quote-touch with ten-second dwell and five-lot capacity, traded-at-level, or seller-print crossing. `STRICT_PRINT_CROSS` is printed beside it only as replay-build verification.

## Frozen result

Market grade on D=804: 1,604 acted legs, 689 credited legs, 150 completed pairs, and 150 under-par pairs. Frontier `<=93 / <=95 / <=97 / <100 / any` is `7 / 14 / 40 / 150 / 150`. Fill-class conservation is 275 quote-touch, 232 traded-at-level, and 182 print-cross.

Strict build verification: 403 credited legs, 91 completed pairs, 91 under-par pairs, and frontier `9 / 13 / 31 / 91 / 91`.

Against the sealed 637-game / 5,253-cent under-par union-reach answer key, V38 grades 17 MATCHED, 113 SHALLOW, and 507 MISSING. The 414 shallow sides lose 2,960 cents. All 924 measurable residual sides conserve to 4,505 cents (median 2, p75 4, p90 9, max 90).

The ranked residual owner is `RISING_REST_FILLED_SHALLOW`: 298 sides in 280 games and 2,190 measurable cents. Next are V36 falling no-chase rest off reach (185 sides / 699 cents), pair-cap arithmetic (133 / 531), and settled rests filled shallow (71 / 512). Every one of the 1,112 residual sides has exactly one primary layer owner.

Named games: ARNROM reach is 88 but remains incomplete (ROM 39; ARN terminal rest 59). BOSCOP reach is 75 but remains incomplete (BOS 30; COP terminal rest 69). NIKVRB reach is 86 and V38 completes at 97 (NIK 27 + VRB 70), both quote-touch, therefore SHALLOW. GANJAN reach is 98 and V38 completes at 99 (GAN 19 + JAN 80), therefore SHALLOW.

## Construction proof

Two clean builds compared 18 regenerable files byte-for-byte with zero mismatches. Focused V38 tests pass 18/18. The inherited V32, V34, V35, V35.1, and V36 policy suites pass. The frozen forbidden-access receipt records zero holdout, live, runtime-network, order, position, exit, settlement, DCA, and deployment access or mutation.

V38 is a frozen replay result, not a live cutover or operative declaration. No deployment, restart, order, position, exit, or configuration action occurred.
