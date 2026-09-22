# EIOS — PAG002 Financial Viability Counterfactual Authority v0.1

**Baseline de autorización:** `main @ 3ff98d6bbee7b2300d3cddf6ce3792f3eb04c43d`  
**Fecha:** 22/09/2026  
**Estado:** AUTORIZADO Y CORREGIDO  
**Ámbito:** semántica de `R-PAG-002 — Plazo de pago insuficiente ante riesgo financiero`.

## 1. Autoridad humana explícita

Se autoriza la propuesta PAG002 Financial Viability Counterfactual Authority v0.1 con las correcciones de alcance y provenance descritas en este documento.

## 2. Semántica de R-PAG-002

Condición autorizada:

```text
la operación no supera el criterio financiero con el plazo ofrecido
pero sí lo supera si se consigue como mínimo P-PAG-001
```

Resultado activo:

```text
COMPRAR CONDICIONADO
```

Condición de compra:

```text
conseguir al menos el plazo mínimo P-PAG-001
```

Metadata:

```text
R1 / ALTA
```

## 3. Corrección — “viable” queda limitado al criterio financiero PAG002

Los estados `VIABLE` y `NON_VIABLE` de esta autoridad no significan viabilidad global de la compra.

Significan exclusivamente:

```text
PAG002_FINANCIALLY_VIABLE
PAG002_FINANCIALLY_NON_VIABLE
```

evaluados con:

```text
financial_capacity_forecast >= P-FIN-002
→ PAG002_FINANCIALLY_VIABLE

financial_capacity_forecast < P-FIN-002
→ PAG002_FINANCIALLY_NON_VIABLE
```

Si la proyección financiera o `P-FIN-002` no son determinables/evidenciados:

```text
PAG002_FINANCIAL_STATE_NOT_DETERMINABLE
```

## 4. Condición TRUE exacta

`R-PAG-002 = TRUE` únicamente si todas las condiciones siguientes están demostradas:

```text
P-PAG-004 = ENABLED

AND offered_payment_term_days < minimum_payment_term_days

AND minimum_payment_term_days = P-PAG-001

AND baseline_financial_state = PAG002_FINANCIALLY_NON_VIABLE

AND minimum_term_financial_state = PAG002_FINANCIALLY_VIABLE

AND baseline y minimum-term pertenecen a la misma operación,
    misma decisión, escenario, snapshot, versiones,
    empresa, artículo, proveedor, moneda e horizonte

AND el único cambio material autorizado entre ambas ejecuciones
    es el calendario de pago de la operación evaluada
```

## 5. Corrección — contrafactual de cambio único

Entre baseline y minimum-term deben permanecer idénticos:

- decision_id;
- scenario_id;
- data_snapshot_id;
- parameters_version;
- company_scope;
- article_id;
- supplier_id;
- currency;
- Finance Basic horizon;
- opening treasury;
- cobros ajenos a la operación;
- pagos ajenos a la operación;
- working-capital inputs si participan;
- cualquier otra entrada financiera material.

El único cambio permitido es:

```text
payment schedule de la operación evaluada
```

y ese cambio debe proceder de una transformación autorizada.

No se permite mejorar simultáneamente liquidez, importe, precio, proveedor, horizonte, FX u otro factor.

## 6. FALSE exacto

Cuando todos los elementos necesarios son determinables, `R-PAG-002 = FALSE` si se demuestra cualquiera de:

```text
baseline_financial_state = PAG002_FINANCIALLY_VIABLE
```

o:

```text
baseline_financial_state = PAG002_FINANCIALLY_NON_VIABLE
AND minimum_term_financial_state = PAG002_FINANCIALLY_NON_VIABLE
```

o:

```text
offered_payment_term_days >= P-PAG-001
```

En esos casos no queda demostrada la condición específica “solo viable financieramente si se amplía hasta el mínimo”.

## 7. NOT_EVALUABLE

`NOT_EVALUABLE` si ocurre cualquiera de:

- P-PAG-004 DISABLED;
- P-PAG-004 ausente/inválido/no evidenciado;
- P-PAG-001 ausente/inválido/no evidenciado;
- plazo ofrecido no disponible/conflictivo/no determinable;
- falta baseline financiero;
- falta minimum-term financiero;
- alguna ejecución financiera no es determinable;
- P-FIN-002 ausente/inválido/no evidenciado;
- identidades incoherentes;
- snapshots/versiones/horizonte/moneda incompatibles;
- no existe autoridad de transformación del calendario de pago;
- el contrafactual modifica cualquier otro factor material;
- evidencia contradictoria.

