# EIOS — PAG002 Counterfactual Due-Date Authority Proposal v0.1

**Baseline:** `main @ 2776cb85f5fc6e2c112d131e39ed4e4855c1bd69`  
**Fecha:** 22/09/2026  
**Estado:** PROPUESTA — REQUIERE AUTORIDAD HUMANA  
**Gate:** `PAG002-CF-DUE-DATE`

## 1. Propósito

Cerrar de forma mínima y fail-closed la transformación necesaria para construir el escenario financiero `minimum-term` de `R-PAG-002`, sin fabricar fechas contractuales ni promover datos simulados a hechos.

## 2. Alcance v0.1

La propuesta soporta exclusivamente operaciones con:

```text
exactamente 1 PAYMENT CashFlow
explícitamente vinculado a la PurchaseOperation evaluada
```

El pago baseline debe tener:

- amount demostrado;
- currency demostrada;
- due_date explícita;
- `due_date_evidenced = true`;
- source_ref;
- flow_id único;
- vínculo documental/operacional trazable con la operación exacta.

Más de un pago/cuota vinculada:

```text
NOT_EVALUABLE
reason = MULTI_INSTALLMENT_COUNTERFACTUAL_UNSUPPORTED
```

No se agregan, promedian ni desplazan cuotas múltiples.

## 3. Precondiciones de plazo

Se requiere:

```text
OfferedPaymentTermObservation.state = AVAILABLE
MinimumPaymentTermResolution.state = AVAILABLE
```

Para materializar el contrafactual:

```text
minimum_payment_term_days > offered_payment_term_days
```

Si:

```text
offered_payment_term_days >= minimum_payment_term_days
```

no se genera escenario minimum-term porque R-PAG-002 ya queda fuera de su condición específica.

## 4. Días enteros

Aunque los carriers de plazo admiten Decimal, la transformación de una `date` exige días enteros.

Se propone:

```text
offered_payment_term_days ∈ Z>=0
minimum_payment_term_days ∈ Z>=0
```

para este productor.

Valor fraccionario:

```text
NOT_EVALUABLE
reason = NON_INTEGER_PAYMENT_TERM_FOR_DATE_TRANSFORMATION
```

No hay redondeo.

## 5. Transformación autorizable propuesta

```text
delta_days
=
minimum_payment_term_days - offered_payment_term_days

counterfactual_due_date
=
baseline_due_date + delta_days calendar days
```

Esta transformación:

- no necesita elegir `operation_date`, `invoice_date` o `receipt_date` como ancla;
- usa como ancla factual la `baseline_due_date` explícitamente evidenciada;
- conserva la distancia relativa autorizada entre plazo ofrecido y mínimo.

No se permiten ajustes de día hábil, fin de mes, festivos, calendario bancario ni redondeo.

## 6. Preservación exacta del flujo

El flujo contrafactual debe conservar exactamente:

```text
flow_id
flow_type = PAYMENT
amount
currency
source_ref factual baseline
```

y solo cambia:

```text
due_date
```

El cambio de fecha no se etiqueta como hecho factual.

## 7. Frontera SCENARIO_ONLY

La nueva fecha es una hipótesis autorizada, no evidencia factual.

Se propone un carrier:

```text
CounterfactualPaymentSchedule
mode = SCENARIO_ONLY
```

con:

```text
decision_id
baseline_scenario_id
data_snapshot_id
parameters_version
company_scope
article_id
supplier_id
operation_ref
flow_id
baseline_due_date
counterfactual_due_date
offered_payment_term_days
minimum_payment_term_days
delta_days
baseline_source_ref
baseline_evidence_refs
payment_binding_ref
transformation_authority_ref
methodology_ref
trace_refs
```

## 8. Integración con Scenario Engine

La transformación debe materializar un `AuthorizedScenarioChange` equivalente a:

```text
variable = payment_due_date:<flow_id>
base_value = baseline_due_date
simulated_value = counterfactual_due_date
unit = calendar_date
authorization = true
origin = PAG002-CF-DUE-DATE-v0.1
```

O2 conserva identidad, fingerprint y versionado del escenario.

No se crea scenario_id paralelo.

## 9. Finance Basic — simulación separada de hechos

Se propone un wrapper especializado:

```text
PAG002CounterfactualFinanceExecution
```

que:

