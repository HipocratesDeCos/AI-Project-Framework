# EIOS — Reference Business Case 001: Positive Synthetic QTG Audit v0.1

**Base:** `main @ f2e97ecc7dd01f44507502e693be43982363e2ca`  
**Scope:** add a physical, hash-bound synthetic fixture that exercises the full
reference sequence with QTG `APTO/ALTA`.

## Design

Clone the physical semantic reference fixture under
`tests/fixtures/reference_business_case_001_qtg_eligible`. Change only the
flow perimeter's declared limitations and the flow IDs on the three review
findings for horizon classification, attribute support and economic
duplication. Recompute their component SHA-256 values and assign a distinct
dataset ID and explicit synthetic limitations in the manifest. The purchase,
context, payment documents, finance inputs and other component bytes remain
identical to the original fixture.

## Audit 1 — exact material

- The package loader checks the exact inventory and SHA-256 of all 13
  components; the reference classifier binds to the new bundle fingerprint.
- Existing negative `NO_APTO/BAJA` coverage remains in place. A positive
  fixture is a separate dataset and reference case ID, never a mutation or
  promotion of the negative case.
- The positive QTG result is obtained through the existing synthetic producer
  and consumer. No status is assigned by the test or injected into the facade.

## Audit 2 — authority

- The full capability chain uses the canonical root purchase/context from the
  bound bundle and the same public provenance-safe invokers as the negative
  reference case.
- Even with `APTO/ALTA` and a completed MVP, the terminal artifact retains
  `material_nature=SYNTHETIC`, `qtg_mode_policy=SYNTHETIC_TEST_ONLY`,
  `operational_path=FORBIDDEN`, `operational_effect=false`, and
  `decision_authority=false`.
- This fixture demonstrates functional product behavior. It contains no real
  company mandate or operational admission. The C0-bound NI wrapper now
  validates the claimed trace for the runtime purchase/context; derivation of
  NI content and identity of a separately executed C0 invoker remain outside
  that guarantee.

## Materialization

Physical fixture plus one E2E test in `tests/test_reference_business_case_001.py`.
No production code, QTG contract, admission route or MVP signature changes.
CI status is determined by the PR and subsequent `main` workflow runs.
