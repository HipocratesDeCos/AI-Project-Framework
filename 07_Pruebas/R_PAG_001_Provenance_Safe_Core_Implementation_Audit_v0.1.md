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

## CI inicial y depuración de integración

CI #1113 sobre `ffe4b0d24743c1e32cfad504b10bfd536550e8c2`: **FAILURE**.

Resultado:

- 2025 tests passed;
- 4 tests failed;
- los 4 fallos correspondían exclusivamente a que R-PAG-001 había sido registrada en el catálogo pero todavía no estaba incorporada a `run_domain_rules` ni a las invariantes de cobertura del catálogo/orquestador.

Corrección aplicada:

- `PaymentTermRuleInputs` añadido al orquestador;
- `evaluate_r_pag_001` integrado en la misma ejecución de dominio;
- invariantes de catálogo actualizadas;
- cobertura del orquestador actualizada de 19 a 20 reglas implementadas.

No se ha cambiado la semántica de R-PAG-001.

**AUDIT 1 DEPURADA — NUEVA CI REQUERIDA.**


## CI de integración #1116 — segunda depuración

CI #1116 sobre `12964e6f69168b7a12639aa6c774670bc80d0155`: **FAILURE**.

Resultado:

- 2029 tests passed;
- 1 test failed;
- fallo exclusivo del helper de monkeypatch del test de orquestación: asumía evaluadores posicionales (`args[2]`), mientras `evaluate_r_pag_001` posee contrato keyword-only y el orquestador lo invoca correctamente con keywords.

Corrección:

- el helper de test admite tanto `args[2]` como `kwargs["rule"]`;
- no se modifica código productivo ni semántica.

**DEPURACIÓN 2 APLICADA — NUEVA CI REQUERIDA.**


## Audit 2 final

CI #1117 sobre `610baa044d5aada9e4107f9dd892c4e9961d7cf1`: **SUCCESS**.

Validado:

- suite Python completa → SUCCESS;
- validación SQL → SUCCESS;
- core R-PAG-001 → integrado en catálogo;
- core R-PAG-001 → integrado en run_domain_rules;
- cobertura de reglas implementadas → 20;
- reconstrucción provenance-safe → preservada;
- P-PAG-005 → no bloqueante;
- no se introdujo semántica adicional durante las dos depuraciones.

```text
DISEÑAR       ✅
AUDITAR       ✅
DEPURAR       ✅
AUDITAR 2     ✅
CERRAR        ✅
MATERIALIZAR  ✅
CI            ✅ #1117
```

**DICTAMEN: R-PAG-001 PROVENANCE-SAFE CORE v0.1 — CERRADO, sujeto únicamente a CI del HEAD documental final y merge.**
