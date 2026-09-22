# EIOS — PAG002 Counterfactual Due-Date Technical Contract v0.1

**Authority:** `01_Modelo/PAG002_Counterfactual_Due_Date_Authority_v0.1.md`  
**Baseline:** `main @ 798b88e2cc45699ed5d21b23da36c3d830db41f7`  
**Estado:** MATERIALIZADO — CI PENDIENTE

## 1. Componentes

- `build_pag002_counterfactual_payment_schedule`
- `build_pag002_counterfactual_finance_execution`
- `validate_pag002_counterfactual_finance_execution`
- `calculate_finance_basic_scenario_due_dates`

## 2. Provenance de entrada

El productor no acepta carriers derivados desprendidos de plazo.

Reconstruye internamente:

```text
SupplierEvidenceResult + PaymentTermSemanticAuthority
→ OfferedPaymentTermObservation

ResolvedConfiguration(P-PAG-001) + ParameterConfigurationEvidence
→ MinimumPaymentTermResolution
```

La pertenencia del PAYMENT a la operación procede de `DocumentaryPaymentCapture` y su binding explícito.

## 3. Transformación

Solo pago único:

```text
delta_days = minimum_payment_term_days - offered_payment_term_days
counterfactual_due_date = baseline_due_date + delta_days
```

Solo enteros; sin redondeo.

## 4. SCENARIO_ONLY

`CounterfactualPaymentSchedule.mode = SCENARIO_ONLY`.

La fecha simulada no modifica el `CashFlow` factual ni su `due_date`.

El cálculo financiero scenario-only recibe el override de fecha por un canal externo al modelo factual.

## 5. Scenario Engine

Se genera exactamente un `AuthorizedScenarioChange`:

```text
payment_due_date:<flow_id>
baseline → counterfactual
calendar_date
origin = PAG002-CF-DUE-DATE-v0.1
```

`create_scenario` de O2 conserva autoridad exclusiva sobre `scenario_id` y fingerprint.

## 6. Finance Basic

`calculate_finance_basic_scenario_due_dates` reutiliza las mismas fórmulas de Finance Basic pero aplica un override externo de fecha para el cálculo del escenario.

No muta:

- FinanceBasicInput;
- CashFlow;
- evidence_state;
- due_date_evidenced.

No amplía P-FIN-001.

## 7. Revalidación

`validate_pag002_counterfactual_finance_execution` reconstruye:

- escenario O2;
- contexto de escenario;
- resultado Finance Basic scenario-only;

y rechaza ejecuciones desprendidas o alteradas.

## 8. Fuera de alcance

- multicuota;
- días fraccionarios;
- días hábiles;
- festivos;
- FX;
- financiación;
- cambio de importe/moneda/source_ref;
- extensión del horizonte;
- persistencia de la fecha simulada como hecho.