1. recibe la ejecución Finance Basic baseline provenance-safe;
2. recibe el `CounterfactualPaymentSchedule`;
3. recibe el `ScenarioVersion` autorizado;
4. reconstruye internamente una copia del FinanceBasicInput;
5. modifica exclusivamente la due_date del flow_id autorizado;
6. reutiliza exactamente el mismo horizonte P-FIN-001;
7. recalcula Finance Basic determinísticamente;
8. publica el resultado únicamente dentro del envelope `SCENARIO_ONLY`.

El resultado contrafactual no se expone como una nueva verdad factual ni como un FinanceBasicResult operacional independiente.

## 10. Invariantes de cambio único

Baseline y counterfactual deben conservar:

- DecisionContext salvo la identidad de scenario derivada por O2;
- data_snapshot_id;
- parameters_version;
- company_scope;
- currency;
- opening treasury;
- P-FIN-001 / horizon;
- P-FIN-002;
- todos los collections;
- todos los payments ajenos a la operación;
- amount/currency/source_ref del pago de operación;
- working-capital inputs;
- external liquidity;
- cualquier otra entrada material.

Solo cambia:

```text
due_date del único PAYMENT vinculado a la operación
```

Cualquier otro cambio:

```text
NOT_EVALUABLE
reason = COUNTERFACTUAL_NOT_SINGLE_CHANGE
```

## 11. Horizonte Finance Basic

Si `counterfactual_due_date > horizon_end`:

- no se amplía el horizonte;
- no se modifica P-FIN-001;
- Finance Basic aplica su semántica ya autorizada y excluye el flujo del horizonte.

El resultado sigue significando únicamente viabilidad financiera PAG002 **dentro del horizonte autorizado**, nunca solvencia global.

## 12. Provenance del pago

La vinculación del PAYMENT a la operación debe ser explícita y verificable.

Se admite como base una cadena equivalente a:

```text
DocumentaryPaymentCapture
+
DocumentaryPaymentBinding(installment_ref, flow_id)
+
operation_ref
```

o un productor operacional futuro con autoridad equivalente.

La mera coincidencia de importes, proveedor, fechas o source_ref no demuestra pertenencia.

## 13. Datos sintéticos

Material `SYNTHETIC` puede utilizarse para tests.

Nunca se promueve a `PRESENTED_OPERATIONAL` ni a evidencia operacional.

## 14. NOT_EVALUABLE

El productor debe fallar cerrado ante:

- más de un PAYMENT de operación;
- cero PAYMENT de operación;
- vínculo de operación no demostrable;
- due_date baseline no evidenciada;
- offered/minimum no disponibles;
- días fraccionarios;
- minimum <= offered para materialización;
- identidad/versiones/snapshot incoherentes;
- amount/currency alterados;
- otro flujo alterado;
- overflow temporal;
- scenario change no autorizado;
- conflicto de evidencia.

## 15. No alcance

No se autoriza:

- multicuota;
- vencimiento medio;
- reparto porcentual;
- consolidación de cuotas;
- operación + N días;
- factura + N días;
- recepción + N días;
- días hábiles;
- festivos;
- fin de mes;
- confirming/factoring;
- descuentos;
- financiación;
- FX;
- modificación de importe/precio;
- extensión del horizonte financiero.

## 16. Consecuencia sobre R-PAG-002

Si esta autoridad se aprueba y se materializa, el gate `PAG002-CF-DUE-DATE` quedará cerrado **solo para pago único**.

Entonces podrá construirse provenance-safe:

```text
baseline Finance Basic
+
minimum-term Scenario Finance Basic
→ dos PAG002FinancialStateResolution
→ R-PAG-002
```

Multicuota seguirá fuera de alcance y producirá NOT_EVALUABLE.

## 17. Gates propuestos

```text
PAG002-CF-G01 → solo pago único
PAG002-CF-G02 → due_date baseline evidenciada
PAG002-CF-G03 → integer calendar days
PAG002-CF-G04 → delta = minimum - offered
PAG002-CF-G05 → new_due = baseline_due + delta
PAG002-CF-G06 → SCENARIO_ONLY
PAG002-CF-G07 → AuthorizedScenarioChange / O2 identity
PAG002-CF-G08 → single-change invariant
PAG002-CF-G09 → mismo horizonte Finance Basic
PAG002-CF-G10 → synthetic ≠ operational
PAG002-CF-G11 → multicuota NOT_EVALUABLE
```

## 18. Decisión requerida

Autorizar o corregir antes de materializar el productor y completar `R-PAG-002`.
