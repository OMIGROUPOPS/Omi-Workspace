# V41 full-book P&L — the true number

Analysis seat only. Read-only. V41 maker machine (`v41_maker_machine_20260808` @ `96d33316`), **maker-only, zero fees**. Certified closes = pre-match `window1_close_cents` (the audited closing line, ARNROM 62/39). Naked P&L = **certified close − entry** (a maker rests a bid → long the contract at entry, marked to its certified final trading price). Conservation: **804 = 243 completed + 343 naked + 218 skip**. Machine artifact: `…/V41_FULL_BOOK_PNL.json`.

## (1) Completed 243 — locked margin per pair

| category | pairs | locked ¢ |
|---|--:|--:|
| ATP_CHALL | 90 | 280 |
| ATP_MAIN | 66 | 243 |
| WTA_CHALL | 28 | 85 |
| WTA_MAIN | 59 | 124 |
| **total** | **243** | **732** |

The 732¢ hedged locked margin (per contract; 3,660¢ at five lots) — guaranteed regardless of match outcome.

## (2) The naked legs — 343 one-legged games

Every naked game marks its filled leg to its certified close. Of 343: **96 losses (-379¢) · 144 winners (+429¢) · 40 flat · 63 open** (no certified close — the JEA class, position unmarked). **Net priced P&L +50¢** across 280 priced legs.

| stat | ¢ |
|---|--:|
| min / p25 / median / p75 / max | -57 / -1 / 1 / 2 / 51 |
| loss cents / win cents | -379 / +429 |
| **net** | **+50** |

| category | naked n | net ¢ | loss/win/flat |
|---|--:|--:|---|
| ATP_CHALL | 136 | +145 | 31/80/25 |
| ATP_MAIN | 53 | -72 | 31/17/5 |
| WTA_CHALL | 30 | +65 | 0/26/4 |
| WTA_MAIN | 61 | -88 | 34/21/6 |

The naked book is a **near coin-flip that lands barely positive** (144 win / 96 loss / 40 flat, median +1¢, tails −57…+51): unhedged directional noise, not an edge. ATP_CHALL (+145) and WTA_CHALL (+65) carry it; ATP_MAIN (−72) and WTA_MAIN (−88) bleed.

## (3) Skips — 218 games, zero cost

| category | skips |
|---|--:|
| ATP_CHALL | 114 |
| ATP_MAIN | 19 |
| WTA_CHALL | 66 |
| WTA_MAIN | 19 |
| **total** | **218** |

No rest ever filled → no position → zero cost. Nearly half are ATP_CHALL (114).

## (4) The true book — locked margin + naked outcomes

| category | completed locked ¢ | naked P&L ¢ | **net ¢** |
|---|--:|--:|--:|
| ATP_CHALL | 280 | +145 | **+425** |
| ATP_MAIN | 243 | -72 | **+171** |
| WTA_CHALL | 85 | +65 | **+150** |
| WTA_MAIN | 124 | -88 | **+36** |
| **total** | **732** | **+50** | **+782** |

**V41's honest P&L on the dev slate = +782¢ per contract** (maker-only, zero fees) — **+3910¢ ($39.10) at five lots**. The hedged completed book (732¢) is the substance; the naked legs add a thin +50¢; skips cost nothing. For contrast, frozen **V36** grossed 3,350¢ (5-lot) but **paid 8,230¢ in taker fees → portfolio net −4,880¢**: V41's maker-only book is positive exactly where V36's fee-laden book was deeply negative.

## (5) Mechanism tags on every naked leg — why the sibling never filled

| tag | legs | P&L ¢ |
|---|--:|--:|
| **CAP_UNFEASIBLE_AT_ARM** | 134 | -255 |
| **OTHER_SIDE_ONE_WAY** | 96 | +174 |
| **RISER_UNFILLED** | 42 | -1 |
| **OTHER** | 71 | +132 |
| **total** | **343** | **+50** |

- **CAP_UNFEASIBLE_AT_ARM (134 legs, −255¢)** — the PUTJEA class: the implied sibling cap (99 − filled entry) sits below the sibling's reachable price, so it structurally cannot rest and fill. The dominant naked class **and the only money-loser** — the filled leg is the one that ran, leaving a losing naked long.
- **OTHER_SIDE_ONE_WAY (96 legs, +174¢)** — the ROUJAK class: the sibling's state is one-directional (dominant directional ≥70% of decisions; *proxy* for the op's ≥90%-of-transitions, calibrated to ROUJAK/NIKVRB — flagged), so it climbs away and never dips to fill; the filled other leg nets positive.
- **RISER_UNFILLED (42 legs, −1¢)** — the NIKVRB class: the unfilled sibling is a climber that simply never armed a fill (not one-directional); ≈ flat.
- **OTHER (71 legs, +132¢)** — residual.

## Named naked legs

| game · filled | entry | close | **P&L** | outcome | tag | unfilled sibling |
|---|--:|--:|--:|---|---|---|
| PUTJEA · JEA | 64 | — (open) | — | OPEN | CAP_UNFEASIBLE_AT_ARM | PUT (cap 35 < its price; reach none) |

- **ROUJAK · ROU** marks **+3** (a small *winner*, not a loss): entry 43 → certified close 46. Tagged OTHER_SIDE_ONE_WAY — JAK climbed 74% RISING and never dipped to its cap-56 fill. (The 'ROU-class losses' premise is refined by the certified mark: this naked leg landed slightly positive.)
- **NIKVRB · NIK** is a **−6 loss** (entry 25 → close 19), tagged RISER_UNFILLED — VRB (climbing, reach 68 ≤ cap 74) never armed a fill and wasn't one-directional.
- **PUTJEA · JEA** is **open/unmarked** (no certified close), tagged CAP_UNFEASIBLE_AT_ARM — PUT's cap 35 sat below its price, so PUT could never rest feasibly.

## Conservation

804 = 243 completed + 343 naked + 218 skip. Completed 732¢ locked (per contract). Naked 343 = 96 loss / 144 win / 40 flat / 63 open; net priced +50¢. Skips 218 (zero cost). **True book +782¢/contract (+3910¢ five-lot)**. Tags {'OTHER_SIDE_ONE_WAY': 96, 'CAP_UNFEASIBLE_AT_ARM': 134, 'RISER_UNFILLED': 42, 'OTHER': 71} summing 343. Package 96d33316, certified closes = window1_close_cents (57daf3c1). Maker fees zero; V36 net −4,880¢ (5-lot, fee-laden) beside.