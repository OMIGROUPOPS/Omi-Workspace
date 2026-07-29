# Window-1 T2 strict sequential oracle and target lap

**Correction:** the prior 41 count was invalid. It added each leg's five-contract fee total directly to a per-contract price. This report compares total five-contract cost with the $5.00 pair payout.

## Target lap

completions: **131/804**, and **131/692** the tape proves

how many of the 510 we now see: **501/510**

what changed since last lap: one bridge now maps recognized depth to the existing maker target expression. It selected an event target for **501/501** recognized events (500 on both legs). Exposure was not changed, so completions were not expected to move.

Why the old layer refused all 501: the scorer populated `best_selected_target_cents` only from pre-existing action rows. Recognition emitted no action row, so null selection was guaranteed by construction—not by an economic veto.

## Strict sequential oracle over the 501

- Any strict sequential five-contract proof: **199/501**
- Maker-fee combined floor under par: **90/501**
- Negative against available Window-1 reference: **158/501** (158/198 among strict sequential proofs with reference; 1 sequential proof lacks reference)
- Complete within two hours: **49/90**
- Complete within four hours: **75/90**
- Complete within eight hours: **90/90**
- Take more than eight hours: **0/90**
- Median gap, all strict sequential proofs: **90.41 minutes**
- Median gap, maker-under-par subset: **96.94 minutes**
- Median gap, negative-vs-reference subset: **92.26 minutes**
- Strict-sequence median by category: ATP_CHALL 80.82m (n=127), ATP_MAIN 129.37m (n=24), WTA_CHALL 127.78m (n=24), WTA_MAIN 95.34m (n=24)

## Both ordering directions

Every event evaluates leg A then leg B and leg B then leg A before choosing the cheaper lawful path.

- Both directions under par: **24**
- Exactly one direction under par: **66**

## Reconciliation of 437 versus the strict oracle

| successive constraint | survivors | removed at this step |
|---|---:|---:|
| development population | 804 | - |
| two independent five-contract floors exist | 692 | 112 |
| independent floors sum below par, pre-fee | 437 | 255 |
| independent floors remain below $5.00 with maker fees | 364 | 73 |
| any strict post-first-fill sequence exists | 252 | 112 |
| strict sequence still costs below $5.00 | 207 | 45 |
| also belongs to the recognized-501 scope | 90 | 117 |

After binding the raw-V5 reader to the frozen range-ladder window, it finds 0 under-par paths outside the earlier independent-floor contract.

The 437 oracle is asynchronous but independent: it adds each leg's best five-contract floor even when those moments cannot form a post-first-fill path. The strict oracle adds maker fees, waits for leg one's five-contract proof, places leg two only afterward, and then applies the separate 501-event scope.

Sequencing is enforced: the first leg must have a lawful five-contract fill proof inside its Window 1; only then is the second resting target placed at the first later BBO, and its proof must occur later still inside its own Window 1.

The vault's 41–62 minute figure measured the gap between independently deepest leg moments. This stricter place-after-first-fill oracle is a different estimator, so the gap is not expected to reproduce that range.

The negative-reference count can exceed the under-par count because the event-specific two-leg Window-1 reference is not fixed at par; some reference sums are above 100 cents.

This is not a completion plateau. Recognition moved the loss from never-seen to seen-not-targeted; this lap moves it again to targeted-not-exposed. Exposure is the next layer.

Holdout stayed sealed. Live and network access stayed off.
