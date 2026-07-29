# Window-1 T2 strict sequential oracle and target lap

## Target lap

completions: **131/804**, and **131/692** the tape proves

how many of the 510 we now see: **501/510**

what changed since last lap: one bridge now maps recognized depth to the existing maker target expression. It selected an event target for **501/501** recognized events (500 on both legs). Exposure was not changed, so completions were not expected to move.

Why the old layer refused all 501: the scorer populated `best_selected_target_cents` only from pre-existing action rows. Recognition emitted no action row, so null selection was guaranteed by construction—not by an economic veto.

## Strict sequential oracle over the 501

- Any strict sequential five-contract proof: **266/501**
- Maker-fee combined floor under par: **41/501**
- Negative against available Window-1 reference: **72/501** (72/265 among strict sequential proofs with reference; 1 sequential proof lacks reference)
- Median gap, all strict sequential proofs: **140.20 minutes**
- Median gap, maker-under-par subset: **605.60 minutes**
- Median gap, negative-vs-reference subset: **338.65 minutes**
- Strict-sequence median by category: ATP_CHALL 92.26m (n=136), ATP_MAIN 369.12m (n=51), WTA_CHALL 129.26m (n=25), WTA_MAIN 223.21m (n=54)

Sequencing is enforced: the first leg must have a lawful five-contract fill proof inside its Window 1; only then is the second resting target placed at the first later BBO, and its proof must occur later still inside its own Window 1.

The vault's 41–62 minute figure measured the gap between independently deepest leg moments. This stricter place-after-first-fill oracle is a different estimator, so the gap is not expected to reproduce that range.

The negative-reference count can exceed the under-par count because the event-specific two-leg Window-1 reference is not fixed at par; some reference sums are above 100 cents.

This is not a completion plateau. Recognition moved the loss from never-seen to seen-not-targeted; this lap moves it again to targeted-not-exposed. Exposure is the next layer.

Holdout stayed sealed. Live and network access stayed off.
