# EIOS — Reference Business Case 001: Negotiation Audit v0.1

**Base:** `main @ c6bf0d79162714fbbcaec85507308a2780799bf5`  
**Scope:** complete the synthetic reference capability sequence with NI and Ladder.

## Design

The existing physical synthetic dataset and reference facade remain unchanged.
The test declares a fictional negotiation authority, a demonstrated synthetic
evidence record, minimal conditional content, and the root C0 trace reference.
The public `build_provenanced_ni_ladder_invokers` constructs both capabilities
from the same frozen source, reproducing NI independently before Ladder.

## Audit 1 — source and authority

- No detached NI or Ladder result enters O1. A denied authority state fails
  before NI can produce a result.
- The invented authority is test material only. It represents neither a real
  corporate mandate nor permission to negotiate with a supplier.
- `decision_twin_reference` and `viability_reference` are omitted: the NI
  producer accepts those as references but does not verify causal binding to
  the independently executed upstream capabilities.

## Audit 2 — effect boundary and limitation

- The facade validates the exact synthetic bundle, QTG receipt/consumption,
  root runtime and CaseProvenance, then invokes the closed MVP once.
- The source C0 trace ID is carried into NI and Ladder. The NI producer checks
  nonempty trace references, but **does not itself recompute their relation to
  C0**. This test uses the actual trace from the same root purchase; the
  terminal artifact must not be interpreted as a cross-capability proof.
- QTG remains `NO_APTO/BAJA`; all capabilities may complete as product tests
  without operational effect, admission, approval or decision authority.

## Materialization

`tests/test_reference_business_case_001.py` verifies the complete canonical
sequence, synthetic closure and rejection of `NOT_AUTHORIZED`. No production
contract is modified. CI status is determined by the PR and `main` runs.
