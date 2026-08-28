# U13 — Aceptación C0

## Estado

**APROBADA — 2026-08-28**

## Base de aceptación

La aceptación se realiza sobre el commit `3f08dc009b817477fb385219b20a5710f32b7ce4` de `main`, cuya ejecución de CI `EIOS Tests #44` finalizó con `success`.

## Criterios

- C0 ejecuta el flujo Input Contract → DecisionContext → Evidence → Evidence Validation → Rule → Assessment → Trace.
- La ausencia de evidencia no se transforma en `FALSE`; produce `NOT_EVALUABLE` cuando la regla requiere evidencia.
- `InputContract` y `DecisionContext` mantienen identidad coherente.
- La versión de regla debe coincidir con `DecisionContext.rules_version`.
- `Trace` conserva el contexto material necesario para reproducibilidad.
- `input_fingerprint` identifica de forma determinista el Input Contract material.
- `trace_id` cambia ante cambios materiales del input y permanece estable ante inputs materiales idénticos.
- Golden tests e integration test pasan en CI.
- No se incorpora responsabilidad de Negotiation, Ladder, CRC, LLM, persistencia, API ni ejecución externa al alcance de C0.

## Dictamen

**U13 APROBADA.**

Con esta aceptación queda formalmente cerrado el ciclo U0–U13 de C0. Cualquier evolución posterior deberá entrar como cambio de alcance/versionado y no como modificación implícita del baseline aceptado.
