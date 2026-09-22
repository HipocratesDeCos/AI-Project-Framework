# EIOS — R-PAG-001 Provenance-Safe Core Implementation Audit v0.1

**Fecha:** 22/09/2026  
**Estado:** AUDIT 1 SUPERADA — CI PENDIENTE

## A1 — Semántica

La implementación usa exclusivamente semántica ya autorizada:

- offered payment term carrier;
- target minus tolerance;
- P-PAG-004 control;
- strict less-than comparator;
- equality FALSE;
- R2 / ALTA / NEGOCIAR.

No se introduce nueva fórmula de negocio.

## A2 — Provenance

Los tres elementos obligatorios se reconstruyen desde fuentes upstream autorizadas dentro de la invocación.

No se aceptan:

- OfferedPaymentTermObservation desprendida;
- PaymentTermToleranceResolution desprendida;
- PaymentTermControlResolution desprendida.

## A3 — P-PAG-005

No aparece como dependencia obligatoria del core.

## A4 — Fail closed

Identity mismatch lanza error de integridad.

Estados no utilizables producen NOT_EVALUABLE, nunca FALSE.

## A4.1 — Correcciones de depuración

Antes de CI se endurece la integración:

- P-PAG-002/003/004 deben compartir exactamente el mismo `effective_at` cuando están presentes;
- un mismo `evidence_id` no puede reutilizarse para parámetros PAG distintos;
- incoherencia de contexto o evidencia reutilizada → NOT_EVALUABLE.

## A5 — Tests

Cubren:

- offered < threshold → TRUE;
- offered == threshold → FALSE;
- offered > threshold → FALSE;
- P-PAG-004 disabled;
- missing P-PAG-004;
- offered term ausente;
- offered term conflictivo;
- threshold ausente;
- supplier identity mismatch;
- metadata R2/ALTA/NEGOCIAR;
- ausencia de P-PAG-005 como requisito;
- effective_at incoherente entre P-PAG-002/003/004;
- evidence_id reutilizado entre parámetros.

## Dictamen

**AUDIT 1 SUPERADA — 0 BLOQUEADORES ESTÁTICOS PARA CI.**
