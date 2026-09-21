# EIOS — PAG001 Offered Payment Term Authority Proposal Audit v0.1

**Baseline:** `main @ 283ad74e6cc253fd533e2ff2a6884cf2443bf2c2`  
**Fecha:** 21/09/2026  
**Estado:** AUDIT 2 DE PROPUESTA — SUPERADA / NO AUTORIZA IMPLEMENTACIÓN

## Hallazgos

### A1 — El dato factual ya existe en Supplier Evidence Core

`SupplierObservation` soporta dimensión `PAYMENT_TERM`, estados KNOWN / NOT_EVIDENCED / CONFLICTING_DATA, valores INTEGER/DECIMAL, unidad, semantic_ref, source_ref, evidence_id, captured_at, vigencia, issues y trace.

Por tanto no se propone un segundo modelo de proveedor.

### A2 — PAYMENT_TERM no equivale por sí solo a plazo ofrecido consumible por Rules

La dimensión es genérica.

Se exige semantic_ref explícita con autoridad upstream para afirmar “plazo ofrecido de la operación actual en días”.

### A3 — Los fixtures no son autoridad

La presencia de ejemplos con `SEM-PAYMENT-DAYS` y `unit=days` demuestra capacidad técnica, no autoridad semántica universal.

No se hardcodea ese literal como fuente de verdad.

### A4 — Multicuota sigue abierta

La cadena documental conserva vencimientos por cuota y asociaciones PAYMENT.

No existe autoridad para reducir varias cuotas a un único plazo.

Se prohíbe esa reducción en esta unidad.

### A5 — Multiplicidad

No existe política autorizada para escoger entre varias observaciones PAYMENT_TERM aplicables.

Se propone `CONFLICTING_DATA` sin selección implícita.

### A6 — Parámetros PAG

La relación funcional de `P-PAG-002/003/004/005` con `R-PAG-001` está documentada, pero P-PAG-003 no tiene transformación exacta cerrada y P-PAG-005 depende de cálculo económico derivado.

Esta unidad no debe saltarse esos gaps.

## Dictamen

La frontera factual puede cerrarse de forma independiente sin inventar semántica de regla.

- DISEÑAR → SUPERADA
- AUDITAR → SUPERADA
- DEPURAR → SUPERADA
- AUDIT 2 → SUPERADA
- CERRAR → BLOQUEADO POR AUTORIZACIÓN HUMANA
- IMPLEMENTAR → BLOQUEADO

**0 bloqueadores documentales para someter PAG001 Offered Payment Term Authority v0.1 a autorización humana.**
