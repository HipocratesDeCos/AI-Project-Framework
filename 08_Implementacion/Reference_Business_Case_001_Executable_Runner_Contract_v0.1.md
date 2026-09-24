# EIOS — Reference Business Case 001 Executable Runner v0.1

**Base:** `main @ e7078fc37a29830d7f65cc0f7feffb789d4da320`  
**Scope:** a runnable synthetic product demonstration using existing closed
capabilities and physical, hash-bound reference fixtures.

## Design

`examples.reference_business_case_001` owns the fictional company material
preparation and one `execute_reference_business_case(variant=...)` entrypoint.
The two permitted variants are `negative` (`NO_APTO/BAJA`) and `qtg-eligible`
(`APTO/ALTA`). It loads an exact fixture, builds the synthetic bundle and QTG
receipt/consumption, derives the canonical root purchase/context, and invokes
the existing reference facade with the eight authorized MVP invokers.

The terminal `ReferenceSimulationExecution` is returned intact. The CLI prints
a concise JSON summary and can write its complete terminal payload to a path
chosen by the caller:

```bash
python -m examples.reference_business_case_001 --variant negative
python -m examples.reference_business_case_001 --variant qtg-eligible --output reference-result.json
```

Run from the repository root after installing project dependencies. The
`--output` file is a product test artifact, not an operational case file.

## Audit 1 — reuse and identity

- Move the former test helpers into `examples/` so the tests and command share
  the same fictional material producers. The generic EIOS core is unchanged.
- Variant selection is a closed enumeration; arbitrary source paths, external
  companies, operational admission and uncontrolled QTG modes are absent.
- The facade recomputes provenance from the exact bundle and checks QTG,
  purchase/context binding, and one controlled MVP call.

## Audit 2 — authority and output

- A favorable QTG result does not promote the case. Both variants retain
  `SYNTHETIC`, `SYNTHETIC_TEST_ONLY`, `FORBIDDEN`, no operational effect, and
  no decision authority.
- The CLI writes the already-produced terminal payload; it does not reconstruct
  or relabel a detached execution outcome.
- The fictional company authority and negotiation content remain test-only.
  C0 trace claims are validated by the bounded NI/Ladder invokers, subject to
  their documented content-derivation and separate C0 execution limits.

## Materialization and verification

- `examples/reference_business_case_001.py` and `examples/__init__.py`;
- existing tests import the shared material producers and verify both runner
  variants;
- direct CLI execution and terminal JSON output were checked locally;
- CI status is determined by the PR and subsequent `main` workflow runs.

## Windows checkout correction

The dataset manifest hashes exact component bytes. Git's `core.autocrlf=true`
can rewrite LF as CRLF during Windows checkout and invalidate those hashes.
`.gitattributes` now marks all `tests/fixtures/**` files `-text`, preserving
their Git blob bytes on every platform. The two affected flow JSON components
and their manifest digests were refreshed so an ordinary pull rewrites those
files in existing checkouts. Their parsed values and QTG semantics are
unchanged. A fresh checkout with `core.autocrlf=true` executed the positive
variant successfully.
