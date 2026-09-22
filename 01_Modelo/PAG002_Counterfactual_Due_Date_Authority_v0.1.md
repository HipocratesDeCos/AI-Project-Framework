# EIOS — PAG002 Counterfactual Due-Date Authority v0.1

**Baseline de autorización:** `main @ 2776cb85f5fc6e2c112d131e39ed4e4855c1bd69`  
**Fecha:** 22/09/2026  
**Estado:** AUTORIZADO Y CORREGIDO  
**Gate:** `PAG002-CF-DUE-DATE`

## 1. Autoridad humana

Se autoriza la propuesta PAG002 Counterfactual Due-Date Authority v0.1 con las correcciones de frontera y provenance descritas en este documento.

## 2. Alcance autorizado v0.1

Solo operaciones con exactamente un `PAYMENT` explícitamente vinculado a la operación evaluada.

Más de un pago/cuota o ausencia de pago inequívocamente vinculado:

```text
NOT_EVALUABLE
```

No se agregan, promedian ni desplazan múltiples cuotas.

## 3. Precondiciones

Se requieren:

```text
OfferedPaymentTermObservation.state = AVAILABLE
MinimumPaymentTermResolution.state = AVAILABLE
```

y:

```text
minimum_payment_term_days > offered_payment_term_days
```

Si `offered >= minimum`, no se materializa escenario minimum-term.

## 4. Días enteros

Para transformación de `date`:

```text
offered_payment_term_days ∈ Z>=0
minimum_payment_term_days ∈ Z>=0
```

Cualquier valor fraccionario:

```text
NOT_EVALUABLE
reason = NON_INTEGER_PAYMENT_TERM_FOR_DATE_TRANSFORMATION
```

No se redondea.

## 5. Fórmula autorizada

```text
delta_days =
minimum_payment_term_days - offered_payment_term_days

counterfactual_due_date =
baseline_due_date + delta_days calendar days
```

La ancla temporal es exclusivamente la `baseline_due_date` evidenciada.

No se autoriza usar por inferencia:

- operation_date;
- invoice_date;
- receipt_date;
- confirmation_date.

## 6. Baseline due_date

La fecha baseline debe ser:

- explícita;
- evidenciada;
- vinculada al único PAYMENT de la operación;
- trazable a la misma decisión/snapshot/contexto.

No basta coincidencia de importe, proveedor o fecha.

## 7. Corrección — fecha simulada nunca es evidencia factual

La `counterfactual_due_date` es una hipótesis autorizada.

Debe viajar únicamente en:

```text
CounterfactualPaymentSchedule
mode = SCENARIO_ONLY
```

No puede:

- usar `evidence_state = DEMONSTRATED`;
- sustituir la baseline factual;
- incorporarse al snapshot como hecho;
- publicarse como obligación contractual real.

## 8. AuthorizedScenarioChange

Debe materializarse exactamente un cambio:

```text
variable = payment_due_date:<flow_id>
base_value = baseline_due_date
simulated_value = counterfactual_due_date
unit = calendar_date
authorization = true
origin = PAG002-CF-DUE-DATE-v0.1
```

O2 conserva la autoridad sobre `scenario_id`, fingerprint y canonicalización.

## 9. Corrección — identidad del escenario

El escenario counterfactual debe derivarse del mismo DecisionContext base mediante O2.

No se admite:

- scenario_id suministrado por el productor;
- fingerprint externo;
- reutilización de ScenarioVersion ajena;
- asociación posterior de un escenario desacoplado.

## 10. Single-change invariant

Baseline y counterfactual deben conservar exactamente:

- data_snapshot_id;
- parameters_version;
- company_scope;
- article_id;
- supplier_id;
- currency;
- opening treasury;
- horizon/P-FIN-001;
- P-FIN-002;
- collections;
- payments ajenos a la operación;
- amount/currency/source_ref del PAYMENT de operación;
- working-capital inputs;
- external liquidity;
- resto de inputs financieros materiales.

