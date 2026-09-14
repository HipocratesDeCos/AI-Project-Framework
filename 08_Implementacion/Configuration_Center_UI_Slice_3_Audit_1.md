# EIOS — Configuration Center UI Slice 3 — Audit 1

**Fecha:** 2026-09-13  
**Baseline auditado:** `cd9b06cf8fde00ab25283f76baa497579607f71a`  
**Dictamen:** APTO PARA DEPURACIÓN — 4 reajustes, 0 bloqueos

## A1 — `AWAITING_CONFIRMATION` debe ser coherente con pending real

No basta con confiar en `ConfigurationUIResult.state`. Antes de retener la propuesta local, Slice 3 debe exigir simultáneamente:

- `result.state == "AWAITING_CONFIRMATION"`;
- `controller.has_pending_confirmation is True`.

Cualquier divergencia debe producir `ConfigurationWorkflowError` y no crear confirmación visual.

## A2 — Resultado no-pending no puede dejar pending oculto

Si `prepare()` devuelve un estado distinto de `AWAITING_CONFIRMATION` pero el controlador conserva pending, existiría una propuesta ejecutable no visible.

Aunque Slice 1 cerrado no debería producir este caso, Slice 3 debe detectarlo como incoherencia técnica y fallar cerrado. No debe representar el resultado como ordinario.

## A3 — `APPLIED` requiere `Configuration` real y pending consumido

Tras `confirm()`:

- `APPLIED` solo es aceptable si `result.configuration is not None`;
- el controlador debe haber consumido `has_pending_confirmation`;
- un `APPLIED` sin configuración o con pending todavía activo es incoherencia técnica y no puede actualizar snapshot.

Igualmente, todo resultado de fallo debe llegar con pending consumido conforme al contrato de Slice 1; si no, Slice 3 debe detectarlo.

## A4 — Carga parcial no debe conservar datos previos como si fueran actuales

Durante `refresh()`, si falla `load_detail()`, Slice 3 debe invalidar detalle e histórico previos y marcar `data_ready=False`.

Si el detalle carga pero falla histórico, puede conservar el nuevo detalle, pero el histórico anterior debe sustituirse por `None`; no puede quedar visible como si perteneciera al refresh actual.

## Verificación transversal

- no se reabre Slice 1 ni Slice 2;
- no se crean productores de empresa/parámetro/actor;
- no se inventa histórico tras apply;
- el flag `history_stale` expresa únicamente frescura técnica local;
- no se introduce semántica de reglas, autorización, simulación o decisión.

**Resultado:** incorporar A1–A4 y ejecutar Audit 2 antes de materializar.
