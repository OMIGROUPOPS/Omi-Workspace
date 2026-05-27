# Full open-position audit — OLD (deployed) vs NEW (v6) per leg — 2026-05-27

Read-only via Kalshi API (`/portfolio/positions`, `/portfolio/orders`). **37 open positions**, 34 with a resting sell, 3 naked (hold). Entry price from the bot's own ENTRY/EXIT log (exact fill).

## ⚠️ Two caveats
- **NEW R uses `raw_max` (optimistic) vs OLD `size_qual_max_250`** — not apples-to-apples (\*‘deeper’ partly model optimism).
- **Actual behavior on swap+restart = (c) leave for ALL legs.** Per `exit_swap_diff_2026-05-27.md` Part C: `_load_exit_table` is init-only and reconcile *adopts* existing resting sells. The (a)/(b) columns below are the **v6-rule-implied** action *if honored manually* — the bot will not repost/cancel open exits on its own.

## ATP_MAIN — 14 open

| ticker | cnt | entry | OLD R | resting sell | NEW band | NEW R/act | v6 sell | proposed action | verdict |
|---|---|---|---|---|---|---|---|---|---|
| …27DUCJOD-JOD | 5 | 95 | 4 | 0x0 | 90-94 | R2 | 97 | (a) cancel @0 -> post @97 (R 4->2) | degrades(shallower) |
| …27BASMIC-MIC | 5 | 64 | 36 | 0x0 | 62-64 | R12 | 76 | (a) cancel @0 -> post @76 (R 36->12) | degrades(shallower) |
| …27HURTIA-HUR | 5 | 58 | 19 | 0x0 | 57-58 | R18 | 76 | (a) cancel @0 -> post @76 (R 19->18) | degrades(shallower) |
| …27NAVMEN-MEN | 5 | 53 | 1 | 0x0 | 52-54 | R11 | 64 | (a) cancel @0 -> post @64 (R 1->11) | improves(deeper*) |
| …27RINBER-BER | 5 | 52 | 38 | 0x0 | 52-54 | R11 | 63 | (a) cancel @0 -> post @63 (R 38->11) | degrades(shallower) |
| …27RINBER-RIN | 5 | 49 | 8 | 0x0 | 49-51 | R50 | 98 | (a) cancel @0 -> post @98 (R 8->50) | improves(deeper*) |
| …27NAVMEN-NAV | 5 | 48 | 8 | 0x0 | 47-48 | R11 | 59 | (a) cancel @0 -> post @59 (R 8->11) | improves(deeper*) |
| …27RUUMED-MED | 5 | 31 | 4 | 0x0 | 31-32 | R14 | 45 | (a) cancel @0 -> post @45 (R 4->14) | improves(deeper*) |
| …27COBYIB-YIB | 5 | 28 | 70 | 0x0 | 26-28 | R71 | 98 | (a) cancel @0 -> post @98 (R 70->71) | improves(deeper*) |
| …27KHATRU-TRU | 5 | 23 | 23 | 0x0 | 23-25 | R22 | 45 | (a) cancel @0 -> post @45 (R 23->22) | degrades(shallower) |
| …27SONPAU-SON | 5 | 16 | 4 | 0x0 | 10-16 | R6 | 22 | (a) cancel @0 -> post @22 (R 4->6) | improves(deeper*) |
| …27MACZVE-MAC | 5 | 15 | 42 | 0x0 | 10-16 | R6 | 21 | (a) cancel @0 -> post @21 (R 42->6) | degrades(shallower) |
| …27CERGAS-GAS | 5 | 12 | 17 | 0x0 | 10-16 | R6 | 18 | (a) cancel @0 -> post @18 (R 17->6) | degrades(shallower) |
| …27DUCJOD-DUC | 5 | 6 | 32 | 0x0 | 5-9 | R63 | 69 | (a) cancel @0 -> post @69 (R 32->63) | improves(deeper*) |

## WTA_MAIN — 23 open

