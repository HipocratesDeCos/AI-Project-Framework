# EIOS — PAG001 Offered Payment Term Authority Proposal v0.1

**Baseline:** `main @ 283ad74e6cc253fd533e2ff2a6884cf2443bf2c2`  
**Fecha:** 21/09/2026  
**Estado:** PROPUESTA — NO AUTORIZADA  
**Ámbito:** carrier factual canónico para el “plazo ofrecido” consumible por `R-PAG-001`.

## 1. Problema

`R-PAG-001` exige evaluar `plazo ofrecido < objetivo`.

El repositorio ya dispone de `SupplierEvidenceResult` y `SupplierObservation` con dimensión `PAYMENT_TERM`, incluyendo observaciones numéricas y unidad.

Todavía no existe una autoridad que permita transformar una observación genérica de proveedor en el escalar canónico de Rules:

`offered_payment_term_days`.

La mera presencia de `PAYMENT_TERM` no basta.

## 2. Objetivo

Autorizar una frontera factual mínima y provenance-safe:

`SupplierEvidenceResult → PaymentTermObservationAdapter → OfferedPaymentTermObservation`.

Esta unidad NO implementa todavía `R-PAG-001`.

## 3. Carrier propuesto

`OfferedPaymentTermObservation`:

- decision_id
- scenario_id
- data_snapshot_id
- company_scope
- article_id
- supplier_id
- evaluation_date
- source_observation_id
- offered_payment_term_days
- state
- source_ref
- evidence_id
- semantic_ref
- authority_ref
- methodology_ref
- trace_refs

Estados:

- AVAILABLE
- NOT_EVIDENCED
- CONFLICTING_DATA
- NOT_DETERMINABLE

## 4. Requisitos para AVAILABLE

El adapter solo podrá publicar `AVAILABLE` cuando exista exactamente una observación aplicable que cumpla todos los requisitos:

1. pertenece al `SupplierEvidenceResult` del mismo decision_id, scenario_id, data_snapshot_id, company_scope, article_id, proveedor actual y evaluation_date;
2. `candidate_id is None`;
3. `dimension == PAYMENT_TERM`;
4. `state == KNOWN`;
5. `value_kind == INTEGER` o `DECIMAL`;
6. valor no negativo y finito;
7. `unit == days`;
8. `semantic_ref` declara explícitamente semántica de plazo de pago ofrecido expresado en días mediante autoridad upstream verificable;
9. existen `source_ref`, `evidence_id` y `captured_at`;
10. no existe contradicción no resuelta;
11. `captured_at <= evaluation_date`;
12. si existe vigencia temporal, cubre `evaluation_date`.

## 5. Regla crítica sobre semantic_ref

La propuesta NO canoniza por nombre una cadena concreta como `SEM-PAYMENT-DAYS`.

El adapter no puede inferir semántica desde:

- `dimension == PAYMENT_TERM`;
- `unit == days`;
- nombres de campos;
- fixtures;
- ejemplos;
- texto libre.

Debe existir una `semantic_ref` explícita cuya autoridad upstream declare que el valor representa el plazo de pago ofrecido de la operación actual en días.

Sin esa autoridad: `NOT_DETERMINABLE`.

## 6. Selección y multiplicidad

Cero observaciones aplicables → `NOT_EVIDENCED`.

Una observación plenamente válida → `AVAILABLE`.

Más de una observación aplicable → `CONFLICTING_DATA`.

No se selecciona por última, primera, máxima, mínima, media, más reciente o mayor evidence_id.

Incluso si los valores coinciden, no se deduplica sin autoridad explícita de resolución.

## 7. Tipos numéricos

Si `INTEGER`: `offered_payment_term_days = Decimal(value_integer)`.

Si `DECIMAL`: `offered_payment_term_days = value_decimal`.

No se redondea.

No se convierten semanas/meses a días.

No se interpreta texto como número.

## 8. Fuente documental de cuotas

La cadena documental de pagos/cuotas existente conserva asociaciones por cuota, PAYMENT flows, importes, moneda, vencimientos y cobertura requerida.

Esta propuesta NO deriva automáticamente un único “plazo ofrecido” desde múltiples vencimientos.

No autoriza:

- media ponderada de días;
- primer vencimiento;
- último vencimiento;
- plazo máximo;
- plazo mínimo;
- días desde pedido/confirmación;
- equivalencia financiera de una estructura multicuota.

Esa normalización requiere autoridad separada.

## 9. Relación con R-PAG-001

Esta propuesta cierra únicamente el input factual `OfferedPaymentTermObservation`.

No cierra todavía la condición completa de `R-PAG-001` porque siguen pendientes:

- transformación exacta de `P-PAG-003`;
- tratamiento ejecutivo de `P-PAG-004`;
- cálculo económico derivado de `P-PAG-005`;
- binding de `ResolvedConfiguration + Evidence` para el conjunto PAG;
- política sobre estructuras multicuota cuando no exista observación escalar explícita.

## 10. Relación con R-PAG-002

Fuera de alcance.

Esta propuesta no demuestra viabilidad contrafactual ni condición “solo viable si se amplía plazo”.

## 11. Fail-closed

Debe producir estado no AVAILABLE si existe identidad incompatible, proveedor distinto, candidate_id no nulo, dimensión distinta, estado no KNOWN, tipo no numérico, unidad distinta de days, semantic_ref sin autoridad suficiente, valor negativo/no finito, evidencia/source ausentes, fecha futura, vigencia incompatible, cero observaciones, múltiples observaciones aplicables o contradicción.

## 12. No alcance

No autoriza R-PAG-001, R-PAG-002, fórmula `P-PAG-003`, cálculo `P-PAG-005`, conversión calendario/meses/semanas, multicuota → escalar, OCR, selección documental, inferencia desde due_date, scoring, QTG ni decisión empresarial.

## 13. Gates propuestos

- PAG001-TERM-G01 → identidad/provenance del carrier cerrada
- PAG001-TERM-G02 → semántica payment-term-days explícita
- PAG001-TERM-G03 → multiplicidad fail-closed
- PAG001-TERM-G04 → sin normalización multicuota implícita
- PAG001-TERM-G05 → separación carrier / regla
- PAG001-TERM-G06 → R-PAG-002 fuera de alcance

## 14. Estado

**PAG001 Offered Payment Term Authority v0.1 — PROPUESTA / NO AUTORIZADA.**
