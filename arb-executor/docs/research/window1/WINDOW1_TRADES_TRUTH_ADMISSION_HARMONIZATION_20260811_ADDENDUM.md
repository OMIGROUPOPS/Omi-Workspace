# Trades-as-truth admission harmonization — 2026-08-11

Status: **EVIDENCE DRIFT FIXED; REQUESTED FANBIG CREDIT BLOCKED FAIL-CLOSED.**

The named `FANBIG|FAN` claim at `653b7f1393adfec23d749de09dfef7591be8397a` joined fields from two different exchange receipts. Epoch `1783854017` identifies receipt `54d11711-fb6b-5bb1-35cc-906d7014588e`, a true **38-cent** print at `2026-07-12T11:00:17.132571Z`, while the active rest was 35 cents. The first canonical 35-cent print after that is receipt `9b39056f-f7c5-5ac7-9a31-b5b715efdccd` at `2026-07-12T15:17:51.137727Z`, after the V47/V48 rest had repriced from 35 to 32 cents at `2026-07-12T15:14:23Z`.

The admission organ is `tradeTruthCredit` at `arb-executor/analysis/window1_v48_trades_as_truth.js:29-38`, called at `arb-executor/analysis/build_window1_v38_maker_only.js:338-339`. The exact binding condition was `print.price <= order.target_cents`: `38 <= 35` was false at the claimed timestamp; `35 <= 32` was false at the actual 35-cent receipt. There is no through-bid, aggressor, ask, dwell, size, or arrival-direction filter in this path.

The focused regression supplies an identified 35-cent print against a 35-cent standing rest while the synthetic book is 38/39. It credits. This proves the book relationship is irrelevant and the executable law already admits a genuine through-bid print.

Accordingly, no policy byte changed. Crediting FAN would require cross-receipt field joining or promotion of carried `last_trade` state into a true print, both forbidden. The harmonization table therefore records `DRIFT->FIXED` on the evidence surface, not a fabricated behavioral fill. Frozen V47/V48 attribution remains byte-bound and has zero changed decision or score rows.

VAULTED: `FANBIG|FAN` is an evidence-join drift, not an admission-organ defect. A fill requires one identified true-print receipt whose timestamp is after the active rest and whose price is at or below that same active rest; fields from distinct receipts never combine.
