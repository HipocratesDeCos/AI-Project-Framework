# EIOS — PAG002 Financial Viability Counterfactual Authority Proposal v0.1

**Baseline:** `main @ 3ff98d6bbee7b2300d3cddf6ce3792f3eb04c43d`  
**Fecha:** 22/09/2026  
**Estado:** PROPUESTA — REQUIERE AUTORIDAD HUMANA  
**Ámbito:** semántica mínima necesaria para `R-PAG-002 — Plazo de pago insuficiente ante riesgo financiero`.

## 1. Regla documental de partida

La condición vigente de `R-PAG-002` es:

> La operación puede ser viable únicamente si se amplía el plazo de pago.

Resultado vigente:

```text
COMPRAR CONDICIONADO
```

Condición de compra vigente:

```text
conseguir el plazo de pago mínimo establecido
```

Metadata vigente:

```text
R1 / ALTA
```

Esta propuesta no altera esos elementos.

## 2. Problema técnico-semántico identificado

Finance Basic puede calcular de forma determinista una proyección de tesorería desde flujos con `due_date` demostrada.

Sin embargo, EIOS no dispone actualmente de autoridad para transformar:

```text
P-PAG-001 = N días
```

en:

```text
nueva due_date del pago de la compra
```

porque no está autorizado:

- desde qué fecha se cuentan los días;
- si el ancla es pedido, factura, recepción, confirmación u otra fecha;
- cómo se tratan múltiples cuotas;
- si se desplazan todas las cuotas o una parte;
- redondeos/calendarios laborables;
- vencimientos contractuales especiales.

Por tanto, `R-PAG-002` no debe fabricar ese escenario.

## 3. Propuesta de carrier contrafactual

Se propone un carrier explícito:

```text
PaymentTermFinancialViabilityCounterfactual
```

con identidad/provenance mínima:

```text
decision_id
scenario_id
data_snapshot_id
parameters_version
company_scope
article_id
supplier_id
evaluation_date

baseline_payment_term_days
minimum_payment_term_days

baseline_finance_execution_ref
minimum_term_finance_execution_ref

baseline_financial_state
minimum_term_financial_state

baseline_evidence_id
minimum_term_evidence_id

transformation_authority_ref
methodology_ref
trace_refs
```

Estados financieros canónicos propuestos:

```text
VIABLE
NON_VIABLE
NOT_DETERMINABLE
```

## 4. Regla de no fabricación

El carrier contrafactual solo puede ser `AVAILABLE` cuando existen dos ejecuciones financieras trazables y comparables:

1. **baseline** — situación financiera con el plazo de pago realmente ofrecido/demostrado;
2. **minimum-term** — misma operación bajo el plazo mínimo `P-PAG-001`.

La segunda ejecución no puede obtener su calendario de pagos por inferencia dentro de Rules.

Debe proceder de una transformación de calendario de pago expresamente autorizada y trazable.

## 5. Propuesta de criterio financiero

Para esta regla se propone utilizar el mismo límite financiero ya autorizado en Finance Basic / `R-FIN-001`:

```text
treasury_minimum = P-FIN-002
```

Estados:

```text
financial_capacity_forecast >= P-FIN-002
→ VIABLE

financial_capacity_forecast < P-FIN-002
→ NON_VIABLE
```

Si Finance Basic o `P-FIN-002` no son determinables/evidenciados:

```text
NOT_DETERMINABLE
```

Esta clasificación se limita al concepto financiero utilizado por `R-PAG-002`; no declara viabilidad global de la compra.

## 6. Propuesta de condición exacta R-PAG-002

`R-PAG-002 = TRUE` únicamente cuando se demuestra simultáneamente:

```text
P-PAG-004 = ENABLED

AND baseline_payment_term_days < minimum_payment_term_days

AND minimum_payment_term_days = P-PAG-001

AND baseline_financial_state = NON_VIABLE

AND minimum_term_financial_state = VIABLE

AND el único cambio financiero material entre ambas ejecuciones
    es el calendario de pago de la operación evaluada,
    conforme a una transformación autorizada
```

Interpretación:

```text
la operación no supera el criterio financiero con el plazo ofrecido
pero sí lo supera si se consigue como mínimo P-PAG-001
→ COMPRAR CONDICIONADO
```

## 7. FALSE propuesto

