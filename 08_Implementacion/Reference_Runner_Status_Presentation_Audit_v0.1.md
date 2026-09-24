# EIOS — Reference Runner Status Presentation Audit v0.1

**Base:** `main @ f5626a7a4b4dab3119c0e806736e1a92a1e43f94`  
**Scope:** human interpretation of the synthetic CLI output.

## Design and audit 1

The negative reference run returns QTG `NO_APTO/BAJA` and MVP execution
`COMPLETED`. Those are distinct facts: QTG expresses functional material
quality; `COMPLETED` expresses that the controlled technical run finished.
The terminal artifact correctly preserves both fields and the synthetic
provenance, but the compact CLI summary did not explain their relationship.
A reader could mistake `COMPLETED` for a quality or operational approval.

## Correction and audit 2

The CLI now prints a short interpretation to stderr after the unchanged JSON
summary on stdout. It labels execution as technical, QTG as functional quality
of a synthetic case, and states that the operational route is forbidden and
no decision authority is granted. It uses the actual status values from the
terminal payload. Both `NO_APTO` and `APTO` variants are checked through the
real command entrypoint, including the written terminal JSON.

No new status, gate, admission, decision, or authority is introduced. The
terminal schema and fingerprint are unchanged. Stderr can be displayed to a
person while stdout remains a single parseable JSON value for tooling.

## Remaining interpretation limit

Completion of individual capabilities is product-test execution. It does not
independently validate every business claim, establish an operational company
mandate, or authorize negotiations or purchases. The reference case remains
synthetic in both variants.
