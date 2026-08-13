# V52e trace-span provenance audit

**Verdict: EXPORT_ONLY_TRUNCATION; RUNNER_AND MATERIALIZED INPUT ARE FULL_SPAN.**

All 60 legs consume their final bounded materialized receipt. The frozen decision export appears short on 44 legs because it emits book decision evaluations only: print receipts are not decision rows, and credited legs stop producing entry decisions after their terminal fill. No runner cutoff and no short materialization were found.

The corrected receipt-span export records the final decision receipt, terminal credit, final materialized receipt consumed, and frozen edge for every leg. The apparent export-gap distribution is frozen in TRACE_SPAN_PROVENANCE_AUDIT.json. Policy bytes are identical to V52e b09aa22b301205d5d44d683497cf3edc5b177cf8; no observation, score, or input changed (17/30 -> 17/30).

SHEVAN correction: VAN credited 58 at T+45540.556s and SHE credited 34 at T+45677.582s. Neither rest remained standing at the later T+772m VAN crossing or T+792m SHE crossing. The d9d9a4e3 Part-B conditional-standing reading arose from treating decision-export cessation as runner cessation.

The full-804 exam remains held.