Cuando todos los datos necesarios son determinables:

`R-PAG-002 = FALSE` si cualquiera de estos casos queda demostrado:

```text
baseline_financial_state = VIABLE
```

o:

```text
baseline_financial_state = NON_VIABLE
AND minimum_term_financial_state = NON_VIABLE
```

o:

```text
baseline_payment_term_days >= P-PAG-001
```

En estos casos no queda demostrada la condición específica “solo sería viable ampliando hasta el mínimo”.

## 8. NOT_EVALUABLE propuesto

`NOT_EVALUABLE` cuando:

- `P-PAG-004` está DISABLED;
- `P-PAG-004` está ausente/inválido/no evidenciado;
- `P-PAG-001` está ausente/inválido/no evidenciado;
- no existe plazo ofrecido canónico;
- falta una de las dos ejecuciones financieras;
- alguna ejecución financiera no es determinable;
- falta `P-FIN-002` o su evidencia;
- las identidades baseline/counterfactual no son coherentes;
- no existe autoridad de transformación del calendario de pago;
- el contrafactual cambia cualquier otro factor material;
- existe conflicto de datos.

No se convierte ausencia/incertidumbre en FALSE.

## 9. P-PAG-004 — extensión de alcance propuesta

Se propone extender a `R-PAG-002` la semántica ya cerrada para R-PAG-001:

```text
Sí → ENABLED
No → DISABLED → R-PAG-002 NOT_EVALUABLE
missing/invalid/evidence-invalid → NOT_EVALUABLE
```

DISABLED no equivale a FALSE.

## 10. P-PAG-005 — tratamiento propuesto

Se propone que `P-PAG-005` sea contexto económico opcional también para R-PAG-002 y **no prerequisito del core financiero de plazo**.

Por tanto:

- puede enriquecer análisis económico futuro;
- no modifica por sí mismo baseline/minimum-term viability;
- no convierte la regla en NOT_EVALUABLE si falta o está deshabilitado;
- no autoriza ningún cálculo de descuento.

## 11. P-PAG-001

`P-PAG-001` se consume como mínimo de plazo de pago, en días exactos.

Restricciones propuestas:

- valor finito y no negativo;
- unidad canónica `días`;
- `ResolvedConfiguration + ParameterConfigurationEvidence`;
- misma versión/contexto efectivo que P-PAG-004;
- el valor inicial de 60 días sigue pendiente de validación empresarial y no se hardcodea.

## 12. Plazo ofrecido baseline

Se reutiliza el carrier ya autorizado:

```text
SupplierEvidenceResult
→ PaymentTermObservationAdapter
→ OfferedPaymentTermObservation
```

No se autoriza derivación desde cuotas o vencimientos documentales.

## 13. Gate que permanece abierto

Incluso si se autoriza esta propuesta, seguirá abierto un gate independiente:

```text
PAG002-CF-DUE-DATE
```

Debe existir una autoridad/productor que transforme las condiciones de pago de la compra en un calendario contrafactual exacto y trazable.

Hasta entonces:

- puede cerrarse la semántica de R-PAG-002;
- puede definirse su contrato de carrier;
- no debe fabricarse una proyección minimum-term operacional.

## 14. No alcance

No se autoriza:

- asumir `operation_date + P-PAG-001`;
- asumir fecha de factura;
- desplazar cuotas por defecto;
- promedio de vencimientos;
- nuevo scoring financiero;
- nueva política de financiación;
- uso automático de crédito;
- descuento financiero implícito;
- P-PAG-005 como fórmula;
- viabilidad global del negocio.

## 15. Gates propuestos

```text
PAG002-G01 → condición TRUE exacta definida
PAG002-G02 → FALSE exacto definido
PAG002-G03 → NOT_EVALUABLE fail-closed
PAG002-G04 → P-PAG-001 binding definido
PAG002-G05 → P-PAG-004 extensión definida
PAG002-G06 → P-PAG-005 no bloqueante
PAG002-G07 → carrier contrafactual provenance-safe definido
PAG002-G08 → criterio financiero acotado a P-FIN-002
PAG002-CF-DUE-DATE → OPEN / requiere autoridad separada
```

## 16. Decisión requerida

Autorizar o corregir esta propuesta antes de cerrar la autoridad y materializar cualquier componente de `R-PAG-002`.
