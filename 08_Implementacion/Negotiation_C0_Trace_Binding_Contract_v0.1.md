# EIOS — Negotiation C0 Trace Binding Contract v0.1

**Base:** `main @ 644faef73f231971cd3bffc3fd1b8887df5592a1`  
**Scope:** additive provenance-safe NI/Ladder invokers for explicit C0 traces.

## Design

`build_c0_bound_ni_ladder_invokers` receives negotiation content evidence,
supporting evidences and nonempty `AssessmentTraceBinding` material. At
construction it snapshots every input, rejects duplicate C0 trace IDs and
requires exact set equality with `content_evidence.trace_refs`.

On **each** NI and Ladder invocation it calls the existing public
`validate_assessment_trace_binding` for every association against the runtime
purchase and context. That validator checks the rule/version, context fields,
purchase fingerprint, assessment fingerprint and reproducible trace ID. Only
afterward does the existing NI producer run. Ladder reconstructs NI and its
structure through the existing producers.

## Audit 1 — rejected shortcuts

- A raw trace ID alone proves neither its purchase nor assessment. Use the
  existing C0 association validator; do not recreate a weaker fingerprint.
- A subset of the C0 bindings would leave unclaimed material. Require exact
  equality of trace references and binding IDs, with no duplicates.
- A constructor-only check would permit runtime identity drift. Validate both
  invokers on every call using frozen snapshots.

## Audit 2 — authority and limits

- This boundary proves that NI's claimed C0 trace material belongs to the
  exact runtime purchase/context and an authorized rule. It **does not prove**
  that NI content was derived from C0 or that a separately supplied C0 invoker
  executed these bindings in the same MVP plan.
- Synthetic negotiation authority remains a fictional test declaration. The
  QTG positive and negative reference cases both remain synthetic and barred
  from operational effects.
- Existing public NI/Ladder builders, producers, QTG, admission,
  `run_mvp_execution` and the reference execution facade are unchanged.

## Materialization and verification

- Additive builder in `eios/rules/negotiation_provenance.py`, exported through
  `eios.rules`.
- Reference Business Case 001 uses it for both physical fixtures.
- Negative checks reject an unclaimed trace, a foreign purchase and a changed
  C0 assessment. Existing `NOT_AUTHORIZED` rejection is retained.
- CI status is determined by the PR and subsequent `main` workflow runs.
