# EIOS — Reference Business Case 001: Decision Twin Audit v0.1

**Base:** `main @ 0f251002a08a785f4072fe8a258d6ac36bceff85`  
**Scope:** integrate the authorized provenance-safe Decision Twin invoker in
the existing synthetic reference case.

## Design

Reuse the two O4/O2 scenario inputs and their child-specific C0 assessments
and traces from Reference Business Case 001. Assign distinct, explicit,
transient `representation_ref` values. The public Decision Twin invoker
revalidates Stage 2 and produces a structural comparison at runtime. The
existing reference execution facade invokes it alongside the previously
integrated capabilities.

## Audit 1 — authority and provenance

- Do not pass an already-computed comparison or arbitrary alternative to O1.
  Use `build_provenanced_decision_twin_invoker` and the existing Stage 2 inputs.
- Keep `representation_ref` separate from `scenario_id`. Neither is a
  persisted or selected business alternative.
- The comparison carries source assessments, VF status and traces. It supplies
  no invented conditions, consequences, risks, preference or ranking.

## Audit 2 — execution boundary

- The facade validates the exact bundle, synthetic provenance, QTG receipt and
  consumption, and root purchase/context before executing the MVP once.
- Both Decision Twin and Scenario Coordination independently reconstruct
  provenance-safe Stage 2 from the frozen source inputs. Duplicate
  `representation_ref` is rejected before comparison.
- The physical fixture retains QTG `NO_APTO/BAJA`. The terminal artifact
  remains `SYNTHETIC`, `operational_path=FORBIDDEN`, without operational
  effect or decision authority. A completed comparison does not override QTG.

## Materialization

`tests/test_reference_business_case_001.py` verifies the combined sequence,
trace coverage, empty unsupported fields, authority boundary and duplicate
reference rejection. No production contract or runtime module was changed.
CI status is determined by the pull request and subsequent `main` runs.
