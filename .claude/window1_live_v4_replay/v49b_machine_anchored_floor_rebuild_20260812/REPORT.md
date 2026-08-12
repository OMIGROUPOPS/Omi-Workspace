# V49b machine-anchored floor rebuild

Status: PASS. The staged f36798fc floor defect is removed: V47 reproduces the old 213 impossible credited-leg rows and the executable-stand rebuild contains zero; V49b also contains zero. No policy or replay behavior changed.

## V49b completed pairs — 810 credited legs

- Sum(entry - rebuilt machine floor): **100c**; distribution min/p25/median/p75/p90/max 0/0/0/0/0/8.
- Sum(entry - market-offered true-trade floor): **3544c**.
- Presence premium, defined as the difference: **3444c**; distribution min/p25/median/p75/p90/max 0/0/1/3/10/88.

The arithmetic conserves on all 810 rows. The market-offer ruler is the lowest lawful true trade in the frozen W1 span. The machine ruler is the lowest qualifying ask or true trade at-or-below an actual executable rest while that rest stood. This isolates the counterfactual replay presence premium; it still cannot measure real queue position or live market impact.

Per-category and category-by-price-region distributions are frozen in PRESENCE_PREMIUM_SUMMARY.json and CATEGORY_X_PRICE_REGION.json.