NOT_EVALUABLE nunca se degrada a FALSE.

## 8. P-PAG-001

`P-PAG-001` es el plazo mínimo deseado.

Contrato autorizado:

```text
ResolvedConfiguration(P-PAG-001)
+
ParameterConfigurationEvidence(P-PAG-001)
```

Restricciones:

- valor finito;
- valor >= 0;
- unidad canónica `días`;
- parameters_version == DecisionContext.parameters_version;
- company_scope coherente;
- configuración vigente;
- evidence válida y vinculada;
- mismo contexto efectivo que P-PAG-004.

El valor inicial de 60 días no queda aprobado como valor empresarial definitivo por esta autoridad.

## 9. P-PAG-004 — extensión autorizada a R-PAG-002

Se extiende a `R-PAG-002` la semántica ya cerrada:

```text
Sí → ENABLED
No → DISABLED
```

Consecuencia:

```text
DISABLED → R-PAG-002 NOT_EVALUABLE
reason = PAYMENT_TERM_CRITERION_DISABLED
```

DISABLED nunca equivale a FALSE.

Ausencia/configuración inválida/evidence inválida mantienen sus propias causas NOT_EVALUABLE.

## 10. P-PAG-005

`P-PAG-005` permanece contexto económico opcional y separado.

No es prerequisito del core `R-PAG-002`.

No modifica por sí mismo:

- baseline_financial_state;
- minimum_term_financial_state;
- P-PAG-001;
- plazo ofrecido;
- comparador principal.

No autoriza ninguna fórmula de descuento.

## 11. Plazo ofrecido

Se reutiliza:

```text
SupplierEvidenceResult
+
PaymentTermSemanticAuthority
→ OfferedPaymentTermObservation
```

No se deriva desde cuotas/documentos si no existe el escalar explícito autorizado.

## 12. Carrier contrafactual autorizado

Se autoriza el contrato semántico de:

```text
PaymentTermFinancialViabilityCounterfactual
```

Debe identificar, como mínimo:

- decision_id;
- scenario_id;
- data_snapshot_id;
- parameters_version;
- company_scope;
- article_id;
- supplier_id;
- evaluation_date;
- baseline_payment_term_days;
- minimum_payment_term_days;
- baseline_finance_execution_ref;
- minimum_term_finance_execution_ref;
- baseline_financial_state;
- minimum_term_financial_state;
- baseline_evidence_id;
- minimum_term_evidence_id;
- transformation_authority_ref;
- methodology_ref;
- trace_refs.

El carrier no tiene autoridad para fabricar el calendario contrafactual que consume.

## 13. Gate PAG002-CF-DUE-DATE

Permanece abierto:

```text
PAG002-CF-DUE-DATE
```

Se requiere una autoridad/productor específico capaz de transformar las condiciones de pago de la operación exacta en un calendario contrafactual exacto y trazable.

No se autoriza asumir:

- operation_date + P-PAG-001;
- invoice_date + P-PAG-001;
- receipt_date + P-PAG-001;
- desplazamiento uniforme de cuotas;
- vencimiento medio;
- calendario laboral implícito;
- redondeo de días;
- transformación de multicuota.

## 14. Finance Basic

Finance Basic puede reutilizarse para recalcular ambas ejecuciones una vez exista un calendario autorizado.

No se modifica Finance Basic ni su autoridad.

## 15. No alcance

No se autoriza:

- viabilidad global;
- financiación automática;
- uso implícito de pólizas/crédito;
- FX implícito;
- descuento por pronto pago implícito;
- alteración de importe/precio/proveedor;
- transformación de calendario no autorizada;
- R-PAG-003 u otras reglas;
- multicuota por inferencia.

## 16. Gates

```text
PAG002-G01 → CLOSED — TRUE exacto
PAG002-G02 → CLOSED — FALSE exacto
PAG002-G03 → CLOSED — NOT_EVALUABLE fail-closed
PAG002-G04 → CLOSED — P-PAG-001 binding
PAG002-G05 → CLOSED — P-PAG-004 extensión a R-PAG-002
PAG002-G06 → CLOSED — P-PAG-005 no bloqueante
PAG002-G07 → CLOSED — carrier contrafactual
PAG002-G08 → CLOSED — criterio financiero acotado a P-FIN-002
PAG002-G09 → CLOSED — contrafactual de cambio único
PAG002-CF-DUE-DATE → OPEN
```

## 17. Estado

**PAG002 Financial Viability Counterfactual Authority v0.1 — AUTORIZADO Y CORREGIDO.**