Solo cambia:

```text
due_date del único PAYMENT autorizado
```

Cualquier diferencia adicional:

```text
NOT_EVALUABLE
reason = COUNTERFACTUAL_NOT_SINGLE_CHANGE
```

## 11. Finance Basic

Se autoriza un wrapper:

```text
PAG002CounterfactualFinanceExecution
```

que:

1. recibe baseline `ProvenancedFinanceBasicExecution`;
2. recibe `CounterfactualPaymentSchedule`;
3. recibe el `ScenarioVersion` O2 exacto;
4. reconstruye internamente una copia de `FinanceBasicInput`;
5. modifica solo la `due_date` autorizada;
6. reutiliza exactamente el mismo `P-FIN-001`;
7. recalcula Finance Basic;
8. encapsula el resultado como `SCENARIO_ONLY`.

El `FinanceBasicResult` interno contrafactual no adquiere autoridad factual independiente.

## 12. Horizonte

Si:

```text
counterfactual_due_date > horizon_end
```

no se amplía el horizonte.

Finance Basic aplica su semántica vigente.

La interpretación sigue limitada al horizonte financiero autorizado.

## 13. Overflow temporal

Si `baseline_due_date + delta_days` no es representable por el tipo de fecha:

```text
NOT_EVALUABLE
reason = COUNTERFACTUAL_DATE_OVERFLOW
```

No se satura ni corrige automáticamente.

## 14. Documentary Payment

Una cadena válida puede usar:

```text
DocumentaryPaymentCapture
+
DocumentaryPaymentBinding
+
operation_ref
```

como demostración de pertenencia del `flow_id` a la operación.

La captura documental no genera por sí misma la fecha contrafactual.

## 15. Datos sintéticos

`SYNTHETIC` es válido para tests.

Nunca se promueve a evidencia operacional.

## 16. NOT_EVALUABLE

Fail-closed ante:

- cero o múltiples PAYMENT de operación;
- pertenencia del flow no demostrada;
- baseline due_date no evidenciada;
- offered/minimum no disponibles;
- offered/minimum fraccionarios;
- minimum <= offered para materialización;
- identidad/contexto incoherentes;
- cambio no autorizado;
- más de un AuthorizedScenarioChange;
- variable/origin/unit incompatibles;
- amount/currency/source_ref alterados;
- cualquier otro input financiero alterado;
- overflow temporal;
- contradicción de evidencia.

## 17. No alcance

No se autoriza:

- multicuota;
- vencimiento medio;
- reparto porcentual;
- consolidación;
- días hábiles;
- festivos;
- fin de mes;
- confirming/factoring;
- descuentos;
- financiación;
- FX;
- extensión de horizonte;
- cambio de importe/precio/proveedor.

## 18. Gates

```text
PAG002-CF-G01 → CLOSED — solo pago único
PAG002-CF-G02 → CLOSED — baseline due_date evidenciada
PAG002-CF-G03 → CLOSED — días enteros
PAG002-CF-G04 → CLOSED — delta = minimum - offered
PAG002-CF-G05 → CLOSED — new_due = baseline_due + delta
PAG002-CF-G06 → CLOSED — SCENARIO_ONLY
PAG002-CF-G07 → CLOSED — AuthorizedScenarioChange / O2 identity
PAG002-CF-G08 → CLOSED — single-change invariant
PAG002-CF-G09 → CLOSED — mismo horizonte Finance Basic
PAG002-CF-G10 → CLOSED — synthetic ≠ operational
PAG002-CF-G11 → CLOSED — multicuota NOT_EVALUABLE
PAG002-CF-G12 → CLOSED — fecha contrafactual nunca factual
PAG002-CF-G13 → CLOSED — overflow fail-closed
```

## 19. Estado

**PAG002 Counterfactual Due-Date Authority v0.1 — AUTORIZADO Y CORREGIDO.**