| ticker | cnt | entry | OLD R | resting sell | NEW band | NEW R/act | v6 sell | proposed action | verdict |
|---|---|---|---|---|---|---|---|---|---|
| …27BEJSWI-SWI | 5 | 95 | 5 | 0x0 | 90-94 | DISABLE | — | (b) ride to settle (DISABLE->HOLD) | v6 wouldn't enter (DISABLE) |
| …27SVIQUE-SVI | 5 | 93 | 1 | 0x0 | 90-94 | DISABLE | — | (b) ride to settle (DISABLE->HOLD) | v6 wouldn't enter (DISABLE) |
| …27RAKMUC-MUC | 5 | 90 | 7 | 0x0 | 90-94 | DISABLE | — | (b) ride to settle (DISABLE->HOLD) | v6 wouldn't enter (DISABLE) |
| …27KASBAN-KAS | 5 | 88 | 3 | 0x0 | 86-89 | R3 | 91 | (c) leave (R unchanged) | unchanged |
| …27BOUPOT-POT | 5 | 80 | 7 | 0x0 | 79-82 | R11 | 91 | (a) cancel @0 -> post @91 (R 7->11) | improves(deeper*) |
| …27OSTLIN-OST | 5 | 78 | 18 | 0x0 | 76-78 | R10 | 88 | (a) cancel @0 -> post @88 (R 18->10) | degrades(shallower) |
| …27JONBOU-BOU | 5 | 77 | 22 | 0x0 | 76-78 | R10 | 87 | (a) cancel @0 -> post @87 (R 22->10) | degrades(shallower) |
| …27CHWMER-MER | 5 | 66 | 19 | 0x0 | 66-69 | R20 | 86 | (a) cancel @0 -> post @86 (R 19->20) | improves(deeper*) |
| …27PAOSIE-PAO | 5 | 64 | 35 | 0x0 | 62-65 | R36 | 98 | (a) cancel @0 -> post @98 (R 35->36) | improves(deeper*) |
| …27PUTOSO-OSO | 5 | 58 | 37 | 0x0 | 58-59 | R8 | 66 | (a) cancel @0 -> post @66 (R 37->8) | degrades(shallower) |
| …27JOVNAV-JOV | 5 | 53 | 32 | 0x0 | 53-54 | DISABLE | — | (b) ride to settle (DISABLE->HOLD) | v6 wouldn't enter (DISABLE) |
| …27PUTOSO-PUT | 5 | 43 | 53 | 0x0 | 42-44 | R56 | 98 | (a) cancel @0 -> post @98 (R 53->56) | improves(deeper*) |
| …27TEIFRE-TEI | 5 | 41 | 36 | 0x0 | 39-41 | R35 | 76 | (a) cancel @0 -> post @76 (R 36->35) | degrades(shallower) |
| …27CHWMER-CHW | 5 | 35 | HOLD | — | 33-35 | HOLD | — | (c) leave (hold unchanged) | unchanged |
| …27SNISTE-SNI | 5 | 34 | HOLD | — | 33-35 | HOLD | — | (c) leave (hold unchanged) | unchanged |
| …27JONBOU-JON | 5 | 24 | 54 | 0x0 | 22-24 | R45 | 69 | (a) cancel @0 -> post @69 (R 54->45) | degrades(shallower) |
| …27SHNKES-KES | 5 | 23 | 35 | 0x0 | 22-24 | R45 | 68 | (a) cancel @0 -> post @68 (R 35->45) | improves(deeper*) |
| …27LYSCIR-LYS | 5 | 22 | 43 | 0x0 | 22-24 | R45 | 67 | (a) cancel @0 -> post @67 (R 43->45) | improves(deeper*) |
| …27BOUPOT-BOU | 5 | 21 | 43 | 0x0 | 19-21 | R33 | 54 | (a) cancel @0 -> post @54 (R 43->33) | degrades(shallower) |
| …27KOSVOL-VOL | 5 | 14 | 46 | 0x0 | 10-14 | R46 | 60 | (c) leave (R unchanged) | unchanged |
| …27KASBAN-BAN | 5 | 13 | HOLD | — | 10-14 | R46 | 59 | (a) post exit @59 (was hold) | changes(hold->exit) |
| …27RAKMUC-RAK | 5 | 11 | 7 | 0x0 | 10-14 | R46 | 57 | (a) cancel @0 -> post @57 (R 7->46) | improves(deeper*) |
| …27STARYB-STA | 5 | 9 | 15 | 0x0 | 5-9 | R25 | 34 | (a) cancel @0 -> post @34 (R 15->25) | improves(deeper*) |

## PART 3 — aggregate

| category | open | with resting sell | naked(hold) |
|---|---|---|---|
| ATP_MAIN | 14 | 14 | 0 |
| WTA_MAIN | 23 | 20 | 3 |
| **TOTAL** | 37 | 34 | 3 |

**By v6-implied proposed action:** (a) 29, (b) 4, (c) 4

**By verdict:** improves(deeper*): 15, degrades(shallower): 13, v6 wouldn't enter (DISABLE): 4, unchanged: 4, changes(hold->exit): 1

### Net effect vs riding old sells
- **4** open legs sit on cells v6 marks **DISABLE** — v6 wouldn't have entered them; as open positions the cleanest path is ride-to-settle (or keep the existing sell, which is what the bot does on swap).
- **15** legs would get a **deeper** target under v6 (more capture if hit, lower fill odds; raw_max-optimistic), **13** a **shallower** target.
- **Actual deploy impact on these 37 open legs ≈ zero** — the bot adopts existing resting sells on restart; v6 only changes **new** entries after the swap. No per-leg cancel/repost happens without manual action or the entry-path code change.
- A dollar 'net effect' isn't quoted: these are in-play positions whose outcome depends on live fills/settlement; quoting an in-sample raw_max delta would be misleading.

*Read-only. No cancels, reposts, swap, or restart. Operator reviews per-leg actions, then approves deploy.*