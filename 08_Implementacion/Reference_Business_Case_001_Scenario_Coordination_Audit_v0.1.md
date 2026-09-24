# EIOS — Reference Business Case 001: Scenario Coordination Audit v0.1

**Base:** `main @ 8f11ce074ce30ebca405e73320e37f0de4bbbd00`  
**Scope:** extend the existing synthetic reference case with the authorized
provenance-safe `SCENARIO_COORDINATION` invoker.

## Design

The physical synthetic dataset and its canonical `PurchaseOperation` and
`DecisionContext` remain the root of the execution. O4/O2 prepares two valid
child scenario identities with quantity deltas of one and two. Each child has
its own purchase, context, R-DAT-003 assessment and C0 trace. These sources
enter `ProvenancedScenarioAnalyticsInput`, then the public
`build_provenanced_scenario_coordination_invoker`. The existing reference
execution facade invokes it alongside PRICE, TCO, SUPPLIER_RISK_VALUE and C0.

## Audit 1 and correction

- A detached O2 support result or a fabricated `CapabilityExecution` would
  bypass the public Stage 2 provenance boundary. Use the authorized builder.
- Reusing the root C0 trace for children would break the exact scenario and
  purchase binding. Produce a separate assessment and trace for each child.
- QTG for the physical fixture remains `NO_APTO/BAJA`. A completed scenario
  capability is an analytical test outcome, not admission or decision authority.

## Audit 2

- The runtime root is extracted from the exact bundle. Preparation uses that
  context; the invoker validates its identity at execution time.
- O2 supplies the child IDs. Child assessments and traces are recomputed for
  their exact purchases. A foreign child binding is rejected by the Stage 2
  provenance validation.
- The existing facade still enforces `SYNTHETIC_TEST`, `TEST_ONLY`,
  `operational_path=FORBIDDEN`, `operational_effect=false`, and
  `decision_authority=false`. No QTG, admission, MVP, or operational contract
  is changed.

## Materialization and verification

The integration and negative provenance test are in
`tests/test_reference_business_case_001.py`. Its expected capability order is
QTG, PRICE, TCO, SUPPLIER_RISK_VALUE, C0, SCENARIO_COORDINATION. The scenario
result must contain both child trace IDs in O2 order. CI status is determined
by the pull request and subsequent `main` workflow runs.
